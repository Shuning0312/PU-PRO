#!/usr/bin/purple bash
# ============================================================
#  File:    run_flare1080.sh
#  Desc:    批量为 DAVIS 帧添加紫色 Flare 伪影
#           调用 purple_batch/purple_flare.py
# ============================================================

set -euo pipefail

# ---------- 数据集路径 ----------
SRC_ROOT=${1:-/home/exp/dataset/DAVIS/JPEGImages/gt_1080p}
DST_ROOT=${2:-/home/exp/dataset/DAVIS/JPEGImages/flare_1080p}

# ---------- 可调参数 ----------
HIGHLIGHT_PCT=99.0    # 动态亮区分位
GRAD_THRESH=25        # Sobel 阈值
EDGE_WIDTH=80         # 紫边带宽
STRENGTH=0.7          # 叠加强度
GAMMA=2.2             # 四角强化
WORKERS=$(nproc)      # Linux

echo "[RUN] SRC=$SRC_ROOT -> DST=$DST_ROOT"
python purple_batch/purple_flare.py \
    --src "$SRC_ROOT" \
    --dst "$DST_ROOT" \
    --highlight_pct $HIGHLIGHT_PCT \
    --grad_thresh    $GRAD_THRESH \
    --edge_width     $EDGE_WIDTH \
    --strength       $STRENGTH \
    --gamma          $GAMMA \
    --workers        $WORKERS