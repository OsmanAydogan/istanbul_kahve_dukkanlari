import json
import random
import os

def generate_race_data():
    print("Veri üretiliyor...")
    
    # Parametreler
    NUM_CANDIDATES = 25
    NUM_DEMANDS = 50
    NUM_SHOPS = 10
    SEED = 12345
    
    random.seed(SEED)
    
    # Mesafe matrisi
    distance_matrix = [
        [round(random.uniform(1, 20), 1) for _ in range(NUM_DEMANDS)]
        for _ in range(NUM_CANDIDATES)
    ]
    
    data = {
        "num_candidates": NUM_CANDIDATES,
        "num_demands": NUM_DEMANDS,
        "num_shops": NUM_SHOPS,
        "distance_matrix": distance_matrix,
        "seed": SEED
    }
    
    output_file = "race_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
        
    print(f"Veri kaydedildi: {os.path.abspath(output_file)}")
    print(f"Aday Sayısı: {NUM_CANDIDATES}")
    print(f"Talep Noktası: {NUM_DEMANDS}")
    print(f"Seçilecek Mağaza: {NUM_SHOPS}")

if __name__ == "__main__":
    generate_race_data()
