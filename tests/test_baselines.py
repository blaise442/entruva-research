import numpy as np
from src.models.baselines import naive_baseline

rng = np.random.default_rng(5)
N = 240
MODELS = rng.choice(["gpt-x", "claude-y", "small-z"], N)
TASKS = rng.choice(["code", "web", "retail"], N)
LENGTH = rng.integers(1, 60, N).astype(float)
# failures concentrate in one model and in long tasks
Y = ((MODELS == "small-z") & (LENGTH > 30)).astype(int) | (rng.uniform(size=N) < 0.05).astype(int)

def test_probabilities_and_signal():
    p = naive_baseline(MODELS, TASKS, LENGTH, Y, MODELS, TASKS, LENGTH)
    assert p.shape == (N,) and ((0 <= p) & (p <= 1)).all()
    assert p[MODELS == "small-z"].mean() > p[MODELS == "gpt-x"].mean()

def test_unseen_categories_do_not_crash_or_collapse():
    # grouped CV holds out agents, not models: the baseline keys are shared, so
    # predictions on new agents using known models must still vary
    test_models = np.array(["gpt-x", "small-z", "brand-new-model"])
    test_tasks = np.array(["code", "retail", "never-seen-task"])
    test_len = np.array([5.0, 50.0, 20.0])
    p = naive_baseline(MODELS, TASKS, LENGTH, Y, test_models, test_tasks, test_len)
    assert p.shape == (3,) and ((0 <= p) & (p <= 1)).all()
    assert p[1] > p[0]
    assert len(np.unique(p)) > 1
