import html
import json

def render(points,snaps,route,line,baseline_line,summary,path):
    import folium
    from folium.plugins import AntPath, Fullscreen
    from branca.element import Element, MacroElement, Template
    center=[sum(p['latitude'] for p in points)/len(points),sum(p['longitude'] for p in points)/len(points)]
    m=folium.Map(location=center,zoom_start=13,tiles='OpenStreetMap',control_scale=True)
    Fullscreen().add_to(m)
    original=folium.FeatureGroup(name='Actual landmark coordinates',show=False).add_to(m)
    labels=folium.FeatureGroup(name='Show node names',show=True).add_to(m)
    snapped_layer=folium.FeatureGroup(name='Snapped road stops',show=True).add_to(m)
    connectors=folium.FeatureGroup(name='Coordinate-to-road offsets (NOT drivable routes)',show=False).add_to(m)
    for i,p in enumerate(points):
        name=html.escape(p['name']);label=f'{i} - {name}'
        lat,lon=p['latitude'],p['longitude']
        folium.CircleMarker([lat,lon],radius=5,color='#64748b',fill=True,popup=f'Original landmark: {label}').add_to(original)
        if snaps:
            s=snaps[i];lat,lon=s['snapped_latitude'],s['snapped_longitude']
            details=f"Snapped to driving graph node {s['node_id']}<br>Offset: {s['snap_offset_m']:.1f} m"
            folium.PolyLine([[p['latitude'],p['longitude']],[lat,lon]],color='gray',weight=2,dash_array='4 8',tooltip='Snap offset, not a driving path').add_to(connectors)
        else:
            details='Preview only: no road snapping or route calculation yet.'
        folium.CircleMarker([lat,lon],radius=8,color='#dc2626' if i==0 else '#059669',fill=True,fill_opacity=1,
            popup=folium.Popup(f'<b>{label}</b><br>{details}',max_width=330),tooltip=label).add_to(snapped_layer)
        folium.Marker([lat,lon],icon=folium.DivIcon(icon_size=(240,25),icon_anchor=(-12,27),html=f'<div style="white-space:nowrap;font:bold 12px Arial;color:#142a44;text-shadow:1px 1px white,-1px -1px white,1px -1px white,-1px 1px white">{label}</div>')).add_to(labels)
    if baseline_line:
        group=folium.FeatureGroup(name='Input-order baseline (roads)',show=False).add_to(m)
        folium.PolyLine(baseline_line,color='#6b7280',weight=4,opacity=.75).add_to(group)
    if line:
        group=folium.FeatureGroup(name='Selected route (roads)',show=True).add_to(m)
        folium.PolyLine(line,color='#2563eb',weight=5,opacity=.8).add_to(group)
        AntPath(line,color='#2563eb',pulse_color='#fef08a',weight=3,delay=850).add_to(group)
        anim=MacroElement()
        anim._template=Template(r"""{% macro script(this, kwargs) %}
        const routeCoords={{ this.coords | safe }};
        const mapRef={{ this.map_name }};
        let animationFrame=null;
        const vehicle=L.circleMarker(routeCoords[0],{radius:7,color:'#854d0e',weight:2,fillColor:'#facc15',fillOpacity:1}).addTo(mapRef);
        const cumulative=[0];
        for(let i=1;i<routeCoords.length;i++) cumulative.push(cumulative[i-1]+mapRef.distance(routeCoords[i-1],routeCoords[i]));
        function startDeliveryAnimation(){
          if(animationFrame)cancelAnimationFrame(animationFrame);
          let start=null,index=1,total=cumulative[cumulative.length-1];
          if(total===0){vehicle.setLatLng(routeCoords[0]);return;}
          function frame(t){
            if(start===null)start=t;
            const fraction=Math.min((t-start)/20000,1),target=fraction*total;
            while(index<cumulative.length-1 && cumulative[index]<target)index++;
            const a=routeCoords[index-1],b=routeCoords[index],span=cumulative[index]-cumulative[index-1];
            const f=span>0?(target-cumulative[index-1])/span:0;
            vehicle.setLatLng([a[0]+(b[0]-a[0])*f,a[1]+(b[1]-a[1])*f]);
            if(fraction<1)animationFrame=requestAnimationFrame(frame);
          }
          animationFrame=requestAnimationFrame(frame);
        }
        const ctl=L.control({position:'bottomleft'});
        ctl.onAdd=function(){let el=L.DomUtil.create('div');el.innerHTML='<button style="padding:10px;border:0;background:#facc15;border-radius:6px;cursor:pointer">Play / restart vehicle</button>';L.DomEvent.disableClickPropagation(el);el.querySelector('button').onclick=startDeliveryAnimation;return el;};
        ctl.addTo(mapRef);startDeliveryAnimation();
        {% endmacro %}""")
        anim.coords=json.dumps(line);anim.map_name=m.get_name();m.add_child(anim)
    if summary:
        heading='Road-distance optimization'
        metrics=f"Baseline: {summary['baseline_km']:.3f} km<br>Nearest neighbor: {summary['greedy_km']:.3f} km<br>Final: {summary['final_km']:.3f} km<br>Reduction vs baseline: {summary['saving_percent']:.2f}%"
        visit=' &rarr; '.join(html.escape(points[i]['name']) for i in route)
        body=metrics+f'<details><summary>Visit sequence and notes</summary><p>{visit}</p><p>Snapped driving nodes; last-meter access excluded. No live traffic, entry permissions or delivery bays verified. Heuristic tour: no global optimality guarantee. Animation is illustrative, not journey time.</p></details>'
    else:
        heading='Real-location preview - NOT optimized'
        body='Real landmark coordinates only. Run python main.py to download driving roads and compute the route. No driving-distance result is shown in this preview.'
    panel=f'<div style="position:fixed;top:12px;left:55px;z-index:1000;background:white;color:#142a44;padding:14px;border-radius:9px;box-shadow:0 2px 9px #999;max-width:320px;max-height:45vh;overflow:auto;font:14px Arial"><b>{heading}</b><p>{body}</p></div>'
    m.get_root().html.add_child(Element(panel))
    folium.LayerControl(collapsed=False).add_to(m)
        # Fit the initial map view around the input locations.
    bounds = [
        [p["latitude"], p["longitude"]]
        for p in points
    ]

    m.fit_bounds(
        bounds,
        padding=(60, 60),
        max_zoom=15
    )
    m.save(str(path))
