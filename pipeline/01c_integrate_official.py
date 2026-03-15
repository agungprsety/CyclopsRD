import geopandas as gpd
import osmnx as ox
import networkx as nx
import os

def integrate_official():
    official_path = r'c:\Users\62823\ExplainMyRoad+\data\jambi_roads_official.geojson'
    
    if not os.path.exists(official_path):
        # Check in data/data if it moved
        alt_path = r'c:\Users\62823\ExplainMyRoad+\data\data\jambi_roads_official.geojson'
        official_path = alt_path if os.path.exists(alt_path) else official_path

    if not os.path.exists(official_path):
        print(f"Official GeoJSON not found at {official_path}")
        return

    print(f"Loading official road network from {official_path}...")
    gdf_roads = gpd.read_file(official_path)
    
    DISTRICTS = [
        'Alam Barajo', 'Danau Sipin', 'Danau Teluk', 'Jambi Selatan', 
        'Jambi Timur', 'Jelutung', 'Kota Baru', 'Paal Merah', 
        'Pasar Jambi', 'Pelayangan', 'Telanaipura'
    ]

    def extract_kecamatan(path):
        if not path: return "Unknown"
        for d in DISTRICTS:
            if d.lower() in path.lower():
                return d
        if 'jelutun' in path.lower(): return 'Jelutung'
        if 'teanaipura' in path.lower(): return 'Telanaipura'
        if 'pasar' in path.lower(): return 'Pasar Jambi'
        return "Unknown"

    gdf_roads['kecamatan'] = gdf_roads['FolderPath'].apply(extract_kecamatan)
    
    # Clean columns for GraphML compatibility
    # Remove columns that cause serialization issues (like lists or objects)
    for col in gdf_roads.columns:
        if col not in ['geometry', 'Name', 'kecamatan', 'Shape_Leng']:
            gdf_roads = gdf_roads.drop(columns=[col])

    print("Building topology...")
    node_id_points = {}
    next_node_id = 1
    
    G = nx.MultiDiGraph()
    G.graph['crs'] = 'epsg:4326'

    for _, row in gdf_roads.iterrows():
        coords = list(row.geometry.coords)
        # Handle Z coordinates if present in SHP (LINESTRING Z)
        start_pt = (round(coords[0][0], 7), round(coords[0][1], 7))
        end_pt = (round(coords[-1][0], 7), round(coords[-1][1], 7))
        
        for pt in [start_pt, end_pt]:
            if pt not in node_id_points:
                node_id_points[pt] = next_node_id
                G.add_node(next_node_id, x=pt[0], y=pt[1])
                next_node_id += 1
                
        u = node_id_points[start_pt]
        v = node_id_points[end_pt]
        
        # Calculate length
        length = row.geometry.length * 111320
        
        # Add edge with standard OSM attributes to keep 02_compute_metrics happy
        G.add_edge(u, v, key=0, 
                   name=str(row.get('Name', 'Unnamed Road')),
                   kecamatan=row['kecamatan'],
                   length=length,
                   highway='tertiary', # Default
                   oneway=False,
                   geometry=row.geometry)

    print(f"Graph stats: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
    ox.save_graphml(G, r'c:\Users\62823\ExplainMyRoad+\data\raw_graph_official.graphml')
    print("Saved to data/raw_graph_official.graphml")

if __name__ == "__main__":
    integrate_official()
