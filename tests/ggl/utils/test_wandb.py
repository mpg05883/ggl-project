import os
from argparse import Namespace

import pytest

from ggl.utils.wandb import init_run


@pytest.fixture(autouse=True)
def isolated_environ(monkeypatch):
    """Give each test its own copy of the environment, so `WANDB_*` variables
    set by `init_run` or `load_dotenv` do not leak between tests."""
    monkeypatch.setattr(os, "environ", os.environ.copy())
    for var in ("WANDB_PROJECT", "WANDB_ENTITY", "WANDB_MODE"):
        os.environ.pop(var, None)


@pytest.fixture
def init_calls(monkeypatch, tmp_path):
    """Replace `wandb.init` with a fake that records its keyword arguments and
    point the repo `.env` at an empty temporary file."""
    calls: list[dict] = []

    def fake_init(**kwargs):
        calls.append(kwargs)
        return kwargs

    monkeypatch.setattr("ggl.utils.wandb.wandb.init", fake_init)
    monkeypatch.setattr(
        "ggl.utils.wandb.resolve_dotenv_file", lambda: tmp_path / ".env"
    )
    return calls


class TestInitRunDisabled:
    """Tests for `init_run` when tracking is off."""

    @pytest.mark.parametrize(
        "args", [Namespace(), Namespace(wandb_mode="disabled")]
    )
    def test_returns_a_disabled_run(self, init_calls, args):
        """Without `wandb_mode` (or with "disabled") a disabled run is made."""
        run = init_run(args, job_type="forecast", name="model")

        assert run == {"mode": "disabled"}
        assert init_calls == [{"mode": "disabled"}]

    def test_sets_wandb_mode_env_var(self, init_calls):
        """Child processes are told to disable tracking too."""
        init_run(Namespace(), job_type="forecast", name="model")

        assert os.environ["WANDB_MODE"] == "disabled"


class TestInitRunEnabled:
    """Tests for `init_run` when tracking is on."""

    def test_uses_project_and_entity_from_dotenv(self, init_calls, tmp_path):
        """An enabled run takes its project and entity from the repo `.env`."""
        (tmp_path / ".env").write_text(
            'WANDB_PROJECT="ChronoSense"\nWANDB_ENTITY="mpg48-yale"\n'
        )

        init_run(
            Namespace(wandb_mode="offline"), job_type="forecast", name="model"
        )

        assert init_calls[0]["project"] == "ChronoSense"
        assert init_calls[0]["entity"] == "mpg48-yale"

    def test_environment_wins_over_dotenv(
        self, init_calls, tmp_path, monkeypatch
    ):
        """Variables already set in the environment are not overridden."""
        (tmp_path / ".env").write_text("WANDB_PROJECT=from-file\n")
        monkeypatch.setenv("WANDB_PROJECT", "from-env")

        init_run(
            Namespace(wandb_mode="online"), job_type="forecast", name="model"
        )

        assert init_calls[0]["project"] == "from-env"

    def test_passes_run_metadata(self, init_calls):
        """The name, job type, group, tags, and notes are passed through."""
        init_run(
            Namespace(wandb_mode="online"),
            job_type="forecast",
            name="Ridge",
            group="my-group",
            tags=["ml", "fixed_window"],
            notes="a note",
        )

        call = init_calls[0]
        assert call["name"] == "Ridge"
        assert call["job_type"] == "forecast"
        assert call["group"] == "my-group"
        assert call["tags"] == ["ml", "fixed_window"]
        assert call["notes"] == "a note"

    def test_group_defaults_to_the_experiment(self, init_calls):
        """With no group, runs are grouped by the experiment name."""
        args = Namespace(wandb_mode="online", experiment="exp")

        init_run(args, job_type="forecast", name="model")

        assert init_calls[0]["group"] == "exp"

    def test_explicit_group_wins_over_the_experiment(self, init_calls):
        """A given group is not replaced by the experiment name."""
        args = Namespace(wandb_mode="online", experiment="exp")

        init_run(args, job_type="forecast", name="model", group="other")

        assert init_calls[0]["group"] == "other"

    def test_no_group_without_an_experiment(self, init_calls):
        """With neither a group nor an experiment, no group is set."""
        init_run(
            Namespace(wandb_mode="online"), job_type="forecast", name="model"
        )

        assert init_calls[0]["group"] is None

    def test_config_has_args_and_extra_config(self, init_calls):
        """The config holds every argument, plus the extra config, which wins
        on a conflict."""
        args = Namespace(wandb_mode="online", seed=1, track="fixed_window")

        init_run(
            args,
            job_type="forecast",
            name="model",
            config={"model": "Ridge", "seed": 2},
        )

        assert init_calls[0]["config"] == {
            "wandb_mode": "online",
            "seed": 2,
            "track": "fixed_window",
            "model": "Ridge",
        }


class TestInitRunFailure:
    """Tests for `init_run` when W&B cannot start a run."""

    def test_falls_back_to_a_disabled_run(self, monkeypatch, tmp_path):
        """A failure to start a run never raises; a disabled run is used."""
        calls: list[dict] = []

        def failing_init(**kwargs):
            calls.append(kwargs)
            if kwargs.get("mode") != "disabled":
                raise RuntimeError("no network")
            return kwargs

        monkeypatch.setattr("ggl.utils.wandb.wandb.init", failing_init)
        monkeypatch.setattr(
            "ggl.utils.wandb.resolve_dotenv_file", lambda: tmp_path / ".env"
        )

        run = init_run(
            Namespace(wandb_mode="online"), job_type="forecast", name="m"
        )

        assert run == {"mode": "disabled"}
        assert calls[-1] == {"mode": "disabled"}
        assert os.environ["WANDB_MODE"] == "disabled"
