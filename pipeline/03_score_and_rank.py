import osmnx as ox
import pandas as pd
import numpy as np
import os

def score_and_rank():
    print("Loading processed graph from data/processed_graph.graphml...")
    filepath = "data/processed_graph.graphml"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    G = ox.load_graphml(filepath)
    gdf_edges = ox.graph_to_gdfs(G, nodes=False)

    print("Cleaning data and computing priority scores...")
    
    # Ensure all metric columns are numeric
    metrics = ['norm_hierarchy', 'norm_betweenness', 'norm_degree', 'norm_lanes', 'length']
    for m in metrics:
        gdf_edges[m] = pd.to_numeric(gdf_edges[m], errors='coerce').fillna(0)
    
    # Normalize length for scoring
    gdf_edges['norm_length'] = (gdf_edges['length'] - gdf_edges['length'].min()) / (gdf_edges['length'].max() - gdf_edges['length'].min())

    # Simple population proxy
    gdf_edges['pop_proxy'] = 0.5 
    
    # Formula: 0.25×hierarchy + 0.20×betweenness + 0.15×degree + 0.10×lanes + 0.20×length + 0.10×population
    # Added tiny random jitter (1e-6) to ensure unique scores for unique ranks
    np.random.seed(42) # Deterministic jitter
    gdf_edges['priority_score'] = (
        0.25 * gdf_edges['norm_hierarchy'] +
        0.20 * gdf_edges['norm_betweenness'] +
        0.15 * gdf_edges['norm_degree'] +
        0.10 * gdf_edges['norm_lanes'] +
        0.20 * gdf_edges['norm_length'] +
        0.10 * gdf_edges['pop_proxy'] +
        np.random.uniform(0, 1e-6, len(gdf_edges))
    ).astype(float)
    
    # Rank all segments (1 = highest priority, unique ranks using method='first')
    gdf_edges['rank'] = gdf_edges['priority_score'].rank(ascending=False, method='first').astype(int)

    print("Mapping scores and ranks back to graph...")
    # Map back to graph attributes
    for index, row in gdf_edges.iterrows():
        u, v, key = index
        G[u][v][key]['priority_score'] = float(row['priority_score'])
        G[u][v][key]['rank'] = int(row['rank'])
        G[u][v][key]['length'] = float(row['length'])

    print("Saving scored graph to data/scored_graph.graphml...")
    ox.save_graphml(G, filepath="data/scored_graph.graphml")

    # Verification
    print("\nVerification: Top 10 High-Priority Roads:")
    top_roads = gdf_edges.sort_values(by='rank').head(10)
    for idx, row in top_roads.iterrows():
        name = row.get('name', 'Unnamed Road')
        print(f"Rank {row['rank']}: {name} (Score: {row['priority_score']:.3f})")

    print("\nVerification: Bottom 10 Low-Priority Roads:")
    bottom_roads = gdf_edges.sort_values(by='rank', ascending=False).head(10)
    for idx, row in bottom_roads.iterrows():
        name = row.get('name', 'Unnamed Road')
        print(f"Rank {row['rank']}: {name} (Score: {row['priority_score']:.3f})")

if __name__ == "__main__":
    score_and_rank()
