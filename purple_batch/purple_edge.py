#!/usr/bin/purple python3
# ============================================================
#  File:    purple_edge.py
#  Author:  Shuning Sun
#  Desc:    批量为视频帧/图像添加稀疏紫边伪影
# ============================================================

import argparse, pathlib, random, multiprocessing as mp, cv2, numpy as np
from functools import partial


# ---------- 单帧紫边增强 ----------
def add_sparse_purple_fringe(img: np.ndarray,
                             intensity: float = 0.2,
                             max_width: int = 1,
                             sparse_ratio: float = 0.1) -> np.ndarray:
    """在 RGB np.uint8 图像上叠加稀疏紫边"""
    img = img.astype(np.float32) / 255.0
    gray = cv2.cvtColor((img * 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)

    edge_idx = np.argwhere(edges > 0)
    if len(edge_idx) == 0:
        return (img * 255).astype(np.uint8)

    idx_sel = edge_idx[np.random.choice(
        len(edge_idx), size=int(len(edge_idx) * sparse_ratio), replace=False
    )]

    mask = np.zeros_like(gray, np.float32)
    for y, x in idx_sel:
        mask[max(0, y - max_width): y + max_width + 1,
             max(0, x - max_width): x + max_width + 1] = 1.0
    mask = cv2.GaussianBlur(mask, (3, 3), 0)

    purple = np.zeros_like(img)
    purple[..., 0], purple[..., 1], purple[..., 2] = 0.6, 0.0, 0.8  # R,G,B

    mask = mask[..., None]
    out = img * (1 - intensity * mask) + purple * (intensity * mask)
    return np.clip(out * 255, 0, 255).astype(np.uint8)


# ---------- worker ----------
def process_one(src_root: pathlib.Path,
                dst_root: pathlib.Path,
                intensity: float,
                max_width: int,
                sparse_ratio: float,
                file_path: pathlib.Path) -> None:
    rel = file_path.relative_to(src_root)
    dst_file = dst_root / rel
    dst_file.parent.mkdir(parents=True, exist_ok=True)

    bgr = cv2.imread(str(file_path))
    if bgr is None:
        print(f"[WARN] Cannot read {file_path}")
        return
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    aug = add_sparse_purple_fringe(rgb, intensity, max_width, sparse_ratio)
    cv2.imwrite(str(dst_file), cv2.cvtColor(aug, cv2.COLOR_RGB2BGR))


# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(
        description="Batch add sparse purple fringe to images.")
    parser.add_argument("--src", required=True,
                        help="Source root (e.g. gt_1080p)")
    parser.add_argument("--dst", required=True,
                        help="Destination root (e.g. edge_1080p)")
    parser.add_argument("--intensity", type=float, default=0.2,
                        help="Blend strength [0.1~0.3]")
    parser.add_argument("--width", type=int, default=1,
                        help="Max edge width in pixels")
    parser.add_argument("--ratio", type=float, default=0.2,
                        help="Sparse edge ratio [0~1]")
    parser.add_argument("--workers", type=int, default=mp.cpu_count(),
                        help="Parallel workers")
    args = parser.parse_args()

    src_root = pathlib.Path(args.src).resolve()
    dst_root = pathlib.Path(args.dst).resolve()
    if not src_root.exists():
        raise FileNotFoundError(src_root)
    dst_root.mkdir(parents=True, exist_ok=True)

    imgs = [p for p in src_root.rglob('*')
            if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}]

    print(f"[INFO] {len(imgs)} images found in {src_root}")
    fn = partial(process_one, src_root, dst_root,
                 args.intensity, args.width, args.ratio)

    with mp.Pool(args.workers) as pool:
        for _ in pool.imap_unordered(fn, imgs):
            pass
    print(f"[DONE] Saved to {dst_root}")


if __name__ == "__main__":
    main()