import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
import os

def normalize(series):
    if series.max() == series.min():
        return series * 0
    return (series - series.min()) / (series.max() - series.min())

def compute_metrics():
    print("Loading graph from data/raw_graph.graphml...")
    filepath = "data/raw_graph.graphml"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    # Load as MultiDiGraph
    G = ox.load_graphml(filepath)
    
    # Convert to DiGraph for centrality calculations (removes parallel edges by keeping one)
    D = nx.DiGraph(G)
    
    print("Computing edge betweenness centrality (this may take a moment)...")
    ebc = nx.edge_betweenness_centrality(D, weight="length", normalized=True)
    
    print("Computing node degree centrality...")
    node_degree = nx.degree_centrality(D)
    
    # Hierarchy mapping
    hierarchy_map = {
        'trunk': 1.0,
        'trunk_link': 0.9,
        'primary': 0.8,
        'primary_link': 0.7,
        'secondary': 0.6,
        'secondary_link': 0.5,
        'tertiary': 0.4,
        'tertiary_link': 0.3
    }

    print("Extracting features and mapping to edges...")
    
    for u, v, key, data in G.edges(keys=True, data=True):
        # 0. Length
        data['length'] = float(data.get('length', 0))

        # 1. Betweenness (use the value from the DiGraph D)
        data['betweenness'] = ebc.get((u, v), 0)
        
        # 2. Degree (max of endpoints)
        data['degree_centrality'] = max(node_degree.get(u, 0), node_degree.get(v, 0))
        
        # 3. Lanes (extract and default to 2)
        lanes = data.get('lanes', 2)
        if isinstance(lanes, list):
            lanes = lanes[0]
        try:
            # Clean lane string if it has text or handle empty strings
            val = str(lanes).split(';')[0]
            if val.strip() == '' or val == 'nan':
                data['lane_count'] = 2.0
            else:
                data['lane_count'] = float(val)
        except:
            data['lane_count'] = 2.0
            
        # 4. Hierarchy
        # SHP data might have 'FolderPath' instead of 'highway'
        highway = data.get('highway', 'tertiary')
        if isinstance(highway, list):
            highway = highway[0]
        
        # If 'FolderPath' exists and highway is default, try to guess or just stay with default
        # In this dataset, centrality will drive the importance.
        data['hierarchy_score'] = hierarchy_map.get(highway, 0.4)

    # Convert to GeoDataFrame for easy normalization
    gdf_edges = ox.graph_to_gdfs(G, nodes=False)
    
    print("Normalizing metrics...")
    gdf_edges['norm_betweenness'] = normalize(gdf_edges['betweenness'])
    gdf_edges['norm_degree'] = normalize(gdf_edges['degree_centrality'])
    gdf_edges['norm_lanes'] = normalize(gdf_edges['lane_count'])
    gdf_edges['norm_hierarchy'] = normalize(gdf_edges['hierarchy_score'])
    
    # Map normalized values back to graph edges
    for index, row in gdf_edges.iterrows():
        u, v, key = index
        G[u][v][key]['norm_betweenness'] = row['norm_betweenness']
        G[u][v][key]['norm_degree'] = row['norm_degree']
        G[u][v][key]['norm_lanes'] = row['norm_lanes']
        G[u][v][key]['norm_hierarchy'] = row['norm_hierarchy']

    print("Saving processed graph to data/processed_graph.graphml...")
    ox.save_graphml(G, filepath="data/processed_graph.graphml")
    
    # Verification
    print("\nVerification: Top 5 roads by betweenness centrality:")
    top_ebc = gdf_edges.sort_values(by='betweenness', ascending=False).head(5)
    for idx, row in top_ebc.iterrows():
        name = row.get('name', 'Unnamed Road')
        print(f"- {name}: Betweenness={row['betweenness']:.4f}")

if __name__ == "__main__":
    compute_metrics()
