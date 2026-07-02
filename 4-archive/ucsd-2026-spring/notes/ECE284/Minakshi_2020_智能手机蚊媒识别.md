---
title: "Automating the Surveillance of Mosquito Vectors from Trapped Specimens Using Computer Vision Techniques"
type: source
tags: [ECE284, 计算机视觉, 智能手机, CNN, 蚊媒监测, 公共卫生, transfer-learning, Inception-ResNet]
sources:
  - raw/ucsd/Spring 2026/ECE284/3378393.3402260.pdf
authors: Mona Minakshi, Pratool Bharti, Willie B. McClinton III, Jamshidbek Mirzakhalov, Ryan M. Carney, Sriram Chellappan
journal: ACM SIGCAS COMPASS '20, June 15-17 2020, Ecuador
doi: 10.1145/3378393.3402260
year: 2020
created: 2026-05-18
updated: 2026-05-18
confidence: high
priority: active
---

# Minakshi et al. 2020 — 智能手机 + CNN 自动化蚊媒 species 识别

> University of South Florida：25,867 张智能手机图（来自 250 个 trapped specimen），Inception-ResNet V2 + transfer learning，**genus 级 92-93.5% accuracy**；最高 species 准确率出现在 **Ae. aegypti（Zika/dengue 关键 vector）** 和 **An. stephensi（malaria 关键 vector）**——这两个最致命 vector 恰好最易识别。用 last conv layer feature map 验证模型在看 thorax / wings / abdomen / legs 正确解剖位置。

---

## 这项研究在解决什么问题？

**蚊媒监测靠 70 岁老 taxonomist 在显微镜下手动识别，全球都在断代——而蚊媒病每年致死 > 100 万人。**

具体：
- 全球 4,500 蚊种，但只有少数 vector 能传 disease
- 公共卫生 workers 设很多 mosquito traps，每天收获几百只蚊子
- Trapped specimen 全送 lab → expert 显微镜下逐只看 → 鉴定 genus + species
- 这个流程：**长 / 累 / 紧 / 需多年经验** + 印度/南美/SSA "all close to 70 yrs old"、taxonomy "is indeed a dying field"
- **目标**：把"看显微镜识别"自动化到"用智能手机拍照 → cloud 上跑 CNN → 直接 dashboard 报警"

## 核心论点（一句话）

**Smartphone 拍 trapped mosquito + Inception-ResNet V2 transfer learning，genus 级 92-93.5% accuracy；species 级整体 80%，但**最致命的 vector（Ae. aegypti / An. stephensi）准确率最高**——意味着可在 low-income 国家 deploy 实用化蚊媒监测系统。**

---

## 数据集

### 采集 setup
- 时间：Fall 2018 - Spring 2019
- 地点：Hillsborough County, Florida 的 mosquito control board traps
- 抓 → 冷冻 → lab → expert 鉴定
- **CO2 trap 只吸引怀孕雌蚊**（因为吸血提供产卵营养）→ dataset 全是 female specimens

### 选择 9 个 species（3 genera × 3 each）
| Genus | Species | Disease 传播 | Geo |
|---|---|---|---|
| Aedes | **aegypti** | Chikungunya, Dengue, Yellow Fever, **Zika** | 4 大洲 |
| Aedes | infirmatus | Eastern Equine Encephalitis | NA, SA |
| Aedes | taeniorhynchus | EEE, West Nile | NA, SA |
| Anopheles | crucians | Malaria | Africa, NA, SA |
| Anopheles | quadrimaculatus | Malaria | NA |
| Anopheles | **stephensi** | **Malaria** | Africa, Asia |
| Culex | coronator | St. Louis EE, West Nile | Africa, NA, SA |
| Culex | nigripalpus | EEE, St. Louis EE, West Nile | Africa, NA, SA |
| Culex | salinarius | EEE, St. Louis EE, West Nile | Africa, NA, SA |

**全部 8 种 wild trapped；只 An. stephensi 是 Florida lab 养（祖先 India trapped）**

### 拍照方法
- 250 specimens 鉴定后，每个用 smartphone 拍多张
- **10 部 phones**: Samsung Galaxy S8 (×3), S9 (×2), iPhone 7 (×2), iPhone 8 plus (×2), Pixel 3 (×1)
- **3 backgrounds**: white / pink / cream tile
- **3 orientations**
- → **6,807 original images**
- + augmentation: zoom 105-150% / 75-90% / brightness ±5-50% → **25,867 final images**

---

## 方法：架构 + Transfer Learning

### Pre-processing：Non-Local Means Denoising
$$NL[v](i) = \sum_{j \in I} w(i,j) v(j)$$
- weight $w(i,j) \in [0,1]$，基于 pixel 周围 RGB block similarity
- 标准化：$\sum_j w(i,j) = 1$
- 处理 smartphone camera 的 random noise / fixed pattern / banding noise
- target pixel neighborhood = 7×7，filter h = 10

### Backbone: Inception-ResNet V2 (IRV2)
- 782 layers
- Pre-trained on **ImageNet** (14M images, 1000 classes)
- 选 IRV2 因为：Inception 解决 mosquito 在图中可以任意 size+position 问题；ResNet residual connections 防止 deep network gradient vanishing

### 3 个 sub-problem
1. **Genus-only** (3 classes: Aedes / Anopheles / Culex)
2. **Species within genus** (3 classes × 3 architectures)
3. **Species directly** (9 classes)

### Genus Architecture (Table 2)
从 IRV2 layer 433 开始，加：
```
block17_10_conv (input: None, 17, 17, 384) → output (None, 17, 17, 1088)
GlobalAveragePooling → (1, 1088)
dense_1: 1088 → 512
dense_2: 512 → 256
dense_3: 256 → 128
dense_4: 128 → 256
concat (dense_1, dense_2, dense_3, dense_4): 1152
softmax: 1152 → 3
```
每个 genus 内部 species 用不同 starting layer (Aedes layer 346 / Anopheles layer 401 / Culex layer 407)

### Training
- Image resize: **299 × 299**
- Optimizer: **Adam** (β1 = 0.89, β2 = 0.999)
- Loss: categorical cross-entropy
- Learning rate: **Cyclic Learning Rate** 2e-7 ↔ 2e-5（triangular waveform）
- **Two phases**:
  - Phase 1: freeze IRV2 + train added dense layers (500 epochs → loss plateau)
  - Phase 2: unfreeze IRV2, lr 0.00001, train all (1200 epochs → plateau)
- Regularization: dropout + early stopping + batch normalization

---

## 关键结果（Table 7 + Table 8 verbatim）

### Validation Accuracy (Table 7)

**Genus 级**:
| Genus | Accuracy |
|---|---|
| Aedes | **92%** |
| **Anopheles** | **93.5%** (highest) |
| Culex | 92% |

**Species within genus**:
| Genus | Species | % Accuracy |
|---|---|---|
| Aedes | aegypti | 85% |
| Aedes | infirmatus | 84% |
| Aedes | taeniorhynchus | 81% |
| Anopheles | crucians | 89% |
| Anopheles | quadrimaculatus | 79% |
| Anopheles | **stephensi** | **98%** |
| Culex | coronator | 69% |
| Culex | nigripalpus | 64% |
| Culex | salinarius | 72% |

**Species directly (9-class)**:
| Species | Accuracy |
|---|---|
| aegypti | 86% |
| infirmatus | 83% |
| taeniorhynchus | 78% |
| crucians | 93% |
| quadrimaculatus | 72% |
| **stephensi** | **100%** |
| coronator | 68% |
| nigripalpus | 71% |
| salinarius | 63% |

### Test Accuracy (unseen 50 specimens, Table 8)
- 新 50 specimen × 12 sets/specimen × 3 orientation = 600 test sets
- **Genus 级**: Aedes 81%, Anopheles 77%, Culex 92%
- **Species drops**: 20-93% range (整体下降)
- **stephensi 仍 98% / 93%** — 最易识别
- Worst on test: nigripalpus 40%, coronator 20%

### 关键 finding
- **Ae. aegypti + An. stephensi 准确率最高** — 这两个分别是 Zika/dengue 和 malaria 最关键 vector
- 即 paper 自己 phrasing: "among the most competent vectors known to mankind"
- **Genus 间 confusion**: Culex 内部 3 species 准确率最低（68-72%）— 形态学也分不清（taxonomist 自己也难分）

---

## 模型 explainability：Feature Map 验证

### 方法
- Last conv layer feature map heatmap = $M_c(i,j) = \sum_k w_k^c f_k(i,j)$
- 投到原图 → 看 model 在 attend 哪些 pixel

### 发现（Figure 2）
- 9 个 species 的 heatmap **全集中在 anatomical components**:
  - Thorax (胸部)
  - Wings
  - Abdomen
  - Legs
- 不被 background 干扰
- **Ae. aegypti** 模型看 thorax 上独特"lyre" 状斑纹（专家鉴定也靠这个）
- **An. crucians** 模型看 wings 上 3 个 dark spots
- **An. quadrimaculatus** 模型看 wings 上 4 个 dark spots（跟 crucians 区分）
- **An. stephensi** 模型看 yellow scutum（其他都没）

→ **Taxonomy expert 看完 heatmap 都 convinced**，这是 paper 重点强调的"AI 跟人类专家在看一样的特征"

### 跟 phylogenetic tree 对账
- Anopheles 跟其他 mosquito 分化 ~217 mya（最早）→ Anopheles 内部 stephensi (107 mya) 跟其他 species 分化也早 → 形态学差异大 → AI 准确率高
- Ae. aegypti (92 mya divergence) 最早 Aedes → 准确率最高
- → "AI accuracy 跟 evolutionary divergence time 正相关"——形态分歧足够大才好分

---

## paper 自己 acknowledged 关键局限

1. **仅 Hillsborough County, FL 数据** — 地理扩展未做，跨 region morphology 可能 vary
2. **仅 female mosquitoes** — CO2 trap bias；male 可以训但没做
3. **An. stephensi 是 lab-raised**（jurisdiction Florida 没野生），跟 wild 可能有 phenotype 差
4. **Specimen prep**：smartphone "attached to a movable fixture **a few feet above** the mosquito"——not random hand-held smartphone photography
5. **Test acc 比 validation acc 掉很多**（80% → 20-93% range）—— 真实部署有 robustness gap
6. **Wing-acoustic alternatives**（用麦克风听 wing beat 频率分类）作者觉得"may not be practical as today"—— image-based 更可靠

---

## ⚠️ 矛盾与未解决问题

- **Validation vs Test gap 大**：Culex coronator validation 69% → test 20%，这种 over-fitting suggest 200 specimen 训练集不够
- **CO2 trap female-only bias**：实际 vector control 也只关心叮人 = 雌蚊；但 dataset 不能 generalize 到 male species ID
- **跟 acoustic-based 方法（Mukundarajan 2016）的 trade-off 没充分讨论** — 音频 features 比 image data 小很多，对 low-bandwidth 部署有优势
- **跟 citizen science (iNaturalist 例) 的整合路径**：paper 想象用户自己拍照上传，但 specimen prep 没做（"a feet above" 固定位置 != hand-held）→ user-acquired image 准确率可能远低于 lab-acquired

---

## 🔗 关联

### 概念
- [[消费级设备健康感知]] — smartphone-based PH automation 跟本研究是同 family；但本是 vector，那个是 human
- 新可能 concept：**Smartphone PH 自动化** (smartphone + transfer learning + on-device / cloud)

### 同主题（smartphone CV PH）
- [[Song_2024_SmartphoneMicroscope]] — smartphone 显微镜直接对接（都是 smartphone optical PH）
- [[Bhamla_2017_Paperfuge]] — frugal PH device 范式相同
- [[Garg_2025_DopFone]] — smartphone-based clinical signal 测量

### 同主题（CV + transfer learning）
- ECE 148 项目用 perception pipeline + transfer learning — Javen 的本科背景对接
- Inception-ResNet V2 + ImageNet pre-training — ECE175B 课程涉及

### 对比维度
- [[Anglemyer_2020_数字接触追踪Cochrane综述]] — 都是数字 PH surveillance，但 Minakshi 是 vector surveillance，Anglemyer 是 contact tracing
- [[Radin_2020_Fitbit流感监测]] — 都是 surveillance 自动化，但 Radin 是 human physiological signal，Minakshi 是 vector morphology
- [[Perez_2019_AppleHeartStudy]] — 都是 large-scale digital deployment（Apple Watch vs smartphone camera）

### 课程对接
- ECE284 vector surveillance 主题（如 syllabus 涵盖）
- "AI 解决 PH dying field" framing 跟课程 ethics/society 主题对接

---

## 📎 来源

- `raw/ucsd/Spring 2026/ECE284/3378393.3402260.pdf`
- ACM SIGCAS COMPASS '20 (Conf on Computing and Sustainable Societies)
- DOI: 10.1145/3378393.3402260
