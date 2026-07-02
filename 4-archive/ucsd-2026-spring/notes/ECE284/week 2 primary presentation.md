# Apple Heart Study — Speaking Script v2

# 演讲稿 v2（中英双语）

---

## Slide 1 — Title / 标题

**EN:** Today I'm presenting the Apple Heart Study, published in the New England Journal of Medicine in 2019. The question is straightforward: Can an Apple Watch detect atrial fibrillation during everyday use? They enrolled over 419,000 people in 8 months, entirely remotely. Let's look at what they found.

**中文：** 今天讲的是Apple Heart Study，2019年发表在《新英格兰医学杂志》上。问题很直接：Apple Watch能不能在日常使用中检测到房颤？他们8个月招了41万多人，全程远程完成。我们来看看他们发现了什么。

---

## Slide 2 — What Is AFib / 什么是房颤

**EN:** First, some background. AFib, or atrial fibrillation, is the most common serious heart rhythm disorder. Normally your heart beats in a steady rhythm. In AFib, the electrical signals in the upper chambers become chaotic, so the heartbeat turns irregular. Why is this dangerous? Blood can pool in the heart, form clots, and if a clot reaches the brain, that's a stroke. AFib increases stroke risk by five times.

The tricky part: AFib often comes and goes. Between episodes, a standard ECG looks completely normal. And many people have no symptoms. About 700,000 people in the U.S. may have AFib without knowing it.

**中文：** 先讲背景。房颤是临床上最常见的严重心律失常。正常心脏有规律地跳动，但房颤时心房的电信号变得混乱，心跳不规则。为什么危险？血液会在心房里淤积、形成血栓，血栓到脑子里就是中风。房颤让中风风险增加5倍。

麻烦的是：房颤经常来了又走。不发作时心电图看上去完全正常。而且很多人没有症状。美国大约有70万人可能有房颤但自己不知道。

---

## Slide 3 — The Detection Gap / 检测的空白

**EN:** So how do we currently detect AFib? Standard ECGs only capture a snapshot. If AFib isn't happening at that moment, you miss it. Holter monitors record for 24 to 48 hours, but that's often too short. Implantable devices work well but require surgery.

What we need is something long-term, passive, non-invasive, and that uses devices people already own. A smartwatch could fill that gap. But can it actually work? That's what this study tested.

**中文：** 那现在怎么检测房颤？标准心电图只是快照，发作时没做就抓不到。Holter动态心电图能记录24到48小时，但往往不够长。植入式设备效果好，但要手术。

我们需要的是长期、被动、无创、用人们已有的设备。智能手表可能填补这个空白。但它真的行吗？这就是这个研究要验证的。

---

## Slide 4 — Study Design / 研究设计

**EN:** This was a prospective, single-arm, siteless, pragmatic study. Let me explain the key terms.

"Single-arm" means no control group. Everyone got the same monitoring. This means sensitivity and specificity can't be calculated, which is a known trade-off of this design.

"Siteless" is the most interesting part. No physical site visits at all. Consent through the app. Monitoring on the watch. Telemedicine by video. ECG patches by mail. This is what made it possible to enroll 419,000 people in 8 months.

They recruited U.S. residents aged 22 and older who owned an Apple Watch and iPhone. Importantly, participants self-reported that they had no prior AFib. The two primary outcomes were: the percentage of notified people with AFib on ECG patch, and the positive predictive value of the irregular tachograms.

**中文：** 这是一个前瞻性、单组、无现场、务实的研究。解释几个关键术语。

"单组"意味着没有对照组。每个人接受同样的监测。所以没法算灵敏度和特异度，这是这种设计的已知局限。

"无现场"是最有意思的部分。全程不需要去任何地方。App同意、手表监测、视频问诊、ECG贴片邮寄。这让8个月招41万人成为可能。

他们招的是22岁以上、有Apple Watch和iPhone的美国居民。重要的是，参与者自己报告没有房颤病史。两个主要结局是：收到通知的人中有多少ECG确认了房颤，以及不规则tachogram的阳性预测值。

---

## Slide 5 — How the Algorithm Works / 算法怎么工作

**EN:** How does the technology work? Five steps.

First, the Apple Watch has a PPG sensor on the back. A green LED shines light onto your wrist. When your heart beats, more blood flows through and absorbs more light. The sensor picks up this pulsing pattern.

Second, the watch generates a "tachogram," a one-minute recording of the intervals between pulses. This happens passively while you're at rest.

Third, an algorithm classifies each tachogram as regular or irregular based on how variable the intervals are.

Fourth, and this is a key design choice: the algorithm does NOT alert after just one irregular reading. It requires multiple irregular tachograms before sending a notification. A single reading could just be noise.

Fifth, if the threshold is met, the user gets one notification. After that, the watch keeps recording but stops showing alerts.

Why does this matter? A single tachogram had a PPV of 0.71. After requiring multiple confirmations, the notification PPV rose to 0.84. The multi-confirmation step meaningfully improved accuracy. The paper mentions this design but does not specify the exact number of readings required or the time interval between them. Those details are in the supplementary materials.

**中文：** 技术怎么工作？五步。

第一，Apple Watch背面有PPG传感器。绿色LED照射手腕，心脏跳动时血流增加、吸收更多光。传感器检测到这个脉动信号。

第二，手表生成一个"tachogram"，一分钟的脉搏间期记录。在你休息时被动采集。

第三，算法判定每条tachogram是规则还是不规则，依据是间期的变异程度。

第四，关键设计：算法不会因为一次不规则就报警。它要求多条不规则tachogram才发通知。单次读数可能只是噪声。

第五，达到门槛后用户收到一次通知。之后手表继续记录，但不再显示警报。

为什么重要？单条tachogram的PPV是0.71。要求多次确认后，通知PPV升到了0.84。多次确认这一步确实提高了准确度。论文提到了这个设计但没有写具体需要几次或间隔多久，这些细节在补充材料里。

---

## Slide 6 — After the Notification / 通知之后

**EN:** What happens after someone gets notified? Six steps. The notification comes through the app. Then a telemedicine visit with a physician to check eligibility and symptoms. If there's no emergency, an ECG patch is mailed out, worn for up to 7 days. The patch is mailed back and read by two clinicians independently. Then a second telemedicine visit to discuss results. Finally, a 90-day follow-up survey.

Notice the attrition at the bottom of this slide. 2,161 people were notified. Only 450 returned an analyzable ECG patch. That's about 20%. The 34% AFib yield we'll talk about next is based on those 450, not all 2,161.

**中文：** 收到通知后怎么走？六步。App推送通知。远程医疗问诊确认资格和症状。没有紧急情况就邮寄ECG贴片，戴最多7天。贴片寄回后两名临床医生独立判读。然后第二次远程问诊讨论结果。最后90天随访问卷。

注意这页底部的流失数据。2,161人收到通知，只有450人返回了可分析的贴片。大约20%。接下来要讲的34%检出率就是基于这450人。

---

## Slide 7 — Result 1: Notification Rate / 结果1：通知率

**EN:** Now the results. Of 419,000 participants, only 0.52% got a notification. Very low. It varies by age: 3.1% for those 65 and older, only 0.16% for 22 to 39 year olds.

This shows the algorithm is conservative by design. It prioritizes not bothering users over catching every case. But it also means we don't know how many real AFib cases were missed.

Let me explain two concepts here. Sensitivity asks: of all people who truly have AFib, how many did the watch catch? This study does not measure that, because they didn't do ECGs on everyone. PPV asks: of all people the watch flagged, how many actually had AFib? That's what this study measures. It was not designed to assess sensitivity.

**中文：** 看结果。419,000人中只有0.52%收到了通知。非常低。按年龄不同：65岁以上3.1%，22到39岁只有0.16%。

这说明算法设计上就是保守的。它优先考虑不打扰用户，而不是抓住每一个病例。但这也意味着我们不知道漏掉了多少真正的房颤。

这里解释两个概念。灵敏度问的是：所有真正有房颤的人里，手表抓到了多少？这个研究没测，因为没给所有人做ECG。PPV问的是：手表报警的人里，有多少真的有房颤？这才是这个研究测的。这个研究不是为了评估灵敏度而设计的。

---

## Slide 8 — Result 2: ECG Yield / 结果2：ECG检出率

**EN:** Of 450 people who returned ECG patches, 153 had AFib confirmed. That's a yield of 34%.

You might think: only 34%? Does that mean 66% were false positives? Not necessarily. The ECG patch was applied on average 13 days after the notification. AFib comes and goes. The episode that triggered the notification could have ended by then. So 34% is a floor estimate, not a false positive rate.

Among the confirmed cases, 89% had episodes lasting at least one hour. These are clinically meaningful.

A quick note on the confidence interval shown here. "97.5% CI: 29 to 39%" means if you repeated this study many times, 97.5% of the time the true value would land between 29% and 39%.

One caveat: only 20% of notified people returned patches. Those who returned and those who didn't had similar baseline characteristics. But we simply don't know the AFib status of the other 80%.

**中文：** 450个返回ECG贴片的人中，153人确认了房颤。检出率34%。

你可能会想：才34%？66%都是假阳性？不一定。ECG贴片平均在通知后13天才贴上。房颤来了又走，触发通知的那次发作可能已经结束了。所以34%是下限估计，不是假阳性率。

确认房颤的人中，89%有持续至少一小时的发作。这些是有临床意义的。

解释一下这里的置信区间。"97.5% CI: 29到39%"意思是如果重复做这个研究很多次，97.5%的时候真实值会在29%到39%之间。

一个注意事项：只有20%的收到通知的人返回了贴片。返回和没返回的人基线特征相似。但那80%到底有没有房颤，我们确实不知道。

---

## Slide 9 — Result 3: PPV / 结果3：阳性预测值

**EN:** Now the accuracy numbers. Single tachogram PPV was 0.71. Notification PPV, after multi-confirmation, was 0.84. This jump shows that requiring multiple readings before alerting actually works.

What about the irregular readings that weren't AFib? Of 600 such cases, 77% were premature atrial contractions, 38% were atrial tachycardia, 16% were premature ventricular contractions. Only about 5% were truly benign.

So even when the algorithm was wrong about AFib, it was mostly picking up real cardiac abnormalities, not random noise. Whether these findings matter clinically is a question worth studying further.

**中文：** 看准确度数据。单条tachogram的PPV是0.71。多次确认后的通知PPV是0.84。这个提升说明要求多次读数再报警确实有效。

那些不规则但不是房颤的读数是什么？600条中77%是房性早搏，38%是房性心动过速，16%是室性早搏。只有大约5%是真的没事。

所以即使算法在房颤这件事上判断错了，它大多数时候也在检测到真实的心脏异常，而不是噪声。这些发现临床上有没有意义，值得进一步研究。

---

## Slide 10 — Result 4: Behavioral Impact / 结果4：行为改变

**EN:** Did the notifications change behavior? Yes. Of those who returned the 90-day survey, 57% contacted a doctor outside the study. 28% got new prescriptions. 33% were told to see a specialist. Overall, 76% sought some form of medical care.

At the end of the study, 44% of notified people reported a new AFib diagnosis, versus only 1% among those never notified.

On safety: 16 app-related adverse events, 15 of which were anxiety. No serious events. No hospitalizations from the app.

**中文：** 通知改变行为了吗？改变了。返回90天问卷的人中，57%联系了研究外的医生。28%被开了新药。33%被建议看专科。总共76%寻求了某种形式的医疗帮助。

研究结束时，44%的收到通知的人报告了新的房颤诊断，没收到通知的人只有1%。

安全方面：16例与app相关的不良事件，15例是焦虑。没有严重事件，没有因为app住院的。

---

## Slide 11 — Limitations / 局限性

**EN:** Now limitations. On the left are things the authors acknowledge in the paper. No sensitivity or specificity, by design. Low ECG patch return rate, only 20%. And self-reported eligibility, meaning some participants actually had prior AFib but still enrolled.

On the right are our observations, outside the paper's scope. There are no clinical hard endpoints. The study proves detection, but not whether early detection reduces strokes or deaths. That would need randomized controlled trials. And regarding PPG and skin tone: PPG signal quality is known to vary with skin pigmentation. The notified group was 81% white, and no subgroup analysis by race was done. This doesn't prove a problem exists, but it's worth noting when thinking about generalizability.

**中文：** 讲局限性。左边是作者在论文中承认的。没有灵敏度和特异度，这是设计决定的。ECG贴片返回率低，只有20%。还有自报入选资格，有些参与者其实有房颤病史但还是参加了。

右边是我们的观察，超出了论文讨论的范围。没有临床硬终点。研究证明了能检测到房颤，但没有回答早期检测是否减少中风或死亡。那需要随机对照试验。还有PPG和肤色的问题：PPG信号质量在不同肤色上有已知差异。通知组81%是白人，没有按种族做亚组分析。这不证明有问题，但在考虑推广性时值得注意。

---

## Slide 12 — Key Takeaways / 关键要点

**EN:** To wrap up. The notification PPV is 0.84. When the watch alerts, it's usually right. The notification rate is very low at 0.52%, showing the algorithm is conservative. 34% of notified people had AFib confirmed on ECG. And notifications drove real clinical action.

What's still open? Does earlier detection actually reduce strokes or deaths? How does it perform across different skin tones and age groups? If this becomes a consumer feature, who's liable for missed diagnoses? And how should FDA regulation adapt?

I think the biggest contribution isn't just the AFib results. It's proving that a siteless, app-based study can enroll 400,000 people in 8 months. That model will shape digital health research going forward. Thank you.

**中文：** 总结一下。通知的PPV是0.84，手表报警时通常是对的。通知率很低只有0.52%，说明算法保守。34%收到通知的人ECG确认了房颤。通知驱动了真实的临床行动。

还有什么没解决？更早检测是否真的减少中风或死亡？在不同肤色和年龄群体中表现如何？如果变成消费功能，漏诊谁负责？FDA监管怎么适应？

我认为最大的贡献不只是房颤检测结果，而是证明了无现场、基于app的研究可以8个月招40万人。这个模式会影响未来的数字健康研究。谢谢大家。

---

## Timing Estimate / 时间估算

|Slide|Topic|~Min|
|---|---|---|
|1|Title|0.5|
|2|What is AFib|1.0|
|3|Detection gap|0.5|
|4|Study design|1.5|
|5|Algorithm|1.5|
|6|Verification|1.0|
|7|Notification rate|1.5|
|8|ECG yield|1.5|
|9|PPV|1.0|
|10|Behavior|0.5|
|11|Limitations|1.5|
|12|Takeaways|1.0|
|**Total**||**~13 min**|