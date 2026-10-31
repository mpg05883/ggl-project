# Hyperparameter Tuning Guide

Distilled from Google's *Deep Learning Tuning Playbook* (Godbole, Dahl, Gilmer, Shallue, Nado, 2023), which is licensed CC BY 4.0. Full text: https://developers.google.com/machine-learning/guides/deep-learning-tuning-playbook

This is a condensed paraphrase, not the original. The authors stress that it reflects their experience, not settled fact. Treat the numbers below as rules of thumb, and see the "Repo-specific rules" section at the bottom for what overrides them.

## 1. Before tuning anything

- Start from an established architecture and optimizer for this type of problem. Reproduce a close prior paper's setup if one exists.
- Begin with a simple, fast, cheap config that gets a reasonable result (clearly better than chance). No fancy schedules or extras until later. A constant learning rate and a smaller model are fine to start.
- Metrics must be implemented and trusted before tuning begins. A tuning run on a buggy metric is wasted compute.
- Batch size is a throughput knob, not a tuning knob. Use the largest size that fits and still increases throughput. With everything else re-tuned, batch size should not change the best achievable validation result. Changing it means re-tuning the learning rate, momentum, and regularization.
- Avoid gradient accumulation just to simulate a bigger batch. It gives no speed benefit.

## 2. The tuning loop

Work in rounds. Each round: pick one narrow goal, run experiments, learn from them, then decide whether to adopt the change. Most time should go to understanding the problem (exploration), not greedily chasing validation numbers.

**Classify every hyperparameter for the current goal:**
- **Scientific:** the thing whose effect you are measuring (e.g. number of layers).
- **Nuisance:** must be re-tuned for each scientific setting for the comparison to be fair (almost always the learning rate and other optimizer settings; regularization strengths).
- **Fixed:** held constant this round. Any conclusion carries a caveat about these values. Don't fix a nuisance parameter that interacts strongly with the scientific one (weight decay vs. model size is the classic example).

Rules of thumb:
- Optimizer hyperparameters (learning rate, momentum, betas, schedule) are almost never scientific, and should usually be tuned per setting, not fixed.
- The *choice* of optimizer, architecture size, and whether to use a technique (dropout yes/no) are typically scientific or fixed.
- Conditional hyperparameters with the same name in different optimizers (e.g. `learning_rate` for SGD vs. Adam) are different parameters with different good ranges.

**Study design:** one study per scientific setting, each tuning over the nuisance parameters, then compare the best trial from each. Budget is a three-way tradeoff: values of the scientific parameter compared, width of nuisance search space, and sampling density.

## 3. Search method

- During exploration, prefer **quasi-random search** (e.g. a scrambled Halton sequence). It's non-adaptive, so you can re-analyze with a different objective afterward, it's reproducible, it parallelizes well, and its uniform coverage makes results easy to read. Plain random search is an acceptable substitute. Grid search is fine only in 1 to 2 dimensions.
- Once exploration is done and the search space is well understood, switch to Bayesian optimization for the final push. It's also more attractive when you can run few trials in parallel but many in sequence. Make sure the tool handles diverged trials as infeasible.
- Anecdotally, adaptive methods struggle to beat quasi-random search given 2x the budget when trials run in parallel.
- Number of trials has a big effect. Even at around 20 trials the luck of a given study can exceed seed-to-seed variance, so never read much into a study with a handful of trials.
- Adam: if under 10 trials, tune only the learning rate; 10 to 25, add beta1; 25+, add epsilon; well beyond that, beta2.

## 4. Checks after every study

1. **Search-space boundaries:** if the best point sits near an edge of the range, expand and rerun. Plot validation metric vs. each hyperparameter (one point per trial) to see this.
2. **Enough samples:** if you can't tell, sample more or lower the ambition of the claim.
3. **Infeasible fraction:** many diverged or NaN trials mean reparameterize the search space, or look for a bug.
4. **Optimization problems:** see section 6.
5. **Training curves of the best trials:** look for validation error rising (problematic overfitting), high step-to-step noise late in training, trials still improving at the end (compute-bound, train longer), or plateaus long before the end (shorten training).
   - If the best trial for a setting overfits, add regularization and rerun before comparing scientific settings.
   - Beware "regularization by accident": a smaller learning rate can hide problems, and picking the best trial favors it.
6. **Isolation plots:** for a scientific hyperparameter, plot the best trial across nuisance settings at each value, so comparisons are apples-to-apples.

Automate the standard plots (hyperparameter axis plots, training curves for all trials) so they actually get looked at.

## 5. Deciding whether to adopt a change

- Variance comes from three sources: **trial variance** (seed to seed), **study variance** (search randomness), and **data sampling variance**.
- Before adopting a change, rerun the best trial several times (N seeds) to estimate trial variance, and compare against the baseline's variance too.
- Don't demand certainty, but adopt only changes whose gain outweighs the complexity they add.
- Pick checkpoints and report results on the validation set during development. Look at the test set only after exploration is over.

## 6. Training length and stability

**How long to train**
- *Compute-bound* (still improving when you stop): longer is better, up to what you can afford. Tune in 1 to 3 rounds with increasing run length; typically short runs to pick model and optimizer settings, then a few long runs on the best points. Warmup length, initialization, and early instability fixes transfer best from short to long runs. Learning rate schedules transfer poorly. Don't spend all the extra steps at a tiny learning rate.
- *Not compute-bound* (plateaus): pick a generous step budget and use it for every trial. Do not tune `max_train_steps` inside a study. Instead look at where the best checkpoint falls: always in the first ~10% means the budget is too high; consistently in the last ~25% means train longer and retune the decay schedule.
- Anything that increases gradient noise (smaller batch, augmentation, dropout) can increase steps needed.

**Schedule defaults:** use some non-constant schedule, and tune it. Linear or cosine decay are good defaults. Don't copy complicated hand-tuned schedules from papers.

**Instability**
- Any model diverges at a large enough learning rate; it's only a problem if it forces the learning rate too low.
- Test: sweep the learning rate, find the best one, then check whether loss curves slightly above it show loss spikes. A short run (~500 steps) at about 2x the best learning rate with evaluation every step catches early instability that normal eval schedules miss.
- Fixes, roughly in order: learning rate warmup (best for early instability), gradient clipping (early or mid-training), a different optimizer, architecture best practices (normalization placed inside the residual branch, zero-init residual branches), and lowering the learning rate as a last resort.
- Warmup: ramp from 0 to a base rate about 10x the unstable one; find the shortest warmup that works (sweep orders of magnitude, e.g. 10, 1e3, 1e4, 1e5); the warmup shouldn't exceed ~10% of total steps; if over ~5% is needed, extend the total budget. Typical values range from ~100 steps to 40k+ (transformers often need longer).
- Gradient clipping: log the unclipped gradient norm; set the threshold near the 90th percentile of norms. If over about half the updates are getting clipped, just lower the learning rate instead.

## 7. Evaluation and bookkeeping

- Evaluate on a fixed step interval (not wall-clock time), with an eval batch at least as large as the training batch.
- Save checkpoints often and choose the best one retrospectively. Don't rely on early stopping.
- Make sure eval metrics on a sampled eval set match the full eval set. For rare classes, log raw counts correct, not just rates.
- Track every study: name, config location, short description, number of trials, best validation score, and the exact command to reproduce. Untracked experiments might as well not exist.
- Multi-host training: log and checkpoint from one host only; use the same RNG seed across hosts for initialization but different seeds for data shuffling.

## Repo-specific rules (these override anything above)

Fill these in for your project. Suggested starting points:

- **Approval:** propose the study plan (goal, scientific/nuisance/fixed split, search space, number of trials, estimated GPU-hours) and wait for my approval before submitting any jobs.
- **Budget:** max ___ trials and ___ GPU-hours per round.
- **Selection metric:** ___ on the validation set. Never tune on the test set.
- **Seeds:** at least ___ seeds before claiming an improvement.
- **Logging:** record hypothesis, config, seed, and git hash for every run in ___.
- **Where results go:** ___. Never overwrite existing results.
- **Cluster:** see the relevant cluster file before writing job scripts.
