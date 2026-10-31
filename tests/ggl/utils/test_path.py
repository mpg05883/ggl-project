from pathlib import Path

import pytest

from ggl.utils import path
from ggl.utils.path import (
    resolve_data_dir,
    resolve_dotenv_file,
    resolve_results_dir,
    resolve_root_dir,
)


@pytest.fixture
def fake_root(monkeypatch, tmp_path):
    """Point `resolve_root_dir` at a temporary directory, so tests of
    `resolve_results_dir` do not create folders in the real repo."""
    monkeypatch.setattr(path, "resolve_root_dir", lambda: tmp_path)
    return tmp_path


class TestResolveRootDir:
    def test_returns_absolute_path(self):
        assert resolve_root_dir().is_absolute()

    def test_is_repo_root(self):
        root = resolve_root_dir()
        assert (root / "pyproject.toml").is_file()
        assert (root / "src" / "ggl").is_dir()

    def test_contains_this_test_file(self):
        assert Path(__file__).resolve().is_relative_to(resolve_root_dir())


class TestResolveDotenvFile:
    def test_is_dot_env_in_root(self):
        assert resolve_dotenv_file() == resolve_root_dir() / ".env"

    def test_does_not_create_file(self, fake_root):
        assert resolve_dotenv_file() == fake_root / ".env"
        assert not (fake_root / ".env").exists()


class TestResolveDataDir:
    def test_is_data_in_root(self):
        assert resolve_data_dir() == resolve_root_dir() / "data"

    def test_does_not_create_directory(self, fake_root):
        assert resolve_data_dir() == fake_root / "data"
        assert not (fake_root / "data").exists()


class TestResolveResultsDir:
    def test_without_subdirs(self, fake_root):
        result = resolve_results_dir("exp")
        assert result == fake_root / "experiments" / "exp" / "results"
        assert result.is_dir()

    def test_with_subdirs(self, fake_root):
        result = resolve_results_dir("exp", ["a", "b"])
        assert result == fake_root / "experiments" / "exp" / "results" / "a" / "b"
        assert result.is_dir()

    def test_empty_subdirs_is_results_dir(self, fake_root):
        assert resolve_results_dir("exp", []) == fake_root / "experiments" / "exp" / "results"

    def test_existing_directory_and_contents_are_kept(self, fake_root):
        existing = fake_root / "experiments" / "exp" / "results"
        existing.mkdir(parents=True)
        (existing / "keep.txt").write_text("x")
        assert resolve_results_dir("exp") == existing
        assert (existing / "keep.txt").read_text() == "x"

    def test_does_not_touch_data_dir(self, fake_root):
        resolve_results_dir("exp", ["a"])
        assert not (fake_root / "data").exists()
