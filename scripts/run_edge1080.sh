#!/usr/bin/env bash
# ============================================================
#  File: run_edge1080.sh
#  Desc: 调用 purple_batch/025..123
#  purple_edge.py 生成 edge_1080p 数据集
# ============================================================

set -euo pipefail

# ----------- 配置路径 ----------
SRC_ROOT=${1:-/home/exp/dataset/DAVIS/JPEGImages/gt_1080p}
DST_ROOT=${2:-/home/exp/dataset/DAVIS/JPEGImages/edge_1080p}

# 可按需调整默认增强参数
INTENSITY=0.2
WIDTH=1
RATIO=0.2
WORKERS=$(nproc)      # Linux；macOS 用 `sysctl -n hw.ncpu`, 用于获取 CPU 核心数，最大化利用 CPU

echo "[RUN] SRC=$SRC_ROOT  DST=$DST_ROOT"
python purple_batch/purple_edge.py \
    --src "$SRC_ROOT" \
    --dst "$DST_ROOT" \
    --intensity $INTENSITY \
    --width $WIDTH \
    --ratio $RATIO \
    --workers $WORKERS