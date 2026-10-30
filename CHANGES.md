# Changes from the earlier offline package

Default input: synthetic demo points -> sourced real London landmark points.
Distance model: Haversine -> directed shortest driving-road length.
Haversine is now used only for graph sizing and coordinate snap checks.
Map: plain SVG -> Folium/Leaflet OpenStreetMap tiles.
Output entry point: results/report.html -> results/street_map.html.
New module: map_view.py. Road code and main.py replaced rather than patched.
Visible node names and IDs are built in once; no duplicate-label loop.
Named markers stay on snapped graph positions; original points are another layer.
Nearest Neighbor and 2-opt remain explicit for DAA explanation.
All costs remain km, not minutes. No live traffic or travel time is invented.

The real CSV is not Starbucks data. It describes real landmarks with approximate
reference coordinates. No real delivery operation is implied.
