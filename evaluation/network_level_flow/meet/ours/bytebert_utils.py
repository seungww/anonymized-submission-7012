# bytebert_utils.py
import torch
import torch.nn as nn
from torch.utils.data import Dataset
import logging, sys

# -----------------------------
# Special tokens and vocab
# -----------------------------
MASK_IDX = 256          # [MASK] token
PAD_IDX  = 257          # [PAD] token
VOCAB_SIZE = 258        # 0x00..0xFF + [MASK] + [PAD]

# -----------------------------
# Logger
# -----------------------------
def setup_logger(logfile="debug.log"):
    logger = logging.getLogger("ByteBERT")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO); ch.setFormatter(formatter)
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.INFO); fh.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch); logger.addHandler(fh)
    return logger

# -----------------------------
# Dataset
# -----------------------------
class FullPacketDataset(Dataset):
    # Each line in the hex file corresponds to one packet
    def __init__(self, path, max_len=80):
        self.samples, self.lengths = [], []
        with open(path, "r") as f:
            for line in f:
                hex_bytes = line.strip().split()
                if not hex_bytes:
                    continue
                vals = [int(b, 16) for b in hex_bytes[:max_len]]
                L = len(vals)
                vals += [PAD_IDX] * (max_len - L)
                self.samples.append(vals)
                self.lengths.append(L)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        x = torch.tensor(self.samples[idx], dtype=torch.long)
        L = torch.tensor(self.lengths[idx], dtype=torch.long)
        return x, L

# -----------------------------
# Transformer Model
# -----------------------------
class CustomTransformerLayer(nn.Module):
    def __init__(self, d_model, nhead, dim_feedforward):
        super().__init__()
        self.self_attn = nn.MultiheadAttention(
            d_model, nhead, batch_first=True
        )
        self.linear1 = nn.Linear(d_model, dim_feedforward)
        self.linear2 = nn.Linear(dim_feedforward, d_model)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(0.1)

    def forward(self, x, key_padding_mask=None):
        attn_out, attn_w = self.self_attn(
            x, x, x,
            need_weights=True,
            average_attn_weights=False,
            key_padding_mask=key_padding_mask
        )
        x = self.norm1(x + self.dropout(attn_out))
        x = self.norm2(x + self.dropout(self.linear2(torch.relu(self.linear1(x)))))
        return x, attn_w

class ByteBERT(nn.Module):
    def __init__(self, seq_len=80, emb_dim=512, hidden=256, n_layers=4, n_heads=8):
        super().__init__()
        self.embed = nn.Embedding(VOCAB_SIZE, emb_dim)
        self.pos_embed = nn.Embedding(seq_len, emb_dim)
        self.layers = nn.ModuleList([
            CustomTransformerLayer(emb_dim, n_heads, hidden) for _ in range(n_layers)
        ])
        self.fc = nn.Linear(emb_dim, VOCAB_SIZE)

    def forward(
        self,
        x,
        key_padding_mask=None,
        return_attn=False,
        return_hidden_last=False,
        return_hidden_all=False,
        return_logits=True,
        return_margins=False,
        return_preencoder=False,
    ):
        B, T = x.size()
        pos = torch.arange(0, T, device=x.device).unsqueeze(0).expand(B, T)

        # Pre-encoder sum (input embedding + position embedding)
        h = self.embed(x) + self.pos_embed(pos)
        pre_encoded = h if return_preencoder else None

        all_attn = []
        hidden_per_layer = []  # store token embeddings after each layer

        for layer in self.layers:
            h, attn = layer(h, key_padding_mask=key_padding_mask)
            if return_hidden_all or return_hidden_last:
                hidden_per_layer.append(h)
            if return_attn or return_hidden_all:  # compute only if needed
                all_attn.append(attn)

        logits = self.fc(h) if return_logits or return_margins else None

        advanced_flags = any([return_hidden_last, return_hidden_all, return_margins, return_preencoder])
        if (not return_attn) and (not advanced_flags):
            return logits

        if return_attn and (not advanced_flags) and (not return_hidden_all) and (not return_hidden_last):
            return logits, all_attn

        # Rich return as dict
        out = {}
        if return_logits and logits is not None:
            out["logits"] = logits
        if return_margins and logits is not None:
            # logit margin = top1 - top2 per token
            top2 = torch.topk(logits, k=2, dim=-1).values  # [B,T,2]
            out["margins"] = top2[..., 0] - top2[..., 1]   # [B,T]
        if return_attn:
            out["attn"] = all_attn                          # list[L] of [B,H,T,T]
        if return_hidden_last:
            out["last_hidden"] = hidden_per_layer[-1]       # [B,T,D]
        if return_hidden_all:
            out["all_hidden"] = hidden_per_layer            # list[L] of [B,T,D]
        if return_preencoder:
            out["pre_encoded"] = pre_encoded                # [B,T,D]
        return out

# -----------------------------
# Masking
# -----------------------------
def mask_inputs(inputs, mask_prob=0.15, pad_idx=PAD_IDX, mask_idx=MASK_IDX):
    # Apply random masking for MLM training
    x = inputs.clone()
    labels = inputs.clone()
    randm = torch.rand(x.shape, device=x.device)
    can_mask = (x != pad_idx)
    mask = (randm < mask_prob) & can_mask
    x[mask] = mask_idx
    labels[~mask] = -100
    return x, labels

# -----------------------------
# Padding mask helper
# -----------------------------
def make_key_padding_mask(lengths, T):
    # Returns [B, T] mask; True means PAD position
    device = lengths.device
    ar = torch.arange(T, device=device).unsqueeze(0)
    key_pad = ar >= lengths.unsqueeze(1)
    return key_pad

