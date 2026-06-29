---
name: Destyle Untrusted Input to Neutralize Prompt Injection
technique: Reformat untrusted input to strip or alter role-tag styling before inserting it into an LLM context, so the model does not mistake it for internal system/reasoning content.
when_to_use: Any pipeline that injects untrusted external text (user messages, web content, tool outputs) alongside system instructions into an LLM context.
source: "https://simonwillison.net/2026/Jun/22/prompt-injection-as-role-confusion/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - prompt-injection
  - security
  - input-sanitization
  - role-confusion
  - defense
  - formatting
verified_by: RAGAS faithfulness (per-claim, via claude -p subscription)
verified_at: 2026-06-29
audience: AI
---
#ai-digest

## claims (each passed RAGAS faithfulness against the source)
- claim: LLMs suffer from 'role confusion': they cannot reliably distinguish their own system instructions from user-provided text that is formatted to resemble those instructions.
  faithfulness: 1.0
- claim: Models prioritize text formatting and style over semantic content when inferring which role a piece of text belongs to.
  faithfulness: 1.0
- claim: Text styled to mimic a model's internal chain-of-thought or reasoning format can override safety training even when the semantic content is clearly adversarial.
  faithfulness: 1.0
- claim: Destyling untrusted input — reformatting it so it no longer resembles expected role-tag or reasoning styles — dramatically reduces prompt injection attack success.
  faithfulness: 1.0
- claim: In the researchers' experiments (Charles Ye, Jasmine Cui, Dylan Hadfield-Menell), destyling reduced attack success rate from 61% to 10%.
  faithfulness: 1.0
