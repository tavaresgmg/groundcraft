#!/usr/bin/env python3
"""Hidden outcome oracle for the tiny label fixture."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path


def main() -> int:
    workspace = Path(sys.argv[1]).resolve()
    module_path = workspace / "ui.py"
    spec = importlib.util.spec_from_file_location("groundcraft_tiny_ui", module_path)
    if spec is None or spec.loader is None:
        return 2
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return 0 if module.save_button_label() == "Save changes" else 1


if __name__ == "__main__":
    raise SystemExit(main())
