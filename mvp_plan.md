# CyclopsRD — MVP Development Plan

> Written from the mindset of a senior engineer who has won hackathons before.
> Rule #1: **Ship something real. A beautiful map with real data beats a feature-complete app that crashes on demo day.**

---

## 0. The MVP Philosophy

**What "MVP" means for a hackathon is different from a startup.**

- Hackathon MVP = **one jaw-dropping demo flow** that proves the idea is real.
- Startup MVP = a usable product you can put in front of paying users.

This plan covers **both**, in two phases:
1. **Phase A — Hackathon Demo** (24–48 hours): Build the shortest path to a compelling 5-minute demo.
2. **Phase B — Post-Hackathon MVP** (2–4 weeks): Turn the prototype into something consultants can actually use.

---

## Phase A: Hackathon Demo Build

### A.1 — The "One Demo Flow" Rule

Before writing any code, define the **exact demo script**. Every engineering decision flows from this.

**Target Demo (5 minutes):**

| Step | What Judges See | Emotional Impact |
|---|---|---|
| 1. Map loads | Jambi road network appears, color-coded by engineering priority | "Wow, that's a real city" |
| 2. District overlay | Kecamatan boundaries glow with transparency gap colors | "I can see the inequity instantly" |
| 3. Click a road | Side panel: rank breakdown, gap score, plain-language explanation | "This is sophisticated analysis" |
| 4. District dashboard | Bar chart: Engineering Need % vs Allocation % | "The data tells a clear story" |
| 5. The punchline | Show the Decision Alignment Score for 2–3 key roads | "This could change policy" |

> **Rule: If it's not in this table, it doesn't get built during the hackathon.**

---

### A.2 — Technical Architecture (Hackathon-Scoped)

```
┌─────────────────────────────────────────────────────────┐
│                   HACKATHON SCOPE                       │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────┐  │
│  │  Python       │    │  Static      │    │  Frontend │  │
│  │  Data Pipeline│───▶│  GeoJSON +   │───▶│  Leaflet  │  │
│  │  (offline)    │    │  JSON files  │    │  + JS     │  │
│  └──────────────┘    └──────────────┘    └───────────┘  │
│                                                         │
│  NO backend server. NO database.                        │
│  The pipeline runs once. Frontend reads static files.   │
└─────────────────────────────────────────────────────────┘
```

**Why no backend?** Every moving piece is a potential crash on demo day. Static files never go down.

---

### A.3 — Directory Structure

```
CyclopsRD/
├── pipeline/                    # Python data pipeline (runs once)
│   ├── 01_fetch_network.py      # Download Jambi road graph from OSM
│   ├── 02_compute_metrics.py    # Betweenness centrality, degree, etc.
│   ├── 03_score_and_rank.py     # Engineering Priority Score formula
│   ├── 04_simulate_allocation.py # Simulated observed allocation
│   ├── 05_calculate_gap.py      # Transparency Gap computation
│   ├── 06_export_geojson.py     # Export map-ready GeoJSON
│   └── requirements.txt        # osmnx, networkx, geopandas, shapely
│
├── data/                        # Pipeline output (committed to repo)
│   ├── jambi_roads.geojson      # Road segments with scores
│   ├── jambi_districts.geojson  # Kecamatan boundaries with gap data
│   ├── district_summary.json    # Aggregate stats per district
│   └── road_details.json        # Per-road score breakdown
│
├── frontend/                    # Static web app
│   ├── index.html               # Main page
│   ├── css/
│   │   └── style.css            # Dark theme, glassmorphism panels
│   ├── js/
│   │   ├── app.js               # Main application logic
│   │   ├── map.js               # Leaflet map initialization + layers
│   │   ├── panel.js             # Side panel for road details
│   │   ├── dashboard.js         # District comparison charts
│   │   └── explanation.js       # Auto-generated text explanations
│   └── assets/
│       └── logo.svg
│
├── hackathon.md                 # Project proposal
├── mvp_plan.md                  # This file
└── README.md                    # Setup instructions
```

---

### A.4 — Pipeline Detailed Specs

Each script is small, single-purpose, and testable independently.

#### `01_fetch_network.py`
- Use `osmnx.graph_from_place("Kota Jambi, Indonesia", network_type="drive")`
- Filter to `highway` in `[trunk, primary, secondary, tertiary, trunk_link, primary_link, secondary_link, tertiary_link]`
- Save raw graph to `data/raw_graph.graphml`
- **Fallback:** If OSM API is down during hackathon, pre-cache the file and commit it

#### `02_compute_metrics.py`
- Load graph from `data/raw_graph.graphml`
- Compute:
  - **Betweenness centrality** (edge-based, weight="length")
  - **Degree centrality** (node-based, mapped to edges via max of endpoints)
  - **Lane count** from `lanes` tag (default to 2 if missing)
  - **Road hierarchy score** from `highway` tag mapping:
    ```python
    HIERARCHY_MAP = {
        "trunk": 1.0, "trunk_link": 0.9,
        "primary": 0.8, "primary_link": 0.7,
        "secondary": 0.6, "secondary_link": 0.5,
        "tertiary": 0.4, "tertiary_link": 0.3,
    }
    ```
- Normalize all metrics to [0, 1] range using min-max scaling
- Store as edge attributes on the graph

#### `03_score_and_rank.py`
- Apply the weighted formula:
  ```
  priority = 0.30 × hierarchy + 0.25 × betweenness + 0.20 × degree + 0.15 × lanes_proxy + 0.10 × population
  ```
- **Population proxy for hackathon:** Use road density within 500m buffer as a stand-in. True population data (BPS census grids) is Phase B.
- Rank all segments by priority score descending
- Assign rank number (1 = highest priority)

#### `04_simulate_allocation.py`
- **This is the trickiest part.** We don't have real allocation data.
- Strategy: Generate a **plausible but imperfect** allocation that creates interesting gaps.
- Method:
  1. Start from the engineering rank as a baseline
  2. Apply **district-level bias factors** (some districts get boosted, others penalized)
  3. Add random noise (±15% jitter)
  4. Re-rank to produce `allocation_rank`
- The bias factors are the "story" — they represent hypothetical political influence
- **Be transparent:** In the UI, label this as "Simulated Allocation (Methodology Demo)"

#### `05_calculate_gap.py`
- Segment-level: `gap = allocation_rank - engineering_rank`
  - Positive = over-prioritized relative to engineering need
  - Negative = under-prioritized
- District-level: Aggregate engineering need % and allocation % per kecamatan
- Compute **Decision Alignment Score** = `100 - abs(gap_percentile) × 100`
- Flag determination:
  - Score ≥ 70: ⚪ "Aligned"
  - Score 40–69: 🟡 "Moderate Misalignment"
  - Score < 40: 🔴 "Significant Misalignment"
- Compute **anomaly threshold** using 1 standard deviation of gap distribution

#### `06_export_geojson.py`
- Convert edges to GeoDataFrame
- Spatial join with kecamatan boundary polygons
- Export:
  - `jambi_roads.geojson` — each feature has: `name`, `highway`, `priority_score`, `priority_rank`, `allocation_rank`, `gap`, `alignment_score`, `flag`, `confidence`, `district`
  - `jambi_districts.geojson` — each polygon has: `name`, `eng_need_pct`, `alloc_pct`, `gap_pct`, `alignment_score`, `flag`
  - `district_summary.json` — tabular data for the dashboard charts
  - `road_details.json` — full breakdown per road for the side panel

---

### A.5 — Frontend Detailed Specs

#### Design System

| Token | Value |
|---|---|
| Background | `#0f1117` (near black) |
| Surface | `#1a1d2e` (dark navy) |
| Panel | `rgba(26, 29, 46, 0.85)` + backdrop blur |
| Accent primary | `#00d4aa` (teal-green) |
| Accent warning | `#ff6b6b` (soft red) |
| Accent info | `#4ecdc4` (light teal) |
| Font | Inter (Google Fonts) |
| Border radius | 12px for panels, 8px for cards |

#### Map Layer — `map.js`

- **Base tile:** CartoDB Dark Matter (`https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png`)
- **Road layer:** GeoJSON polylines, styled by `priority_score`
  - Color ramp: `#00d4aa` (low priority) → `#ffd93d` (medium) → `#ff6b6b` (high priority)
  - Line weight: 2px for tertiary, 3px for secondary, 4px for primary, 5px for trunk
- **District layer:** GeoJSON polygons, styled by `gap_pct`
  - Fill: choropleth from blue (under-resourced) through transparent (aligned) to red (over-resourced)
  - Opacity: 0.3 base, 0.6 on hover
  - Border: white, 1px
- **Interaction:**
  - Hover on road → highlight + tooltip with name and alignment score
  - Click on road → open side panel
  - Hover on district → highlight border + show tooltip
  - Click on district → zoom to bounds + show district stats

#### Side Panel — `panel.js`

When a road segment is clicked:

```
┌─────────────────────────────────┐
│  Jl. Sultan Thaha               │
│  Primary Road · Kota Baru       │
│─────────────────────────────────│
│                                 │
│  Engineering Rank    #2         │
│  Allocation Rank     #14        │
│  Gap                 -12        │
│                                 │
│  Decision Alignment             │
│  ████░░░░░░  32/100    🔴       │
│                                 │
│─────────────────────────────────│
│  Score Breakdown                │
│  ├─ Hierarchy     0.80  ████▓  │
│  ├─ Betweenness   0.92  █████  │
│  ├─ Connectivity  0.71  ████   │
│  ├─ Traffic Proxy 0.65  ███▓   │
│  └─ Population    0.48  ██▓    │
│                                 │
│  Confidence: HIGH               │
│─────────────────────────────────│
│  📝 Plain-Language Explanation  │
│                                 │
│  "This road ranks #2 in         │
│   engineering priority due to    │
│   high betweenness centrality    │
│   and primary road status.       │
│   Despite this, it ranks only    │
│   #14 in maintenance allocation  │
│   — a 12-rank gap that places    │
│   it in the top 10% of           │
│   under-prioritized segments."   │
│                                 │
└─────────────────────────────────┘
```

#### District Dashboard — `dashboard.js`

- Triggered by a "Dashboard" toggle button or tab
- **Chart 1:** Grouped bar chart (Chart.js)
  - X-axis: Kecamatan names
  - Y-axis: Percentage
  - Two bars per district: Engineering Need % (teal) vs Allocation % (rose)
- **Chart 2:** Horizontal bar chart — Decision Alignment Score per district
  - Sorted worst-to-best
  - Color-coded by flag (red/yellow/green)

#### Auto-Explanation — `explanation.js`

Template-based text generation:

```javascript
function generateExplanation(road) {
  const factors = getTopFactors(road, 2); // top 2 contributing factors
  const gapPercentile = getGapPercentile(road.gap);

  return `${road.name} ranks #${road.priority_rank} in engineering priority ` +
    `due to ${factors.join(' and ')}. ` +
    `Despite this, it ranks #${road.allocation_rank} in maintenance allocation` +
    ` — a ${Math.abs(road.gap)}-rank gap that places it in the ` +
    `top ${gapPercentile}% of ${road.gap < 0 ? 'under' : 'over'}-prioritized segments.`;
}
```

---

### A.6 — Hackathon Sprint Plan (24 Hours)

> **The golden rule: Get the map on screen by Hour 6. Everything else is polish.**

| Hours | Task | Deliverable | Risk Mitigation |
|---|---|---|---|
| **0–1** | Environment setup | Python venv, npm, folder structure | Pre-install osmnx (it takes 10 min) |
| **1–3** | Pipeline scripts 01–03 | Raw graph + computed metrics + scores | Pre-cache OSM data in case API is slow |
| **3–4** | Pipeline scripts 04–06 | Simulated allocation + gap + GeoJSON exports | Use hardcoded bias if algorithm is slow |
| **4–6** | Basic Leaflet map | Roads load and are colored by priority | This is the "save point." If everything after this fails, you still have a demo |
| **6–8** | District overlay + interaction | Choropleth + click-to-zoom | |
| **8–10** | Side panel | Click road → see scores + gap + explanation | |
| **10–12** | Dashboard charts | Bar charts comparing districts | |
| **12–14** | Polish: dark theme, animations | Smooth transitions, glassmorphism panels, tooltips | |
| **14–16** | Decision Alignment Score | The "killer feature" display for each road | |
| **16–18** | Confidence indicators + methodology panel | Shows data quality per segment | Stretch goal |
| **18–20** | Bug fixing + edge cases | Handle missing data, empty segments | |
| **20–22** | Demo rehearsal | Practice the 5-minute flow 3× | |
| **22–24** | README + slide deck | Documentation + pitch | |

#### "Oh Shit" Checkpoints

| Hour | Check | If Behind... |
|---|---|---|
| 3 | Is the pipeline running? | Use pre-computed GeoJSON, skip to frontend |
| 6 | Is the map rendering? | Drop everything and fix the map |
| 10 | Does clicking a road show data? | Simplify panel to just show raw JSON |
| 14 | Does the dashboard work? | Replace Chart.js with a simple HTML table |

---

### A.7 — Data Quality Strategy

**The #1 killer of hackathon geo projects: bad data.**

Pre-compute these checks in the pipeline:

| Check | Action if Failed |
|---|---|
| Road has no `name` tag | Use `highway` type + auto-generated ID (e.g., "Tertiary Road #47") |
| Road has no `lanes` tag | Default to 2 lanes |
| Road has 0 betweenness centrality | It's an isolated stub — exclude from ranking but keep on map (grey) |
| District polygon is missing | Log a warning, assign "Unknown District" |
| Score is NaN | Set to 0.0, set confidence to "LOW" |

---

## Phase B: Post-Hackathon MVP (2–4 Weeks)

### B.1 — Architecture Upgrade

```
┌────────────┐     ┌────────────┐     ┌──────────────┐
│  Frontend   │────▶│  FastAPI    │────▶│  PostgreSQL  │
│  Vite + JS  │     │  Backend   │     │  + PostGIS   │
└────────────┘     └────────────┘     └──────────────┘
                         │
                   ┌─────┴─────┐
                   │  Pipeline  │
                   │  Scheduled │
                   │  (Celery)  │
                   └───────────┘
```

**Key changes from hackathon version:**
- Move from static files to a proper API
- Add PostGIS for spatial queries
- Add user authentication (API keys for organizations)
- Add city selector (multi-city support)

### B.2 — Real Data Integration

| Data Source | What It Provides | Integration Method |
|---|---|---|
| OSM (Overpass API) | Road network + attributes | Scheduled daily pull |
| BPS Indonesia | Population grids, kecamatan boundaries | Manual GeoJSON import |
| Lapor.go.id | Citizen road complaints | API scraping (if available) or CSV upload |
| Municipal budget PDFs | Allocation data | Manual data entry + PDF parsing (stretch) |

### B.3 — Features to Add

| Feature | Priority | Effort |
|---|---|---|
| Multi-city support (dropdown selector) | P0 | 1 week |
| Weight-tuning slider in UI | P0 | 2 days |
| Temporal gap tracking (quarterly snapshots) | P1 | 1 week |
| Export to PDF report | P1 | 3 days |
| User accounts + saved views | P2 | 1 week |
| Notification system for worsening gaps | P2 | 3 days |
| Embed mode (iframe for journalists/NGOs) | P3 | 2 days |

### B.4 — Metrics That Matter

Track these from day one:

| Metric | Target |
|---|---|
| Page load time (LCP) | < 2 seconds |
| Time to meaningful interaction | < 3 seconds |
| GeoJSON file size | < 5 MB per city |
| Engineering Priority Score computation time | < 30 seconds per city |
| Number of cities supported | 3+ by end of month 1 |

---

## Appendix: Key Technical Decisions

### Why Leaflet over Deck.gl?
Deck.gl is more powerful but has a steeper learning curve. For a hackathon, Leaflet's simplicity and huge plugin ecosystem win. Post-hackathon, migrate to Deck.gl if we need WebGL-level performance for large road networks (>50K segments).

### Why static files over a real backend?
Zero failure modes. The Python pipeline runs once on your laptop, outputs JSON/GeoJSON, and the frontend reads them directly. No server to crash, no CORS to debug, no deployment to configure. For a hackathon, this is the optimal architecture.

### Why simulated allocation data?
Real allocation data doesn't exist in machine-readable form. Rather than pretending, we simulate it transparently and frame the hackathon as a **methodology demonstration**. The tech works; the data integration is a sales/partnership problem, not an engineering one.

### Why not use React/Vue/Angular?
Vanilla JS + Leaflet loads faster, has fewer build issues, and is easier to debug under pressure. A framework adds value at 10K+ lines of code. Our frontend will be ~1,500 lines. Keep it simple.

---

## Appendix: Risk Register

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| 1 | OSM API rate-limited during hackathon | Medium | High | Pre-cache all data before the event |
| 2 | Betweenness centrality takes too long to compute | Low | High | Use approximate betweenness (k=100 samples) |
| 3 | GeoJSON file too large for browser | Medium | Medium | Simplify geometries with `shapely.simplify(tolerance=0.0001)` |
| 4 | Kecamatan boundaries don't align with road network | Medium | Medium | Use spatial buffer (50m) when joining |
| 5 | Demo laptop has no internet | Low | Critical | Bundle all tiles offline using `mbtiles` |
| 6 | Judges don't understand "Transparency Gap" | Medium | High | Lead with the visual (map colors), explain concept second |
| 7 | Political sensitivity of the project | Low | Medium | Use neutral language throughout: "warrants investigation", not "proves corruption" |

---

## Appendix: Winning Hackathon Tips (From Experience)

1. **Demo first, code second.** Write your demo script before writing any code.
2. **Pre-cache everything.** Download all data, install all dependencies, test all APIs *before* the hackathon starts.
3. **The map IS the product.** If the map looks impressive, judges will assume the analysis behind it is impressive too.
4. **Dark theme always wins.** It looks professional, hides UI imperfections, and makes data visualizations pop.
5. **Have a "wow" moment.** Ours is the Decision Alignment Score — showing a specific road where there's a 68-rank gap between engineering need and actual maintenance.
6. **Practice the demo 3 times.** The difference between "eh" and "wow" is presentation timing.
7. **The README is your insurance policy.** If the demo crashes, judges can still read what you built.

---

*CyclopsRD — "Auditing Infrastructure with Data."*
