<p align="center">
  <strong>🔭 CyclopsRD</strong><br>
  <em>Seeing Infrastructure Decisions Clearly.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Leaflet.js-1.9-green?logo=leaflet&logoColor=white" />
  <img src="https://img.shields.io/badge/Chart.js-4-orange?logo=chartdotjs&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

---

> ⚠️ **Proof of Concept Disclaimer:** The financial allocation patterns and "transparency gaps" shown in this project are **mathematically simulated** using real political representation metrics (DPRD 2024 seats). They are designed to demonstrate the capability of the Decision Audit Engine and **do not reflect actual historical government spending, intentional neglect, or official audits** of the Kota Jambi government.

---

## 🧠 The Problem

> Trillions are spent globally on road infrastructure every year.
> But **who audits the _decisions_ behind the spending?**

Highway maintenance prioritization in most countries is a **black box**. Citizens suspect favoritism. Engineers see misallocation. Yet no one has the tools to prove — or disprove — it with data.

| The Current Reality | The Consequence |
|---|---|
| Maintenance records are unpublished or fragmented | Under-served roads deteriorate, raising safety risks |
| No methodology compares *need* vs. *spending* | Freight costs rise in neglected corridors |
| Citizens suspect political favoritism but can't prove it | Trust in public institutions erodes |
| Accountability is reactive, not analytical | No feedback loop between data and spending decisions |

**CyclopsRD changes this.** We built the first **Infrastructure Decision Audit Engine** — a system that computes an objective "Engineering Priority" for every road segment using graph theory, then compares it against a politically-influenced allocation to expose **Transparency Gaps**.

---

## 💡 The Core Concept

CyclopsRD asks one question:

> **"Does this road get maintained because it _needs_ to be — or because of _who_ represents the district?"**

We answer it in three steps:

```
┌─────────────────────┐     ┌────────────────────────┐     ┌──────────────────────────┐
│  1. ENGINEERING      │     │  2. POLITICAL           │     │  3. THE AUDIT             │
│     PRIORITY         │     │     ALLOCATION          │     │     (Transparency Gap)    │
│                      │     │                         │     │                           │
│  Score every road    │────▶│  Simulate a budget      │────▶│  Compare: Did the road   │
│  by graph theory,    │     │  constrained by real     │     │  get funded because of   │
│  centrality, and     │     │  DPRD Jambi 2024 seat   │     │  NEED or POLITICS?       │
│  infrastructure need │     │  distributions          │     │                           │
└─────────────────────┘     └────────────────────────┘     └──────────────────────────┘
```

### The Result: A Decision Alignment Score

Every road segment receives a **Decision Alignment Score (0–100)**:

- 🟢 **Aligned (100):** Correctly funded OR correctly deferred. The system works.
- 🟡 **Moderate Gap — Neglect (50):** High engineering need, but **not funded**. A critical road is being ignored.
- 🔴 **Significant Gap — Favoritism (30):** Low engineering need, but **funded anyway**. Resources go to politically connected districts.

---

## 🗺️ What It Looks Like

### Interactive Map — Three Lenses

| Mode | What It Shows |
|---|---|
| **🔬 Priority** | Every road color-coded by pure Engineering Priority. Red = critical infrastructure. Green = low priority. |
| **💰 Allocation** | Binary overlay: Teal = Allocated (funded this year). Grey = Unallocated. |
| **🔍 Audit** | The transparency gap. Green = aligned decisions. Yellow = neglected roads. Red = politically favored roads. |

### Side Panel Detail
Click any road to see its full audit breakdown: Engineering Rank, Allocation Status, Score Breakdown (Hierarchy, Centrality, Length, Traffic, Population), and an AI-generated plain-language explanation of **why** the gap exists.

### District Dashboard
A full-screen modal with interactive Chart.js charts comparing **Length-Weighted Engineering Need %** vs **Financial Allocation %** across all 11 Kecamatans (sub-districts) of Kota Jambi.

---

## 🏗️ Architecture

```
                        CyclopsRD Architecture
┌─────────────────────────────────────────────────────────────┐
│                          DATA PIPELINE                       │
│             (Python · Runs once · Offline)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐  │
│  │ 01_fetch      │  │ 02_compute   │  │ 03_score_and_rank │  │
│  │ _network.py   │─▶│ _metrics.py  │─▶│ .py               │  │
│  │ (OSMnx)       │  │ (Centrality) │  │ (Weighted Score)  │  │
│  └──────────────┘  └──────────────┘  └───────────────────┘  │
│                                              │               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────▼───────────┐  │
│  │ 06_export     │  │ 05_calculate │  │ 04_simulate       │  │
│  │ _geojson.py   │◀─│ _gap.py      │◀─│ _allocation.py    │  │
│  │ (Final Output)│  │ (The Audit)  │  │ (DPRD Bias)       │  │
│  └──────┬───────┘  └──────────────┘  └───────────────────┘  │
│         │                                                    │
└─────────┼────────────────────────────────────────────────────┘
          │
          ▼  Static GeoJSON + JSON
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│          (Vanilla JS · Leaflet.js · Chart.js)                │
│                                                              │
│  • Dark theme map with glassmorphism panels                  │
│  • Three visualization modes (Priority / Allocation / Audit)│
│  • Click-to-detail side panel with explanation engine        │
│  • Full-screen district comparison dashboard                 │
│  • Road search with fuzzy matching                           │
│                                                              │
│  NO backend server. NO database. Static files never crash.   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔬 Methodology (Summary)

> See [`methodology_overview.md`](methodology_overview.md) for the full technical deep-dive.

### Step 1: Engineering Priority Score
> **Implementation:** [`pipeline/03_score_and_rank.py`](pipeline/03_score_and_rank.py)

A weighted sum of 6 geospatial metrics, yielding a score from 0–1 for every road segment:

```
Priority = 0.25 × Hierarchy + 0.20 × Betweenness + 0.20 × Length
         + 0.15 × Degree    + 0.10 × Lanes       + 0.10 × Population
```

Every segment receives a **globally unique rank** (1 = most critical) using deterministic micro-jitter to break ties.

### Step 2: Political Allocation Simulation
> **Implementation:** [`pipeline/04_simulate_allocation.py`](pipeline/04_simulate_allocation.py)

We inject **real political data** — the 2024 DPRD Kota Jambi election results — mapping **45 legislative seats** across 5 Electoral Districts (Dapil) to the 11 Kecamatans. Districts with more political representation receive a bias modifier that inflates their allocation propensity.

```
Propensity = (Inverted Engineering Rank ^ 0.8) × (1.0 + Political Bias) + Jitter
```

The top **25%** of roads by Propensity Score are marked as **Allocated**. The rest are **Unallocated**.

### Step 3: The Decision Audit
> **Implementation:** [`pipeline/05_calculate_gap.py`](pipeline/05_calculate_gap.py)

We compare the pure engineering rank against the politically-influenced allocation to determine if each decision was **just** or **biased**.

| Scenario | Engineering Priority | Allocation Status | Verdict |
|---|---|---|---|
| Top 25% Need + Funded | ✅ High | ✅ Allocated | 🟢 **Aligned** |
| Bottom 75% Need + Not Funded | ❌ Low | ❌ Unallocated | 🟢 **Aligned** |
| Top 25% Need + Not Funded | ✅ High | ❌ Unallocated | 🟡 **Neglect** |
| Bottom 50% Need + Funded | ❌ Low | ✅ Allocated | 🔴 **Favoritism** |

> **The Story is in the Tails:** While an average alignment score might seem relatively high city-wide, CyclopsRD is designed to find the critical outliers where the system breaks down. In our Jambi data, the system successfully exposed **108 flagged segments**, comprising **41 neglected high-priority roads** and **12 clear instances of political favoritism**.

---

## 📊 Real Data Sources

This is **not** a toy demo. CyclopsRD is anchored to real-world data:

| Source | What It Provides | How We Use It |
|---|---|---|
| **OpenStreetMap** (via OSMnx) | Road network graph: 1,038 segments (412.6 km) with hierarchy, lanes, surface | Engineering Priority Score |
| **Official Jambi GeoJSON** | 11 Kecamatan administrative boundaries | District-level aggregation |
| **2024 DPRD Kota Jambi Election** | 45 seats across 5 Dapils, mapped to Kecamatans | Political Bias Factor |

### DPRD Seat Distribution (Source of Political Bias)

| Dapil | Kecamatan(s) | Seats | Bias Effect |
|---|---|---|---|
| Dapil 1 | Kota Baru | 6 | 📉 Below average → negative bias |
| Dapil 2 | Alam Barajo | 8 | 📉 Below average → slight negative |
| Dapil 3 | Telanaipura, Danau Sipin, Danau Teluk | 8 | 📉 Below average → slight negative |
| Dapil 4 | Pelayangan, Jambi Timur, Pasar Jambi, Jelutung | 11 | 📈 Above average → positive bias |
| Dapil 5 | Jambi Selatan, Paal Merah | 12 | 📈 Most seats → strongest bias |

> Average = 9 seats/Dapil. Districts above 9 get a budget boost. Districts below 9 get penalized. This is how political representation warps infrastructure decisions.

---

## 🚀 Quick Start

### View the Dashboard (Locally)

```bash
cd frontend
python -m http.server 8000
# Open http://localhost:8000
```

### 🌍 One-Click Deploy (Vercel)
CyclopsRD is pre-configured for zero-downtime static deployment. Simply push the repository to GitHub and import it into Vercel. Our pre-configured `vercel.json` automatically routes the `/frontend` directory to the root.

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2A%2Agithub.com%2Fagungprsety%2FCyclopsRD)


### Run the Full Pipeline

```bash
# 1. Clone & Setup
git clone https://github.com/agungprsety/CyclopsRD.git
cd CyclopsRD
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r pipeline/requirements.txt

# 2. Execute Pipeline (in order)
python pipeline/01_fetch_network.py       # Fetch OSM road graph
python pipeline/02_compute_metrics.py     # Betweenness, degree, hierarchy
python pipeline/03_score_and_rank.py      # Weighted scoring + unique ranking
python pipeline/04_simulate_allocation.py # DPRD-influenced budget allocation
python pipeline/05_calculate_gap.py       # Decision Alignment audit
python pipeline/06_export_geojson.py      # Export to frontend-ready GeoJSON

# 3. Run Tests
python -m pytest tests/test_pipeline.py -v
```

---

## 📁 Project Structure

```
CyclopsRD/
├── pipeline/                       # Python data pipeline (runs once, offline)
│   ├── 01_fetch_network.py         # Download Jambi road graph from OSM
│   ├── 02_compute_metrics.py       # Betweenness centrality, degree, lanes
│   ├── 03_score_and_rank.py        # Engineering Priority Score + unique ranking
│   ├── 04_simulate_allocation.py   # DPRD-biased budget allocation simulation
│   ├── 05_calculate_gap.py         # Decision Alignment audit + district stats
│   ├── 06_export_geojson.py        # Export GeoJSON for the map
│   └── requirements.txt
│
├── frontend/                       # Static web application
│   ├── index.html                  # Main page
│   ├── css/style.css               # Dark theme, glassmorphism, animations
│   ├── js/app.js                   # Map, panels, dashboard, search
│   └── data/                       # Pipeline outputs consumed by the map
│       ├── jambi_roads.geojson     # Road segments + all computed attributes
│       ├── jambi_districts.geojson # Kecamatan boundaries + gap data
│       ├── district_summary.json   # Aggregate stats for dashboard charts
│       └── road_details.json       # Per-road score breakdowns
│
├── tests/
│   └── test_pipeline.py            # Pytest suite: metrics, ranks, allocation, export
│
├── data/                           # Raw + intermediate pipeline outputs
├── methodology_overview.md         # Full technical methodology document
├── hackathon.md                    # Original hackathon proposal + startup strategy
├── demo_script.md                  # 5-minute pitch rehearsal script
└── README.md                       # ← You are here
```

---

## 🛡️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Road Graph | OSMnx + NetworkX | OpenStreetMap-native, centrality computation built-in |
| Spatial Ops | GeoPandas + Shapely | Polygon joins, centroid fallbacks, CRS management |
| Scoring | Pandas + NumPy | Fast vectorized weighted scoring |
| Map | Leaflet.js | Open, lightweight, hackathon-proven, dark tile support |
| Charts | Chart.js | Clean bar/doughnut charts with animation |
| Styling | Vanilla CSS | Dark theme, glassmorphism panels, micro-animations |
| Testing | Pytest | Validates rank uniqueness, allocation logic, export integrity |
| Hosting | Vercel / Static | Zero failure modes — static files never crash on demo day |

---

## 🎯 Why CyclopsRD Wins

1. **The methodology is neutral.** We don't accuse anyone. We build the infrastructure for accountability. The tool reveals patterns; humans investigate causes.
2. **The data is real.** The road network, centrality scores, and political seat distribution are computed from real OpenStreetMap and DPRD Kota Jambi 2024 election data.
3. **It scales.** Any city with OSM data can run this pipeline. The methodology is portable, open-source, and designed for replication across Indonesia — and beyond.
4. **No backend, no downtime.** The pipeline runs once. The frontend reads static files. **Static files never crash on demo day.**

---

## 🔮 Future Vision

> *CyclopsRD could become the standard methodology for infrastructure equity auditing — not just in Indonesia, but in any country with OpenStreetMap coverage.*

- **V2:** Real municipal budget integration, multi-city support, temporal trend tracking
- **V3:** Full GovTech platform with policy simulation for BAPPENAS/World Bank
- **V4:** The "**Bloomberg Terminal for Infrastructure Governance**"

---

<p align="center">
  <strong>CyclopsRD</strong> — Auditing Infrastructure with Data.<br>
  <em>One road at a time.</em>
</p>

## License
MIT License