from pathlib import Path

import pytest

from voxagent.utils import ensure_output_path, slugify_filename


def test_slugify_filename_removes_unsafe_characters() -> None:
    assert slugify_filename("../demo<>.py") == "demo_.py"


def test_ensure_output_path_stays_inside_output(tmp_path: Path) -> None:
    output_dir = tmp_path / "output"
    output_dir.mkdir()

    target = ensure_output_path(output_dir, "notes.txt")

    assert target == output_dir / "notes.txt"


def test_ensure_output_path_rejects_escape_attempt() -> None:
    output_dir = Path("C:/safe/output")

    with pytest.raises(ValueError):
        ensure_output_path(output_dir, "../../secret.txt")
