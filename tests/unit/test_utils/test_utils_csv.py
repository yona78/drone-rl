"""Unit tests for drone_rl.utils module — CSV export."""

import csv
import tempfile
from pathlib import Path

from drone_rl.utils import export_episodes_to_csv


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
