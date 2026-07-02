# PROJECT_BRIEF — ECE 175B ADG

## Goal
Implement Attribute-Disentangled Guidance (ADG): decompose CFG's single guidance scale `w` into K per-attribute scales `w_k`, enabling independent attribute control in conditional diffusion sampling without backbone retraining.

## User
Javen Cao | ECE 175B Spring 2026 final project | Course = Deep Generative Models

## MVP
- Conditional DDPM trained on CelebA 64×64 with K=4 attributes (smile / eyeglasses / male / young)
- ADG sampling: K+1 forward passes, linear combine in noise prediction space
- At least 1 attribute-sweep visualization (fix others, vary one `w_k` 0→6)

## Non-goals
- Not higher resolution (stay 64×64 per proposal §4)
- Not more attributes (K=4 is the spec)
- Not training UNet backbone from scratch (use diffusers `UNet2DModel`)
- Not exploring other guidance methods (CFG → ADG is the contribution)

## Definition of Done
- ✅ Midterm report submitted 2026-05-08 (Gradescope confirmed)
- [x] Final report drafted 2026-06-16 by daemon — final_report.tex (6 sections, NeurIPS style, corrected numbers from checkpoint manifest); pending Javen compile + submit
- [ ] GitHub repo link submitted with final report

## Status (2026-05-18)
- Code skeleton: complete (data.py / model.py / ddpm.py / cfg.py / adg.py / train.py / sample.py / eval_*)
- Notebooks: train_kaggle.ipynb + train_colab.ipynb both ready
- ⚠️ Blocker: Javen GUI 跑 Kaggle Free T4 training (Add Data → Run All)
- Midterm report done; final report blocked on training completion

## Files of interest
- `train.py` — entry; CelebA + conditional DDPM + dropout 0.1
- `adg.py` — main contribution; K+1 forward pass linear combine
- `sample.py` — visualization + attribute sweep
- `eval_fid.py` / `eval_disentangle.py` — quantitative eval
- `notebooks/train_kaggle.ipynb` — primary training entry

## Constraints
- Budget: $0 (Kaggle Free T4)
- Training time: ~4-6h for midterm scope (20-30 epoch + 50k subset)
- No backbone retraining (per proposal)
- diffusers + DDPMScheduler (1000-step linear) — fixed choice

## Related vault entries
- task-board: `task-017`
- proposal: `MyBrain/raw/ucsd/Spring 2026/ECE175B/proposal.pdf`
- notes: `MyBrain/notes/ucsd/Spring 2026/ECE175B/`
