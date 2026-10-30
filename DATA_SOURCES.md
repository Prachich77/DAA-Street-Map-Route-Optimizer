# Data provenance

The CSV is a small, manually curated educational list of six real London landmarks.
It is not a live business directory, customer-order dataset, or the tutorial Starbucks CSV.
Each source_url points to the public coordinate page used for that row (consulted
21 October 2026). These are approximate landmark reference points, NOT verified
vehicle entrances, public parking, delivery bays or accessible drop-off positions.
The code snaps reference coordinates to driving road nodes and exports offsets.
Sources may give different coordinates for large sites: use the per-row source as
the basis of this sample, not a claim of survey-grade accuracy.

The first landmark (Trafalgar Square) is the modeled depot for demonstration only.
No claim is made that deliveries, depots or business operations exist at these sites.
Use verified access coordinates for operational use.

Road graph: OpenStreetMap contributors, ODbL.
Map tiles: OpenStreetMap contributors; visible attribution retained by Folium.
https://www.openstreetmap.org/copyright
Respect the public tile and Overpass services; this is a small educational demo,
not a production fleet service or a bulk tile downloader.

Video inspiration: https://youtu.be/aBEkINl2ed4
Tutorial repository: https://github.com/NeuronalLab/Route_Optimization_Python
The original CSV could not be retrieved during this update, so this package does
not claim to include or reproduce its Starbucks dataset.
