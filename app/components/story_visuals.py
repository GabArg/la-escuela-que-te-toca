"""Visuales SVG editoriales derivados de los datos existentes."""
from __future__ import annotations

from html import escape
from typing import Any, Iterable

import pandas as pd

MAP_BOUNDS = (-74.0, -53.0, -56.0, -21.0)


def _rings(coordinates: Any) -> Iterable[list[list[float]]]:
    if not isinstance(coordinates, list) or not coordinates:
        return
    first = coordinates[0]
    if isinstance(first, list) and first and isinstance(first[0], (int, float)):
        yield coordinates
        return
    for child in coordinates:
        yield from _rings(child)


def _project(point: list[float], width: float, height: float) -> tuple[float, float]:
    min_lon, max_lon, min_lat, max_lat = MAP_BOUNDS
    lon, lat = point[:2]
    return ((lon - min_lon) / (max_lon - min_lon) * width, (max_lat - lat) / (max_lat - min_lat) * height)


def _feature_path(feature: dict[str, Any], width: float, height: float) -> tuple[str, tuple[float, float] | None]:
    paths: list[str] = []
    visible_points: list[list[float]] = []
    for ring in _rings(feature["geometry"]["coordinates"]):
        mainland_ring = [point for point in ring if point[1] >= MAP_BOUNDS[2]]
        if len(mainland_ring) < 3:
            continue
        visible_points.extend(mainland_ring)
        projected = [_project(point, width, height) for point in mainland_ring]
        paths.append("M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in projected) + "Z")
    if not visible_points:
        return "", None
    centroid = _project(
        [
            sum(point[0] for point in visible_points) / len(visible_points),
            sum(point[1] for point in visible_points) / len(visible_points),
        ],
        width,
        height,
    )
    return "".join(paths), centroid


def territory_mesh_svg(
    geojson: dict[str, Any],
    highlighted_ids: tuple[str, ...] = (),
    connect: bool = False,
    css_class: str = "story-map",
) -> str:
    """Dibuja las unidades existentes; no modifica el GeoJSON ni persiste derivados."""
    width, height = 420.0, 700.0
    highlights = set(highlighted_ids)
    paths: list[str] = []
    centers: dict[str, tuple[float, float]] = {}
    for feature in geojson["features"]:
        territory_id = str(feature["properties"]["departamento_id"])
        path, centroid = _feature_path(feature, width, height)
        if centroid is not None:
            centers[territory_id] = centroid
        paths.append(
            f'<path class="{"territory-accent" if territory_id in highlights else "territory-line"}" '
            f'data-territory="{escape(territory_id)}" d="{path}"/>'
        )
    connection = ""
    if connect and len(highlighted_ids) == 2 and all(item in centers for item in highlighted_ids):
        start, end = (centers[item] for item in highlighted_ids)
        connection = (
            f'<path class="territory-connection" d="M{start[0]:.1f},{start[1]:.1f} '
            f'L{end[0]:.1f},{end[1]:.1f}"/>'
        )
    return (
        f'<svg class="{escape(css_class)}" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'data-territories="{len(geojson["features"])}" role="img" '
        'aria-label="Argentina representada por sus unidades territoriales">'
        f'{connection}{"".join(paths)}</svg>'
    )


def territory_silhouette_svg(
    geojson: dict[str, Any], territory_id: str, label: str, css_class: str = "story-silhouette"
) -> str:
    """Normaliza una geometría real dentro de su propio viewBox, sin ejes ni interacción."""
    feature = next(
        (item for item in geojson["features"] if str(item["properties"]["departamento_id"]) == str(territory_id)),
        None,
    )
    if feature is None:
        raise ValueError(f"No existe geometría para el territorio {territory_id}.")
    rings = [list(ring) for ring in _rings(feature["geometry"]["coordinates"])]
    points = [point for ring in rings for point in ring]
    if not points:
        raise ValueError(f"La geometría del territorio {territory_id} está vacía.")
    min_lon, max_lon = min(p[0] for p in points), max(p[0] for p in points)
    min_lat, max_lat = min(p[1] for p in points), max(p[1] for p in points)
    width, height, pad = 260.0, 220.0, 12.0
    lon_span, lat_span = max(max_lon - min_lon, 1e-9), max(max_lat - min_lat, 1e-9)
    scale = min((width - 2 * pad) / lon_span, (height - 2 * pad) / lat_span)
    offset_x = (width - lon_span * scale) / 2
    offset_y = (height - lat_span * scale) / 2
    paths = []
    for ring in rings:
        projected = [
            (offset_x + (point[0] - min_lon) * scale, offset_y + (max_lat - point[1]) * scale)
            for point in ring
        ]
        paths.append("M" + " ".join(f"{x:.1f},{y:.1f}" for x, y in projected) + "Z")
    return (
        f'<svg class="{escape(css_class)}" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'data-territory="{escape(str(territory_id))}" role="img" aria-label="Silueta real de {escape(label)}">'
        f'<path d="{"".join(paths)}"/></svg>'
    )


def national_trajectory_svg(national_history: pd.DataFrame) -> str:
    annual = national_history.set_index("anio").sort_index().copy()
    annual["value"] = annual.sobreedad / annual.matricula_grados_comparables * 100
    annual = annual.loc[annual.value.notna()]
    if annual.empty:
        return ""
    width, height, pad = 720.0, 150.0, 8.0
    min_year, max_year = float(annual.index.min()), float(annual.index.max())
    min_value, max_value = float(annual.value.min()), float(annual.value.max())
    span_year = max(max_year - min_year, 1)
    span_value = max(max_value - min_value, 1)
    points = [
        (
            pad + (float(year) - min_year) / span_year * (width - 2 * pad),
            pad + (max_value - float(value)) / span_value * (height - 2 * pad),
        )
        for year, value in annual.value.items()
    ]
    path = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    start, end = points[0], points[-1]
    return (
        f'<svg class="story-trajectory" viewBox="0 0 {width:.0f} {height:.0f}" role="img" '
        'aria-label="Trayectoria nacional de la sobreedad entre 2011 y 2025">'
        f'<path d="{path}"/><circle cx="{start[0]:.1f}" cy="{start[1]:.1f}" r="5"/>'
        f'<circle cx="{end[0]:.1f}" cy="{end[1]:.1f}" r="5"/></svg>'
    )
