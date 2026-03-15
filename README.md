# CyclopsRD — Infrastructure Decision Audit Dashboard

A data visualization platform that analyzes road infrastructure in Kota Jambi, Indonesia to audit "transparency gaps" between engineering priority rankings and maintenance allocation.

![Dashboard Preview](https://via.placeholder.com/800x400?text=CyclopsRD+Dashboard)

## Overview

CyclopsRD (Cyclops Road Data) is a hackathon-winning proof-of-concept that demonstrates how geospatial analysis can reveal misalignments between technical infrastructure needs and actual budget allocation.

## Features

- **Interactive Map** — Leaflet-based dark theme map of Jambi road network
- **Priority Visualization** — Color-coded roads by engineering priority score
- **Allocation Tracking** — Binary allocation status (work in progress / not scheduled)
- **Decision Audit** — Alignment scoring showing gaps between need and allocation
- **District Dashboard** — Comparative charts of engineering need vs. financial allocation
- **Road Search** — Find specific roads by name or ID

## Quick Start (Frontend Only)

### Option 1: Direct Browser
```bash
# Simply open frontend/index.html in your browser
```

### Option 2: Local Server
```bash
cd frontend
python -m http.server 8000
# Open http://localhost:8000
```

### Option 3: Vercel Deployment
```bash
npm i -g vercel
vercel
```

## Development Setup (Full Pipeline)

### Prerequisites
- Python 3.9+
- Node.js (optional, for Vercel)

### 1. Clone & Setup
```bash
git clone <repo-url>
cd ExplainMyRoad+
```

### 2. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r pipeline/requirements.txt
```

### 3. Run Pipeline
```bash
cd pipeline

# Step 1: Fetch road network from OSM
python 01_fetch_network.py

# Step 2: Compute centrality metrics
python 02_compute_metrics.py

# Step 3: Score and rank roads
python 03_score_and_rank.py

# Step 4: Simulate allocation
python 04_simulate_allocation.py

# Step 5: Calculate transparency gaps
python 05_calculate_gap.py

# Step 6: Export to GeoJSON
python 06_export_geojson.py
```

### 4. Run Tests
```bash
pytest tests/test_pipeline.py -v
```

## Deployment to Vercel

### Automated (Recommended)
1. Push code to GitHub
2. Import project in Vercel dashboard
3. Set root directory to `frontend`
4. Deploy!

### Manual
```bash
cd frontend
npm i -g vercel
vercel --prod
```

### Vercel Configuration
The project includes `vercel.json` configured for static hosting.

## Project Structure

```
ExplainMyRoad+/
├── frontend/           # Static web app
│   ├── index.html
│   ├── css/style.css
│   ├── js/app.js
│   └── data/         # GeoJSON data files
├── pipeline/         # Python data processing
│   ├── 01_fetch_network.py
│   ├── 02_compute_metrics.py
│   ├── 03_score_and_rank.py
│   ├── 04_simulate_allocation.py
│   ├── 05_calculate_gap.py
│   ├── 06_export_geojson.py
│   └── requirements.txt
├── data/             # Pipeline outputs (generated)
├── tests/            # Test suite
└── README.md
```

## Methodology

### Engineering Priority Score
Weighted combination of:
- Road Hierarchy (25%) — trunk/primary/secondary/tertiary
- Betweenness Centrality (20%) — graph connectivity metric
- Degree Centrality (15%) — intersection density
- Lane Count (10%) — traffic proxy
- Length (20%) — segment length
- Population Proxy (10%) — area density

### Transparency Gap
```
Gap = Allocation Status - Engineering Priority
```
- Positive = Under-prioritized (needs attention)
- Negative = Over-prioritized (favored allocation)

### Decision Alignment Score (0-100)
- ≥70: Aligned (green)
- 40-69: Moderate Gap (yellow)  
- <40: Significant Gap (red)

## Tech Stack

- **Data Pipeline:** Python, NetworkX, OSMnx, GeoPandas, Shapely
- **Frontend:** Vanilla JavaScript, Leaflet.js, Chart.js
- **Styling:** Custom CSS (dark theme, glassmorphism)
- **Deployment:** Vercel (static hosting)

## License

MIT License

## Credits

- Road network data: OpenStreetMap
- District boundaries: Indonesian geospatial data
- Methodology: Infrastructure auditing frameworks
