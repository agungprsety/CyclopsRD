/**
 * CyclopsRD 
 * Main Application Logic
 */

// --- Configuration ---
const CONFIG = {
    startCenter: [-1.61, 103.6],
    startZoom: 13,
    tileUrl: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
    offlineTileUrl: 'assets/tiles/{z}/{x}/{y}.png',
    roadData: 'data/jambi_roads.geojson'
};

// --- State ---
let map;
let roadLayer;
let currentMode = 'priority'; // 'priority', 'allocation', 'audit'
let auditDataMap = new Map(); // Store pre-calculated audit results for performance

// --- Initialization ---
async function initApp() {
    initMap();
    await loadBaseRoads();
    setupEventListeners();
}

function initMap() {
    map = L.map('map', {
        zoomControl: true,
        attributionControl: false
    }).setView(CONFIG.startCenter, CONFIG.startZoom);

    const activeTileUrl = navigator.onLine ? CONFIG.tileUrl : CONFIG.offlineTileUrl;
    L.tileLayer(activeTileUrl, { maxZoom: 19 }).addTo(map);
}



// --- Search Logic ---
let searchData = [];
let highlightLayer;

function initSearch(features) {
    searchData = features.map(f => {
        const name = f.properties.name || f.properties.Name || 'Unnamed Link';
        return {
            id: f.properties.id || f.properties.uid,
            name: name,
            bounds: L.geoJSON(f).getBounds(),
            properties: f.properties,
            feature: f
        };
    });
}

function handleSearch(query) {
    const resultsContainer = document.getElementById('search-results');
    if (!query || query.trim() === '') {
        resultsContainer.innerHTML = '';
        resultsContainer.classList.add('hidden');
        return;
    }

    const matches = searchData.filter(item =>
        item.name.toLowerCase().includes(query.toLowerCase()) ||
        item.id.toLowerCase().includes(query.toLowerCase())
    ).slice(0, 10);

    if (matches.length > 0) {
        resultsContainer.innerHTML = '';
        matches.forEach(item => {
            const div = document.createElement('div');
            div.className = 'search-item';
            div.innerHTML = `
                <span class="road-name">${item.name}</span>
                <span class="road-id">${item.id}</span>
            `;
            div.addEventListener('click', () => {
                selectRoad(item.id);
                resultsContainer.classList.add('hidden');
                document.getElementById('road-search').value = '';
            });
            resultsContainer.appendChild(div);
        });
        resultsContainer.classList.remove('hidden');
    } else {
        resultsContainer.innerHTML = '<div class="search-item">No results found</div>';
        resultsContainer.classList.remove('hidden');
    }
}

window.selectRoad = function (id) {
    const item = searchData.find(d => d.id === id);
    if (item) {
        const resultsContainer = document.getElementById('search-results');
        resultsContainer.innerHTML = '';
        resultsContainer.classList.add('hidden');
        document.getElementById('road-search').value = '';

        map.fitBounds(item.bounds, { maxZoom: 18, padding: [50, 50] });
        openDetailPanel(item.properties);

        if (highlightLayer) map.removeLayer(highlightLayer);

        highlightLayer = L.geoJSON(item.feature, {
            style: { color: '#fff', weight: 10, opacity: 0.6, lineCap: 'round' }
        }).addTo(map);

        setTimeout(() => {
            if (highlightLayer) {
                let opacity = 0.6;
                const fade = setInterval(() => {
                    opacity -= 0.1;
                    if (opacity <= 0) {
                        clearInterval(fade);
                        map.removeLayer(highlightLayer);
                        highlightLayer = null;
                    } else {
                        highlightLayer.setStyle({ opacity: opacity });
                    }
                }, 50);
            }
        }, 2000);
    }
};

function setupEventListeners() {
    document.getElementById('mode-priority').addEventListener('click', () => setMapMode('priority'));
    document.getElementById('mode-allocation').addEventListener('click', () => setMapMode('allocation'));
    document.getElementById('mode-audit').addEventListener('click', () => setMapMode('audit'));


    document.getElementById('close-panel').addEventListener('click', () => {
        document.getElementById('side-panel').classList.add('hidden');
    });

    document.getElementById('toggle-dashboard').addEventListener('click', () => {
        document.getElementById('dashboard-overlay').classList.remove('hidden');
        initDashboard();
    });

    document.getElementById('close-dashboard').addEventListener('click', () => {
        document.getElementById('dashboard-overlay').classList.add('hidden');
    });

    const searchInput = document.getElementById('road-search');
    searchInput.addEventListener('input', (e) => handleSearch(e.target.value));

    searchInput.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.getElementById('search-results').classList.add('hidden');
        }
    });

    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            document.getElementById('search-results').classList.add('hidden');
        }
    });
}

function getTooltipContent(feature) {
    const audit = auditDataMap.get(feature.properties.uid || feature.properties.id);
    const roadName = feature.properties.name || feature.properties.Name || 'Unnamed Link';
    const length = parseFloat(feature.properties.length || 0).toFixed(1);

    let modeLabel, modeValue;
    if (currentMode === 'audit') {
        modeLabel = 'Alignment';
        modeValue = (audit ? audit.alignmentScore : '?') + '%';
    } else if (currentMode === 'allocation') {
        modeLabel = 'Status';
        modeValue = feature.properties.is_allocated === 1 ? 'Allocated' : 'Unallocated';
    } else {
        modeLabel = 'Engineering Rank';
        modeValue = '#' + (audit ? audit.engRank : '?');
    }

    return `
        <div class="tooltip-title">${roadName}</div>
        <div class="tooltip-info">Length: ${length} m</div>
        <div class="tooltip-info">${modeLabel}: <span class="tooltip-score">${modeValue}</span></div>
    `;
}

function setMapMode(mode) {
    currentMode = mode;

    // Update button states
    document.getElementById('mode-priority').classList.toggle('active', mode === 'priority');
    document.getElementById('mode-allocation').classList.toggle('active', mode === 'allocation');
    document.getElementById('mode-audit').classList.toggle('active', mode === 'audit');

    // Refresh layer styles
    if (roadLayer) roadLayer.setStyle(f => getFeatureStyle(f));

    // Refresh all tooltip content for the new mode
    if (roadLayer) {
        roadLayer.eachLayer(layer => {
            if (layer.feature) {
                layer.setTooltipContent(getTooltipContent(layer.feature));
            }
        });
    }

    updateLegend();
}

/**
 * Feature Styling Logic
 */
function getFeatureStyle(feature) {
    const audit = auditDataMap.get(feature.properties.uid || feature.properties.id);
    
    // Mode-specific styling
    if (currentMode === 'priority') {
        const rank = audit ? audit.engRank : 999;
        // High priority = Deep Red/Pink
        return {
            color: rank <= 50 ? '#ff4d6d' : (rank <= 200 ? '#f6ad55' : '#00d4aa'),
            weight: rank <= 50 ? 6 : 4,
            opacity: 0.8
        };
    } else if (currentMode === 'allocation') {
        const allocated = feature.properties.is_allocated === 1;
        return {
            color: allocated ? '#2ecc71' : '#4a5568', // Green if Allocated, Slate if Not
            weight: allocated ? 6 : 2,
            opacity: allocated ? 1.0 : 0.5
        };
    } else {
        // Audit Mode: Color by alignment flag
        const color = audit?.alignmentScore < 40 ? '#ff4d6d' : 
                     (audit?.alignmentScore < 75 ? '#f6ad55' : '#00d4aa');
        return {
            color: color,
            weight: audit?.alignmentScore < 40 ? 8 : 5,
            opacity: audit?.alignmentScore < 40 ? 1.0 : 0.8
        };
    }
}

async function loadBaseRoads() {
    try {
        const res = await fetch(CONFIG.roadData);
        const geo = await res.json();

        // Initialize Search Index
        initSearch(geo.features);

        // PERFORMANCE: Pre-calculate all audit results
        geo.features.forEach(f => {
            const id = f.properties.uid || f.properties.id || `f_${Math.random().toString(36).substr(2, 9)}`;
            f.properties.uid = id; 
            auditDataMap.set(id, getAuditMetrics(f.properties));
        });

        roadLayer = L.geoJSON(geo, {
            style: (feature) => {
                return getFeatureStyle(feature);
            },
            onEachFeature: (feature, layer) => {
                layer.bindTooltip(getTooltipContent(feature), { sticky: true });

                layer.on({
                    mouseover: (e) => {
                        const l = e.target;
                        l.setStyle({ weight: 10, color: '#ffffff', opacity: 1 });
                        if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
                            l.bringToFront();
                        }
                    },
                    mouseout: (e) => {
                        const l = e.target;
                        roadLayer.resetStyle(l);
                    },
                    click: (e) => {
                        openDetailPanel(feature.properties);
                        L.DomEvent.stopPropagation(e);
                    }
                });
            }
        }).addTo(map);

        // Update Audit Summary Stats Dynamically
        const totalLength = geo.features.reduce((sum, f) => sum + parseFloat(f.properties.length || 0), 0);
        const networkKm = (totalLength / 1000).toFixed(1);

        const auditValues = Array.from(auditDataMap.values());
        const flaggedSegments = auditValues.filter(a => a.alignmentScore < 75).length;

        const neglectedPriority = geo.features.filter(f => {
            const rank = parseInt(f.properties.rank);
            return rank <= 250 && f.properties.is_allocated !== 1;
        }).length;

        const politicallyFavored = geo.features.filter(f => {
            const rank = parseInt(f.properties.rank);
            return rank > 300 && f.properties.is_allocated === 1;
        }).length;

        document.getElementById('stat-total').innerText = geo.features.length;
        document.getElementById('stat-coverage').innerText = networkKm + ' km';
        document.getElementById('stat-flagged').innerText = flaggedSegments;
        document.getElementById('stat-neglected').innerText = neglectedPriority;
        document.getElementById('stat-favored').innerText = politicallyFavored;

        // Add Anomalous Hotspots for Demo
        initAnomalies();

        // Initialize legend from JS (replaces static HTML)
        updateLegend();

    } catch (err) {
        console.error("Link load error:", err);
    }
}

async function initAnomalies() {
    try {
        const res = await fetch('data/anomalies.json');
        if (!res.ok) {
            console.warn('anomalies.json not found, using fallback data');
            renderAnomalyMarkers([
                { lat: -1.6153, lng: 103.5852, name: "Neglected Priority Road", score: 42, type: "neglect" },
                { lat: -1.6028, lng: 103.5748, name: "Politically Favored Road", score: 38, type: "favor" },
                { lat: -1.5952, lng: 103.5735, name: "Allocation Gap Detected", score: 31, type: "gap" }
            ]);
            return;
        }
        const anomalies = await res.json();
        renderAnomalyMarkers(anomalies);
    } catch (err) {
        console.warn('Error loading anomalies:', err);
    }
}

function renderAnomalyMarkers(anomalies) {
    anomalies.forEach(a => {
        const icon = L.divIcon({
            className: 'pulse-marker',
            iconSize: [20, 20]
        });
        const label = a.name || a.road_name || 'Anomaly';
        const score = a.score || a.alignment_score || '?';
        const typeLabel = a.type === 'neglect' ? '⚠️ Neglected' : 
                         (a.type === 'favor' ? '🔴 Favored' : '🟡 Gap');
        L.marker([a.lat, a.lng], { icon: icon })
            .addTo(map)
            .bindTooltip(`<strong>${label}</strong><br>${typeLabel}<br>Alignment: ${score}/100`, {
                direction: 'top',
                offset: [0, -10]
            });
    });
}

/**
 * Decision Audit Simulation
 * Now updated to use real properties from GeoJSON if available.
 */
function getAuditMetrics(props) {
    // Check if we have real data in props
    const hasRealData = props.rank !== undefined;

    if (hasRealData) {
        const engRank = parseInt(props.rank);
        const alignmentScore = Math.round(parseFloat(props.alignment_score));
        const isAllocated = props.is_allocated === 1;
        
        let flag = { label: 'Aligned', class: 'flag-aligned', icon: '⚪' };
        if (alignmentScore < 75) flag = { label: 'Moderate', class: 'flag-moderate', icon: '🟡' };
        if (alignmentScore < 40) flag = { label: 'Significant', class: 'flag-significant', icon: '🔴' };

        // Scale factors logic
        const factors = [
            { name: 'Priority Index', val: Math.round((parseFloat(props.priority_score) || 0) * 100) },
            { name: 'Length Weight', val: Math.min(100, Math.round(parseFloat(props.length || 0) / 5)) },
            { name: 'Council Influence', val: 50 + (parseInt(props.rank) % 40) }, 
            { name: 'Strategic Value', val: isAllocated ? 90 : 35 },
            { name: 'Allocation State', val: isAllocated ? 100 : 0 }
        ];

        return { engRank, isAllocated, alignmentScore, flag, factors, confidence: 'HIGH' };
    }

    // Fallback/Deterministic seed for elements without pipe data
    const seed = parseInt(props.id?.split('_')[1] || '0') || 42;
    const engRank = 10 + (seed % 200);
    const alignmentScore = 85;

    let flag = { label: 'Aligned', class: 'flag-aligned', icon: '⚪' };
    const factors = [
        { name: 'Hierarchy', val: 60 + (seed % 40) },
        { name: 'Volume', val: 40 + ((seed * 7) % 55) },
        { name: 'Length', val: 50 },
        { name: 'Density', val: 30 + ((seed * 3) % 65) },
        { name: 'Pavement', val: 20 + ((seed * 9) % 75) }
    ];

    return { engRank, isAllocated: false, alignmentScore, flag, factors, confidence: 'LOW' };
}

/**
 * Generates plain-language explanation for a road's audit status.
 */
function generateExplanation(audit, props) {

    const isAllocated = props.is_allocated === 1;
    const isTopPriority = audit.engRank <= 150; // Threshold for high engineering priority

    let sentiment = "";
    if (isTopPriority && isAllocated) {
        sentiment = `This high-priority link is <strong>successfully allocated</strong> for current year work, following technical needs.`;
    } else if (isTopPriority && !isAllocated) {
        sentiment = `This link is identified as a <strong>priority gap</strong>: it remains unallocated despite a high engineering rank (#${audit.engRank}).`;
    } else if (!isTopPriority && isAllocated) {
        sentiment = `This link shows <strong>favored allocation</strong>: it is being worked on despite a relatively low maintenance priority (#${audit.engRank}).`;
    } else {
        sentiment = `This link is correctly <strong>deferred</strong> as it currently has a low technical engineering priority rank.`;
    }

    const districtInfo = props.kecamatan && props.kecamatan !== 'Unknown' ? ` in <strong>${props.kecamatan}</strong>` : '';
    const lengthInfo = props.length ? ` Spanning <strong>${parseFloat(props.length).toFixed(1)} meters</strong>, it` : ' It';

    return `
        ${sentiment}${lengthInfo} stands at <strong>Rank #${audit.engRank}</strong> in the city-wide index${districtInfo}.
    `;
}

function openDetailPanel(props) {
    const panel = document.getElementById('side-panel');
    const content = document.getElementById('panel-content');

    // Get simulated audit data
    const audit = auditDataMap.get(props.uid || props.id) || getAuditMetrics(props);
    const explanationText = generateExplanation(audit, props);

    content.innerHTML = `
        <div class="badge badge-confidence">
            Reliability: ${audit.confidence}
        </div>

        <div class="panel-header">
            <h2>${props.name || props.Name || 'Unnamed Road'}</h2>
            <p class="road-id">Segment ID: ${props.id || 'N/A'}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-item highlight">
                <label>Engineering Rank</label>
                <div class="value">#${audit.engRank}</div>
            </div>
            <div class="stat-item">
                <label>Allocation Status</label>
                <div class="value" style="color: ${audit.isAllocated ? '#00d4aa' : '#a0aec0'}">
                    ${audit.isAllocated ? 'WORK IN PROGRESS' : 'NOT SCHEDULED'}
                </div>
            </div>
        </div>

        <div class="audit-section">
            <h3>
                <span>Decision Alignment Score</span>
                <span class="badge ${audit.flag.class}">${audit.flag.icon} ${audit.flag.label}</span>
            </h3>
            
            <div class="score-progress">
                <div id="score-fill" class="score-fill"></div>
                <div class="score-marker" style="left: ${audit.alignmentScore}%"></div>
            </div>
            <div style="text-align: right; font-weight: 700; font-size: 1.2rem; font-family: 'Outfit';">
                ${audit.alignmentScore} / 100
            </div>
        </div>

        <div class="audit-section">
            <h3>Audit Drivers</h3>
            <div class="factors-list">
                ${audit.factors.map(f => `
                    <div class="factor-item">
                        <div class="factor-header">
                            <span>${f.name}</span>
                            <span>${f.val}%</span>
                        </div>
                        <div class="factor-bar-bg">
                            <div class="factor-bar-fill" style="width: 0%" data-val="${f.val}%"></div>
                        </div>
                    </div>
                `).join('')}
            </div>
        </div>

        <div class="explanation-box">
            <p>${explanationText}</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-item">
                <label>Link Length</label>
                <div class="value">${parseFloat(props.length || 0).toFixed(1)} m</div>
            </div>
            <div class="stat-item">
                <label>District</label>
                <div class="value">${props.kecamatan || 'N/A'}</div>
            </div>
        </div>
    `;

    panel.classList.remove('hidden');

    // Trigger animations after a micro-task
    setTimeout(() => {
        const scoreFill = document.getElementById('score-fill');
        if (scoreFill) scoreFill.style.width = audit.alignmentScore + '%';

        document.querySelectorAll('.factor-bar-fill').forEach(el => {
            el.style.width = el.getAttribute('data-val');
        });
    }, 50);
}

function updateLegend() {
    const legend = document.getElementById('legend');
    if (currentMode === 'priority') {
        legend.innerHTML = `
            <h4>Engineering Need</h4>
            <div class="legend-item"><div class="legend-color" style="background:#ff4d6d"></div><span>High Priority</span></div>
            <div class="legend-item"><div class="legend-color" style="background:#f6ad55"></div><span>Medium Priority</span></div>
            <div class="legend-item"><div class="legend-color" style="background:#00d4aa"></div><span>Maintenance Only</span></div>
        `;
    } else if (currentMode === 'allocation') {
        legend.innerHTML = `
            <h4>Work Status</h4>
            <div class="legend-item"><div class="legend-color" style="background:#2ecc71"></div><span>Allocated (Active)</span></div>
            <div class="legend-item"><div class="legend-color" style="background:#4a5568"></div><span>Unallocated</span></div>
        `;
    } else if (currentMode === 'audit') {
        legend.innerHTML = `
            <h4>Decision Audit</h4>
            <div class="legend-item"><div class="legend-color" style="background:#00d4aa"></div><span>🟢 Aligned</span></div>
            <div class="legend-item"><div class="legend-color" style="background:#f6ad55"></div><span>🟡 Moderate Gap</span></div>
            <div class="legend-item"><div class="legend-color" style="background:#ff4d6d"></div><span>🔴 Significant Gap</span></div>
        `;
    }
}

function getColor(score) {
    return score > 0.6 ? '#ff4d6d' :
        score > 0.3 ? '#f6ad55' :
            '#00d4aa';
}

let needAllocChart = null;
let alignmentChart = null;

async function initDashboard() {
    try {
        const response = await fetch('data/district_summary.json');
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

        const data = await response.json();
        if (!data || Object.keys(data).length === 0) {
            console.warn("Dashboard data is empty");
            return;
        }

        const labels = Object.keys(data).filter(k => k !== 'Unknown');
        if (labels.length === 0) {
            console.warn("No valid district labels found in dashboard data");
            return;
        }
        const needData = labels.map(l => data[l].need_pct.toFixed(2));
        const allocData = labels.map(l => data[l].alloc_pct.toFixed(2));

        const ctx1 = document.getElementById('need-alloc-chart').getContext('2d');
        if (needAllocChart) needAllocChart.destroy();

        needAllocChart = new Chart(ctx1, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Engineering Need (%)',
                        data: needData,
                        backgroundColor: '#00d4aa',
                        borderRadius: 6
                    },
                    {
                        label: 'Financial Allocation (%)',
                        data: allocData,
                        backgroundColor: '#ff4d6d',
                        borderRadius: 6
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: { beginAtZero: true, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0aec0' } },
                    x: { grid: { display: false }, ticks: { color: '#a0aec0' } }
                },
                plugins: {
                    legend: { labels: { color: 'white', font: { family: 'Inter' } } }
                }
            }
        });

        const alignmentData = labels.map((l, i) => {
            const val = data[l].avg_alignment > 0 ? data[l].avg_alignment : (20 + (i * 15) % 80);
            return val.toFixed(1);
        });

        const ctx2 = document.getElementById('alignment-district-chart').getContext('2d');
        if (alignmentChart) alignmentChart.destroy();

        alignmentChart = new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Alignment Score',
                    data: alignmentData,
                    backgroundColor: alignmentData.map(v => v > 75 ? '#00d4aa' : (v > 40 ? '#f6ad55' : '#ff4d6d')),
                    borderRadius: 6
                }]
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: { max: 100, grid: { color: 'rgba(255,255,255,0.05)' }, ticks: { color: '#a0aec0' } },
                    y: { grid: { display: false }, ticks: { color: '#a0aec0' } }
                },
                plugins: {
                    legend: { display: false }
                }
            }
        });

    } catch (err) {
        console.error("Dashboard error:", err);
    }
}

initApp();
