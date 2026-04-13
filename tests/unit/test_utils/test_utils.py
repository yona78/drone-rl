"""Unit tests for drone_rl.utils module."""

import csv
import random
import tempfile
from pathlib import Path

from drone_rl.utils import (
    CONFIG_DIR,
    LAYOUTS_DIR,
    LOGS_DIR,
    POLICIES_DIR,
    PROJECT_ROOT,
    clamp,
    create_rng,
    epsilon_decay,
    export_episodes_to_csv,
    is_valid_coordinate,
    manhattan_distance,
)


class TestPathConstants:
    """Verify pathlib-based path resolution (Review Point #4)."""

    def test_project_root_resolves_to_valid_directory(self) -> None:
        assert PROJECT_ROOT.is_dir(), f"PROJECT_ROOT not a dir: {PROJECT_ROOT}"

    def test_config_dir_exists_under_project_root(self) -> None:
        assert CONFIG_DIR == PROJECT_ROOT / "config"
        assert CONFIG_DIR.is_dir()

    def test_policies_dir_path(self) -> None:
        assert POLICIES_DIR == PROJECT_ROOT / "policies"

    def test_logs_dir_path(self) -> None:
        assert LOGS_DIR == PROJECT_ROOT / "logs"

    def test_layouts_dir_path(self) -> None:
        assert LAYOUTS_DIR == PROJECT_ROOT / "layouts"


class TestCreateRng:
    """Verify local RNG creation (Review Point #3)."""

    def test_create_rng_returns_local_random_instance(self) -> None:
        rng = create_rng(42)
        assert isinstance(rng, random.Random)

    def test_create_rng_deterministic_with_same_seed(self) -> None:
        rng1 = create_rng(42)
        rng2 = create_rng(42)
        seq1 = [rng1.random() for _ in range(10)]
        seq2 = [rng2.random() for _ in range(10)]
        assert seq1 == seq2

    def test_create_rng_different_seeds_different_sequences(self) -> None:
        rng1 = create_rng(42)
        rng2 = create_rng(99)
        seq1 = [rng1.random() for _ in range(10)]
        seq2 = [rng2.random() for _ in range(10)]
        assert seq1 != seq2


class TestClamp:
    """Tests for clamp() utility."""

    def test_clamp_lower_bound(self) -> None:
        assert clamp(-5.0, 0.0, 10.0) == 0.0

    def test_clamp_upper_bound(self) -> None:
        assert clamp(15.0, 0.0, 10.0) == 10.0

    def test_clamp_within_range(self) -> None:
        assert clamp(5.0, 0.0, 10.0) == 5.0


class TestIsValidCoordinate:
    """Tests for is_valid_coordinate() bounds check."""

    def test_is_valid_coordinate_true(self) -> None:
        assert is_valid_coordinate(0, 0, 10, 10) is True
        assert is_valid_coordinate(9, 9, 10, 10) is True

    def test_is_valid_coordinate_false_out_of_bounds(self) -> None:
        assert is_valid_coordinate(-1, 0, 10, 10) is False
        assert is_valid_coordinate(0, -1, 10, 10) is False
        assert is_valid_coordinate(10, 0, 10, 10) is False
        assert is_valid_coordinate(0, 10, 10, 10) is False


class TestManhattanDistance:
    """Tests for manhattan_distance()."""

    def test_manhattan_distance_diagonal(self) -> None:
        assert manhattan_distance(0, 0, 3, 4) == 7

    def test_manhattan_distance_same_point(self) -> None:
        assert manhattan_distance(5, 5, 5, 5) == 0


class TestEpsilonDecay:
    """Tests for epsilon_decay()."""

    def test_epsilon_decay_reduces_value(self) -> None:
        result = epsilon_decay(1.0, 0.995)
        assert result < 1.0
        assert result == 0.995

    def test_epsilon_decay_never_negative(self) -> None:
        result = epsilon_decay(0.001, 0.5)
        assert result >= 0.0


class TestExportEpisodesToCsv:
    """Tests for export_episodes_to_csv()."""

    def test_export_episodes_to_csv_writes_expected_headers(self) -> None:
        rows = [
            {
                "episode": 0,
                "total_reward": 10.0,
                "steps": 3,
                "terminal_reason": "GOAL",
                "epsilon": 1.0,
            }
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "episodes.csv"
            export_episodes_to_csv(rows, str(path))
            with path.open() as fh:
                reader = csv.DictReader(fh)
                headers = reader.fieldnames or []
        expected = {
            "episode",
            "total_reward",
            "steps",
            "terminal_reason",
            "epsilon_used",
            "success_rate",
        }
        assert expected.issubset(set(headers))

    def test_export_episodes_to_csv_writes_cumulative_success_rate(self) -> None:
        rows = [
            {
                "episode": 0,
                "total_reward": 10.0,
                "steps": 3,
                "terminal_reason": "GOAL",
                "epsilon": 1.0,
            },
            {
                "episode": 1,
                "total_reward": -1.0,
                "steps": 5,
                "terminal_reason": "TRAP",
                "epsilon": 0.9,
            },
        ]
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "episodes.csv"
            export_episodes_to_csv(rows, str(path))
            with path.open() as fh:
                out_rows = list(csv.DictReader(fh))
        assert len(out_rows) == 2
        assert out_rows[0]["success_rate"] == "1.0"
        assert out_rows[1]["success_rate"] == "0.5"
