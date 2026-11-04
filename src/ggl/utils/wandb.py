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


def create_wandb_config() -> dict[str, Any]:
    """Create a W&B config dictionary from the SLURM environment variables.

    Returns:
        dict[str, Any]: The W&B config dictionary.
    """
    job_id = os.environ.get("SLURM_JOB_ID")
    job_name = os.environ.get("SLURM_JOB_NAME")
    array_job_id = os.environ.get("SLURM_ARRAY_JOB_ID")
    array_task_id = os.environ.get("SLURM_ARRAY_TASK_ID")

    # Convert SLURM environment variables to integers if they are not None.
    if job_id is not None:
        job_id = int(job_id)
    if array_job_id is not None:
        array_job_id = int(array_job_id)
    if array_task_id is not None:
        array_task_id = int(array_task_id)

    return {
        "slurm_job_id": job_id,
        "slurm_job_name": job_name,
        "slurm_array_job_id": array_job_id,
        "slurm_array_task_id": array_task_id,
    }
