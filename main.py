import argparse
import csv
import json
import math
import time
import webbrowser
from pathlib import Path
from algorithms import nearest_neighbor,two_opt,cost
BASE=Path(__file__).resolve().parent

def load_points(path):
    with open(path,encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if not {'name','latitude','longitude'}.issubset(reader.fieldnames or []):
            raise ValueError('CSV requires name,latitude,longitude headers.')
        points=[]
        for row in reader:
            lat,lon=float(row['latitude']),float(row['longitude'])
            if not math.isfinite(lat) or not math.isfinite(lon) or not -90<=lat<=90 or not -180<=lon<=180:
                raise ValueError('Invalid coordinates.')
            if not row['name'].strip():raise ValueError('Empty location name.')
            points.append(dict(name=row['name'].strip(),latitude=lat,longitude=lon,source_url=row.get('source_url','')))
    if not 2<=len(points)<=60:raise ValueError('Provide 2-60 locations including the depot.')
    return points

def export_csv(path,rows):
    with path.open('w',newline='',encoding='utf-8') as f:csv.writer(f).writerows(rows)

def main():
    parser=argparse.ArgumentParser(description='Real London locations + OpenStreetMap road routing')
    parser.add_argument('--csv',type=Path,default=BASE/'data'/'locations.csv')
    parser.add_argument('--preview',action='store_true',help='Display landmark markers without road calculations')
    parser.add_argument('--refresh',action='store_true',help='Refresh graph cache using OSM service')
    parser.add_argument('--no-browser',action='store_true')
    args=parser.parse_args()
    points=load_points(args.csv)
    out=BASE/'results';out.mkdir(exist_ok=True)
    from map_view import render
    if args.preview:
        path=out/'locations_preview.html'
        render(points,[],[],[],[],None,path)
        print('Preview only:',path)
    else:
        from road_network import build,geometry
        graph,nodes,matrix,snaps,road_seconds=build(points,BASE/'cache',args.refresh)
        baseline=list(range(len(points)))+[0]
        t=time.perf_counter();greedy=nearest_neighbor(matrix);greedy_s=time.perf_counter()-t
        t=time.perf_counter();improved=two_opt(greedy,matrix);improve_s=time.perf_counter()-t
        route=min([baseline,greedy,improved],key=lambda r:cost(r,matrix))
        before,after=cost(baseline,matrix),cost(route,matrix)
        summary=dict(mode='OpenStreetMap directed driving-road distances, km',locations=len(points),baseline_km=before,greedy_km=cost(greedy,matrix),two_opt_km=cost(improved,matrix),final_km=after,saving_percent=100*(before-after)/before if before else 0,route=route,road_preprocessing_seconds=road_seconds,greedy_seconds=greedy_s,two_opt_seconds=improve_s,notes='Landmark coordinates snapped to road nodes; no last-meter access, traffic or access-permission verification. Heuristic tour.')
        print(json.dumps(summary,indent=2))
        (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
        export_csv(out/'distance_matrix.csv',[['from/to']+list(range(len(points)))]+[[i]+row for i,row in enumerate(matrix)])
        export_csv(out/'route.csv',[['step','stop_id','name','latitude','longitude']]+[[s,i,points[i]['name'],points[i]['latitude'],points[i]['longitude']] for s,i in enumerate(route)])
        export_csv(out/'snapped_stops.csv',[list(snaps[0])]+[list(s.values()) for s in snaps])
        legs=[]
        for a,b in zip(route,route[1:]):legs.append({'from_id':a,'to_id':b,'from':points[a]['name'],'to':points[b]['name'],'distance_km':matrix[a][b]})
        (out/'legs.json').write_text(json.dumps(legs,indent=2),encoding='utf-8')
        path=out/'street_map.html'
        render(points,snaps,route,geometry(graph,nodes,route),geometry(graph,nodes,baseline),summary,path)
    if not args.no_browser:webbrowser.open(path.resolve().as_uri())
    print('Open the HTML report in Chrome/Edge. Internet is needed for map tiles and JavaScript assets.')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        raise SystemExit(f'ERROR: {exc}\nCheck README troubleshooting. No straight-line fallback was silently used.')
