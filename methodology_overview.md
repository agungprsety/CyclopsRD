# CyclopsRD — Methodology & Scoring Model

## 1. Engineering Priority Score (The "Ideal" Need)
The score is a weighted sum of five key geospatial factors:

| Factor | Weight | Rationale |
|---|---|---|
| **Road Hierarchy** | 30% | Trunk/Primary roads are the skeleton of the economy. |
| **Betweenness Centrality** | 25% | Graph-based metric showing how many shortest paths pass through this segment. |
| **Connectivity Degree** | 20% | Number of intersections; high-degree roads are critical hubs. |
| **Traffic Proxy** | 15% | Number of lanes and road surface data used as a stand-in for volume. |
| **Population Exposure** | 10% | Density within 500m of the road segment. |

## 2. Observed Allocation (The "Reality")
For the MVP, we use citizen-reported maintenance data and budget proxies to rank where the municipality is currently spending its effort.

## 3. The Transparency Gap (The Audit)
```
Transparency Gap = Allocation Rank - Engineering Rank
```
- **Positive Gap (+) :** "Political Favorite" (getting more than engineering need suggests).
- **Negative Gap (-) :** "Systemic Neglect" (getting less than engineering need suggests).

## 4. Decision Alignment Score
A normalized metric (0-100) that flags anomalies outside of 1 standard deviation of the global mean.
- **Score < 40:** Trigger for audit investigation.
- **Score > 70:** Aligned decision-making.

---
*InfraLens: Seeing infrastructure decisions clearly.*
