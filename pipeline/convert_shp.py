import geopandas as gpd
import os

shp_path = r'c:\Users\62823\ExplainMyRoad+\Jalan_Merge.shp'

if os.path.exists(shp_path):
    try:
        gdf = gpd.read_file(shp_path)
        print("Columns in SHP:", gdf.columns)
        print("First 5 rows:")
        print(gdf.head())
        # If successful, export to GeoJSON
        target_path = r'c:\Users\62823\ExplainMyRoad+\frontend\data\jambi_roads_official.geojson'
        gdf.to_file(target_path, driver='GeoJSON')
        print(f"Successfully converted and saved to {target_path}")
    except Exception as e:
        print(f"Error reading shapefile: {e}")
        print("Note: .dbf file might be missing, which is required for attributes.")
else:
    print(f"File not found: {shp_path}")
