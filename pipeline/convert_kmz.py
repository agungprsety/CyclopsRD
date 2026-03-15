import zipfile
import os
import geopandas as gpd
import fiona

# Enable KML support in fiona
fiona.drvsupport.supported_drivers['KML'] = 'rw'
fiona.drvsupport.supported_drivers['LIBKML'] = 'rw'

def convert_kmz_to_geojson(kmz_path, output_path):
    print(f"Opening KMZ: {kmz_path}")
    
    # Extract KMZ
    temp_dir = "temp_kmz_extract"
    os.makedirs(temp_dir, exist_ok=True)
    
    with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
        
    # Find KML file
    kml_file = None
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file.endswith(".kml"):
                kml_file = os.path.join(root, file)
                break
    
    if not kml_file:
        print("Error: No KML file found inside KMZ.")
        return

    print(f"Reading KML: {kml_file}")
    
    # KML files can have multiple layers. We'll try to read them.
    layers = fiona.listlayers(kml_file)
    print(f"Found layers: {layers}")
    
    all_gdfs = []
    for layer in layers:
        try:
            gdf = gpd.read_file(kml_file, layer=layer)
            if not gdf.empty:
                all_gdfs.append(gdf)
        except Exception as e:
            print(f"Warning: Could not read layer {layer}: {e}")

    if not all_gdfs:
        print("Error: No geometries found in KML.")
        return

    # Merge all layers
    final_gdf = gpd.pd.concat(all_gdfs, ignore_index=True)
    
    print(f"Saving to GeoJSON: {output_path}")
    final_gdf.to_file(output_path, driver='GeoJSON')
    print("Conversion successful!")

if __name__ == "__main__":
    kmz = r"C:\Users\62823\ExplainMyRoad+\Jalan_Status_Kota_Jambi 2025.kmz"
    output = r"C:\Users\62823\ExplainMyRoad+\data\jalan_status_2025.geojson"
    os.makedirs("data", exist_ok=True)
    convert_kmz_to_geojson(kmz, output)
