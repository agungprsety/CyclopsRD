import osmnx as ox
import pandas as pd
import numpy as np
import os

def calculate_gap():
    print("Loading allocated graph from data/allocated_graph.graphml...")
    filepath = "data/allocated_graph.graphml"
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    G = ox.load_graphml(filepath)
    gdf_edges = ox.graph_to_gdfs(G, nodes=False)

    # Ensure numeric types (flatten if lists)
    for col in ['rank', 'priority_score', 'length', 'is_allocated']:
        if col in gdf_edges.columns:
            # Handle potential list values from GraphML
            gdf_edges[col] = gdf_edges[col].apply(lambda x: x[0] if isinstance(x, list) else x)
            gdf_edges[col] = pd.to_numeric(gdf_edges[col], errors='coerce').fillna(0)

    print("Calculating realignment scores based on binary allocation...")
    # Alignment Rules:
    # 1. Aligned: (Top 25% Rank AND Allocated) OR (Not Top 25% Rank AND Not Allocated)
    # 2. Political Favor (Favoritism): Bottom 50% Rank AND Allocated
    # 3. Under-prioritized (Neglect): Top 25% Rank AND Not Allocated
    
    # Get thresholds
    num_edges = len(gdf_edges)
    threshold_top = int(num_edges * 0.25)
    threshold_low = int(num_edges * 0.50)

    def calculate_alignment(row):
        is_top = row['rank'] <= threshold_top
        is_low = row['rank'] > threshold_low
        allocated = row.get('is_allocated', 0) == 1
        
        if is_top and allocated:
            return 100.0, "Aligned", "⚪"
        if not is_top and not allocated:
            return 100.0, "Aligned", "⚪"
        if is_low and allocated:
            return 30.0, "Significant", "🔴" # Favoritism
        if is_top and not allocated:
            return 50.0, "Moderate", "🟡" # Neglect
        
        return 80.0, "Aligned", "⚪" # Default neutral

    results = gdf_edges.apply(calculate_alignment, axis=1)
    gdf_edges['alignment_score'] = [r[0] for r in results]
    gdf_edges['flag'] = [r[1] for r in results]
    gdf_edges['flag_icon'] = [r[2] for r in results]
    
    # Gap is now qualitative for JS tooltips
    # If allocated, we treat 'gap' as positive/negative based on merit
    def get_gap(row):
        is_top = row['rank'] <= threshold_top
        allocated = row.get('is_allocated', 0) == 1
        if is_top and not allocated: return 1 # Needs attention
        if not is_top and allocated: return -1 # Favoritism
        return 0

    gdf_edges['gap'] = gdf_edges.apply(get_gap, axis=1)

    print("Aggregating to district level (Length-Weighted)...")
    # District Alignment Summary
    # Need %: Sum of (priority_score * length) in district / total weighted score
    # Allocation %: Sum of (is_allocated * length) in district / total allocated length
    
    gdf_edges['weighted_priority'] = gdf_edges['priority_score'] * gdf_edges['length']
    gdf_edges['allocated_length'] = gdf_edges['is_allocated'] * gdf_edges['length']
    
    total_weighted_need = gdf_edges['weighted_priority'].sum()
    total_allocated_len = gdf_edges['allocated_length'].sum()
    
    # Avoid division by zero
    if total_weighted_need == 0: total_weighted_need = 1
    if total_allocated_len == 0: total_allocated_len = 1

    district_stats = gdf_edges.groupby('kecamatan').agg({
        'weighted_priority': 'sum',
        'allocated_length': 'sum',
        'alignment_score': 'mean',
        'gap': 'mean'
    }).rename(columns={
        'weighted_priority': 'eng_need_total',
        'allocated_length': 'alloc_total',
        'alignment_score': 'avg_alignment'
    })
    
    district_stats['need_pct'] = (district_stats['eng_need_total'] / total_weighted_need) * 100
    district_stats['alloc_pct'] = (district_stats['alloc_total'] / total_allocated_len) * 100
    district_stats['gap_pct'] = district_stats['alloc_pct'] - district_stats['need_pct']

    print("Mapping results back to graph...")
    for index, row in gdf_edges.iterrows():
        u, v, key = index
        G[u][v][key]['gap'] = int(row['gap'])
        G[u][v][key]['alignment_score'] = float(row['alignment_score'])
        G[u][v][key]['flag'] = row['flag']
        G[u][v][key]['flag_icon'] = row['flag_icon']
        G[u][v][key]['is_allocated'] = int(row.get('is_allocated', 0))
        G[u][v][key]['priority_score'] = float(row.get('priority_score', 0))

    print("Saving gap-analyzed graph to data/gap_graph.graphml...")
    ox.save_graphml(G, filepath="data/gap_graph.graphml")
    
    # Save district summary for the dashboard
    district_stats.to_json("data/district_summary.json", orient='index', indent=2)

    # Verification
    print("\nVerification: District Alignment Summary Table")
    print(district_stats[['need_pct', 'alloc_pct', 'gap_pct', 'avg_alignment']].sort_values(by='gap_pct', ascending=False))

if __name__ == "__main__":
    calculate_gap()
