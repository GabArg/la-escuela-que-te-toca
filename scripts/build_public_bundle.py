"""Construye el bundle mínimo de serving sin recalcular indicadores."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "data" / "processed"
DEFAULT_TARGET = ROOT / "data" / "public"
BUNDLE_VERSION = "2026.09.13.1"

ARTIFACTS: dict[str, dict[str, Any]] = {
    "perfiles_territoriales.parquet": {
        "required": ["departamento_id", "departamento_nombre", "provincia_nombre", "clave_territorial"],
        "logical_source": "Perfil territorial integrado",
    },
    "senales_prioritarias_perfiles.parquet": {
        "required": ["departamento_id", "prioridad", "dimension", "senal", "evidencia"],
        "logical_source": "Señales prioritarias auditadas",
    },
    "pares_comparables.parquet": {
        "required": ["departamento_id", "par_departamento_id", "tipo_comparacion", "distancia"],
        "logical_source": "Motor de pares comparables",
    },
    "brechas_entre_pares.parquet": {
        "required": ["departamento_id", "par_departamento_id", "tipo_comparacion"],
        "logical_source": "Brechas descriptivas posteriores a similitud",
    },
    "ra_2011_2025_long.parquet": {
        "required": ["anio", "departamento_id", "variable", "valor"],
        "logical_source": "Serie histórica RA comparable",
    },
    "departamentos_argentina.geojson": {
        "required": ["provincia_id", "provincia_nombre", "departamento_id", "departamento_nombre", "clave_territorial"],
        "logical_source": "GeoRef Argentina, geometrías no simplificadas",
    },
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def inspect_artifact(path: Path, spec: dict[str, Any]) -> tuple[int, list[str]]:
    if path.suffix == ".parquet":
        frame = pd.read_parquet(path)
        rows, columns = len(frame), list(frame.columns)
    else:
        document = json.loads(path.read_text(encoding="utf-8"))
        features = document.get("features")
        if not isinstance(features, list):
            raise ValueError(f"{path.name}: GeoJSON sin lista features")
        rows = len(features)
        columns = sorted({key for feature in features for key in feature.get("properties", {})})
        ids = [str(feature.get("properties", {}).get("departamento_id")) for feature in features]
        if rows != 529 or len(set(ids)) != 529 or "None" in ids:
            raise ValueError(f"{path.name}: se esperaban 529 IDs territoriales únicos")
    missing = sorted(set(spec["required"]) - set(columns))
    if missing:
        raise ValueError(f"{path.name}: faltan columnas obligatorias: {', '.join(missing)}")
    return rows, columns


def build_bundle(source: Path = DEFAULT_SOURCE, target: Path = DEFAULT_TARGET) -> dict[str, Any]:
    missing = [name for name in ARTIFACTS if not (source / name).is_file()]
    if missing:
        raise FileNotFoundError("Faltan artefactos procesados: " + ", ".join(missing))
    target.mkdir(parents=True, exist_ok=True)
    files = []
    for name, spec in ARTIFACTS.items():
        origin, destination = source / name, target / name
        rows, columns = inspect_artifact(origin, spec)
        shutil.copy2(origin, destination)
        files.append({
            "name": name,
            "sha256": sha256(destination),
            "size_bytes": destination.stat().st_size,
            "rows": rows,
            "columns": len(columns),
            "column_names": columns,
            "logical_source": spec["logical_source"],
        })
    manifest = {
        "bundle_version": BUNDLE_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "notice": "Artefactos derivados exclusivamente de datos públicos oficiales; no son fuentes raw.",
        "files": files,
    }
    (target / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--target", type=Path, default=DEFAULT_TARGET)
    args = parser.parse_args()
    manifest = build_bundle(args.source.resolve(), args.target.resolve())
    total = sum(item["size_bytes"] for item in manifest["files"])
    print(f"Bundle {manifest['bundle_version']}: {len(manifest['files'])} archivos, {total} bytes")


if __name__ == "__main__":
    main()
