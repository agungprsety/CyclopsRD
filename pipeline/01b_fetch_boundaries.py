import osmnx as ox
import geopandas as gpd
import os

def fetch_boundaries():
    print("Fetching Jambi Kecamatan boundaries...")
    city = "Kota Jambi, Indonesia"
    
    if not os.path.exists("data"):
        os.makedirs("data")
        
    try:
        # Fetch administrative boundaries at level 8 (Kecamatan in Indonesia)
        # Note: tags={'admin_level': '8'} is common for kecamatan
        boundaries = ox.features_from_place(city, tags={'admin_level': '8'})
        
        if not boundaries.empty:
            # Filter to keep only relevant columns and ensure it's polygons
            # Sometimes points are returned for administrative centers
            kecamatan = boundaries[boundaries.geometry.type.isin(['Polygon', 'MultiPolygon'])]
            
            # Keep name and geometry
            kecamatan = kecamatan[['name', 'geometry']]
            
            # Save as GeoJSON
            kecamatan.to_file("data/jambi_kecamatan.geojson", driver='GeoJSON')
            print(f"Successfully saved {len(kecamatan)} kabupaten/kecamatan boundaries to data/jambi_kecamatan.geojson")
            print("Districts found:", ", ".join(kecamatan['name'].tolist()))
        else:
            print("No boundaries found with admin_level=8.")
            
    except Exception as e:
        print(f"Error fetching boundaries: {e}")

if __name__ == "__main__":
    fetch_boundaries()
