"""
Optimal Konum Planlayıcı - Web Sunucusu
Tesis/mağaza/depo vb. için optimal konum belirleme uygulaması
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import requests
from collections import namedtuple
from functools import lru_cache


# .env dosyasını yükle
load_dotenv()

# NamedPoint for location representation
NamedPoint = namedtuple("NamedPoint", ["name", "x", "y"])  # x=lng, y=lat

app = Flask(__name__)
CORS(app)

# Google Maps API Key
GOOGLE_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")


@app.route("/")
def index():
    """Ana sayfa"""
    return render_template("index.html", api_key=GOOGLE_API_KEY)

## ilk 100 çağrıyı cachledik. 
@lru_cache(maxsize=100)
def get_autocomplete_results(query):
    """Google Places Autocomplete API çağrısını cache'ler."""
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": query,
        "key": GOOGLE_API_KEY,
        "language": "tr",
        "components": "country:tr"
    }
    response = requests.get(url, params=params, timeout=10)
    return response.json()


@app.route("/api/places/autocomplete")
def places_autocomplete():
    """Google Places Autocomplete proxy"""
    query = request.args.get("q", "")
    if not query:
        return jsonify({"predictions": []})
    
    try:
        data = get_autocomplete_results(query)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e), "predictions": []})


@lru_cache(maxsize=100)
def get_place_details(place_id):
    """Google Places Details API çağrısını cache'ler."""
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        "place_id": place_id,
        "key": GOOGLE_API_KEY,
        "fields": "name,formatted_address,geometry"
    }
    response = requests.get(url, params=params, timeout=10)
    return response.json()


@app.route("/api/places/details")
def place_details():
    """Google Places Details - koordinat almak için"""
    place_id = request.args.get("place_id", "")
    if not place_id:
        return jsonify({"error": "place_id gerekli"})
    
    try:
        data = get_place_details(place_id)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/optimize", methods=["POST"])
def run_optimization():
    """Optimizasyon çalıştır - Gerçek yol mesafesi ile"""
    data = request.get_json()
    
    demand_points = data.get("demand_points", [])
    candidate_locations = data.get("candidate_locations", [])
    num_shops = data.get("num_shops", 5)
    
    if not demand_points or not candidate_locations:
        return jsonify({
            "error": "Hem talep noktaları hem de aday konumlar gerekli"
        }), 400
    
    try:
        # Orijinal verileri sakla (adresler için)
        demand_data = {p["name"]: p for p in demand_points}
        candidate_data = {p["name"]: p for p in candidate_locations}
        
        # NamedPoint nesnelerine dönüştür
        demands = [
            NamedPoint(p["name"], p["lng"], p["lat"]) 
            for p in demand_points
        ]
        candidates = [
            NamedPoint(p["name"], p["lng"], p["lat"]) 
            for p in candidate_locations
        ]
        
        # Google Maps Distance Matrix API ile gerçek mesafeleri al
        distance_matrix = fetch_distance_matrix(candidates, demands)
        
        if distance_matrix is None:
            return jsonify({
                "error": "Mesafe matrisi hesaplanamadı. API hatası."
            }), 500
        
        # MILP Optimizasyon
        import pulp
        
        mdl = pulp.LpProblem("coffee_shops", pulp.LpMinimize)
        
        # Değişkenler
        shop_vars = pulp.LpVariable.dicts(
            "is_shop", 
            range(len(candidates)), 
            cat="Binary"
        )
        link_vars = {
            (i, j): pulp.LpVariable(f"link_{i}_{j}", cat="Binary")
            for i in range(len(candidates))
            for j in range(len(demands))
        }
        
        # Kısıtlar
        # Her talep noktası bir dükana bağlı olmalı
        for j in range(len(demands)):
            mdl += pulp.lpSum(link_vars[i, j] for i in range(len(candidates))) == 1
        
        # Bağlantı sadece açık dükanlara yapılabilir
        for i in range(len(candidates)):
            for j in range(len(demands)):
                mdl += link_vars[i, j] <= shop_vars[i]
        
        # Açılacak dükkan sayısı
        mdl += pulp.lpSum(shop_vars[i] for i in range(len(candidates))) == min(num_shops, len(candidates))
        
        # Amaç fonksiyonu: toplam GERÇEK YOL mesafesini minimize et
        mdl += pulp.lpSum(
            link_vars[i, j] * distance_matrix[i][j]
            for i in range(len(candidates))
            for j in range(len(demands))
        )
        
        # Çöz
        mdl.solve(pulp.PULP_CBC_CMD(msg=0))
        
        # MILP Status kontrolü - çözüm başarılı mı?
        if mdl.status != pulp.LpStatusOptimal:
            return jsonify({
                "error": f"Optimal çözüm bulunamadı. Durum: {pulp.LpStatus[mdl.status]}",
                "suggestion": "Konum sayılarını veya kısıtlamaları kontrol edin."
            }), 500
        
        # Sonuçları topla
        selected_shops = []
        unreachable_count = 0  # Ulaşılamaz bağlantı sayısı
        
        for i in range(len(candidates)):
            if pulp.value(shop_vars[i]) == 1:
                shop = candidates[i]
                shop_info = candidate_data.get(shop.name, {})
                connected = []
                for j in range(len(demands)):
                    if pulp.value(link_vars[i, j]) == 1:
                        d = demands[j]
                        d_info = demand_data.get(d.name, {})
                        dist = distance_matrix[i][j]
                        
                        # 9999 km (ulaşılamaz) değerleri filtrele
                        if dist >= 9999:
                            unreachable_count += 1
                            continue  # Bu bağlantıyı atla
                        
                        connected.append({
                            "name": d.name,
                            "address": d_info.get("address", ""),
                            "lat": d.y,
                            "lng": d.x,
                            "distance": round(dist, 2)
                        })
                selected_shops.append({
                    "name": shop.name,
                    "address": shop_info.get("address", ""),
                    "lat": shop.y,
                    "lng": shop.x,
                    "connected_points": connected
                })
        
        total_distance = pulp.value(mdl.objective)
        
        response_data = {
            "success": True,
            "total_distance_km": round(total_distance, 2),
            "selected_shops": selected_shops,
            "num_demand_points": len(demands),
            "num_candidates": len(candidates),
            "distance_type": "real_road"  # Gerçek yol mesafesi kullanıldı
        }
        
        # Ulaşılamaz nokta uyarısı ekle
        if unreachable_count > 0:
            response_data["warning"] = f"{unreachable_count} adet bağlantı için rota bulunamadı (farklı kara parçaları veya yol yok)."
        
        return jsonify(response_data)
        
    except Exception as e:
        import traceback
        return jsonify({
            "error": str(e),
            "traceback": traceback.format_exc()
        }), 500


def fetch_distance_matrix(origins, destinations):
    """
    Google Maps Distance Matrix API ile gerçek yol mesafelerini hesapla.
    Returns: 2D liste [origin_idx][dest_idx] = mesafe (km)
    """
    n_origins = len(origins)
    n_dests = len(destinations)
    
    # Sonuç matrisi
    matrix = [[0.0 for _ in range(n_dests)] for _ in range(n_origins)]
    
    # API limiti: 25 origin x 25 destination per request
    # Chunk'lara böl
    CHUNK_SIZE = 10
    
    for origin_start in range(0, n_origins, CHUNK_SIZE):
        origin_end = min(origin_start + CHUNK_SIZE, n_origins)
        origin_chunk = origins[origin_start:origin_end]
        
        for dest_start in range(0, n_dests, CHUNK_SIZE):
            dest_end = min(dest_start + CHUNK_SIZE, n_dests)
            dest_chunk = destinations[dest_start:dest_end]
            
            # API isteği
            origins_str = "|".join([f"{o.y},{o.x}" for o in origin_chunk])
            dests_str = "|".join([f"{d.y},{d.x}" for d in dest_chunk])
            
            url = "https://maps.googleapis.com/maps/api/distancematrix/json"
            params = {
                "origins": origins_str,
                "destinations": dests_str,
                "mode": "driving",
                "key": GOOGLE_API_KEY
            }
            
            try:
                response = requests.get(url, params=params, timeout=30)
                data = response.json()
                
                if data.get("status") != "OK":
                    status = data.get("status")
                    error_messages = {
                        "OVER_QUERY_LIMIT": "Google Maps API kotası aşıldı. Lütfen daha sonra tekrar deneyin.",
                        "REQUEST_DENIED": "API erişimi reddedildi. API key'inizi kontrol edin.",
                        "INVALID_REQUEST": "Geçersiz koordinatlar veya parametreler.",
                        "ZERO_RESULTS": "Konumlar arasında rota bulunamadı.",
                        "UNKNOWN_ERROR": "Google Maps servisi geçici olarak kullanılamıyor."
                    }
                    error_msg = error_messages.get(status, f"API Hatası: {status}")
                    print(f"Distance Matrix API Hatası: {status} - {error_msg}")
                    return None
                
                # Sonuçları matrise yerleştir
                for i, row in enumerate(data.get("rows", [])):
                    for j, element in enumerate(row.get("elements", [])):
                        if element.get("status") == "OK":
                            # Metre → Kilometre
                            distance_km = element["distance"]["value"] / 1000.0
                            matrix[origin_start + i][dest_start + j] = distance_km
                        else:
                            # Ulaşılamıyorsa çok büyük değer (ceza)
                            matrix[origin_start + i][dest_start + j] = 99999.0
                            
            except Exception as e:
                print(f"Distance Matrix hatası: {e}")
                return None
    
    return matrix



if __name__ == "__main__":
    print("=" * 50)
    print(" Optimal Konum Planlayıcı")
    print("=" * 50)
    print(f"Sunucu başlatılıyor: http://localhost:5000")
    print(f"API Key: {'Yüklendi' if GOOGLE_API_KEY else 'BULUNAMADI!'}")
    print("=" * 50)
    app.run(debug=True, port=5000)
