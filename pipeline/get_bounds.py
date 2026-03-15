import json
import os

file_path = r'c:\Users\62823\ExplainMyRoad+\data\jambi_kecamatan.geojson'

try:
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    min_lng, min_lat = float('inf'), float('inf')
    max_lng, max_lat = float('-inf'), float('-inf')
    
    for feature in data['features']:
        geom = feature['geometry']
        if not geom: continue
        
        if geom['type'] == 'MultiPolygon':
            coords = geom['coordinates']
        elif geom['type'] == 'Polygon':
            coords = [geom['coordinates']]
        else:
            continue
            
        for poly in coords:
            for ring in poly:
                for coord in ring:
                    lng, lat = coord[0], coord[1]
                    min_lng = min(min_lng, lng)
                    min_lat = min(min_lat, lat)
                    max_lng = max(max_lng, lng)
                    max_lat = max(max_lat, lat)
                    
    print(f"Bounds for Jambi:")
    print(f"Min Lat: {min_lat}")
    print(f"Max Lat: {max_lat}")
    print(f"Min Lng: {min_lng}")
    print(f"Max Lng: {max_lng}")
    
except Exception as e:
    print(f"Error: {e}")
