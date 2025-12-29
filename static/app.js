/**
 * Optimal Konum Planlayıcı - Frontend
 */

// ===== Limits =====
// Google Maps Distance Matrix API kotasını korumak için
// Max 100x15 = 1500 element per optimization
const MAX_DEMAND_POINTS = 100;
const MAX_CANDIDATE_LOCATIONS = 15;

// ===== Sektör Terminolojisi =====
const SECTOR_CONFIG = {
    general: {
        facility: "tesis",
        facilityPlural: "tesis",
        demandDesc: "Hizmet verilmesi gereken lokasyonlar",
        candidateDesc: "Tesis kurulabilecek potansiyel yerler",
        countLabel: "Açılacak tesis sayısı:"
    },
    retail: {
        facility: "mağaza",
        facilityPlural: "mağaza",
        demandDesc: "Müşteri yoğunluğu olan bölgeler",
        candidateDesc: "Mağaza açılabilecek potansiyel yerler",
        countLabel: "Açılacak mağaza sayısı:"
    },
    health: {
        facility: "sağlık merkezi",
        facilityPlural: "sağlık merkezi",
        demandDesc: "Hizmet verilecek nüfus bölgeleri",
        candidateDesc: "Sağlık merkezi kurulabilecek yerler",
        countLabel: "Açılacak merkez sayısı:"
    },
    logistics: {
        facility: "depo",
        facilityPlural: "depo",
        demandDesc: "Teslimat yapılacak bölgeler",
        candidateDesc: "Depo kurulabilecek potansiyel yerler",
        countLabel: "Açılacak depo sayısı:"
    },
    public: {
        facility: "hizmet noktası",
        facilityPlural: "hizmet noktası",
        demandDesc: "Vatandaşlara hizmet verilecek bölgeler",
        candidateDesc: "Hizmet noktası açılabilecek yerler",
        countLabel: "Açılacak nokta sayısı:"
    },
    energy: {
        facility: "istasyon",
        facilityPlural: "istasyon",
        demandDesc: "Şarj/enerji talebi olan bölgeler",
        candidateDesc: "İstasyon kurulabilecek potansiyel yerler",
        countLabel: "Açılacak istasyon sayısı:"
    }
};

// ===== State =====
const state = {
    demandPoints: [],
    candidateLocations: [],
    currentSector: "general",
    map: null,
    markers: {
        demand: [],
        candidate: [],
        selected: [],
        connections: []
    }
};

// ===== Resize Sidebar =====
function initResizeSidebar() {
    const sidebar = document.getElementById("sidebar");
    const handle = document.getElementById("resizeHandle");

    let isResizing = false;
    let startX, startWidth;

    handle.addEventListener("mousedown", (e) => {
        isResizing = true;
        startX = e.clientX;
        startWidth = sidebar.offsetWidth;
        handle.classList.add("active");
        document.body.style.cursor = "ew-resize";
        document.body.style.userSelect = "none";
    });

    document.addEventListener("mousemove", (e) => {
        if (!isResizing) return;

        const diff = e.clientX - startX;
        const newWidth = Math.min(
            Math.max(startWidth + diff, 350), // min
            700 // max
        );
        sidebar.style.width = newWidth + "px";

        // Haritayı yeniden boyutlandır
        if (state.map) {
            state.map.invalidateSize();
        }
    });

    document.addEventListener("mouseup", () => {
        if (isResizing) {
            isResizing = false;
            handle.classList.remove("active");
            document.body.style.cursor = "";
            document.body.style.userSelect = "";
        }
    });
}

// ===== Sektör Seçimi =====
function initSectorSelector() {
    const sectorSelect = document.getElementById("sectorSelect");

    sectorSelect.addEventListener("change", (e) => {
        state.currentSector = e.target.value;
        updateTerminology();
    });
}

function updateTerminology() {
    const config = SECTOR_CONFIG[state.currentSector];

    // Talep noktaları açıklamasını güncelle
    const demandDesc = document.querySelector(".location-section:first-of-type .section-desc");
    if (demandDesc) demandDesc.textContent = config.demandDesc;

    // Aday konumlar açıklamasını güncelle
    const candidateDesc = document.querySelector(".location-section:last-of-type .section-desc");
    if (candidateDesc) candidateDesc.textContent = config.candidateDesc;

    // Sayı etiketi güncelle
    const countLabel = document.querySelector(".settings-section label");
    if (countLabel) countLabel.textContent = config.countLabel;
}

// ===== Initialize =====
document.addEventListener("DOMContentLoaded", () => {
    initResizeSidebar();
    initSectorSelector();
    initMap();
    initSearch("demandSearch", "demandSuggestions", "demand");
    initSearch("candidateSearch", "candidateSuggestions", "candidate");
    initOptimizeButton();
});

// ===== Map =====
function initMap() {
    // İstanbul merkezli harita
    state.map = L.map("map").setView([41.015, 28.979], 11);

    // OpenStreetMap tile layer
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(state.map);
}

// ===== Search =====
function initSearch(inputId, suggestionsId, type) {
    const input = document.getElementById(inputId);
    const suggestions = document.getElementById(suggestionsId);

    let debounceTimer;

    input.addEventListener("input", (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();

        if (query.length < 2) {
            suggestions.classList.remove("active");
            return;
        }

        debounceTimer = setTimeout(() => {
            fetchSuggestions(query, suggestions, type);
        }, 300);
    });

    // Dışarı tıklayınca kapat
    document.addEventListener("click", (e) => {
        if (!input.contains(e.target) && !suggestions.contains(e.target)) {
            suggestions.classList.remove("active");
        }
    });
}

async function fetchSuggestions(query, suggestionsEl, type) {
    try {
        const response = await fetch(`/api/places/autocomplete?q=${encodeURIComponent(query)}`);
        const data = await response.json();

        if (data.predictions && data.predictions.length > 0) {
            suggestionsEl.innerHTML = data.predictions.map(p => `
                <div class="suggestion-item" data-place-id="${p.place_id}" data-type="${type}">
                    <div class="suggestion-name">${p.structured_formatting?.main_text || p.description}</div>
                    <div class="suggestion-address">${p.structured_formatting?.secondary_text || ""}</div>
                </div>
            `).join("");

            suggestionsEl.classList.add("active");

            // Tıklama eventleri
            suggestionsEl.querySelectorAll(".suggestion-item").forEach(item => {
                item.addEventListener("click", () => handleSuggestionClick(item));
            });
        } else {
            suggestionsEl.classList.remove("active");
        }
    } catch (error) {
        console.error("Arama hatası:", error);
    }
}

async function handleSuggestionClick(item) {
    const placeId = item.dataset.placeId;
    const type = item.dataset.type;

    try {
        // Place details al (koordinatlar için)
        const response = await fetch(`/api/places/details?place_id=${placeId}`);
        const data = await response.json();

        if (data.result) {
            const place = data.result;
            const location = {
                name: place.name,
                address: place.formatted_address,
                lat: place.geometry.location.lat,
                lng: place.geometry.location.lng,
                placeId: placeId
            };

            addLocation(location, type);
        }
    } catch (error) {
        console.error("Detay hatası:", error);
    }

    // Temizle
    const inputId = type === "demand" ? "demandSearch" : "candidateSearch";
    document.getElementById(inputId).value = "";
    item.parentElement.classList.remove("active");
}

// ===== Location Management =====
function addLocation(location, type) {
    const list = type === "demand" ? state.demandPoints : state.candidateLocations;
    const listEl = document.getElementById(type === "demand" ? "demandList" : "candidateList");
    const countEl = document.getElementById(type === "demand" ? "demandCount" : "candidateCount");
    const maxLimit = type === "demand" ? MAX_DEMAND_POINTS : MAX_CANDIDATE_LOCATIONS;
    const typeName = type === "demand" ? "Talep noktası" : "Aday konum";

    // Limit kontrolü
    if (list.length >= maxLimit) {
        alert(`⚠️ Maksimum ${maxLimit} ${typeName.toLowerCase()} ekleyebilirsiniz!\n\nSebep: Google Maps API kotasını korumak için bu limit uygulanmaktadır.`);
        return;
    }

    // Zaten var mı kontrol et
    if (list.some(l => l.placeId === location.placeId)) {
        alert("Bu konum zaten ekli!");
        return;
    }

    list.push(location);

    // UI güncelle
    const li = document.createElement("li");
    li.className = "location-item";
    li.dataset.placeId = location.placeId;
    li.innerHTML = `
        <span class="location-name" title="${location.address}">${location.name}</span>
        <button class="remove-btn" onclick="removeLocation('${location.placeId}', '${type}')">✕</button>
    `;
    listEl.appendChild(li);

    countEl.textContent = list.length;

    // Haritaya ekle
    addMarker(location, type);
}

function removeLocation(placeId, type) {
    const list = type === "demand" ? state.demandPoints : state.candidateLocations;
    const listEl = document.getElementById(type === "demand" ? "demandList" : "candidateList");
    const countEl = document.getElementById(type === "demand" ? "demandCount" : "candidateCount");

    // State'den kaldır
    const index = list.findIndex(l => l.placeId === placeId);
    if (index > -1) {
        list.splice(index, 1);
    }

    // UI'dan kaldır
    const item = listEl.querySelector(`[data-place-id="${placeId}"]`);
    if (item) {
        item.remove();
    }

    countEl.textContent = list.length;

    // Haritadan kaldır
    removeMarker(placeId, type);
}

// ===== Markers =====
function addMarker(location, type) {
    const color = type === "demand" ? "#3b82f6" : "#f59e0b";

    const marker = L.circleMarker([location.lat, location.lng], {
        radius: 10,
        fillColor: color,
        color: "#ffffff",
        weight: 2,
        opacity: 1,
        fillOpacity: 0.9
    }).addTo(state.map);

    marker.bindPopup(`<b>${location.name}</b><br>${location.address || ""}`);
    marker.placeId = location.placeId;

    state.markers[type].push(marker);

    // Haritayı tüm markerları gösterecek şekilde ayarla
    fitMapToMarkers();
}

function removeMarker(placeId, type) {
    const markers = state.markers[type];
    const index = markers.findIndex(m => m.placeId === placeId);

    if (index > -1) {
        markers[index].remove();
        markers.splice(index, 1);
    }
}

function fitMapToMarkers() {
    const allMarkers = [...state.markers.demand, ...state.markers.candidate];

    if (allMarkers.length > 0) {
        const group = L.featureGroup(allMarkers);
        state.map.fitBounds(group.getBounds().pad(0.1));
    }
}

function clearOptimizationResults() {
    // Seçilen marker ve bağlantıları temizle
    state.markers.selected.forEach(m => m.remove());
    state.markers.selected = [];

    state.markers.connections.forEach(c => c.remove());
    state.markers.connections = [];
}

// ===== Optimization =====
function initOptimizeButton() {
    const btn = document.getElementById("optimizeBtn");

    btn.addEventListener("click", async () => {
        if (state.demandPoints.length === 0) {
            alert("En az bir talep noktası ekleyin!");
            return;
        }

        if (state.candidateLocations.length === 0) {
            alert("En az bir aday konum ekleyin!");
            return;
        }

        const numShops = parseInt(document.getElementById("numShops").value) || 3;

        if (numShops > state.candidateLocations.length) {
            alert(`Tesis sayısı aday konum sayısından (${state.candidateLocations.length}) fazla olamaz!`);
            return;
        }

        btn.disabled = true;
        btn.textContent = "⏳ Hesaplanıyor...";

        try {
            const response = await fetch("/api/optimize", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    demand_points: state.demandPoints,
                    candidate_locations: state.candidateLocations,
                    num_shops: numShops
                })
            });

            const result = await response.json();

            if (result.success) {
                displayResults(result);
            } else {
                alert("Hata: " + (result.error || "Bilinmeyen hata"));
            }
        } catch (error) {
            alert("Sunucu hatası: " + error.message);
        } finally {
            btn.disabled = false;
            btn.textContent = "Optimize Et";
        }
    });
}

function displayResults(result) {
    clearOptimizationResults();

    const resultArea = document.getElementById("resultArea");
    const resultContent = document.getElementById("resultContent");

    // Sonuçları göster
    let html = "";

    result.selected_shops.forEach((shop, shopIndex) => {
        // Seçilen dükkanı haritada yeşil yap
        const marker = L.circleMarker([shop.lat, shop.lng], {
            radius: 15,
            fillColor: "#22c55e",
            color: "#ffffff",
            weight: 3,
            opacity: 1,
            fillOpacity: 0.9
        }).addTo(state.map);

        // Popup'ta adres göster
        marker.bindPopup(`
            <b>⭐ ${shop.name}</b><br>
            <span style="color:#888;font-size:12px;">${shop.address || "Seçilen dükkan konumu"}</span>
        `);
        state.markers.selected.push(marker);

        // Bağlantı çizgilerini çiz
        shop.connected_points.forEach(point => {
            const line = L.polyline(
                [[shop.lat, shop.lng], [point.lat, point.lng]],
                { color: "#22c55e", weight: 5, opacity: 0.85 }
            ).addTo(state.map);
            state.markers.connections.push(line);
        });

        // Bağlı noktaların listesi (adresli)
        const connectedPointsHtml = shop.connected_points.map(point =>
            `<div class="connected-point">
                <div class="point-info">
                    <span class="point-name">📍 ${point.name}</span>
                    <span class="point-address">${point.address || ""}</span>
                </div>
                <span class="point-distance">${point.distance} km</span>
            </div>`
        ).join("");

        html += `
            <div class="result-item" onclick="toggleResultDetails(${shopIndex})">
                <div class="result-header">
                    <div class="result-shop-name">⭐ ${shop.name}</div>
                    <div class="result-shop-address">${shop.address || ""}</div>
                    <div class="result-connections">
                        ${shop.connected_points.length} noktaya hizmet verir
                        <span class="expand-icon" id="expandIcon${shopIndex}">▼</span>
                    </div>
                </div>
                <div class="result-details hidden" id="resultDetails${shopIndex}">
                    ${connectedPointsHtml}
                </div>
            </div>
        `;
    });

    html += `
        <div class="total-distance">
            📏 Toplam Mesafe: ${result.total_distance_km} km
        </div>
    `;

    resultContent.innerHTML = html;
    resultArea.classList.remove("hidden");

    // Haritayı sonuçlara odakla
    fitMapToMarkers();
}

// Sonuç detaylarını aç/kapat
function toggleResultDetails(shopIndex) {
    const details = document.getElementById(`resultDetails${shopIndex}`);
    const icon = document.getElementById(`expandIcon${shopIndex}`);

    if (details.classList.contains("hidden")) {
        details.classList.remove("hidden");
        icon.textContent = "▲";
    } else {
        details.classList.add("hidden");
        icon.textContent = "▼";
    }
}
