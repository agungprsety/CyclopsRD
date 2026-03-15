import osmnx as ox
import geopandas as gpd
import pandas as pd
import os

def fetch_all_kecamatan_robustly():
    print("Robust District Fetcher: Kota Jambi")
    
    place_name = "Kota Jambi, Indonesia"
    kec_names = [
        "Kota Baru", "Alam Barajo", "Jambi Selatan", "Paal Merah",
        "Jelutung", "Pasar Jambi", "Telanaipura", "Danau Sipin",
        "Danau Teluk", "Pelayangan", "Jambi Timur"
    ]
    
    found_gdfs = []
    missing = []
    
    for name in kec_names:
        print(f"Working on: {name}...")
        try:
            # Strategy 1: Geocode directly
            gdf = ox.geocode_to_gdf(f"Kecamatan {name}, Kota Jambi, Indonesia")
            if not gdf.empty:
                gdf['name'] = name
                found_gdfs.append(gdf[['name', 'geometry']])
                print(f"  Success (Strategy 1)")
                continue
        except:
            pass
            
        try:
            # Strategy 2: Features from place with name filter
            # Broaden the search slightly
            tags = {'name': True}
            # This is expensive but sure to find it if it exists in OSM
            features = ox.features_from_place(place_name, tags={'name': lambda x: name.lower() in str(x).lower()})
            polys = features[features.geometry.type.isin(['Polygon', 'MultiPolygon'])]
            if not polys.empty:
                # Take the largest one (usually the district itself)
                best = polys.copy()
                best['area'] = best.geometry.area
                best = best.sort_values(by='area', ascending=False).iloc[0:1]
                best['name'] = name
                found_gdfs.append(best[['name', 'geometry']])
                print(f"  Success (Strategy 2)")
                continue
        except:
            pass
            
        print(f"  FAILED: {name}")
        missing.append(name)
        
    if found_gdfs:
        final_gdf = pd.concat(found_gdfs, ignore_index=True)
        final_gdf = gpd.GeoDataFrame(final_gdf, crs="EPSG:4326")
        
        os.makedirs("data", exist_ok=True)
        final_gdf.to_file("data/jambi_kecamatan.geojson", driver='GeoJSON')
        
        print(f"\nFinal count: {len(final_gdf)} / 11")
        if missing:
            print(f"Still missing: {missing}")
    else:
        print("Fatal: No districts found.")

if __name__ == "__main__":
    fetch_all_kecamatan_robustly()
