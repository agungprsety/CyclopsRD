import osmnx as ox
import geopandas as gpd
import pandas as pd
import numpy as np
import os
import random

def simulate_allocation():
    print("Loading scored graph and kecamatan boundaries...")
    graph_path = "data/scored_graph.graphml"
    districts_path = "data/jambi_kecamatan.geojson"
    
    if not os.path.exists(graph_path):
        print(f"Error: Missing input graph file {graph_path}.")
        return

    G = ox.load_graphml(graph_path)
    gdf_edges = ox.graph_to_gdfs(G, nodes=False)
    
    # Ensure numeric types
    gdf_edges['priority_score'] = pd.to_numeric(gdf_edges['priority_score'], errors='coerce').fillna(0)
    gdf_edges['rank'] = pd.to_numeric(gdf_edges['rank'], errors='coerce').fillna(0)
    
    kecamatan_centroids = {
        'Telanaipura': (-1.61, 103.58),
        'Danau Teluk': (-1.58, 103.58),
        'Danau Sipin': (-1.60, 103.59),
        'Pasar Jambi': (-1.59, 103.62),
        'Jambi Timur': (-1.59, 103.64),
        'Jambi Selatan': (-1.62, 103.63),
        'Jelutung': (-1.61, 103.61),
        'Kota Baru': (-1.64, 103.58),
        'Alam Barajo': (-1.63, 103.55),
        'Paal Merah': (-1.65, 103.62),
        'Pelayangan': (-1.57, 103.60)
    }

    if os.path.exists(districts_path):
        print("Performing spatial join...")
        gdf_districts = gpd.read_file(districts_path)
        gdf_districts = gdf_districts.rename(columns={'name': 'dist_name'})
        gdf_edges = gdf_edges.to_crs(gdf_districts.crs)
        
        gdf_edges_centroids = gdf_edges.copy()
        gdf_edges_centroids['geometry'] = gdf_edges_centroids.geometry.centroid
        
        joined = gpd.sjoin(gdf_edges_centroids, gdf_districts[['dist_name', 'geometry']], how='left', predicate='within')
        gdf_edges['kecamatan'] = joined['dist_name']
    else:
        print("Districts file skipping. Using centroid fallback directly...")
        gdf_edges['kecamatan'] = None

    # Fallback for Unknown (outside polygons or file missing)
    def assign_nearest_kecamatan(row):
        if pd.notna(row['kecamatan']) and row['kecamatan'] != 'Unknown':
            return row['kecamatan']
        
        # Simple Euclidean distance to centroids (lat/lon approx)
        point = row.geometry.centroid
        y, x = point.y, point.x
        
        nearest = 'Unknown'
        min_dist = float('inf')
        for name, (cy, cx) in kecamatan_centroids.items():
            dist = (y - cy)**2 + (x - cx)**2
            if dist < min_dist:
                min_dist = dist
                nearest = name
        return nearest

    print("Finalizing kecamatan assignments...")
    gdf_edges['kecamatan'] = gdf_edges.apply(assign_nearest_kecamatan, axis=1)

    print("Mapping districts to their Dapil and associated DPRD seats (2024)...")
    # Source: Pemilu 2024 Dapil DPRD Kota Jambi
    # Note: For shared Dapils, the total seats of the Dapil are used as the influence factor.
    dapil_seats = {
        'Kota Baru': 6,       # Dapil 1
        'Alam Barajo': 8,     # Dapil 2
        'Telanaipura': 8,     # Dapil 3 (Shared with Danau Sipin & Danau Teluk)
        'Danau Sipin': 8,     # Dapil 3
        'Danau Teluk': 8,     # Dapil 3
        'Pelayangan': 11,     # Dapil 4 (Shared with Jambi Timur, Pasar Jambi, Jelutung)
        'Jambi Timur': 11,    # Dapil 4
        'Pasar Jambi': 11,    # Dapil 4
        'Jelutung': 11,       # Dapil 4
        'Jambi Selatan': 12,  # Dapil 5 (Shared with Paal Merah)
        'Paal Merah': 12      # Dapil 5
    }
    
    # Calculate empirical multipliers purely based on DPRD seat distribution
    # Average seats per Dapil = 9 (45 total / 5 Dapils)
    # The README states: Propensity = Inverted Rank + ((Seats - 9) / 9) * 0.3 + Jitter
    
    avg_seats = 9.0
    district_multipliers = {}
    
    for dist, seats in dapil_seats.items():
        # Baseline is 1.0. A district with 12 seats gets a +10% boost (1.1). 
        # A district with 6 seats gets a -10% penalty (0.9).
        bias_effect = ((seats - avg_seats) / avg_seats) * 0.3
        district_multipliers[dist] = 1.0 + bias_effect
        
    print("Computed Political Bias Multipliers from DPRD Seats:")
    for dist, mult in district_multipliers.items():
        print(f"  {dist}: {mult:.3f} (Seats: {dapil_seats.get(dist, 0)})")
    
    print("Applying dramatic demo biases and simulating binary allocation...")
    def get_allocation_propensity(row):
        # Base Propensity: Engineering Rank (inverted)
        max_rank = gdf_edges['rank'].max()
        inverted_rank = (max_rank - row['rank']) / max_rank
        
        # Apply district-specific multiplier
        target_dist = row['kecamatan']
        multiplier = district_multipliers.get(target_dist, 1.0)
        
        # Add a "High Influence" bonus for segments near certain nodes/hotspots if we wanted, 
        # but district-level is clearer for the dashboard.
        
        # Final Score = (Technical Rank^0.8) * Multiplier + Noise
        # Using power < 1 makes the rank differences slightly less dominant than political bias
        propensity = (inverted_rank ** 0.8) * multiplier
        
        # Add random noise to simulate 'irregularities'
        noise = random.uniform(-0.4, 0.4)
        
        return propensity + noise

    gdf_edges['allocation_propensity'] = gdf_edges.apply(get_allocation_propensity, axis=1)
    
    # Select top 25% for allocation
    budget_count = int(len(gdf_edges) * 0.25)
    allocated_indices = gdf_edges.sort_values(by='allocation_propensity', ascending=False).head(budget_count).index
    
    gdf_edges['is_allocated'] = 0
    gdf_edges.loc[allocated_indices, 'is_allocated'] = 1

    print(f"Allocated {budget_count} segments (25% of network).")

    print("Mapping allocation data back to graph...")
    for index, row in gdf_edges.iterrows():
        u, v, key = index
        G[u][v][key]['kecamatan'] = str(row['kecamatan'])
        G[u][v][key]['is_allocated'] = int(row['is_allocated'])
        # Keep allocation_score for debugging/internal but UI will use is_allocated
        G[u][v][key]['allocation_score'] = float(row['allocation_propensity'])

    print("Saving allocated graph...")
    ox.save_graphml(G, filepath="data/allocated_graph.graphml")

    print("\nVerification: District Allocation Summary")
    summary_gdf = gdf_edges[gdf_edges['kecamatan'] != 'Unknown'].copy()
    summary = summary_gdf.groupby('kecamatan').agg({
        'rank': 'mean',
        'is_allocated': 'sum',
        'allocation_propensity': 'mean'
    }).rename(columns={
        'rank': 'Avg Eng Rank', 
        'is_allocated': 'Allocated Links',
        'allocation_propensity': 'Avg Propensity'
    })
    
    print(summary.sort_values(by='Allocated Links', ascending=False))

if __name__ == "__main__":
    simulate_allocation()
