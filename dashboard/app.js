// State Management
let appData = null;
let currentSlide = 1;
let selectedBrand = "Global";
let simBudgets = {}; // Channel -> Spend (for active brand)
let activeCharts = {};

// DOM Elements
const brandSelector = document.getElementById("brand-selector");
const prevBtn = document.getElementById("prev-btn");
const nextBtn = document.getElementById("next-btn");
const navItems = document.querySelectorAll(".nav-item");
const slideContainers = document.querySelectorAll(".slide-container");

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
    fetch("results.json")
        .then(response => {
            if (!response.ok) {
                throw new Error("JSON file could not be loaded");
            }
            return response.json();
        })
        .then(json => {
            appData = json;
            initUI();
        })
        .catch(err => {
            console.error("Initialization Error:", err);
            alert("Could not load results.json. Make sure python pipeline was run successfully.");
        });
});

function initUI() {
    // 1. Populate Brand Selector
    appData.meta.brands.forEach(brand => {
        const opt = document.createElement("option");
        opt.value = brand;
        opt.textContent = brand;
        brandSelector.appendChild(opt);
    });

    // 2. Add Brand Change Event
    brandSelector.addEventListener("change", (e) => {
        selectedBrand = e.target.value;
        updateDashboard();
    });

    // 3. Setup Navigation
    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const slideNum = parseInt(item.getAttribute("data-slide"));
            goToSlide(slideNum);
        });
    });

    prevBtn.addEventListener("click", () => {
        if (currentSlide > 1) goToSlide(currentSlide - 1);
    });

    nextBtn.addEventListener("click", () => {
        if (currentSlide < 9) goToSlide(currentSlide + 1);
    });

    // 4. Set Initial Display
    goToSlide(1);
    updateDashboard();
}

function goToSlide(slideNum) {
    currentSlide = slideNum;
    
    // Update Navigation UI
    navItems.forEach(item => {
        const itemNum = parseInt(item.getAttribute("data-slide"));
        if (itemNum === currentSlide) {
            item.classList.add("active");
        } else {
            item.classList.remove("active");
        }
    });

    // Update Slide Cards Display
    slideContainers.forEach(container => {
        const containerId = container.getAttribute("id");
        if (containerId === `slide-${currentSlide}`) {
            container.classList.add("active");
        } else {
            container.classList.remove("active");
        }
    });

    // Toggle Prev/Next Buttons state
    prevBtn.disabled = (currentSlide === 1);
    nextBtn.disabled = (currentSlide === 9);

    // Refresh charts for visual layouts
    renderSlideSpecifics();
}

// Update Dashboard when brand scope or active slide changes
function updateDashboard() {
    // Update Header or Global Indicators if needed
    renderSlideSpecifics();
}

function renderSlideSpecifics() {
    if (!appData) return;

    // Get active brand data
    const isGlobal = (selectedBrand === "Global");
    const brandData = isGlobal ? null : appData.optimization_report.brands[selectedBrand];
    const attrData = isGlobal ? appData.attribution_report.global : appData.attribution_report.brands[selectedBrand];

    switch(currentSlide) {
        case 1:
            renderSlide1(attrData, isGlobal);
            break;
        case 2:
            renderSlide2(appData.sifter_report);
            break;
        case 3:
            renderSlide3(attrData);
            break;
        case 4:
            renderSlide4(attrData);
            break;
        case 5:
            renderSlide5(appData.persona_channel_matrix);
            break;
        case 6:
            renderSlide6(attrData, selectedBrand);
            break;
        case 7:
            renderSlide7(attrData, brandData, selectedBrand);
            break;
        case 8:
            // Action items (static styled metrics, no chart refresh needed)
            break;
        case 9:
            // Roadmap (timeline transitions)
            break;
    }
}

// Slide 1: Executive Summary
function renderSlide1(attrData, isGlobal) {
    document.getElementById("s1-total-spend").textContent = `₹${attrData.total_spend_crore.toFixed(2)} Crore`;
    document.getElementById("s1-total-conversions").textContent = attrData.total_conversions.toLocaleString();
}

// Slide 2: Bot Auditing
function renderSlide2(sifter) {
    document.getElementById("s2-capital-saved").textContent = `₹${sifter.capital_saved_crore.toFixed(2)} Crore`;
    
    // Draw Bot Traffic Doughnut Chart
    const ctx = document.getElementById("bot-users-chart").getContext("2d");
    destroyChart("botUsersChart");
    
    activeCharts["botUsersChart"] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Clean Consumers', 'Audited Bot Traffic'],
            datasets: [{
                data: [sifter.total_users - sifter.bot_users, sifter.bot_users],
                backgroundColor: ['#3b82f6', '#ef4444'],
                borderWidth: 1,
                borderColor: '#161b2e'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#f3f4f6', font: { family: 'Plus Jakarta Sans' } }
                }
            }
        }
    });

    // Populate bot savings table
    const tbody = document.querySelector("#bot-savings-table tbody");
    tbody.innerHTML = "";
    
    for (const [channel, details] of Object.entries(sifter.savings_by_channel)) {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td class="text-bold">${channel}</td>
            <td>${details.click_count.toLocaleString()}</td>
            <td>₹${getCPCRateText(channel)}</td>
            <td class="text-bold text-emerald">₹${details.capital_saved_crore.toFixed(4)} Crore</td>
        `;
        tbody.appendChild(row);
    }
}

function getCPCRateText(channel) {
    const rates = {
        "Instagram": "10,000",
        "Google Search": "15,000",
        "Influencer Networks": "30,000",
        "YouTube": "20,000",
        "E-commerce Marketplaces": "25,000"
    };
    return rates[channel] || "0";
}

// Slide 3: Transition Matrix
function renderSlide3(attrData) {
    const table = document.getElementById("transition-matrix-table");
    table.innerHTML = "";
    
    const states = ["Start", "Instagram", "Google Search", "Influencer Networks", "YouTube", "E-commerce Marketplaces", "Conversion", "Null"];
    
    // Generate Header
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    headerRow.appendChild(document.createElement("th")); // empty top-left cell
    states.forEach(s => {
        const th = document.createElement("th");
        th.textContent = s;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Generate Rows
    const tbody = document.createElement("tbody");
    attrData.transition_matrix.forEach(rowInfo => {
        const tr = document.createElement("tr");
        const thFrom = document.createElement("td");
        thFrom.textContent = rowInfo.from_state;
        thFrom.className = "text-bold";
        tr.appendChild(thFrom);
        
        states.forEach(s => {
            const td = document.createElement("td");
            const val = rowInfo.transitions[s] || 0.0;
            td.textContent = (val * 100).toFixed(1) + "%";
            
            // Heatmap color code cells based on intensity
            if (val > 0.0) {
                const alpha = Math.min(0.8, val * 1.5);
                td.style.backgroundColor = `rgba(59, 130, 246, ${alpha})`;
                td.style.color = val > 0.3 ? '#ffffff' : 'var(--color-text-main)';
            }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
}

// Slide 4: Primers vs Closers
function renderSlide4(attrData) {
    const tbody = document.querySelector("#funnel-classification-table tbody");
    tbody.innerHTML = "";
    
    const channels = appData.meta.channels;
    const chartLabels = [];
    const primerScores = [];
    const closerScores = [];

    channels.forEach(ch => {
        const info = attrData.funnel_classification[ch];
        
        chartLabels.push(ch);
        primerScores.push(info.primer_score);
        closerScores.push(info.closer_score);
        
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="text-bold">${ch}</td>
            <td>${(info.primer_score * 100).toFixed(1)}%</td>
            <td>${(info.closer_score * 100).toFixed(1)}%</td>
            <td><span class="funnel-badge ${info.classification === 'Primer' ? 'badge-primer' : 'badge-closer'}">${info.classification}</span></td>
        `;
        tbody.appendChild(tr);
    });

    // Bar chart comparison
    const ctx = document.getElementById("funnel-position-chart").getContext("2d");
    destroyChart("funnelPositionChart");
    
    activeCharts["funnelPositionChart"] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartLabels,
            datasets: [
                {
                    label: 'Primer Score (Top of Funnel)',
                    data: primerScores,
                    backgroundColor: 'rgba(59, 130, 246, 0.75)',
                    borderColor: '#3b82f6',
                    borderWidth: 1
                },
                {
                    label: 'Closer Score (Bottom of Funnel)',
                    data: closerScores,
                    backgroundColor: 'rgba(16, 185, 129, 0.75)',
                    borderColor: '#10b981',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#f3f4f6', font: { family: 'Plus Jakarta Sans' } }
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9ca3af' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { 
                        color: '#9ca3af',
                        callback: function(val) { return (val*100) + '%'; }
                    }
                }
            }
        }
    });
}

// Slide 5: Persona Channel Matrix Heatmap
function renderSlide5(matrix) {
    const table = document.getElementById("persona-matrix-table");
    table.innerHTML = "";
    
    const channels = appData.meta.channels;
    const personas = appData.meta.personas;
    
    // Header
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");
    headerRow.appendChild(document.createElement("th"));
    channels.forEach(ch => {
        const th = document.createElement("th");
        th.textContent = ch;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Body
    const tbody = document.createElement("tbody");
    personas.forEach(p => {
        const tr = document.createElement("tr");
        const tdPersona = document.createElement("td");
        tdPersona.textContent = p;
        tdPersona.className = "text-bold";
        tr.appendChild(tdPersona);
        
        // Find max in row for heatmap normalization
        let rowMax = 0;
        channels.forEach(ch => {
            const val = matrix[p]?.[ch] || 0;
            if (val > rowMax) rowMax = val;
        });
        
        channels.forEach(ch => {
            const td = document.createElement("td");
            const val = matrix[p]?.[ch] || 0;
            td.textContent = val.toLocaleString();
            
            if (val > 0) {
                const alpha = Math.min(0.8, val / rowMax);
                td.style.backgroundColor = `rgba(16, 185, 129, ${alpha})`;
                td.style.color = (val / rowMax) > 0.45 ? '#ffffff' : 'var(--color-text-main)';
            }
            tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
}

// Slide 6: Fatigue curves
function renderSlide6(attrData, brand) {
    const isGlobal = (brand === "Global");
    
    // Get alphas (if global, average alpha across brands)
    const alphas = {};
    const channels = appData.meta.channels;
    
    if (isGlobal) {
        channels.forEach(ch => {
            let sumAlpha = 0;
            let count = 0;
            appData.meta.brands.forEach(b => {
                const allocations = appData.optimization_report.brands[b].allocations;
                const match = allocations.find(a => a.channel === ch);
                if (match) {
                    sumAlpha += match.alpha;
                    count++;
                }
            });
            alphas[ch] = count > 0 ? (sumAlpha / count) : 0.0;
        });
    } else {
        const allocations = appData.optimization_report.brands[brand].allocations;
        allocations.forEach(a => {
            alphas[a.channel] = a.alpha;
        });
    }

    // Generate Chart data
    const xValues = [];
    for (let x = 0; x <= 10; x += 0.5) {
        xValues.push(x);
    }
    
    const datasets = [];
    const colors = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];
    
    channels.forEach((ch, idx) => {
        const alpha = alphas[ch] || 0.0;
        const dataPoints = xValues.map(x => round(alpha * Math.log(x + 1), 1));
        
        datasets.push({
            label: `${ch} (\u03b1=${alpha.toFixed(1)})`,
            data: dataPoints,
            borderColor: colors[idx],
            backgroundColor: colors[idx] + '1A',
            borderWidth: 2,
            tension: 0.3,
            pointRadius: 0
        });
    });

    const ctx = document.getElementById("fatigue-curves-chart").getContext("2d");
    destroyChart("fatigueCurvesChart");
    
    activeCharts["fatigueCurvesChart"] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: xValues.map(x => x.toFixed(1) + " Cr"),
            datasets: datasets
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: { color: '#f3f4f6', font: { family: 'Plus Jakarta Sans' } }
                },
                tooltip: {
                    mode: 'index',
                    intersect: false
                }
            },
            scales: {
                x: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9ca3af' },
                    title: { display: true, text: 'Budget Allocation (Crore)', color: '#f3f4f6' }
                },
                y: {
                    grid: { color: 'rgba(255, 255, 255, 0.05)' },
                    ticks: { color: '#9ca3af' },
                    title: { display: true, text: 'Expected Conversions', color: '#f3f4f6' }
                }
            }
        }
    });
}

// Slide 7: Portfolio Reallocation
function renderSlide7(attrData, brandData, brand) {
    const isGlobal = (brand === "Global");
    const channels = appData.meta.channels;
    
    // For Slide 7, if selected brand is "Global", we aggregate brand-level allocation results
    // Let's create an aggregated metrics object
    let allocations = [];
    let totalHistSpend = 0.0;
    let totalOptSpend = 0.0;
    let totalHistConvs = 0;
    let totalOptConvs = 0;
    let totalScaledConvs = 0;

    if (isGlobal) {
        // Aggregate
        channels.forEach(ch => {
            let chHistSpend = 0.0;
            let chOptSpend = 0.0;
            let chHistConvs = 0.0;
            let chOptConvs = 0.0;
            let chScaledSpend = 0.0;
            
            appData.meta.brands.forEach(b => {
                const bAlloc = appData.optimization_report.brands[b].allocations;
                const match = bAlloc.find(a => a.channel === ch);
                if (match) {
                    chHistSpend += match.historical_spend;
                    chOptSpend += match.optimized_spend;
                    chHistConvs += match.historical_conversions;
                    chOptConvs += match.expected_optimized_conversions;
                    chScaledSpend += match.scaled_historical_spend;
                }
            });
            
            allocations.push({
                "channel": ch,
                "historical_spend": chHistSpend,
                "historical_conversions": chHistConvs,
                "scaled_historical_spend": chScaledSpend,
                "optimized_spend": chOptSpend,
                "expected_optimized_conversions": chOptConvs
            });
        });
        
        totalHistSpend = appData.optimization_report.global_historical_conversions; // placeholder check
        totalHistConvs = appData.optimization_report.global_historical_conversions;
        totalOptConvs = appData.optimization_report.global_optimized_conversions;
        totalScaledConvs = appData.optimization_report.global_scaled_historical_conversions;
        
        const gainPct = appData.optimization_report.global_efficiency_gain_pct;
        document.getElementById("efficiency-gain-badge").textContent = `Conglomerate Gain: +${gainPct.toFixed(1)}%`;
    } else {
        allocations = brandData.allocations;
        totalHistConvs = brandData.historical_conversions_total;
        totalOptConvs = brandData.optimized_conversions_total;
        totalScaledConvs = brandData.scaled_historical_conversions_total;
        
        const gainPct = brandData.efficiency_gain_pct;
        document.getElementById("efficiency-gain-badge").textContent = `Brand Gain: +${gainPct.toFixed(1)}%`;
    }

    // Populate Table
    const tbody = document.querySelector("#reallocation-table tbody");
    tbody.innerHTML = "";
    
    allocations.forEach(alloc => {
        const histSpend = alloc.historical_spend;
        const optSpend = alloc.optimized_spend;
        const delta = optSpend - histSpend;
        const convs = alloc.expected_optimized_conversions || 0.0;
        const cpa = alloc.historical_conversions > 0 ? histSpend / alloc.historical_conversions : 0.0;
        
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td class="text-bold">${alloc.channel}</td>
            <td>₹${histSpend.toFixed(2)} Cr</td>
            <td class="text-bold text-emerald">₹${optSpend.toFixed(2)} Cr</td>
            <td class="${delta >= 0 ? 'text-emerald' : 'text-red'}">${delta >= 0 ? '+' : ''}₹${delta.toFixed(2)} Cr</td>
            <td>₹${cpa.toFixed(4)} Cr</td>
            <td class="text-bold">${Math.round(convs).toLocaleString()}</td>
        `;
        tbody.appendChild(tr);
    });

    // Populate Interactive Sliders
    // SImulators operate on Brand-level context (or Global using averaged coefficients)
    // If Global is selected, we use Brand A as default or average the alpha parameters
    const activeBrandName = isGlobal ? "Brand A" : brand;
    const activeBrandData = appData.optimization_report.brands[activeBrandName];
    
    // Store current simulator brand alphas
    simBudgets = {};
    const simAlphas = {};
    activeBrandData.allocations.forEach(a => {
        simAlphas[a.channel] = a.alpha;
        simBudgets[a.channel] = a.historical_spend; // Start simulator at historical allocation
    });

    const slidersList = document.querySelector(".sliders-list");
    slidersList.innerHTML = "";
    
    channels.forEach(ch => {
        const group = document.createElement("div");
        group.className = "slider-group";
        
        const histVal = simBudgets[ch];
        
        group.innerHTML = `
            <div class="slider-label">
                <span>${ch}</span>
                <strong id="label-${ch.replace(/\s+/g, '-')}">₹${histVal.toFixed(2)} Crore</strong>
            </div>
            <input type="range" class="sim-slider" 
                   data-channel="${ch}" 
                   min="0.0" max="5.0" step="0.1" 
                   value="${histVal.toFixed(1)}">
        `;
        slidersList.appendChild(group);
    });

    // Set interactive model targets
    document.getElementById("model-optimal-convs").textContent = Math.round(activeBrandData.optimized_conversions_total).toLocaleString();
    
    // Add Event listeners to sliders
    const sliders = document.querySelectorAll(".sim-slider");
    sliders.forEach(slider => {
        slider.addEventListener("input", (e) => {
            const chName = e.target.getAttribute("data-channel");
            const val = parseFloat(e.target.value);
            simBudgets[chName] = val;
            
            // Update slider label
            const labelId = "label-" + chName.replace(/\s+/g, '-');
            document.getElementById(labelId).textContent = `₹${val.toFixed(2)} Crore`;
            
            recalculateSimulation(simAlphas);
        });
    });

    // Actions
    document.getElementById("reset-sim-btn").onclick = () => {
        activeBrandData.allocations.forEach(a => {
            simBudgets[a.channel] = a.historical_spend;
            const slider = document.querySelector(`.sim-slider[data-channel="${a.channel}"]`);
            slider.value = a.historical_spend.toFixed(1);
            
            const labelId = "label-" + a.channel.replace(/\s+/g, '-');
            document.getElementById(labelId).textContent = `₹${a.historical_spend.toFixed(2)} Crore`;
        });
        recalculateSimulation(simAlphas);
    };

    document.getElementById("apply-optimal-btn").onclick = () => {
        activeBrandData.allocations.forEach(a => {
            simBudgets[a.channel] = a.optimized_spend;
            const slider = document.querySelector(`.sim-slider[data-channel="${a.channel}"]`);
            slider.value = a.optimized_spend.toFixed(1);
            
            const labelId = "label-" + a.channel.replace(/\s+/g, '-');
            document.getElementById(labelId).textContent = `₹${a.optimized_spend.toFixed(2)} Crore`;
        });
        recalculateSimulation(simAlphas);
    };

    recalculateSimulation(simAlphas);
}

function recalculateSimulation(alphas) {
    let totalBudget = 0.0;
    let expectedConvs = 0.0;
    
    for (const [ch, spend] of Object.entries(simBudgets)) {
        totalBudget += spend;
        const alpha = alphas[ch] || 0.0;
        expectedConvs += alpha * Math.log(spend + 1);
    }
    
    const budgetEl = document.getElementById("sim-total-budget");
    budgetEl.textContent = `₹${totalBudget.toFixed(2)} Crore`;
    
    // Color code if sum != 10 Crore
    // We give a small margin of error (e.g. 0.05 Crore)
    if (Math.abs(totalBudget - 10.0) < 0.1) {
        budgetEl.style.color = "var(--color-green)";
    } else {
        budgetEl.style.color = "var(--color-red)";
    }
    
    document.getElementById("sim-expected-convs").textContent = Math.round(expectedConvs).toLocaleString();
}

// Chart Destroyer helper
function destroyChart(chartKey) {
    if (activeCharts[chartKey]) {
        activeCharts[chartKey].destroy();
        delete activeCharts[chartKey];
    }
}

// Simple Rounding utility
function round(value, decimals) {
    return Number(Math.round(value+'e'+decimals)+'e-'+decimals);
}
