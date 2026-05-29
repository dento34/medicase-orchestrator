"""Build helper for the MediCase coded-agent package.

Copies the shared `agents` package into this project (so the package is
self-contained for `uipath pack`), then you can run the UiPath CLI:

    python build.py            # refresh the local agents/ copy
    uipath init                # regenerate entry-points.json (4 entrypoints)
    uipath pack                # -> .uipath/medicase-coded-agents.<ver>.nupkg
    uipath publish --tenant    # publish to the tenant package feed

Auth: the CLI reads UIPATH_URL and UIPATH_ACCESS_TOKEN. Map them from the
repo .env (UIPATH_TENANT_URL / UIPATH_PAT) before calling publish, e.g.:

    set UIPATH_URL=%UIPATH_TENANT_URL%
    set UIPATH_ACCESS_TOKEN=%UIPATH_PAT%

The 4 entrypoints exposed by this package (see uipath.json):
    LanguageAgent    main_language.py:main     (Stage 1 Intake)
    RTSLookupAgent   main_rts.py:main          (Stage 2 Stabilization)
    SummaryAgent     main.py:main              (Stage 3 Handoff)
    ComplianceAgent  main_compliance.py:main   (Stage 4 Post-incident)
"""
from __future__ import annotations

import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE.parent / "agents"
DST = HERE / "agents"


def main() -> None:
    if not SRC.is_dir():
        raise SystemExit(f"Source package not found: {SRC}")
    if DST.exists():
        shutil.rmtree(DST)
    shutil.copytree(
        SRC,
        DST,
        ignore=shutil.ignore_patterns("__pycache__", "tests", "*.pyc"),
    )
    print(f"Copied {SRC} -> {DST}")


if __name__ == "__main__":
    main()
