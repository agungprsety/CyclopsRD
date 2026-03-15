import math
import os
import requests
import time

# Jambi Bounds (derived from data/jambi_kecamatan.geojson)
MIN_LAT, MAX_LAT = -1.69613, -1.54667
MIN_LNG, MAX_LNG = 103.52422, 103.68106

# Zoom levels: 12 (overview) to 15 (street level)
# Higher zooms (16+) would result in exponentially more tiles
ZOOMS = range(12, 16) 

# CartoDB Dark Matter tile pattern
TILE_URL = "https://basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png"
OUTPUT_DIR = r"c:\Users\62823\ExplainMyRoad+\frontend\assets\tiles"

def deg2num(lat_deg, lon_deg, zoom):
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)

def download_tiles():
    print(f"Starting tile download for Jambi area...")
    print(f"Bounds: Lat({MIN_LAT}, {MAX_LAT}), Lng({MIN_LNG}, {MAX_LNG})")
    print(f"Zoom levels: {list(ZOOMS)}")
    
    total_downloaded = 0
    
    for z in ZOOMS:
        # Get tile range for this zoom
        # Note: deg2num y increases from North to South
        x_min, y_min = deg2num(MAX_LAT, MIN_LNG, z)
        x_max, y_max = deg2num(MIN_LAT, MAX_LNG, z)
        
        # Ensure ranges are correct
        x_range = range(min(x_min, x_max), max(x_min, x_max) + 1)
        y_range = range(min(y_min, y_max), max(y_min, y_max) + 1)
        
        print(f"Zoom {z}: Tiles x({x_range.start}-{x_range.stop-1}), y({y_range.start}-{y_range.stop-1})")
        
        for x in x_range:
            for y in y_range:
                url = TILE_URL.format(z=z, x=x, y=y)
                
                # Create standard tile directory structure: z/x/y.png
                tile_dir = os.path.join(OUTPUT_DIR, str(z), str(x))
                os.makedirs(tile_dir, exist_ok=True)
                
                path = os.path.join(tile_dir, f"{y}.png")
                
                if not os.path.exists(path):
                    try:
                        response = requests.get(url, timeout=10)
                        if response.status_code == 200:
                            with open(path, 'wb') as f:
                                f.write(response.content)
                            total_downloaded += 1
                            # Polite delay
                            time.sleep(0.05)
                        else:
                            print(f"Failed to download {url}: Status {response.status_code}")
                    except Exception as e:
                        print(f"Error downloading {url}: {e}")
    
    print(f"\nFinished! Total new tiles downloaded: {total_downloaded}")
    print(f"Tiles stored in: {OUTPUT_DIR}")

if __name__ == "__main__":
    download_tiles()
