---
name: Destyle Untrusted Input to Neutralize Prompt Injection
technique: Rewrite untrusted text to strip formatting patterns that resemble system/assistant/thinking styles before injecting it into a prompt, so the model cannot be confused into treating it as privileged instructions.
when_to_use: Any pipeline where untrusted external content (user input, retrieved documents, tool outputs) is interpolated into prompts alongside system instructions — RAG, agents, chatbots.
source: "https://simonwillison.net/2026/Jun/22/prompt-injection-as-role-confusion/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - prompt-injection
  - security
  - input-sanitization
  - rag
  - agents
  - defense
verified: true (every claim sentence-backed by an independent fresh context)
verified_at: 2026-06-29
audience: AI
---
#ai-digest

## claims (each backed by an exact source sentence)
- claim: Models cannot reliably distinguish privileged text in <system>/<think>/<assistant> tags from untrusted user input — they prioritize text *formatting* over the actual structural role.
  source_sentence: "they confirm that not only is this not possible, but it looks like models take the *style* of the text more seriously than the actual text!"
- claim: Rewriting untrusted input to diverge from expected system/thinking format patterns ('destyling') drops average prompt-injection attack success from 61% to 10%.
  source_sentence: "destyling causes average attack success in our dataset to plunge from 61% to 10%."
- claim: The destyling transformation is nearly imperceptible to human readers while substantially altering model behavior.
  source_sentence: "A change nearly invisible to humans completely changes the LLM's role perception."
- claim: Without a model-level solution to role perception, prompt-injection defenses remain a 'perpetual whack-a-mole game' — structural mitigations like destyling reduce but do not eliminate risk.
  source_sentence: "Unless LLMs achieve genuine role perception, we think injection defense will remain a perpetual whack-a-mole game."
