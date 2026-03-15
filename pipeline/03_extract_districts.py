import geopandas as gpd
import pandas as pd
import os

def extract_jambi_districts_robust():
    print("Extracting all 11 Kota Jambi districts from regional GeoJSON...")
    geojson_path = r"c:\Users\62823\ExplainMyRoad+\GeoJson-Indonesia-38-Provinsi\Kabupaten\38 Provinsi Indonesia - Kabupaten.json"
    
    # Standard Jambi Kecamatan list
    kec_names = [
        "Kota Baru", "Alam Barajo", "Jambi Selatan", "Paal Merah",
        "Jelutung", "Pasar Jambi", "Telanaipura", "Danau Sipin",
        "Danau Teluk", "Pelayangan", "Jambi Timur"
    ]
    
    try:
        if not os.path.exists(geojson_path):
            print(f"Error: Could not find source file at {geojson_path}")
            return

        gdf = gpd.read_file(geojson_path)
        
        # Filter 1: Jambi Province or City Jambi in WADMKK/WADMPR
        # We look for features that correspond to Jambi
        prov_mask = gdf['WADMPR'].str.contains("Jambi", case=False, na=False)
        kab_mask = gdf['WADMKK'].str.contains("Jambi", case=False, na=False)
        
        subset = gdf[prov_mask | kab_mask].copy()
        
        print(f"Found {len(subset)} candidate features in Jambi region.")
        
        # Filter 2: Exactly match one of our 11 Kecamatan names
        # Note: WADMKC is the column for Kecamatan in this dataset structure
        district_mask = subset['WADMKC'].str.contains('|'.join(kec_names), case=False, na=False)
        matched_gdf = subset[district_mask].copy()
        
        if matched_gdf.empty:
            print("Zero matches found for target names. Checking unique values for debugging...")
            print(subset['WADMKC'].unique())
            return

        # Dissolve by WADMKC to ensure 1 polygon per district (if split into kelurahans)
        final_gdf = matched_gdf.dissolve(by='WADMKC').reset_index()
        
        # Map original names back to standard list case if possible
        # but the set usually uses the BPS names which are good enough.
        
        # Keep only relevant columns
        final_gdf = final_gdf[['WADMKC', 'geometry']]
        final_gdf.columns = ['name', 'geometry']
        
        os.makedirs("data", exist_ok=True)
        final_gdf.to_file("data/jambi_kecamatan.geojson", driver='GeoJSON')
        
        print(f"\nSuccess: Exported {len(final_gdf)} districts to data/jambi_kecamatan.geojson")
        print("Districts included:", final_gdf['name'].tolist())
        
        # Check for missing
        found_names = [n.lower() for n in final_gdf['name'].tolist()]
        missing = [n for n in kec_names if n.lower() not in found_names]
        if missing:
            print(f"Warning: Missing {len(missing)} districts: {missing}")
            
    except Exception as e:
        print(f"Error during extraction: {e}")

if __name__ == "__main__":
    extract_jambi_districts_robust()
