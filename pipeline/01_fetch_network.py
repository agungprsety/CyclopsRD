import osmnx as ox
import os

def fetch_and_filter_network():
    print("Fetching filtered road network for Kota Jambi...")
    city = "Kota Jambi, Indonesia"
    
    # Ensure data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")
        
    # Custom filter for highway types: trunk, primary, secondary, tertiary (+ links)
    # This filter ensures we get the main road skeleton, excluding residential/living streets for the Demo
    custom_filter = (
        '["highway"~"trunk|primary|secondary|tertiary|'
        'trunk_link|primary_link|secondary_link|tertiary_link"]'
    )
    
    try:
        # Fetch road network with custom filter
        G = ox.graph_from_place(city, custom_filter=custom_filter)
        
        edge_count = len(G.edges)
        node_count = len(G.nodes)
        print(f"Successfully fetched network.")
        print(f"Nodes: {node_count}")
        print(f"Edges: {edge_count}")
        
        # Verify: graph has > 500 edges
        if edge_count > 500:
            print("Verification PASSED: Graph has more than 500 edges.")
        else:
            print(f"Verification WARNING: Graph has only {edge_count} edges (expected > 500).")
        
        # Save as GraphML for persistence
        filepath = "data/raw_graph.graphml"
        ox.save_graphml(G, filepath=filepath)
        print(f"Filtered graph saved to {filepath}")
        
    except Exception as e:
        print(f"Error fetching network: {e}")

if __name__ == "__main__":
    fetch_and_filter_network()
