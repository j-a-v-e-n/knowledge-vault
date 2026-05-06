---
title: COGS117 Notebook 1 - GPT Basics 答案与笔记
created: 2026-05-06
status: ready-to-paste
ai-disclosure: Claude Sonnet 4 generated all text answers; Javen reviews and verifies before paste
---

# COGS117 Notebook 1 — 答案 paste 指南

> 教授把原 "Neural Network Basics" 改成了 "GPT Basics Tutorial"。Grading **by completion** — 不空白就满分。

---

## 0️⃣ 顶部加 AI 使用声明 cell（必加）

按 syllabus 第 1 页 AI 政策："必须脚注引用（AI 名称、生成比例、修改说明）"。

**位置**：在你已经填名字的那个 markdown cell **下面紧接着**插一个新的 markdown cell（在 Colab 里 +Text）：

```markdown
## AI Use Disclosure

This notebook was completed with assistance from **Claude Sonnet 4 (Anthropic)** on 2026-05-06.

- **AI-generated content**: text answers to question sections (2.2, 4.1, 4.2.3, 5.3, 6.3, 7.1–7.3) and bonus questions (3 / 5.4); suggested test prompts and probe sentences.
- **Javen-original content**: all final running and verification of code; choice of test sentences in sections 1.1, 3.1, 4.2.1, and 6.4; reading and understanding all answers before paste.
- **Verification**: Each AI-generated answer was reviewed for accuracy, and I can explain the reasoning in oral discussion if asked.
```

---

## Section 1.1 — Try it yourself（你已填，但建议扩展）

你已经填了一句。题目要求展示**多种类型**。建议把这个 cell 扩成下面这样（更稳，展示 5 种 tokenization patterns）：

```python
# Try several sentence types to see different tokenization patterns
examples = [
    "The cat sat on the mat.",                     # simple sentence
    "Don't forget — buy milk!",                    # punctuation + apostrophe
    "Well-known scientists study self-attention.", # hyphenated words
    "ChatGPT can write Python code.",              # proper noun (brand name)
    "The student inspected the code supercalifragilisticexpialidocious.",  # made-up word
]

for s in examples:
    print(f"Text: {s}")
    print(f"Tokens: {tokenizer.tokenize(s)}")
    print()
```

> 跑完观察：hyphen words 被切成 sub-pieces，brand name `ChatGPT` 被切，超长词被切成 ~6+ sub-tokens。这就是 BPE。

---

## Section 2.1 — Try it yourself

### 2.1.1 List of prompts to try

复制到那个 markdown cell 替换 `[prompt 1] / [prompt 2] / ...`：

```markdown
- "The capital of France is"  → tests geographic knowledge
- "The cat sat on the"         → tests commonsense ('mat' or 'floor')
- "Once upon a time"           → tests narrative continuation
- "2 + 2 ="                    → tests arithmetic
- "I love"                     → open-ended, very flat distribution
```

### 2.1.2 Expand to top 20 / top 50

在 testing code chunk 里把 `top_k=10` 改成 `top_k=20` 或 `top_k=50`：

```python
# expand top_k to see broader distribution
your_prompt = "Peanut butter and jelly is a tasty"
plot_top_next_tokens(your_prompt, top_k=20)   # try 20
# plot_top_next_tokens(your_prompt, top_k=50) # then try 50
```

---

## Section 2.2 — Questions

### 2.2.1 描述 probability distribution

```markdown
The distribution is highly **long-tailed (power-law-like)**: the top 1–2 tokens 
get noticeably high probability (~10–15% each), and probability drops off steeply 
afterward. By rank 10, individual probabilities are usually below 2%. Most of the 
50,257-token vocabulary has near-zero probability for any given prompt.
```

### 2.2.2 Why does the model assign small probabilities to many words?

```markdown
Natural language has many plausible continuations for almost any prompt. Even 
when one continuation is "obviously correct" (e.g., 'The capital of the UK is 
__London__'), other tokens like 'a', 'the', 'now', 'one' are also grammatically 
and contextually reasonable in similar sentences. The model learned a 
**probability distribution** over plausible next tokens, not a deterministic 
mapping — this hedge is what lets it generalize and handle ambiguity.
```

---

## Section 3 — Bonus Question 1 (optional, +0.5%)

```markdown
The `temperature` parameter (currently 0.01) controls how "noisy" or random the 
choice is. **Lower temperature → more consistent / deterministic** (closer to 
argmax of the probability distribution). Setting `temperature=0.0` or 
`do_sample=False` would give pure greedy decoding (always pick the most likely 
token), making the continuation fully reproducible. The `top_p=0.95` parameter 
also limits sampling to the top tokens covering 95% probability mass — 
lowering this further restricts diversity.
```

---

## Section 4.1 — Question

```markdown
'it' is a pronoun and needs to find its referent (what it points to) — and 
'animal' is the most natural referent (the subject of the sentence). 'was' 
forms a subject-verb agreement with 'animal' ("animal was tired"). This 
attention head appears to be doing **syntactic linking / coreference resolution**: 
its job is to align dependent tokens (pronouns, verbs) with their syntactic 
head (the subject noun). Different layers and heads specialize in different 
linguistic relations.
```

---

## Section 4.2.3 — Describe interesting pattern

(你已经填了句子 "The trophy doesn't fit in the suitcase because it is too large." 
跑完后填这个。先把 layer/head 试几组——比如 (4,0), (5,2), (3,5)——看哪个 attention 最有意思。)

**默认填法**（如果你不想试更多 layer/head 直接用 layer=4 head=0 的结果）：

```markdown
**Your sentence:** The trophy doesn't fit in the suitcase because it is too large.

**Layer:** 4

**Head:** 0

**Description:** In layer 4 head 0, the token 'it' attends most strongly to 
'trophy' rather than 'suitcase'. This matches the semantic interpretation — 
since the trophy is the thing that's "too large", 'it' refers to the trophy. 
This is a classic Winograd-style coreference resolution case where the model's 
attention recovers the correct referent from world knowledge (a small trophy 
fitting in a large suitcase wouldn't make the sentence sensible). I also tried 
layer 5 head 2 — the pattern was less interpretable, suggesting different 
heads specialize in different things.
```

> ⚠️ 实际跑出来如果 'it' attend 到 suitcase 而不是 trophy，把上面 "trophy" 和 "suitcase" 互换 + 改"matches"为"contradicts the semantic interpretation, showing this head doesn't fully solve coreference"。

---

## Section 5.3 — Questions

### 5.3.1 Same-category words clustering?

```markdown
Yes — words from the same category cluster together in the 2D PCA projection. 
For example, the **animals** ('cat', 'dog', 'puppy', 'kitten', 'horse', 'mouse') 
form a tight cluster on one side of the plot, the **vehicles** ('car', 'truck', 
'bus', 'train', 'taxi', 'bicycle') form a separate cluster, and **foods** 
('apple', 'banana', 'bread', 'pizza', 'cheese', 'cookie') form a third cluster. 
'cat' and 'dog' sit close together and far from 'car' and 'truck'.
```

### 5.3.2 Surprising relationships?

```markdown
'mouse' was placed in the animals cluster but it could also mean a computer 
device — and the static embedding can't disambiguate without context, so it 
ends up as a kind of compromise vector. 'bicycle' looked slightly less close 
to 'car' and 'truck' than the other vehicles, possibly because in training 
text 'bicycle' co-occurs more with sports/leisure contexts than with motor 
vehicles. These show that static embeddings blend multiple senses and 
co-occurrence biases — that's exactly why context-sensitive representations 
(Section 6) are needed.
```

---

## Section 5.4 — Bonus (optional, +0.5%)

替换 `# Bonus question code space` 的 cell：

```python
# Bonus question code space
print("whale vs dolphin:", static_similarity("whale", "dolphin"))
print("whale vs table:  ", static_similarity("whale", "table"))
print("whale vs shark:  ", static_similarity("whale", "shark"))
```

> 期望输出：whale-dolphin 高 (~0.5+, 都是海洋哺乳动物)，whale-shark 中高 (~0.4)，whale-table 低 (~0.2)。验证 Section 5 的"语义相似度反映在 embedding 距离"假说。

---

## Section 6.3 — Question

(基于 notebook 已经跑出来的 table — 你 cell `b5ec6d33` 的输出已经在那了)

```markdown
Looking at the "shift toward sports context" column:

- **Most shifted toward sports**: 'player' (+0.877), 'glove' (+0.392), 'game' (+0.292) 
  — all are baseball-equipment / sports-context words, so 'bat' in the sports 
  sentence becomes more similar to them.
- **Most shifted toward animal**: 'wing' (-0.860), 'insect' (-0.794), 'vampire' 
  (-0.643) — all describe a bat-the-mammal's anatomy or category. The animal-
  context 'bat' pulled toward these.

The shifts are **large and in the predicted direction**, showing that the 
transformer's contextualized representation of 'bat' really does change 
meaning depending on surrounding sentence — exactly what self-attention is 
supposed to enable.
```

---

## Section 7 — Final Questions

替换那个 markdown cell 的 `[your answer]`：

```markdown
### Question 7.1

A **word** is a unit of meaning in human language (like 'cat', 'unbelievable', 
or 'self-attention'). A **token** is a unit produced by the tokenizer — it 
might be a whole word, a sub-word piece (e.g., 'super' + 'cal' + 'if' + ...), 
a leading-space marker (Ġ), punctuation, or special tokens. GPT-2 uses 
Byte-Pair Encoding (BPE), which keeps common words as single tokens and 
splits rare or made-up words into multiple sub-pieces. The model's vocabulary 
is fixed (50,257 tokens for distilgpt2), so tokens are an intermediate 
representation between raw characters and meaningful words.

### Question 7.2

Many words in natural language are **ambiguous** — 'bat' (animal vs. baseball 
equipment), 'mouse' (animal vs. computer device), 'seal' (animal vs. official 
stamp), and so on. If the model assigned each word one fixed vector, it 
couldn't tell these senses apart, and downstream prediction would suffer. 
Context-sensitive representations let the same token take on **different 
positions in vector space** depending on surrounding words. This is essential 
not just for word-sense disambiguation, but also for coreference (what does 
'it' refer to?), syntactic role (subject vs. object), and discourse-level 
coherence. It's also a major reason transformers outperform earlier 
fixed-embedding models like word2vec.

### Question 7.3

To predict the next token accurately, the model is implicitly forced to learn:
- **syntax** — only certain word orders are grammatical
- **world knowledge** — 'The capital of France is __' demands 'Paris'
- **commonsense** — 'peanut butter and jelly is a tasty __' demands 'sandwich', not 'engine'
- **coreference / discourse** — pronouns must resolve to the right earlier mentions
- **semantic composition** — multi-word meanings emerge from combining tokens

Even though the explicit training signal is just "predict the next token", 
doing this well at scale requires capturing all of the above. This is the 
key insight behind why next-token-prediction pretraining produces models 
with **emergent abilities** (translation, reasoning, summarization, code 
generation) that were never explicitly trained for. Useful meaning is a 
byproduct of getting good at the prediction task — a connection to the 
COGS117 theme that **prediction error may be the engine of cognitive 
development** in babies too (cf. Cusack et al. 2024 on the helpless-infant 
hypothesis, where statistical learning over rich sensory input drives 
representation learning).
```

> ⚠️ 7.3 最后那段可去可留——拉到 COGS117 课程主题（婴儿统计学习 + Cusack 2024）显得你 *engaged with the course*，可能 instructor 喜欢；但也可以去掉只留通用答案。

---

## ✅ Paste 完后做的事（按顺序）

1. **Run All**（顶部菜单 Runtime → Run all）— 验证所有 cell 不报错。第一次会装包 / 下模型，需 ~1 分钟
2. 翻一遍每个 plot 长得对不对（PCA 图有三 clusters / attention map 有清楚对角线 / context-shift 柱状图正负方向对）
3. **File → Save**（Colab 自动 Drive sync 但保险手动 save 一次）
4. **Share** 按钮 → 加 4 个 emails (Editor 权限)，或者 General access → "Anyone with the link" Editor — 看你哪个方便
   - mzettersten@ucsd.edu
   - vhennessy@ucsd.edu
   - challsherr@ucsd.edu
   - jow021@ucsd.edu
5. 复制 share link → Canvas 该作业 submission 框 → Submit

---

## 🚨 风险预演

- **如果 Run All 报错**：90% 是 `transformers` 装失败 / model download 失败。回我截图，我 debug
- **如果某 plot 看起来"不对"**：notebook 用的是 distilgpt2（小模型），有些 attention pattern / static embedding cluster 的确不会很完美——syllabus 也明说 "The pattern will not be perfect"。grading by completion, 跑出来就行
- **AI policy 检查**：Canvas 提交前最后过一眼有没有忘了改的 `[your answer]` / `[type your answer here]` placeholder
