"""File path resolving utilities."""

from pathlib import Path


def resolve_root_dir() -> Path:
    """Resolve the path to the project's root directory.

    Returns:
        Path: The path to the project's root directory.
    """
    return Path(__file__).resolve().parent.parent.parent


def resolve_dotenv_file() -> Path:
    """Resolve the path to the project's .env file.

    Returns:
        Path: The path to the project's .env file.
    """
    return resolve_root_dir() / ".env"


def resolve_data_dir() -> Path:
    """Resolve the path to the project's data directory.

    Returns:
        Path: The path to the project's data directory.
    """
    return resolve_root_dir() / "data"


def resolve_results_dir(experiment: str, subdirs: list[str] | None = None) -> Path:
    """Resolve the path to the results directory for the given experiment.
    Optionally, specify any subdirectories in the experiment's results
    directory to resolve the path to.

    Args:
        experiment (str): The name of the experiment to resolve the path to the
            results directory for.
        subdirs (list[str] | None): The subdirectories to resolve the path to
            in the experiment's results directory. Defaults to None.

    Returns:
        Path: The path to the results directory for the given experiment and
            subdirectories, if specified. If no subdirectories are specified,
            return the path to the experiment's results directory.
    """
    path = resolve_root_dir() / "experiments" / experiment / "results"
    if subdirs is not None:
        for subdir in subdirs:
            path /= subdir
    path.mkdir(parents=True, exist_ok=True)
    return path
