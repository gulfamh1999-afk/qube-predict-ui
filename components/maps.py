"""Folium map helpers."""

from __future__ import annotations

from typing import Any

import folium
from folium.plugins import Draw, Fullscreen, MeasureControl, MousePosition
from streamlit.components.v1 import html


TILES = {
    "Street": "OpenStreetMap",
    "Terrain": "Stamen Terrain",
    "Satellite": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "Hybrid": "CartoDB positron",
}


def render_parcel_map(
    points: list[tuple[float, float]],
    *,
    height: int = 520,
    draw: bool = True,
    show_grid: bool = False,
    tile_mode: str = "Street",
) -> Any:
    """Render a Leaflet map with parcel overlay and drawing controls."""

    center = _center(points)
    tile = TILES.get(tile_mode, "OpenStreetMap")
    attr = "Tiles" if not str(tile).startswith("http") else "Esri World Imagery"
    fmap = folium.Map(location=[center[1], center[0]], zoom_start=16, tiles=tile, attr=attr)
    if points:
        lat_lon = [(lat, lon) for lon, lat in points]
        folium.Polygon(lat_lon, color="#38c7e8", fill=True, fill_opacity=0.25, weight=3).add_to(fmap)
        for idx, (lon, lat) in enumerate(points, start=1):
            folium.CircleMarker([lat, lon], radius=4, tooltip=f"P{idx}: {lon:.6f}, {lat:.6f}", color="#f0b64a").add_to(fmap)
    if show_grid:
        _add_grid(fmap, center)
    if draw:
        Draw(export=True, draw_options={"polyline": False, "circle": False, "circlemarker": False}).add_to(fmap)
    MeasureControl(position="bottomleft", primary_length_unit="meters").add_to(fmap)
    MousePosition(position="bottomright", separator=", ", prefix="Coordinates").add_to(fmap)
    Fullscreen().add_to(fmap)
    return _display_folium(fmap, height)


def _display_folium(fmap: folium.Map, height: int) -> Any:
    try:
        from streamlit_folium import st_folium

        return st_folium(fmap, height=height, use_container_width=True, returned_objects=["last_clicked", "all_drawings"])
    except ImportError:
        html(fmap.get_root().render(), height=height)
        return {}


def _center(points: list[tuple[float, float]]) -> tuple[float, float]:
    if not points:
        return 72.8777, 19.0760
    return sum(x for x, _ in points) / len(points), sum(y for _, y in points) / len(points)


def _add_grid(fmap: folium.Map, center: tuple[float, float]) -> None:
    lon, lat = center
    step = 0.0005
    for idx in range(-8, 9):
        folium.PolyLine([(lat - 0.004, lon + idx * step), (lat + 0.004, lon + idx * step)], color="#ffffff", opacity=0.18, weight=1).add_to(fmap)
        folium.PolyLine([(lat + idx * step, lon - 0.004), (lat + idx * step, lon + 0.004)], color="#ffffff", opacity=0.18, weight=1).add_to(fmap)