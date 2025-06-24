#!/usr/bin/env python3
# ============================================================
#  File:    purple_flare.py
#  Author:  Shuning Sun
#  Desc:    批量为图片添加“紫晕”伪影
# ============================================================

import argparse, pathlib, multiprocessing as mp, cv2, numpy as np
from functools import partial


# ---------- 细腻紫晕核心 ----------
def add_subtle_purple_fringe(img: np.ndarray,
                             highlight_thresh: int = 240,
                             grad_thresh: int = 30,
                             edge_width: int = 3,
                             strength: float = 0.6,
                             radial_gamma: float = 2.2):
    """
    在 BGR uint8 图像上叠加细腻紫晕。

    ▶ 返回:
        - np.ndarray: 有紫晕时的 BGR uint8 图像
        - None      : 无紫晕可加（后续流程将跳过保存）
    """
    h, w = img.shape[:2]
    f_img = img.astype(np.float32)

    # 1) 亮区检测
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bright = (gray > highlight_thresh).astype(np.uint8)
    if not np.any(bright):
        return None                                  # <<< 无亮区 → 跳过

    # 2) Sobel 细边
    sobelx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    grad = cv2.magnitude(sobelx, sobely)
    edge = (grad > grad_thresh).astype(np.uint8)

    # 3) 亮区-边缘交集
    candidates = cv2.bitwise_and(bright, edge)
    if not np.any(candidates):
        return None                                  # <<< 没有交集 → 跳过

    # 4) 膨胀＋羽化 → 紫边宽度
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                       (edge_width, edge_width))
    band = cv2.dilate(candidates, kernel, iterations=1).astype(np.float32)
    band = cv2.GaussianBlur(band, (0, 0), sigmaX=edge_width * 0.6)

    if band.max() < 1e-6:                            # <<< band 全 0 → 跳过
        return None

    # 5) 径向衰减（四角更浓）
    y, x = np.ogrid[:h, :w]
    cx, cy = w / 2, h / 2
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    radial = (dist / dist.max()) ** radial_gamma

    alpha = (band / band.max()) * radial * strength
    alpha = alpha[..., None]

    # 6) 叠加紫色
    purple = np.zeros_like(f_img)
    purple[..., 0], purple[..., 1], purple[..., 2] = 255, 100, 255  # BGR
    out = f_img * (1 - alpha) + purple * alpha
    return np.clip(out, 0, 255).astype(np.uint8)


def auto_percentile_thresh(gray: np.ndarray, pct: float = 99.5) -> int:
    """返回灰度图 pct% 分位数对应的阈值（动态亮区阈）"""
    return int(np.percentile(gray, pct))


# ---------- worker ----------
def _process_one(src_root: pathlib.Path,
                 dst_root: pathlib.Path,
                 highlight_pct: float,
                 grad_thresh: int,
                 edge_width: int,
                 strength: float,
                 radial_gamma: float,
                 file_path: pathlib.Path) -> None:
    rel = file_path.relative_to(src_root)
    dst_file = dst_root / rel
    dst_file.parent.mkdir(parents=True, exist_ok=True)

    bgr = cv2.imread(str(file_path))
    if bgr is None:
        print(f"[WARN] Cannot read {file_path}")
        return

    ht = auto_percentile_thresh(cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY),
                                highlight_pct)
    aug = add_subtle_purple_fringe(bgr, ht, grad_thresh,
                                   edge_width, strength, radial_gamma)

    # ----------- 无紫晕则跳过保存 -----------
    if aug is None:
        return                                            # <<< 直接返回

    cv2.imwrite(str(dst_file), aug)


# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(
        description="Batch add subtle purple fringe to images (skip frames without fringe)")
    parser.add_argument("--src", required=True,
                        help="Source root (e.g. gt_1080p)")
    parser.add_argument("--dst", required=True,
                        help="Destination root (e.g. subtle_1080p)")
    parser.add_argument("--highlight_pct", type=float, default=99.0,
                        help="Percentile for highlight threshold (default 99)")
    parser.add_argument("--grad_thresh", type=int, default=25,
                        help="Sobel gradient threshold")
    parser.add_argument("--edge_width", type=int, default=80,
                        help="Edge band width in pixels")
    parser.add_argument("--strength", type=float, default=0.7,
                        help="Blend strength 0-1")
    parser.add_argument("--gamma", type=float, default=2.2,
                        help="Radial gamma >1 (corner strength)")
    parser.add_argument("--workers", type=int, default=mp.cpu_count(),
                        help="Parallel workers (CPU cores by default)")
    args = parser.parse_args()

    src_root = pathlib.Path(args.src).resolve()
    dst_root = pathlib.Path(args.dst).resolve()
    if not src_root.exists():
        raise FileNotFoundError(src_root)
    dst_root.mkdir(parents=True, exist_ok=True)

    imgs = [p for p in src_root.rglob('*')
            if p.suffix.lower() in {'.jpg', '.jpeg', '.png'}]
    print(f"[INFO] {len(imgs)} images found in {src_root}")

    fn = partial(_process_one, src_root, dst_root,
                 args.highlight_pct, args.grad_thresh,
                 args.edge_width, args.strength, args.gamma)

    with mp.Pool(args.workers) as pool:
        for _ in pool.imap_unordered(fn, imgs):
            pass
    print(f"[DONE] Saved to {dst_root}")


if __name__ == "__main__":
    main()