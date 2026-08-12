# PyTorch

## Training-loop correctness - the bugs that waste GPU-days

1. **The loop order is liturgy:** `optimizer.zero_grad()` -> forward -> `loss.backward()` -> `optimizer.step()` (scheduler after optimizer). A missing `zero_grad` accumulates gradients silently; a missing `step` trains nothing while the loss "runs."
2. **Mode switches are mandatory:** `model.train()` for training, `model.eval()` + `torch.no_grad()`/`inference_mode()` for evaluation - dropout and batchnorm behave differently, and eval without `no_grad` leaks memory into stored graphs.
3. **Loss functions have input contracts - read them:** `CrossEntropyLoss` takes raw logits and class indices (not softmaxed probs, not one-hot); `BCEWithLogitsLoss` over sigmoid+BCE (numerical stability). Wrong-input losses train - badly and silently.
4. **Shapes and broadcasting are asserted, not hoped:** a (N,1) vs (N,) target mismatch broadcasts into garbage loss without erroring. Assert shapes at module boundaries; `einops`/named comments for non-obvious rearranges.
5. **Non-determinism is opt-out, reproducibility is work:** seed everything (`torch.manual_seed`, cuda, numpy, dataloader workers via `worker_init_fn`/generator), note that full determinism costs speed (`use_deterministic_algorithms`) - decide and document per project.

## Device, memory, performance

6. **Device-agnostic code:** `device = "cuda" if available else "cpu"` once, `.to(device)` for model and every batch; never hardcode `.cuda()`. Create tensors on-device (`torch.zeros(..., device=device)`), don't create-then-move in hot loops.
7. **The silent GPU-memory leaks:** accumulating `loss` (the graph) instead of `loss.item()` in running totals; storing tensors with history in lists; forgetting `detach()` before logging/plotting. Metrics use `.item()`/`.detach()`.
8. **DataLoader is usually the bottleneck:** `num_workers > 0`, `pin_memory=True` on GPU, transforms that don't fight the GIL; profile before blaming the model. Batch size tuned with AMP (`torch.autocast` + `GradScaler` where applicable) before gradient tricks.
9. **`torch.compile` where the project's version supports it and it wins** - measured, not assumed; know graph breaks. Version check (`requirements`/lockfile) before using newer APIs at all.

## Structure and lifecycle

10. **Modules are composable and parameterized:** layers in `__init__`, computation in `forward` (call the module, never `module.forward()` directly), no hardcoded batch sizes/shapes, config through constructor args not globals.
11. **Checkpoints are `state_dict`s, never pickled whole models:** save `{model, optimizer, scheduler, epoch, ...}` dicts; load with `map_location`; `weights_only=True` when loading anything you didn't create (pickle is code execution). Resume must restore optimizer state, not just weights.
12. **Validate the pipeline before the science:** overfit a single batch first (loss -> ~0 proves model+loss+optimizer wiring), then train. A model that can't memorize 32 samples has a bug, not a hyperparameter problem.
13. **Gradient hygiene when it applies:** clipping (`clip_grad_norm_`) declared with the value logged, `requires_grad`/freeze semantics explicit when fine-tuning, `with torch.no_grad()` for manual weight surgery.
14. **Log like an experimenter:** loss curves, LR, sample predictions to the project's tracker (wandb/tensorboard); every run reproducible from config + seed + code version - an untracked good run is an unrepeatable rumor.
