# Sparse-Purple-Fringe Dataset Generator

> 批量将 **DAVIS** 的1080p分辨率的数据转换为带“稀疏紫边”伪影的 `edge_1080p`。  

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
            └── bear/00000.jpg
```

## 3. 启动脚本
> 确保已在 purple 环境中，确认好`/run_edge1080.sh`中的路径。

终端运行👇
```bash
cd PU-PRO
bash ./scripts/run_edge1080.sh
```

## 4. 参数调整

| 变量名         | 作用                | 典型范围       |
| ----------- | ----------------- | ---------- |
| `INTENSITY` | 紫边混合强度            | 0.1 – 0.3  |
| `WIDTH`     | 单侧膨胀像素（边宽）        | 1 – 2      |
| `RATIO`     | 着色的边缘点比例          | 0.05 – 0.3 |
| `WORKERS`   | 并行进程数（默认=CPU 核心数） | 4+         |

> 修改方法：编辑 `run_edge1080.sh` 顶部对应变量。

---



Enjoy your **purple** dataset! 🎉

