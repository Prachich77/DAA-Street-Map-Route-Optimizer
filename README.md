# DAA Street-Map Route Optimizer - replacement project

## What changed
- Six real London landmarks with sourced coordinates, instead of synthetic stops.
- OpenStreetMap street basemap with zoom/pan, layer toggles and fullscreen.
- Road-following shortest-path geometry, not straight lines between stops.
- Permanent ID-and-name labels (toggle off if crowded), popups and snap offsets.
- Greedy + 2-opt optimization based on actual directed road lengths in km.
- Animated vehicle and route-direction effect; baseline road layer for comparison.
- Road graph caching and CSV/JSON exports. Customers sharing a node are retained.

This is NOT the original Starbucks dataset or an exact reproduction of the video.
The demonstration models real landmarks as hypothetical delivery stops. It is not
verified for legal driving access, parking, unloading, or last-meter navigation.
The first row is the depot. Read DATA_SOURCES.md and each CSV source_url.

## Setup in VS Code (Windows)
1. Extract this ZIP into a NEW folder. Keep the old project as a backup.
2. Open DAA_Street_Map_Project with File -> Open Folder.
3. Install Python 3.10-3.12 (3.11 is a conservative choice for dependency support)
   and Microsoft's Python extension. Select your interpreter in VS Code.
4. Terminal -> New Terminal:

    python -m venv .venv
    .venv\Scripts\python.exe -m pip install --upgrade pip
    .venv\Scripts\python.exe -m pip install -r requirements.txt
    .venv\Scripts\python.exe main.py

These commands avoid PowerShell activation-policy issues. If python is not found,
create the environment with `py -m venv .venv` instead.
Without an environment, use `python -m pip install -r requirements.txt` and
`python main.py`. Select the same interpreter for install and execution.

macOS/Linux: python3 -m venv .venv; then use .venv/bin/python for the same commands.

## First run
Internet is required. The program downloads a local driving graph, calculates
shortest road distances, optimizes the order, then opens results/street_map.html.
The initial download may take several minutes. Later runs reuse cache/*.graphml.
Map tiles and Leaflet/Folium JavaScript assets need internet even with a cached graph.
There is no API key, but external public services can be unavailable/rate-limited.
No false offline driving-distance result is used when a download fails.

## Commands (prefix with your environment Python as appropriate)
    python main.py
    python main.py --preview
    python main.py --refresh
    python main.py --csv "my_locations.csv"
    python main.py --no-browser
    python -m unittest discover -s tests -v

--preview only displays real landmark markers. It does NOT calculate routes or
claim distance savings. It can help check map loading independently of OSMnx.
--refresh redownloads the graph (HTTP response cache may still be reused by OSMnx).

## Map controls
- Pan and zoom like a normal street map.
- Red circle = depot; green = delivery stops; yellow moving point = vehicle.
- Play/restart button replays an illustrative 20-second animation, NOT travel time.
- Layer control toggles names, baseline road route, original landmark coordinates,
  snapped road markers, and coordinate-to-road offset connectors.
- Gray dashed offsets are not routes and are excluded from optimized driving cost.
- Blue route follows graph road geometry. Intersections/roads can be revisited even
  though each customer appears once in the delivery sequence.

## Outputs
results/street_map.html: map and metric panel.
results/summary.json: costs, selected route and measured timings.
results/route.csv: delivery sequence with original landmark coordinates.
results/snapped_stops.csv: actual graph positions and offset from original points.
results/distance_matrix.csv: labeled road-distance matrix, kilometers.
results/legs.json: selected pairwise leg distances.
results/locations_preview.html: created only with --preview.

## Fair interpretation
Nearest neighbor and 2-opt are heuristics; global optimality is not guaranteed.
Final route is the best observed among baseline, greedy and improved tours.
All compared tours use the same directed driving-distance matrix and depot.
Driving-distance costs exclude the final access leg between a graph node and the
landmark point. No traffic times, capacity, multiple vehicles or time windows.
Dijkstra calculates individual pairwise road paths; it does not choose tour order.

## Source files
main.py: command line, input validation, orchestration, result exports.
algorithms.py: greedy, full-cost 2-opt, tour evaluation; Haversine for graph sizing.
road_network.py: OSMnx graph/cache, snap checks, Dijkstra matrix, geometry.
map_view.py: Folium map, layers, name labels, animation and metrics panel.
data/locations.csv: included real-location reference data with source URLs.
tests/test_project.py: offline input/algorithm unit tests.
requirements.txt: third-party packages. No OR-Tools is used in this version.
DATA_SOURCES.md: provenance and access limitations.
CHANGES.md: upgrade notes. run_windows.bat: convenience launcher after setup.
.vscode/launch.json: debug launch; .gitignore: excludes cache/results/env files.

## Complexity
Offline tour optimization uses O(n^2) greedy and O(p*n^3) full-cost 2-opt,
p <= 100. Matrix is O(n^2) space. Directed road matrix uses one single-source
Dijkstra run per distinct snapped node; graph storage adds O(V+E) space.

## Troubleshooting
No module named ...: install requirements with the SAME Python executable.
Map background blank: check internet/tile/JavaScript access; try another browser.
Road download fails: retry later; public Overpass service can be unavailable.
Unreachable stop: inspect coordinates or increase graph margin in road_network.py.
Long snap offset: inspect snapped_stops.csv and replace coordinates with verified
vehicle-access points, not by blindly relaxing checks.
Label overlap: toggle Show node names; hover or click markers for names.
Wrong old report: open this NEW folder's results/street_map.html, not old report.html.
Do not combine old and new main.py/map files; use the extracted folder as a unit.

## Verification scope
Input and algorithm tests were run when packaging. Live OSM downloads, real-road
routing and browser animation require your runtime/network and have NOT been
end-to-end verified in the packaging environment. No computed road totals are
pre-invented. Install dependencies and run main.py to produce them.

## GitHub
Upload extracted source files/folders, not only the ZIP. Keep the provenance file.
Do not commit .venv or cache. Add your name/course and optional screenshots to README.
