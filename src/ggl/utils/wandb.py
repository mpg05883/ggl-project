"""Wandb experiment tracking."""

import logging
import os
from argparse import Namespace
from typing import Any

import wandb
from dotenv import load_dotenv
from wandb import Run

from ggl.utils.path import resolve_dotenv_file

logger = logging.getLogger(__name__)


def init_run(
    args: Namespace,
    *,
    job_type: str,
    name: str,
    group: str | None = None,
    config: dict[str, Any] | None = None,
    tags: list[str] | None = None,
    notes: str | None = None,
) -> Run:
    """Start a W&B run. Does nothing if `wandb_mode` is set to "disabled".

    Args:
        args (Namespace): The script's parsed arguments. All of them are logged
            as the run config.
        job_type (str): The kind of run (e.g., "forecast" or "evaluate").
        name (str): The run name (e.g., the model name).
        group (str | None): Groups the array tasks of one experiment. Defaults
            to "<experiment>/<track>" from `args`.
        config (dict[str, Any] | None): Additional config values to add to the
            run config. Defaults to None.
        tags (list[str] | None): Tags for filtering runs in the UI. Defaults to
            None.
        notes (str | None): Notes for the run. Defaults to None.

    Returns:
        Run: The active run, which is a disabled run if tracking is off or
            failed to start.
    """
    # If wandb_mode is set to "disabled", return a disabled run
    if getattr(args, "wandb_mode", "disabled") == "disabled":
        os.environ["WANDB_MODE"] = "disabled"
        return wandb.init(mode="disabled")

    experiment = getattr(args, "experiment", None)

    # Default group to <experiment> if not provided
    if group is None and experiment is not None:
        group = experiment

    load_dotenv(resolve_dotenv_file())

    kwargs: dict[str, Any] = {
        "project": os.environ.get("WANDB_PROJECT"),
        "entity": os.environ.get("WANDB_ENTITY"),
        "name": name,
        "group": group,
        "job_type": job_type,
        "tags": tags,
        "config": {**vars(args), **(config or {})},
        "notes": notes,
    }

    try:
        return wandb.init(**kwargs)
    except Exception as e:  # noqa: BLE001 - never let tracking kill a job
        logger.warning(f"W&B tracking disabled: could not start a run ({e})")
        os.environ["WANDB_MODE"] = "disabled"
        return wandb.init(mode="disabled")
