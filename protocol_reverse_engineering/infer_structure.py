# infer_structure.py
import argparse, torch
from datetime import datetime
from bytebert_utils import (
    FullPacketDataset, ByteBERT,
    setup_logger, make_key_padding_mask, MASK_IDX
)
import numpy as np


def _loo_logits_probs(model, x_1T, L_int, device, mask_token=MASK_IDX):
    T = x_1T.size(1)
    if L_int <= 0:
        return None, None
    x_batch = x_1T.repeat(L_int, 1)
    ar = torch.arange(L_int, device=device)
    x_batch[ar, ar] = mask_token
    lengths = torch.full((L_int,), L_int, device=device, dtype=torch.long)
    key_pad = make_key_padding_mask(lengths, T)
    logits = model(x_batch, key_padding_mask=key_pad)      # [L, T, V]
    probs  = torch.softmax(logits, dim=-1)                 # [L, T, V]
    return logits, probs

def infer_metric_all(model, dataset, device, logger,
                    num_samples=5, display_start=0, display_end=None,
                    th_final=5.0, use_peak=True):
    model.eval()
    with torch.no_grad():
        for i in range(min(len(dataset), num_samples)):
            x, L = dataset[i]
            x = x.unsqueeze(0).to(device)
            L_int = int(L.item())
            if L_int == 0:
                logger.info(f"ByteF {i+1:>2}: [empty display range]")
                continue

            # LOO logits & probs
            logits_loo, probs_loo = _loo_logits_probs(model, x, L_int, device, mask_token=MASK_IDX)
            if logits_loo is None:
                logger.info(f"ByteF {i+1:>2}: [empty display range]")
                continue

            ar = torch.arange(L_int, device=device)
            true_toks = x[0, :L_int]

            # Prob/Entropy/Margin
            p_loo  = probs_loo[ar, ar, true_toks].clamp_min(1e-9)
            H      = (-torch.log2(p_loo)).cpu().numpy()
            top2   = torch.topk(logits_loo[ar, ar, :], k=2, dim=-1)
            margin = (top2.values[:, 0] - top2.values[:, 1]).cpu().numpy()

            # Derivatives
            dH   = np.zeros(L_int, dtype=np.float64)
            curH = np.zeros(L_int, dtype=np.float64)
            dM   = np.zeros(L_int, dtype=np.float64)
            curM = np.zeros(L_int, dtype=np.float64)
            for j in range(1, L_int):
                dH[j] = H[j] - H[j-1]
                dM[j] = margin[j] - margin[j-1]
            for j in range(1, L_int-1):
                curH[j] = H[j+1] - 2.0*H[j] + H[j-1]
                curM[j] = margin[j+1] - 2.0*margin[j] + margin[j-1]

            #w_dH, w_curH, w_dM, w_curM = 0.1, 0.1, 0.5, 0.3
            w_dH, w_curH, w_dM, w_curM = 0.1, 0.1, 0.3, 0.5
            final = np.zeros(L_int, dtype=np.float64)
            for j in range(1, L_int-1):
                final[j] = (w_dH  * abs(dH[j])   +
                            w_curH* abs(curH[j]) +
                            w_dM  * abs(dM[j])   +
                            w_curM* abs(curM[j]))

            # range
            start = max(0, display_start)
            end   = L_int if display_end is None else min(L_int, display_end)
            if start >= end:
                logger.info(f"ByteF {i+1:>2}: [empty display range]")
                continue

            # Boundary flags based on final (threshold + optional peak)
            cond = np.zeros(L_int, dtype=bool)
            cond |= (np.abs(final) >= th_final)

            if use_peak:
                peak = np.zeros(L_int, dtype=bool)
                for j in range(max(start,1), min(end-1, L_int-1)):
                    if final[j] >= final[j-1] and final[j] > final[j+1]:
                        peak[j] = True
                cond &= peak

            hex_tokens = [f"{int(x[0, j].item()):02X}" for j in range(start, end)]
            byte_line = hex_tokens[0]
            for k in range(1, len(hex_tokens)):
                j = start + k
                if cond[j]:
                    byte_line += "|" + hex_tokens[k] 
                else:
                    byte_line += hex_tokens[k] 

            logger.info(f"ByteF {i+1:>2}: {byte_line}")


def print_metric_all(model, dataset, device, logger,
                     num_samples=5, display_start=0, display_end=None,
                     th_dH=5.0, th_curH=5.0, th_dM=5.0, th_curM=5.0, th_final=5.0):
    model.eval()
    with torch.no_grad():
        for i in range(min(len(dataset), num_samples)):
            x, L = dataset[i]
            x = x.unsqueeze(0).to(device)
            L_int = int(L.item())
            if L_int == 0:
                logger.info(f" POS {i+1:>2}: [empty display range]")
                continue

            # LOO logits & probs
            logits_loo, probs_loo = _loo_logits_probs(model, x, L_int, device, mask_token=MASK_IDX)
            if logits_loo is None:
                logger.info(f" POS {i+1:>2}: [empty display range]")
                continue

            ar = torch.arange(L_int, device=device)
            true_toks = x[0, :L_int]

            # Probability (LOO)
            p_loo = probs_loo[ar, ar, true_toks].clamp_min(1e-9)
            prob_vals = p_loo.cpu().numpy()

            # Entropy
            H = (-torch.log2(p_loo)).cpu().numpy()

            # Margin (Top1 - Top2)
            top2 = torch.topk(logits_loo[ar, ar, :], k=2, dim=-1)
            margin = (top2.values[:, 0] - top2.values[:, 1]).cpu().numpy()

            # Derivatives for H
            dH = [0.0] * L_int
            for j in range(1, L_int):
                dH[j] = H[j] - H[j-1]
            curH = [0.0] * L_int
            for j in range(1, L_int-1):
                curH[j] = H[j+1] - 2.0*H[j] + H[j-1]

            # Derivatives for Margin
            dM = [0.0] * L_int
            for j in range(1, L_int):
                dM[j] = margin[j] - margin[j-1]
            curM = [0.0] * L_int
            for j in range(1, L_int-1):
                curM[j] = margin[j+1] - 2.0*margin[j] + margin[j-1]

            w_dH, w_curH, w_dM, w_curM = 0.1, 0.1, 0.3, 0.5
            final = [0.0] * L_int
            for j in range(1, L_int-1):
                final[j] = w_dH * abs(dH[j]) + w_curH * abs(curH[j]) + w_dM * abs(dM[j]) + w_curM * abs(curM[j])

            # display range
            start = max(0, display_start)
            end   = L_int if display_end is None else min(L_int, display_end)
            if start >= end:
                logger.info(f" POS {i+1:>2}: [empty display range]")
                continue

            # Columns
            pos_cols = [f"{j+1:>5}" for j in range(start, end)]
            hex_cols = [f"{int(x[0, j].item()):02X}".rjust(5) for j in range(start, end)]
            prb_cols = [f"{prob_vals[j]:.2f}".rjust(5) for j in range(start, end)]
            H_cols   = [f"{H[j]:.1f}".rjust(5) for j in range(start, end)]
            m_cols   = [f"{margin[j]:.2f}".rjust(5) for j in range(start, end)]

            dH_cols = []
            for j in range(start, end):
                tok = f"{dH[j]:+5.1f}"
                if j == start:
                    dH_cols.append(tok) 
                else:
                    dH_cols.append( ("|" if abs(dH[j]) >= th_dH else " ") + tok )


            cH_cols = []
            for j in range(start, end):
                tok = f"{curH[j]:+5.1f}"
                if j == start:
                    cH_cols.append(tok)
                else:
                    cH_cols.append( ("|" if abs(curH[j]) >= th_curH else " ") + tok )
                    
            dM_cols = []
            for j in range(start, end):
                tok = f"{dM[j]:+5.1f}"
                if j == start:
                    dM_cols.append(tok)
                else:
                    dM_cols.append( ("|" if abs(dM[j]) >= th_dM else " ") + tok )

            cM_cols = []
            for j in range(start, end):
                tok = f"{curM[j]:+5.1f}"
                if j == start:
                    cM_cols.append(tok)
                else:
                    cM_cols.append( ("|" if abs(curM[j]) >= th_curM else " ") + tok )

            final_cols = []
            for j in range(start, end):
                tok = f"{final[j]:+5.1f}"
                if j == start:
                    final_cols.append(tok)
                else:
                    final_cols.append( ("|" if abs(final[j]) >= th_final else " ") + tok )

            # Logging
            logger.info(f" POS {i+1:>2}: " + " ".join(pos_cols))
            logger.info(f" HEX {i+1:>2}: " + " ".join(hex_cols))
            logger.info(f"Prob {i+1:>2}: " + " ".join(prb_cols))
            logger.info(f"Entr {i+1:>2}: " + " ".join(H_cols))
            logger.info(f" dH  {i+1:>2}: " + "".join(dH_cols))
            logger.info(f"curH {i+1:>2}: " + "".join(cH_cols))
            logger.info(f"Marg {i+1:>2}: " + " ".join(m_cols))
            logger.info(f" dM  {i+1:>2}: " + "".join(dM_cols))
            logger.info(f"curM {i+1:>2}: " + "".join(cM_cols))
            logger.info(f" Res {i+1:>2}: " + "".join(final_cols))
            logger.info("")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--hex_file", type=str, required=True)
    parser.add_argument("--model_path", type=str, required=True)
    parser.add_argument("--num_examples", type=int, default=5)
    parser.add_argument("--max_len", type=int, default=80)
    parser.add_argument("--display_start", type=int, default=0)
    parser.add_argument("--display_end", type=int, default=None)
    args = parser.parse_args()

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"infer_structure_{now}.log"
    logger = setup_logger(log_file)

    device = "cuda" if torch.cuda.is_available() else "cpu"

    dataset = FullPacketDataset(args.hex_file, max_len=args.max_len)
    model = ByteBERT(seq_len=args.max_len)
    state = torch.load(args.model_path, map_location=device)
    model.load_state_dict(state)
    model.to(device)

    infer_metric_all(model, dataset, device, logger, num_samples=args.num_examples, display_start=args.display_start, display_end=args.display_end, th_final=1.0)
    # print_metric_all(model, dataset, device, logger, num_samples=args.num_examples, display_start=args.display_start, display_end=args.display_end,th_dH=1.0, th_curH=1.0, th_dM=1.0, th_curM=1.0)


if __name__ == "__main__":
    main()

