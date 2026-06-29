---
name: Prompt Injection via Role Confusion — Destyle Untrusted Input
description: LLMs perceive style/formatting as more authoritative than role tags; sanitize (destyle) untrusted content before injecting it into any prompt to resist injection attacks that impersonate internal reasoning.
tags:
  - ai-usage
  - ai-digest
  - prompt-injection
  - security
  - agentic-systems
  - defense
  - llm-architecture
source: "https://simonwillison.net/2026/Jun/22/prompt-injection-as-role-confusion/#atom-everything"
status: proposed
origin: ai-digest (subscription)
updated: 2026-06-29
---

#ai-digest

# Prompt Injection via Role Confusion — Destyle Untrusted Input

## What

LLMs cannot reliably tell the difference between text that belongs to a privileged internal role (system prompt, internal reasoning/thinking blocks) and untrusted user-supplied text, purely based on role labels like `<system>` or `<user>` tags. What actually drives the model's perception is **formatting style**: content that *looks like* internal deliberation is treated more like internal deliberation, regardless of which tag wraps it.

This means an attacker can craft user-supplied input that mimics the stylistic patterns of a model's internal reasoning output, and the model will treat those injected instructions with elevated trust — a vulnerability the article frames as "role confusion" rather than traditional injection.

## When to use

Apply this whenever you build a system that:
- Injects untrusted external content (user messages, tool results, web-scraped data, file contents) into a prompt that also contains privileged system instructions or thinking blocks
- Uses models that expose visible reasoning traces (e.g., extended thinking)
- Chains multiple LLM calls where earlier outputs become later inputs — each handoff is a potential injection vector

## How it works

**The vulnerability:** Researchers demonstrated that wrapping malicious instructions in language patterns matching a model's own internal thinking style raised attack success rates to ~61%. The content was not special — the *style* was.

**The mitigation — destyling:** Before passing any untrusted text into a prompt, reformat it to strip or neutralize stylistic markers that resemble internal reasoning blocks. This means: removing or replacing XML-like tags that match the model's internal format, normalizing whitespace/indentation patterns characteristic of thinking traces, and potentially wrapping the content in an explicit "this is external untrusted input" framing that is stylistically dissimilar from your system content.

Applying this destyling step in the cited research dropped attack success from ~61% to ~10%, without changing the semantic content of the injected text at all.

**Design implication:** Treat the *presentation format* of untrusted content as a security surface, not just its semantic meaning. Your prompt pipeline should have an explicit sanitization stage that normalizes user/external content into a format that looks nothing like your privileged internal content.

## Caveats

- This is a mitigation, not a cure: the article notes that without genuine "role perception" inside the model, this is an arms race — attackers can adapt their styling to whatever safe style you choose.
- Destyling is a practical near-term defense, not a solved problem at the architecture level.
- The 61%→10% figure is from a specific research setup; real-world numbers will vary by model, system prompt structure, and attacker sophistication.
- This insight also applies to multi-agent pipelines: when one agent's output becomes another agent's input, the receiving agent cannot tell whether that text originated as trusted orchestrator content or was injected mid-stream. Destyle at every trust boundary.

---
*Source: https://simonwillison.net/2026/Jun/22/prompt-injection-as-role-confusion/#atom-everything. Distilled by the AI-itself digest — review before blessing.*
