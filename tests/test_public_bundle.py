import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd

from scripts.build_public_bundle import ARTIFACTS, inspect_artifact

PUBLIC = Path("data/public")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_manifest_and_required_artifacts():
    manifest = json.loads((PUBLIC / "manifest.json").read_text(encoding="utf-8"))
    entries = {item["name"]: item for item in manifest["files"]}
    assert set(entries) == set(ARTIFACTS)
    assert manifest["bundle_version"]
    for name, entry in entries.items():
        path = PUBLIC / name
        assert path.is_file()
        assert path.stat().st_size == entry["size_bytes"]
        assert _sha256(path) == entry["sha256"]


def test_bundle_schemas():
    for name, spec in ARTIFACTS.items():
        rows, columns = inspect_artifact(PUBLIC / name, spec)
        assert rows > 0
        assert set(spec["required"]).issubset(columns)


def test_profile_and_geojson_have_same_529_ids():
    profiles = pd.read_parquet(PUBLIC / "perfiles_territoriales.parquet")
    geojson = json.loads((PUBLIC / "departamentos_argentina.geojson").read_text(encoding="utf-8"))
    geo_ids = {str(item["properties"]["departamento_id"]) for item in geojson["features"]}
    assert len(profiles) == profiles.departamento_id.nunique() == 529
    assert geo_ids == set(profiles.departamento_id.astype(str))


def test_clean_clone_loading_without_processed(tmp_path):
    empty_processed = tmp_path / "processed"
    empty_processed.mkdir()
    env = os.environ.copy()
    env["PUBLIC_DATA_DIR"] = str(PUBLIC.resolve())
    env["PROCESSED_DATA_DIR"] = str(empty_processed)
    env["APP_ALLOW_PIPELINE_REBUILD"] = "0"
    code = (
        "from app.components.data import load_profiles,load_signals,load_pairs,load_gaps,load_history;"
        "assert len(load_profiles())==529;assert len(load_signals())==751;"
        "assert len(load_pairs())==4975;assert len(load_gaps())==4975;"
        "assert not load_history().empty"
    )
    subprocess.run([sys.executable, "-c", code], cwd=Path.cwd(), env=env, check=True)


def test_manifest_contains_no_absolute_local_paths():
    text = (PUBLIC / "manifest.json").read_text(encoding="utf-8")
    assert "C:\\" not in text and "/Users/" not in text and "/home/" not in text
