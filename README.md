# Sparse-Purple-Fringe Dataset Generator

> 批量将 [**DAVIS**](https://davischallenge.org/davis2017/code.html) 的1080p分辨率的数据转换为带“紫边”、“紫晕”伪影的 `edge_1080p`、`flare_1080p`，。 

本仓库现在同时提供 **两种** 紫边 / 紫晕伪影批量生成器：

| 目标风格                | 输出目录示例       | 脚本文件                      |
|-------------------------|-------------------|-------------------------------|
| 稀疏、细线条状紫边          | `edge_1080p`      | `scripts/run_edge1080.sh`     |
| 大面积、四角渐浓的紫晕  | `flare_1080p`    | `scripts/run_flare1080.sh`|


---

## 1. 环境配置（Conda）

推荐使用专用环境以避免与其他项目冲突；下面以 **`purple`** 环境为例。

```bash
# 创建并激活环境
conda env create -f environment.yml
conda activate purple

# 若无 requirements.yml，可手动安装必要依赖：
# pip install -U numpy opencv-python tqdm
```

## 2. 目录示例

```
dataset/
└── DAVIS/
    └── JPEGImages/
        ├── gt_1080p/           # GT 帧
        │   └── bear/00000.jpg
        └── edge_1080p/         # 运行脚本后自动生成
        │   └── bear/00000.jpg
        └── flare_1080p/        # 紫晕运行后生成
            └── bear/00000.jpg
```

## 3. 启动脚本
> 确保已在 purple 环境中，确认好`/run_*.sh`中的路径。

终端运行👇
```bash
cd PU-PRO
bash ./scripts/run_edge1080.sh
bash ./scripts/run_flare1080.sh
```

## 4. 参数调整

### `run_edge1080.sh`

| 变量        | 作用                 | 典型范围          |
|-------------|----------------------|-------------------|
| **INTENSITY** | 紫边混合强度          | 0.1 – 0.3         |
| **WIDTH**     | 单侧膨胀像素（边宽）   | 1 – 2             |
| **RATIO**     | 著色边缘点比例        | 0.05 – 0.3        |
| **WORKERS**   | 并行进程数           | ≥ CPU 核心数      |

---

### `run_flare1080.sh`

| 变量              | 作用                     | 典型范围        |
|-------------------|--------------------------|-----------------|
| **HIGHLIGHT_PCT** | 动态亮区分位阈值          | 98 – 99.5       |
| **GRAD_THRESH**   | Sobel 边缘阈             | 20 – 40         |
| **EDGE_WIDTH**    | 紫晕带宽（像素）          | 40 – 120        |
| **STRENGTH**      | 叠加强度                 | 0.5 – 0.8       |
| **GAMMA**         | 四角强化 γ 指数          | 1.8 – 2.5       |
| **WORKERS**       | 并行进程数               | ≥ CPU 核心数    |



> 修改方法：编辑 `run_*.sh` 顶部对应变量。



## 5. 常见问题
	1.	RuntimeWarning: invalid value encountered in divide
已在 purple_flare.py 中处理：当图像无紫晕可加时直接跳过，不再保存文件。
	2.	macOS 无 nproc
将脚本中的 $(nproc) 替换为 $(sysctl -n hw.ncpu)。

---
Enjoy your **purple** dataset! 🎉

