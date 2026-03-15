import pytest
import os
import osmnx as ox
import pandas as pd
import numpy as np

# Mocking data paths for tests if needed, but here we test the real outputs
DATA_DIR = "data"

def test_02_metrics_exist():
    """Verify that compute_metrics produces a graph with essential metrics."""
    processed_path = os.path.join(DATA_DIR, "processed_graph.graphml")
    assert os.path.exists(processed_path), "processed_graph.graphml missing"
    
    G = ox.load_graphml(processed_path)
    gdf = ox.graph_to_gdfs(G, nodes=False)
    
    expected_cols = ['length', 'betweenness', 'norm_betweenness', 'norm_hierarchy']
    for col in expected_cols:
        assert col in gdf.columns, f"Missing metric column: {col}"
    
    assert gdf['length'].dtype in [np.float64, np.int64], "Length should be numeric"

def test_03_rank_uniqueness():
    """Verify that every road segment has a unique engineering rank."""
    scored_path = os.path.join(DATA_DIR, "scored_graph.graphml")
    assert os.path.exists(scored_path)
    
    G = ox.load_graphml(scored_path)
    gdf = ox.graph_to_gdfs(G, nodes=False)
    
    assert 'rank' in gdf.columns
    unique_ranks = gdf['rank'].nunique()
    total_roads = len(gdf)
    
    assert unique_ranks == total_roads, f"Ranks are not unique! {unique_ranks} vs {total_roads}"

def test_04_allocation_binary():
    """Verify that allocation is binary and uses the 25% threshold."""
    allocated_path = os.path.join(DATA_DIR, "allocated_graph.graphml")
    assert os.path.exists(allocated_path)
    
    G = ox.load_graphml(allocated_path)
    gdf = ox.graph_to_gdfs(G, nodes=False)
    
    assert 'is_allocated' in gdf.columns
    gdf['is_allocated'] = pd.to_numeric(gdf['is_allocated'], errors='coerce').fillna(0).astype(int)
    assert set(gdf['is_allocated'].unique()).issubset({0, 1})
    
    allocated_count = gdf['is_allocated'].sum()
    expected_approx = int(len(gdf) * 0.25)
    # Allow small deviation if sorting ties occurred (though method='first' prevents this)
    assert abs(allocated_count - expected_approx) <= 1

def test_05_alignment_logic():
    """Verify that alignment scores match the defined logic categories."""
    gap_path = os.path.join(DATA_DIR, "gap_graph.graphml")
    assert os.path.exists(gap_path)
    
    G = ox.load_graphml(gap_path)
    gdf = ox.graph_to_gdfs(G, nodes=False)
    
    # Check for presence of gap flags
    assert 'flag' in gdf.columns
    assert 'alignment_score' in gdf.columns
    
    # Check a specific logic: Top rank and allocated should be Aligned
    num_edges = len(gdf)
    threshold_top = int(num_edges * 0.25)
    
    gdf['rank'] = pd.to_numeric(gdf['rank'], errors='coerce')
    gdf['is_allocated'] = pd.to_numeric(gdf['is_allocated'], errors='coerce')
    
    top_allocated = gdf[(gdf['rank'] <= threshold_top) & (gdf['is_allocated'] == 1)]
    if not top_allocated.empty:
        assert (top_allocated['flag'] == "Aligned").all()

def test_06_geojson_export():
    """Verify that the final GeoJSON contains all properties needed by the frontend."""
    geojson_path = os.path.join(DATA_DIR, "jambi_roads.geojson")
    assert os.path.exists(geojson_path)
    
    import json
    with open(geojson_path, 'r') as f:
        data = json.load(f)
        
    assert data['type'] == "FeatureCollection"
    assert len(data['features']) > 0
    
    props = data['features'][0]['properties']
    required_props = ['name', 'length', 'rank', 'is_allocated', 'alignment_score', 'kecamatan']
    for p in required_props:
        assert p in props, f"GeoJSON missing property: {p}"
