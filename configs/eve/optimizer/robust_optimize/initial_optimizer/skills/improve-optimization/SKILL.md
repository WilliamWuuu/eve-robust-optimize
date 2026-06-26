---
name: improve-optimization
description: "Improve the Phase 2 control optimization loop to find better controls that work well on the true PDE solver."
---

Use this skill when focusing on improving the optimization phase (Phase 2) that uses the frozen surrogate to find optimal controls.

## Context

After Phase 1 trains the operator G_θ, Phase 2 freezes it and uses gradient-based optimization to find controls m that minimize:
- `J(u, m) = 0.5 * ||u - u_d||² + (α/2) * ||m||²` (Poisson/Burgers)
- `J(u, m) = 0.5 * ||u - u_d||² + (α/2) * ||∇m||²` (Darcy)

The evaluation score measures how close the optimized control's true objective (via FDM solver) is to the surrogate-predicted objective.

The relevant file is:
- `src/robust_optimize/optimization.py` — the optimization loop, per-problem optimizer functions

## Strategies to Explore

### 1. Optimizer Choice
- The current code supports Adam and L-BFGS. Try:
  - Different learning rates and schedules (cosine annealing, warm restarts)
  - L-BFGS with different history sizes and line search strategies
  - Natural gradient or conjugate gradient methods
  - Switching optimizer mid-optimization (e.g., Adam for warm-up, L-BFGS for refinement)

### 2. Initialization Strategies
- Better initial controls can avoid local minima and reduce the number of iterations
- Try initializing from the training data mean, or from a coarse-to-fine strategy
- For Poisson: the current random Fourier basis initialization could be improved
- For Burgers: try initializing from the uncontrolled solution or a smooth interpolation

### 3. Regularization Tuning
- Adjust the regularization parameter α — too small leads to distribution shift, too large restricts the control space
- Try different regularization norms: L1 (sparsity), TV (piecewise constant), H1 (smoothness)
- Try adaptive regularization that increases when the surrogate confidence drops

### 4. Multi-Start and Ensemble
- Run optimization from multiple random initial points and pick the best result
- Average optimized controls from multiple starts to reduce variance
- Use the ensemble disagreement as a signal for where the surrogate is unreliable

### 5. Trust Region Methods
- Constrain how far the control can move from the training distribution in each step
- Use the surrogate's prediction uncertainty (if available) to adapt the trust region
- Project the control back onto a "safe" manifold after each gradient step

### 6. Post-Processing
- After optimization, refine the control using the true FDM solver for a few steps
- Smooth the optimized control to reduce high-frequency artifacts
- Validate the optimized control on multiple FDM solver resolutions

## What to Track

When making changes, always:
- Log the final objective value from both the surrogate and the FDM solver
- Track the convergence curve (objective vs iteration)
- Record the relative L2 error between surrogate and FDM predictions at the optimized control
- Note the optimization wall-clock time
