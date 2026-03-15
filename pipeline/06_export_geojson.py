import osmnx as ox
import geopandas as gpd
import pandas as pd
import json
import os

def export_data():
    print("Loading final analyzed graph from data/gap_graph.graphml...")
    filepath = "data/gap_graph.graphml"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    G = ox.load_graphml(filepath)
    
    # 1. Export Roads GeoJSON
    print("Exporting jambi_roads.geojson...")
    gdf_edges = ox.graph_to_gdfs(G, nodes=False)
    
    # Clean up gdf for GeoJSON (ensure important scores are kept)
    # Map 'Name' to 'name' if necessary
    if 'Name' in gdf_edges.columns:
        if 'name' in gdf_edges.columns:
            gdf_edges['name'] = gdf_edges['name'].fillna(gdf_edges['Name'])
        else:
            gdf_edges['name'] = gdf_edges['Name']
    
    # If still missing, check for 'id' to use as fallback name
    if 'name' not in gdf_edges.columns:
        gdf_edges['name'] = "Unnamed Road"
    
    cols_to_keep = [
        'name', 'highway', 'kecamatan', 'priority_score', 'rank', 
        'is_allocated', 'allocation_score', 'gap', 'alignment_score', 
        'flag', 'flag_icon', 'length', 'geometry'
    ]
    # Filter columns that actually exist
    existing_cols = [c for c in cols_to_keep if c in gdf_edges.columns]
    gdf_roads = gdf_edges[existing_cols].copy()
    
    # Ensure numeric columns are actually numeric for JS to parse easily
    numeric_cols = ['priority_score', 'rank', 'is_allocated', 'allocation_score', 'allocation_rank', 'gap', 'alignment_score']
    for col in numeric_cols:
        if col in gdf_roads.columns:
            gdf_roads[col] = pd.to_numeric(gdf_roads[col], errors='coerce').fillna(0)

    gdf_roads['name'] = gdf_roads['name'].fillna('Unnamed Road')
    
    # Save as the expected frontend filename directly to avoid manual copy errors during testing
    gdf_roads.to_file("data/jambi_roads.geojson", driver='GeoJSON')

    # 2. Export Districts GeoJSON (with aggregated stats)
    print("Exporting jambi_districts.geojson...")
    districts_path = "data/jambi_kecamatan.geojson"
    summary_path = "data/district_summary.json"
    
    if os.path.exists(districts_path) and os.path.exists(summary_path):
        gdf_districts = gpd.read_file(districts_path)
        with open(summary_path, 'r') as f:
            summary_data = json.load(f)
            
        # Map summary data back to districts
        # summary_data is keyed by kecamatan name
        # We need to ensure names match
        def map_stats(row):
            name = row['name']
            stats = summary_data.get(name, {})
            return pd.Series(stats)

        # Merge stats
        stats_df = gdf_districts.apply(map_stats, axis=1)
        gdf_districts_final = pd.concat([gdf_districts, stats_df], axis=1)
        
        gdf_districts_final.to_file("data/jambi_districts.geojson", driver='GeoJSON')
    else:
        print("Warning: Skipping district GeoJSON export due to missing inputs.")

    # 3. Export Road Details JSON (for the side panel)
    print("Exporting road_details.json...")
    # We'll create a simple list of road details keyed by a unique ID if possible, 
    # or just a list that the frontend can filter.
    road_details = []
    # Use reset_index to get a stable index
    gdf_roads_indexed = gdf_roads.reset_index(drop=True)
    for idx, row in gdf_roads_indexed.iterrows():
        detail = row.drop('geometry').to_dict()
        detail['id'] = idx
        road_details.append(detail)
        
    with open("data/road_details.json", 'w') as f:
        json.dump(road_details, f, indent=2)

    print("\nVerification: Export complete.")
    print(f"- data/jambi_roads.geojson (~{os.path.getsize('data/jambi_roads.geojson')/1024:.1f} KB)")
    if os.path.exists("data/jambi_districts.geojson"):
        print(f"- data/jambi_districts.geojson (~{os.path.getsize('data/jambi_districts.geojson')/1024:.1f} KB)")
    print(f"- data/district_summary.json")
    print(f"- data/road_details.json")

if __name__ == "__main__":
    export_data()
