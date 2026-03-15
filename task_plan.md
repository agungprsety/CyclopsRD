# CyclopsRD — Task Plan & Checklist

> Track every step from zero to demo-ready. Check items off as you go.

---

## Pre-Hackathon Preparation

- [x] Install Python 3.10+ and create virtual environment
- [x] Install core Python packages: `osmnx`, `networkx`, `geopandas`, `shapely`, `pandas`, `numpy`
- [x] Pre-download Jambi road network from OSM (cache locally in case API goes down)
- [x] Pre-download kecamatan boundary GeoJSON from BPS Indonesia
- [x] Test that `osmnx.graph_from_place("Kota Jambi, Indonesia")` works
- [x] Set up project folder structure (see below)
- [x] Install frontend tooling: a local HTTP server (eg `python -m http.server`)
- [x] Download offline map tiles (CartoDB Dark Matter) as backup
- [x] Write and rehearse the 5-minute demo script
- [x] Prepare a 1-page "methodology" slide in case judges ask about weights

---

## Phase A — Hackathon Build (24 Hours)

### A1. Project Scaffolding (Hour 0–1)

- [x] Create directory structure:
  ```
  CyclopsRD/
  ├── pipeline/
  ├── data/
  ├── frontend/
  │   ├── css/
  │   ├── js/
  │   └── assets/
  ├── hackathon.md
  ├── mvp_plan.md
  ├── task_plan.md
  └── README.md
  ```
- [x] Create `pipeline/requirements.txt`
- [x] Create empty `index.html` + `style.css` + `app.js` and verify they load in browser

---

### A2. Data Pipeline — Fetch & Compute (Hour 1–3)

#### `01_fetch_network.py`
- [x] Fetch Jambi road graph using `osmnx.graph_from_place()`
- [x] Filter to highway types: trunk, primary, secondary, tertiary (+ links)
- [x] Save raw graph to `data/raw_graph.graphml`
- [x] Verify: graph has > 500 edges (print count to console)

#### `02_compute_metrics.py`
- [x] Load graph from `data/raw_graph.graphml`
- [x] Compute edge betweenness centrality (weight="length")
- [x] Compute node degree centrality, map to edges via max of endpoints
- [x] Extract lane count from `lanes` tag (default = 2)
- [x] Map `highway` tag to hierarchy score (trunk=1.0 → tertiary_link=0.3)
- [x] Normalize all four metrics to [0, 1] range (min-max)
- [x] Store metrics as edge attributes
- [x] Verify: print top 5 roads by betweenness centrality

#### `03_score_and_rank.py`
- [x] Apply weighted formula: `0.30×hierarchy + 0.25×betweenness + 0.20×degree + 0.15×lanes + 0.10×population_proxy`
- [x] Use road density in 500m buffer as population proxy
- [x] Compute final `priority_score` for each edge
- [x] Rank all segments (1 = highest priority)
- [x] Verify: print top 10 and bottom 10 roads with their scores

**🔴 CHECKPOINT (Hour 3): Pipeline scripts 01–03 must be working. If not, use pre-cached data.**

---

### A3. Data Pipeline — Allocation & Gap (Hour 3–4)

#### `04_simulate_allocation.py`
- [x] Define district-level bias factors (e.g., Kota Baru = +0.3, Paal Merah = -0.2)
- [x] Start from engineering rank, apply district biases
- [x] Add random noise (±15% jitter)
- [x] Produce `allocation_rank` for each segment
- [x] Verify: some districts should be clearly over/under-allocated

#### `05_calculate_gap.py`
- [x] Compute segment-level gap: `allocation_rank - engineering_rank`
- [x] Aggregate to district level: engineering need % and allocation %
- [x] Compute Decision Alignment Score: `100 - abs(gap_percentile) × 100`
- [x] Apply anomaly threshold (1 std dev) to classify flags
- [x] Assign flags: ⚪ Aligned / 🟡 Moderate / 🔴 Significant
- [x] Verify: print district summary table to console

#### `06_export_geojson.py`
- [x] Convert graph edges to GeoDataFrame
- [x] Spatial join with kecamatan boundary polygons
- [x] Export `data/jambi_roads.geojson` (road features with all scores)
- [x] Export `data/jambi_districts.geojson` (district polygons with gap data)
- [x] Export `data/district_summary.json` (tabular stats)
- [x] Export `data/road_details.json` (per-road breakdowns)
- [x] Verify: open GeoJSON in geojson.io to visually confirm correctness

**🔴 CHECKPOINT (Hour 4): All 4 data files exist and are valid. If not, hardcode sample GeoJSON.**

---

### A4. Frontend — Map Foundation (Hour 4–6)

#### `index.html`
- [x] Set up HTML5 boilerplate with proper meta tags
- [x] Include Leaflet CSS/JS from CDN
- [x] Include Chart.js from CDN
- [x] Include Inter font from Google Fonts
- [x] Add map container div (`#map`, full viewport)
- [x] Add side panel container (`#panel`, hidden by default)
- [x] Add dashboard container (`#dashboard`, hidden by default)
- [x] Add top-left logo/title overlay
- [x] Add layer toggle buttons (Roads / Districts / Dashboard)

#### `css/style.css`
- [x] Apply dark theme (background `#0f1117`)
- [x] Style map to fill viewport
- [x] Style side panel: glassmorphism (blur + translucent navy), slide-in from right
- [x] Style dashboard overlay: centered modal with blur background
- [x] Style buttons/toggles: glowing accent (`#00d4aa`)
- [x] Add hover/active states with smooth transitions
- [x] Style tooltips: dark background, rounded, small shadow
- [x] Make responsive (panel stacks below map on mobile)

#### `js/map.js`
- [x] Initialize Leaflet map centered on Jambi (-1.6, 103.6), zoom 13
- [x] Add CartoDB Dark Matter tile layer
- [x] Fetch and render `jambi_roads.geojson` as polylines
- [x] Color roads by `priority_score` using color ramp (green → yellow → red)
- [x] Set line weight by highway type (trunk=5px → tertiary=2px)
- [x] Add road hover: highlight + tooltip (road name + alignment score)
- [x] Add road click: open side panel with road details
- [x] Fetch and render `jambi_districts.geojson` as polygons
- [x] Color districts by `gap_pct` (blue → transparent → red choropleth)
- [x] Add district hover: border highlight + tooltip
- [x] Add district click: zoom to district bounds
- [x] Add layer toggle controls
- [x] Verify: map loads with colored roads within 2 seconds

**🔴 CHECKPOINT (Hour 6): Map is on screen with colored roads. THIS IS THE "SAVE POINT."**

---

### A5. Frontend — Side Panel (Hour 6–8)

#### `js/panel.js`
- [x] Create `openDetailPanel(props, type)` function
- [x] Display road name, link ID, length
- [x] Display Engineering Rank and Allocation Rank (large numbers)
- [x] Display Gap value logic (Gap between ranks)
- [x] Display Decision Alignment Score as gradient progress bar (0–100)
- [x] Display flag icon (⚪/🟡/🔴)
- [x] Display score breakdown (5 factors) as horizontal bar chart
- [x] Display confidence level (HIGH/MEDIUM) badge
- [x] Create `closePanel()` function with slide-out effect
- [x] Add close button (X) to panel
- [x] Verify: clicking any road opens panel with correct data

---

### A6. Frontend — Auto-Explanation (Hour 8–10)
- [x] Create `generateExplanation(audit, props, isStationing)` function
- [x] Identify top 2 contributing factors for each road
- [x] Generate template-based plain-language text
- [x] Calculate gap and relative rank positioning
- [x] Display explanation text in the side panel
- [x] Verify: explanations are readable and factually correct for 5+ roads

---

### A7. Frontend — District Dashboard (Hour 10–12)
- [x] Create dashboard toggle button in navbar
- [x] Fetch `district_summary.json`
- [x] Render grouped bar chart (Chart.js):
  - X-axis: kecamatan names
  - Bars: Engineering Need % (teal) vs Allocation % (rose)
- [x] Render alignment score bar chart
- [x] Style charts to match dark theme
- [x] Add chart animation on open
- [x] Verify: charts match the data in `district_summary.json`

**🔴 CHECKPOINT (Hour 12): Core features complete. Everything after this is polish.**

---

### A8. Polish & Visual Excellence (Hour 12–16)
- [x] Add smooth hover highlights and tooltips
- [x] Add loading states for stationing layers
- [x] Add Dynamic Legend overlay
- [x] Style tooltips with structured rich text
- [x] Add subtle white glow effect on hovered roads
- [x] Verify: overall visual feels premium and "dark dashboard" aesthetic

---

### A10. Efficiency & View Toggles (Hour 16–18)
- [x] Pre-calculate all audit data on load for speed
- [x] Implement View Mode Toggle (Priority, Allocation, Audit)
- [x] Update Legend dynamically
- [x] Fix Dashboard closing interaction (ensure z-index/events)
- [x] Add prominent "Audit Score" to every road tooltip
- [x] Integrate Decision Alignment into the side panel explanation
- [x] Verify: speed increase and toggle smoothness

---

### A11. Bug Fixing & Edge Cases (Hour 18–20)
- [x] Handle roads with no name gracefully
- [x] Handle empty/null GeoJSON properties
- [x] Fix z-index issues (Dashboard vs Map)
- [x] Ensure `.hidden` class is globally available in CSS
- [x] Test map performance: pre-calculation for zoom/pan smoothness
- [x] Verify all data files load (added fetch error handling)

---

### A12. Demo Preparation (Hour 20–24)

- [ ] Write final demo script (minute-by-minute breakdown)
- [ ] Practice demo run #1 — time it (target: 4:30)
- [ ] Practice demo run #2 — fix any awkward transitions
- [ ] Practice demo run #3 — record video as backup
- [ ] Prepare for Q&A: list 5 likely judge questions and rehearse answers
- [ ] Write `README.md`:
  - Project description (2 paragraphs)
  - Screenshot of the map
  - Setup instructions (3 steps max)
  - Tech stack list
  - Team members
- [ ] Final git commit: tag as `v0.1-hackathon`
- [ ] Verify: demo runs flawlessly from a cold browser start

---

## Phase B — Post-Hackathon MVP (2–4 Weeks)

### B1. Architecture Migration (Week 1)

- [ ] Set up FastAPI backend project
- [ ] Set up PostgreSQL + PostGIS database
- [ ] Migrate pipeline output to PostGIS tables
- [ ] Create REST API endpoints:
  - `GET /api/cities` — list available cities
  - `GET /api/roads?city=jambi` — GeoJSON road features
  - `GET /api/districts?city=jambi` — GeoJSON district features
  - `GET /api/district-summary?city=jambi` — aggregate stats
  - `GET /api/road/{id}` — single road detail
- [ ] Migrate frontend to Vite build system
- [ ] Connect frontend to API (replace static file fetches)
- [ ] Verify: app works identically but now uses API

### B2. Multi-City Support (Week 1–2)

- [ ] Parameterize pipeline scripts to accept city name as argument
- [ ] Run pipeline for 2 additional cities (e.g., Palembang, Pekanbaru)
- [ ] Add city selector dropdown to frontend
- [ ] Verify: switching cities reloads map with correct data

### B3. Real Data Integration (Week 2–3)

- [ ] Research Lapor.go.id API availability
- [ ] Build CSV upload feature for manual allocation data
- [ ] Integrate BPS population grid data (replace road-density proxy)
- [ ] Add data freshness indicator ("Last updated: ...")
- [ ] Verify: scores change meaningfully when real population data is used

### B4. Enhanced Features (Week 3–4)

- [ ] Add weight-tuning slider panel (live recalculation)
- [ ] Add temporal tracking: quarterly snapshots with time slider
- [ ] Add PDF report export (summary + map screenshot + charts)
- [ ] Add user authentication (API keys for organizations)
- [ ] Add embed mode (iframe-friendly version for journalists)
- [ ] Verify: each feature works independently and together

### B5. Launch Preparation

- [ ] Deploy backend to cloud (Railway / Render / Fly.io)
- [ ] Deploy frontend to Vercel / Netlify
- [ ] Set up custom domain
- [ ] Write landing page with product explanation
- [ ] Create 2-minute product demo video
- [ ] Prepare outreach list: 10 infrastructure consultants / NGOs
- [ ] Verify: end-to-end flow works on production URL

---

## Quick Reference: "Oh Shit" Recovery Plans

| Situation | Recovery |
|---|---|
| OSM API is down | Use pre-cached `raw_graph.graphml` |
| Pipeline crashes mid-way | Use hardcoded sample GeoJSON with 50 roads |
| Leaflet map won't render | Check CDN link, fallback to local Leaflet copy |
| GeoJSON too large (>10MB) | Run `shapely.simplify(tolerance=0.0001)` on geometries |
| Chart.js not rendering | Replace with a simple HTML `<table>` |
| Demo laptop dies | Have the demo recorded on phone as video backup |
| Judges ask "is this real data?" | "The road network is real OSM data. The allocation is simulated to demonstrate the methodology." |

---

*Check items off as you complete them. Ship something real. 🚀*
