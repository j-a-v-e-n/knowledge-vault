---
name: Ephemeral, Accountless Deployment for AI Agents
description: Give AI agents time-limited, credential-free access to real infrastructure so they can do real work without holding persistent accounts; humans claim and keep results if desired.
tags:
  - ai-usage
  - ai-digest
  - agent-autonomy
  - credentials
  - infrastructure
  - safety
  - ephemeral
source: "https://simonwillison.net/2026/Jun/21/temporary-cloudflare-accounts/#atom-everything"
status: proposed
origin: ai-digest (subscription)
updated: 2026-06-29
---

#ai-digest

# Ephemeral, Accountless Deployment for AI Agents

## What

Instead of provisioning full accounts or long-lived credentials for AI agents to use real infrastructure, deploy resources in an *ephemeral* mode — no account required upfront, resources auto-expire after a short window (e.g. 60 minutes), and a separate *claim link* lets a human convert the resource to a permanent, owned asset if the result is worth keeping.

Cloudflare demonstrated this with a `--temporary` flag on their Workers deploy CLI: an agent can deploy a live, publicly accessible service without ever logging in. The agent gets a working URL immediately. A human (or the agent passing it downstream) can optionally follow a claim link to attach the deployment to a real account before it expires.

## When to use

- An AI agent needs to deploy, test, or verify something on *real* infrastructure during a task (not mocked).
- You want the agent to have genuine capability without holding persistent credentials that could be leaked or misused.
- The human should decide *after* seeing the result whether to keep it — not before the agent starts.
- Reducing blast radius: if the agent goes wrong, resources self-destruct rather than accumulating.

## How it works

1. **Agent invokes a credential-free deploy command** — the platform handles identity internally, assigns a random name, and returns a live URL.
2. **Agent uses the live resource** for its task (testing, verifying, sharing a result).
3. **Platform sets a short TTL** (e.g. 60 minutes) and provides a separate human-facing claim URL.
4. **Human reviews and claims** if the output is useful — converting the ephemeral resource to a permanent one under their account. If not claimed, it vanishes automatically.

## Caveats

- **Platform support required**: this pattern only works if the infrastructure provider offers accountless ephemeral provisioning. Not universally available yet.
- **Short TTL may be too tight** for long-running agent tasks — design the claim step to happen before expiry, or use the claim link programmatically.
- **The claim link itself has a longer but finite TTL** (e.g. ~50 hours per the Cloudflare implementation), so humans still need to act within a window.
- **Not a substitute for auth in production**: ephemeral deployment is for *agent work sessions*, not for serving real users permanently without accountability.

---
*Source: https://simonwillison.net/2026/Jun/21/temporary-cloudflare-accounts/#atom-everything. Distilled by the AI-itself digest — review before blessing.*
