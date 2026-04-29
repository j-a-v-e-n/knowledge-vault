# ECE 284 Proposal — Trimmed Version

---

## SLIDES

### Slide 1: Problem & Motivation

**Title:** Does Signal Processing Help ML Estimate Heart Rate from Noisy PPG?

- Smartwatch PPG sensors: accurate at rest, unreliable during exercise (30+ BPM error)
- Exercise is when accurate HR matters most
- Two approaches: signal processing (SP) vs. machine learning (ML)
- This project: compare pure SP, pure ML, and SP+ML on the same dataset

---

### Slide 2: Existing Work & Goal

- TROIKA (Zhang, 2015): SP method, MAE ≈ 2.34 BPM
- ML methods (CNN, LSTM) also applied to this dataset
- SP+ML combinations have shown promise in recent work
- **My goal:** controlled experiment — same model, same features, only vary whether SP preprocessing is applied

---

### Slide 3: Approach & Requirements

- **Route A (SP):** bandpass filter → spectral subtraction → peak detection
- **Route B (ML):** frequency features from raw signal → Random Forest
- **Route C (SP+ML):** clean signal first → same features → same Random Forest
- **Dataset:** IEEE SPC 2015 — 12 subjects, PPG + accelerometer + ECG, public
- **Tools:** Python, SciPy, scikit-learn

---

---

## ORAL SCRIPT (~3 min)

### Slide 1 (~1 min)

**English:** My project is about heart rate estimation during exercise. many people use smartwatches to measure their heart rate when exercise. and Exercise is when accurate heart rate matters most. Smartwatches use PPG sensors for detection . it Works well at rest. but During exercise like running, arm movement creates noise, errors go above 30 BPM.

Two ways to fix this. Signal processing uses the accelerometer to identify and remove the motion noise. Machine learning lets a model learn to predict heart rate from the noisy data directly. My project tests a third option: clean the signal with signal processing first, then give the cleaned signal to ML. I want to see if that combination is better than either one alone.

**中文：** 我的 project 是关于运动中的心率估计。智能手表用 PPG 传感器——背面的绿光。静止时准，运动时手臂晃动产生噪声，误差超过 30 BPM。

两种解决方式。信号处理用加速度计识别并去除运动噪声。机器学习让模型直接从带噪声的数据预测心率。我的 project 测试第三种：先用信号处理清洗信号，再把干净信号交给 ML。看这个组合是不是比单独用任何一种更好。

---

### Slide 2 (~1 min)

**English:** The most well-known signal processing method is TROIKA from 2015 by Zhang. It reported an average error of 2.34 BPM. On the ML side, CNNs and LSTMs have also been applied. And some recent work has combined both approaches.

My project is not proposing anything new. It is a controlled experiment. I use the same ML model, the same features — the only thing I change is whether the signal was cleaned first. This way I can directly measure if that cleaning step helps or not.

**中文：** 最知名的信号处理方法是 2015 年的 TROIKA，平均误差 2.34 BPM。ML 方面，CNN 和 LSTM 也被用过。近期也有研究把两者结合。

我的 project 不是提出新方法。它是一个控制实验。同一个 ML 模型、同样的特征，唯一改变的是信号有没有先被清洗。这样我能直接测量清洗这一步到底有没有帮助。

---

### Slide 3 (~1 min)

**English:** Three routes. Route A: pure signal processing — filter, subtract motion noise using accelerometer, find the heart rate peak. Route B: pure ML — extract frequency features from the raw signal, train a Random Forest. Route C: clean the signal with Route A first, then do the same thing as Route B.

Dataset is the IEEE Signal Processing Cup 2015. 12 subjects running on a treadmill, with PPG, accelerometer, and ECG recorded simultaneously. Publicly available, free.

Thanks.

**中文：** 三条路线。路线 A：纯信号处理——滤波，用加速度计减去运动噪声，找心率峰。路线 B：纯 ML——从原始信号提取频域特征，训练 Random Forest。路线 C：先用路线 A 清洗信号，再做和路线 B 一样的事。

数据集是 IEEE Signal Processing Cup 2015。12 个人在跑步机上跑步，同时录了 PPG、加速度计和 ECG。公开免费。

谢谢。


## PART 3: Q&A (English + Chinese)

---

**Q1: Why Random Forest?**

12 subjects, about 1800 samples. Random Forest is stable on small data. Deep learning usually needs more. I chose Random Forest as the primary model for this reason.

12 个人，约 1800 个样本。Random Forest 在小数据上稳定。深度学习通常需要更多数据。所以选 Random Forest 作为主要模型。

---

**Q2: What is Random Forest?**

Many decision trees, each trained on a random subset of data and features. Each tree predicts a heart rate value. The final output is the average of all predictions.

很多棵决策树，每棵用随机抽取的一部分数据和特征训练。每棵树预测一个心率值，最终输出是所有预测的平均。

---

**Q3: What is 1D CNN?**

A neural network that slides small filters along the time-series signal to extract patterns automatically. Unlike Random Forest, it does not need hand-crafted features.

一种神经网络，用小的卷积核沿时间序列信号滑动，自动提取模式。和 Random Forest 不同，不需要手动设计特征。

---

**Q4: What if Route C is not better than Route B?**

That means ML can handle the noise on its own. The preprocessing is redundant. That is a valid and useful finding for wearable system design.

那说明 ML 自己就能处理噪声，预处理是多余的。这对可穿戴系统设计是有用的发现。

---

**Q5: What if Route C is worse than Route B?**

That means signal processing is removing information that ML could have used. It suggests preprocessing should be applied carefully.

那说明信号处理去掉了 ML 本来能用的信息。意味着预处理需要谨慎使用。

---

**Q6: Is the dataset free?**

Yes. Released by Zhang with the TROIKA paper. Used as the official IEEE Signal Processing Cup 2015 dataset. Available on Zenodo. Requirement is to cite the original paper.

是的。Zhang 和 TROIKA 论文一起发布的。是 IEEE Signal Processing Cup 2015 的官方数据集。在 Zenodo 上可下载。要求引用原文。

---

**Q7: Only 12 subjects — is that enough?**

For deep learning, it is small. For signal processing and Random Forest, it is workable. This constraint reflects real clinical wearable research where data is often limited.

对于深度学习来说偏小。对于信号处理和 Random Forest 来说可以。这个约束反映了真实临床可穿戴研究中数据往往有限的情况。

---

**Q8: What features do you extract?**

From each 8-second window: PPG dominant frequency, spectral energy in the heart rate band (0.4–5 Hz), ratio of tallest peak to second tallest, and accelerometer magnitude. Same features for Route B and C.

从每个 8 秒窗口提取：PPG 主频率、心率频段（0.4–5 Hz）的频谱能量、最高峰与第二高峰的比值、加速度计幅度。路线 B 和 C 用同样的特征。

---

**Q9: What does "simplified TROIKA" mean?**

Original TROIKA uses a complex sparse optimization algorithm (M-FOCUSS). I replace it with standard FFT plus spectral subtraction. Same core idea — use accelerometer to find motion noise, subtract from PPG, find heart rate peak — but simpler implementation.

原版 TROIKA 用了复杂的稀疏优化算法（M-FOCUSS）。我用标准 FFT 加频谱减法替代。核心思路一样——用加速度计找运动噪声，从 PPG 减掉，找心率峰——但实现更简单。

---

**Q10: Has combining SP and ML been done before?**

Yes. Some studies have shown benefits of combining them. My project is not claiming this is new. I am doing a controlled experiment — same model, same features, only varying preprocessing — to understand the specific effect of the SP step on this dataset.

有。一些研究已经展示了组合两者的好处。我的 project 不是声称这是新的。我在做一个控制实验——同一个模型、同样的特征、只改变是否预处理——来理解信号处理步骤在这个数据集上的具体效果。