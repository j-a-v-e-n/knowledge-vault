---
title: "Application of microscopic smartphone attachment for remote preoperative lab testing"
type: source
tags: [即时诊断, 智能手机显微镜, 血细胞计数, 资源匮乏地区, 计算机视觉, ECE284]
sources: [raw/ucsd/Spring 2026/ECE284/Song_2024_SmartphoneMicroscope.pdf]
created: 2026-04-10
updated: 2026-04-10
confidence: high
priority: active
---

# Application of microscopic smartphone attachment for remote preoperative lab testing

> Song & Adams (2024) 将已验证的 m-phone 智能手机显微镜附件从 Android 平台迁移至 iOS，并集成自定义应用程序与 Hough 圆检测算法，构建出一套用于术前化验（血细胞计数）的即时诊断完整系统，在红细胞计数任务上实现 R² = 0.895、召回率 0.9312、精确率 0.8663，处理时间约 1 秒，适用于资源匮乏或远距就医的环境。

---

## 问题背景

### 术前化验的现实障碍
- 术前化验（全血细胞计数、尿液分析等）是手术安全评估的必要前置步骤
- 超过 50% 的美国患者接受了非必要的术前检查；约 1/4 患者需长途旅行（>100 英里）接受先天性心脏病手术
- 检查排队、结果延误 → 择期手术推迟；农村地区样本运输困难、专业人员稀缺
- 解决思路：降低检查成本和门槛，而非削减项目

### m-phone 系统
- 已有研究提出 m-phone：智能手机外接显微镜附件，原用于 Android（OnePlus 9）
- 本研究：验证跨平台迁移（iOS，iPhone 14 Pro Max），集成自定义应用 + 细胞计数算法，形成可部署的完整系统

---

## 系统设计

### 硬件
- 智能手机 + 外接显微镜附件（m-phone）
- 针对 iOS 平台调整：修改支架以适配相机和闪光灯位置
- 光路改进：在光导两端加入玻璃球透镜（ball lens），提高光照均匀度和亮度，减少成像中的污渍伪影

### 软件（iOS 自定义应用）
- 手动对焦 + ISO / 快门时间调节 → 适配不同机型
- 采集后图像传入 Python + OpenCV 处理流水线

### 图 3–4：m-phone 硬件原型与图像处理流程图

![[Song_2024_SmartphoneMicroscope_page05.png]]

> **Fig 3**（上）：iOS m-phone 原型实物图，标注各部件：Ball Lens（入射）、Light Pipe、Ball Lens（出射）、iPhone 14 Pro Max 机身、Optical System（光学组件）、Slide Holder（载玻片支架）、Housing（外壳）。Ball Lens 双端设计提高光照均匀度，减少污渍伪影。
> **Fig 4**（下）：完整图像处理流程图：原始图像 → 裁剪（去暗角）→ 灰度 → 圆形 FOV 掩膜 → min-max 归一化 → 缩放 501×501 px → 高斯滤波（降噪）→ 锐化 → Hough 圆检测 → 输出带标注细胞坐标的图像。

### 细胞计数算法（Hough 圆检测）

```
原始图像
    ↓ 裁剪为正方形（去除暗角）
    ↓ 灰度化
    ↓ 圆形掩膜（仅保留视野 FOV 区域）
    ↓ 像素强度 min-max 归一化
    ↓ 缩放至 501×501 px（降低计算量）
    ↓ 高斯滤波（5×5，降噪）
    ↓ 锐化滤波（增强细胞边缘）
    ↓ Hough 圆检测（OpenCV HoughCircles）
输出：检测到的细胞中心坐标 + 半径
```

**Hough 参数（红细胞）**：最小半径 2.5 μm，最大半径 5 μm，圆心最小间距 4.5 μm（防止重叠误检）。

---

## 实验设计与结果

### 数据集
- 一名研究者的指尖采血血涂片（单张）
- 22 张非重叠图像，人工计数作为 ground truth

### 图像质量
- 像素分辨率：**26.3 px/mm**
- 空间分辨率：**2.19 mm**（与 Android 原型相同）

### 算法性能

| 指标 | 数值 |
|------|------|
| R²（算法计数 vs 人工计数）| **0.895** |
| 召回率（Recall）| **0.9312** |
| 精确率（Precision）| **0.8663** |
| 平均绝对误差（MAE）| **3.36** |
| 均方误差（MSE）| **18.27** |
| 处理时间 | **~1 秒** |

**解读**：高召回率意味着几乎不漏检细胞；相对较低的精确率意味着部分污渍/伪影被误识为细胞。

---

### 图 5–6：结果示例（血涂片图像 + 算法标注）

![[Song_2024_SmartphoneMicroscope_page06.png]]

> **Fig 5**（左）：m-phone 拍摄的血涂片原始图像（左）与算法检测结果（右）——绿色圆圈标注被识别的红细胞，红色圆圈标注被漏检或误识的区域。高召回（0.9312）在图中体现为绿圈覆盖大多数细胞；部分误识（精确率 0.8663）来自污渍/灰尘被误标。
> **讨论摘要**（右）：系统证明了智能手机低成本显微诊断的可行性，处理速度（约 1 秒）和准确度（R²=0.895）满足 POC 应用要求；但数据集规模极小（22 张，单人），泛化性待验证。

---

## 局限性与未来方向

### 当前局限
- 数据集规模极小（22 张图像，单人血样），泛化性未验证
- 算法精确率低于召回率：污渍/灰尘产生 I 类错误
- 硬件光源亮度不足（非全密封，污渍会影响图像质量）
- 目前只处理静态图像，不能分析视频流
- 仅测试红细胞计数，未验证白细胞分类（需更大数据库）

### 未来方向
- 集成微流控通道：直接观测液态样本，无需手动制备血涂片
- 与电子健康记录（EHR）集成，支持数据共享
- 整合 App 与算法（实时视频分析）
- 适配血细胞计数板（hemocytometer）以符合临床标准

---

## ⚠️ 矛盾与未解决问题

1. **极小数据集的可信度**：22 张图像来自单人血样，R² = 0.895 的结论难以代表真实临床场景中的多样性（不同肤色、健康状况、设备型号）。
2. **光照不稳定性**：m-phone 的光路设计（非全密封）对成像稳定性有影响，改进后（加玻璃球透镜）的效果与改进前未做系统对比，改进程度尚不清晰。

---

## 🔗 关联

- [[Bhamla_2017_Paperfuge]] — 同属资源匮乏地区即时诊断工具；paperfuge 提供样本离心预处理，m-phone 提供显微成像计数，两者可互补组成完整 POC 流程
- [[Garg_2025_DopFone]] — 同属"smartphone-as-medical-device"范式；m-phone 用相机做血细胞计数（视觉模态），DopFone 用扬声器+麦克风做胎心率（主动声学模态）——两个互补的智能手机健康感知模态，都瞄准低资源场景

---

## 📎 来源

- `raw/ucsd/Spring 2026/ECE284/Song_2024_SmartphoneMicroscope.pdf`
- Song, K., & Adams, A. T. (2024). Application of microscopic smartphone attachment for remote preoperative lab testing. *Frontiers in Digital Health*, 6, 1461559. DOI: 10.3389/fdgth.2024.1461559
