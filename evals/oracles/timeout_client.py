#!/usr/bin/env python3
"""Hidden outcome oracle for the shared timeout fixture."""

from __future__ import annotations

import importlib
import sys
from pathlib import Path


def main() -> int:
    workspace = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(workspace))
    services = importlib.import_module("services")
    return 0 if (services.auth_timeout(), services.profile_timeout()) == (0.25, 0.5) else 1


if __name__ == "__main__":
    raise SystemExit(main())
