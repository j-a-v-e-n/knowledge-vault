---
name: ephemeral-accountless-cloudflare-deploy
technique: Deploy a Cloudflare Worker to a live temporary URL (60 min TTL) with zero account setup via `npx wrangler deploy --temporary`
when_to_use: When an AI agent needs to spin up a real HTTP endpoint (webhook receiver, demo UI, tool server) mid-task without requiring the user to authenticate or own a Cloudflare account
source: "https://simonwillison.net/2026/Jun/21/temporary-cloudflare-accounts/#atom-everything"
tags:
  - ai-usage
  - ai-digest
  - agent-tool-use
  - deployment
  - ephemeral
  - cloudflare-workers
  - no-auth
  - agentic-workflow
verified: true (every claim sentence-backed by an independent fresh context)
verified_at: 2026-06-29
audience: AI
---
#ai-digest

## claims (each backed by an exact source sentence)
- claim: Running `npx wrangler deploy --temporary` deploys a Cloudflare Worker without requiring a Cloudflare account.
  source_sentence: "you can now create a Cloudflare Workers project and run this, without even creating a Cloudflare account: `npx wrangler deploy --temporary`"
- claim: The temporary deployment expires and becomes unavailable after 60 minutes.
  source_sentence: "Cloudflare will deploy the application to a new, ephemeral project which will stay live for 60 minutes."
- claim: The deployment output includes a claim URL that lets the user convert the ephemeral deployment into a permanent account-linked project.
  source_sentence: "Running the deployment spits out the URL to a page for claiming the new project, for if you want it to last for more than 60 minutes."
- claim: The claim URL itself has its own expiration window (approximately 49 hours in the documented example), so it must be acted on before that window closes.
  source_sentence: "A red banner at top reads 'This claim link expires in 49:26'."
