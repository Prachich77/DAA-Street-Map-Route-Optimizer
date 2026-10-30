import hashlib
import json
import time
from pathlib import Path
from algorithms import haversine

def build(points,cache_dir,refresh=False):
    import osmnx as ox
    import networkx as nx
    ox.settings.use_cache=True
    ox.settings.cache_folder=str(Path(cache_dir)/'http')
    ox.settings.requests_timeout=180
    center={'latitude':sum(p['latitude'] for p in points)/len(points),
            'longitude':sum(p['longitude'] for p in points)/len(points)}
    radius=max(4000,int(max(haversine(center,p) for p in points)*1000+4000))
    if radius>25000:
        raise ValueError('Use a local dataset: this demo supports a graph radius of at most 25 km.')
    payload=json.dumps([round(center['latitude'],6),round(center['longitude'],6),radius,'drive-v2'])
    key=hashlib.sha256(payload.encode()).hexdigest()[:16]
    folder=Path(cache_dir);folder.mkdir(parents=True,exist_ok=True)
    path=folder/(key+'.graphml')
    started=time.perf_counter()
    if path.exists() and not refresh:
        print('Loading cached driving graph:',path.name)
        graph=ox.load_graphml(path)
    else:
        print('Downloading OpenStreetMap driving roads. First run may take several minutes...')
        graph=ox.graph_from_point((center['latitude'],center['longitude']),dist=radius,network_type='drive')
        ox.save_graphml(graph,path)
    snapped=list(ox.distance.nearest_nodes(graph,X=[p['longitude'] for p in points],Y=[p['latitude'] for p in points]))
    snap_info=[]
    for i,(p,node) in enumerate(zip(points,snapped)):
        q={'latitude':graph.nodes[node]['y'],'longitude':graph.nodes[node]['x']}
        offset=haversine(p,q)*1000
        if offset>1000:
            raise ValueError(f"{p['name']} is {offset:.0f} m from the nearest driving node; review input.")
        snap_info.append(dict(stop_id=i,name=p['name'],node_id=int(node),
                              snapped_latitude=q['latitude'],snapped_longitude=q['longitude'],
                              snap_offset_m=round(offset,2)))
    matrix=[]
    # Reuse single-source results when customers share the same road node.
    distances={}
    for node in dict.fromkeys(snapped):
        distances[node]=nx.single_source_dijkstra_path_length(graph,node,weight='length')
    for i,node in enumerate(snapped):
        row=[]
        for j,target in enumerate(snapped):
            if target not in distances[node]:
                raise ValueError(f"No directed road path from {points[i]['name']} to {points[j]['name']}. Review stops or enlarge graph margin.")
            row.append(distances[node][target]/1000)
        matrix.append(row)
    return graph,snapped,matrix,snap_info,time.perf_counter()-started

def geometry(graph,nodes,route):
    import networkx as nx
    coords=[]
    for a,b in zip(route,route[1:]):
        path=nx.shortest_path(graph,nodes[a],nodes[b],weight='length')
        if len(path)==1:
            coords.append((graph.nodes[path[0]]['y'],graph.nodes[path[0]]['x']))
        for u,v in zip(path,path[1:]):
            edge=min(graph[u][v].values(),key=lambda d:d.get('length',float('inf')))
            shape=edge.get('geometry')
            if shape is None:
                segment=[(graph.nodes[u]['x'],graph.nodes[u]['y']),(graph.nodes[v]['x'],graph.nodes[v]['y'])]
            else:
                segment=list(shape.coords)
                x,y=graph.nodes[u]['x'],graph.nodes[u]['y']
                if (segment[-1][0]-x)**2+(segment[-1][1]-y)**2 < (segment[0][0]-x)**2+(segment[0][1]-y)**2:
                    segment.reverse()
            coords.extend((y,x) for x,y in segment)
    return coords
