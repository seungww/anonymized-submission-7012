# pretrain_bytebert.py
import argparse, math, torch, random
from torch.utils.data import DataLoader, random_split
import torch.nn as nn
from datetime import datetime

from bytebert_utils import (
    FullPacketDataset, ByteBERT,
    setup_logger, mask_inputs, make_key_padding_mask,
    VOCAB_SIZE
)

def build_scheduler(optimizer, num_train_steps, warmup_ratio=0.05):
    warmup_steps = max(1, int(num_train_steps * warmup_ratio))
    def lr_lambda(current_step):
        if current_step < warmup_steps:
            return float(current_step) / float(max(1, warmup_steps))
        progress = float(current_step - warmup_steps) / float(max(1, num_train_steps - warmup_steps))
        return 0.5 * (1.0 + math.cos(math.pi * progress)) 
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

def eval_loss(model, dataloader, device, loss_fn):
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        for x, lengths in dataloader:
            x = x.to(device); lengths = lengths.to(device)
            key_pad = make_key_padding_mask(lengths, x.size(1))
            masked, labels = mask_inputs(x) 
            logits = model(masked, key_padding_mask=key_pad)
            loss = loss_fn(logits.view(-1, VOCAB_SIZE), labels.view(-1))
            total += loss.item()
            count += 1
    return total / max(1, count)

def train_loop(
    model, train_loader, val_loader, device, logger,
    epochs=100, mask_prob=0.15, lr=1e-4, model_best_path="model_best.pt",
    model_last_path="model_last.pt", warmup_ratio=0.05, patience=10
):
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    loss_fn = nn.CrossEntropyLoss(ignore_index=-100)
    model.to(device)

    total_steps = epochs * len(train_loader)
    scheduler = build_scheduler(optimizer, total_steps, warmup_ratio)

    best_val = float("inf")
    best_epoch = -1
    no_improve = 0
    global_step = 0

    for epoch in range(1, epochs + 1):
        model.train()
        total_train = 0.0

        for x, lengths in train_loader:
            x = x.to(device); lengths = lengths.to(device)
            key_pad = make_key_padding_mask(lengths, x.size(1))
            masked, labels = mask_inputs(x, mask_prob=mask_prob)
            logits = model(masked, key_padding_mask=key_pad)
            loss = loss_fn(logits.view(-1, VOCAB_SIZE), labels.view(-1))

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            scheduler.step()

            total_train += loss.item()
            global_step += 1

        avg_train = total_train / max(1, len(train_loader))
        val = eval_loss(model, val_loader, device, loss_fn)
        logger.info(f"Epoch {epoch}/{epochs} | Train: {avg_train:.4f} | Val: {val:.4f}")

        if val < best_val:
            best_val = val
            best_epoch = epoch
            torch.save(model.state_dict(), model_best_path)
            logger.info(f"[Best Model Saved] Val: {val:.4f} → {model_best_path}")
            no_improve = 0
        else:
            no_improve += 1

        if no_improve >= patience:
            logger.info(f"[Early Stopping] No improvement for {patience} epochs. Best epoch={best_epoch}.")
            break

    torch.save(model.state_dict(), model_last_path)
    logger.info(f"[Last Model Saved] → {model_last_path}")
    logger.info(f"[Training Completed] Best val: {best_val:.4f} at epoch {best_epoch}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hex_file", type=str, required=True)
    parser.add_argument("--epochs", type=int, default=500)
    parser.add_argument("--batch_size", type=int, default=64)
    parser.add_argument("--mask_prob", type=float, default=0.15)
    parser.add_argument("--max_len", type=int, default=80)
    parser.add_argument("--lr", type=float, default=1e-4)
    parser.add_argument("--warmup_ratio", type=float, default=0.05)
    parser.add_argument("--patience", type=int, default=10)
    parser.add_argument("--val_ratio", type=float, default=0.10)
    args = parser.parse_args()

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"pretrain_{now}.log"
    model_best_path = f"pretrained_model_best_{now}.pt"
    model_last_path = f"pretrained_model_last_{now}.pt"

    logger = setup_logger(log_file)
    device = "cuda" if torch.cuda.is_available() else "cpu"

    full = FullPacketDataset(args.hex_file, max_len=args.max_len)
    val_len = max(1, int(len(full) * args.val_ratio))
    train_len = max(1, len(full) - val_len)
    generator = torch.Generator().manual_seed(42)
    train_set, val_set = random_split(full, [train_len, val_len], generator=generator)

    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=args.batch_size, shuffle=False)

    model = ByteBERT(seq_len=args.max_len)
    train_loop(
        model, train_loader, val_loader, device, logger,
        epochs=args.epochs, mask_prob=args.mask_prob, lr=args.lr,
        model_best_path=model_best_path, model_last_path=model_last_path,
        warmup_ratio=args.warmup_ratio, patience=args.patience
    )

if __name__ == "__main__":
    main()

