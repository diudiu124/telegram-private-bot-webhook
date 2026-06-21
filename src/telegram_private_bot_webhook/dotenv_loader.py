from __future__ import annotations

import os
from pathlib import Path


def load_dotenv_file(path: str = ".env") -> None:
    candidates = []

    cwd = Path.cwd().resolve()
    candidates.extend(parent / path for parent in (cwd, *cwd.parents))

    module_dir = Path(__file__).resolve().parents[2]
    candidates.extend(parent / path for parent in (module_dir, *module_dir.parents))

    seen: set[Path] = set()
    file_path = None
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.exists():
            file_path = candidate
            break

    if file_path is None:
        return

    for raw_line in file_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")

        if key:
            os.environ.setdefault(key, value)
