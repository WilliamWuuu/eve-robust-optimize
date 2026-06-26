---
name: improve-robustness
description: "Improve the robustness of the neural operator surrogate against distribution shift during optimization."
---

Use this skill when focusing on improving the operator training phase (Phase 1) to make the surrogate more robust.

## Context

The core challenge is the mismatch between the learned operator G_θ and the true PDE solver. When Phase 2 optimization pushes the control `m` away from the training distribution, G_θ's predictions degrade. The evaluation score penalizes this gap.

The relevant files are:
- `src/robust_optimize/training.py` — the training loop, adversarial training logic, loss functions
- `src/robust_optimize/utils/attacks.py` — PGD adversarial attack implementation
- `src/robust_optimize/models/operators.py` — FNO architecture definition

## Strategies to Explore

### 1. Adversarial Training Improvements
- Modify the PGD attack in `attacks.py`: try different epsilon schedules, norm constraints (L2 vs L-inf), or entirely new attack strategies (e.g., spectral perturbations targeting Fourier features)
- The current implementation uses relative epsilon (proportional to each sample's max absolute value). Consider adaptive epsilon based on the operator's local Lipschitz estimate.

### 2. Curriculum Design
- In `training.py`, experiment with different curriculum schedules for adversarial strength — not just linear increments
- Try exponential, cosine, or step-based schedules for the PGD step count `k`
- Adjust `curriculum_patience` to control how quickly difficulty ramps up

### 3. Loss Function Design
- Add regularization terms that penalize high Lipschitz constants of the operator
- Add consistency losses: `||G_θ(m + δ) - G_θ(m)||` should be small for small perturbations δ
- Try spectral normalization on the operator weights
- Add a loss term that directly minimizes `||G_θ(m*) - u_true||` where `m*` is the optimized control from Phase 2

### 4. Architecture Changes
- In `operators.py`, try deeper FNO with residual connections
- Experiment with different activation functions (GELU, SiLU vs ReLU)
- Add dropout or spectral normalization layers
- Try different FNO modes (more/fewer Fourier modes)

## What to Track

When making changes, always:
- Log the relative L2 error on both clean and adversarial validation sets
- Compare surrogate prediction vs FDM solution for the optimized control
- Note the trade-off between clean accuracy and adversarial robustness
- Record any changes to training time or convergence speed
