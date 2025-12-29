"""
BRUTE FORCE TESTİ
=================
25 aday, 50 talep, 10 seçim
C(25,10) = 3,268,760 kombinasyon

Bu scripti MILP scripti ile aynı anda çalıştırın!
"""

from itertools import combinations
import time
import json
import os

# Veri dosyasını yükle
DATA_FILE = "race_data.json"

if not os.path.exists(DATA_FILE):
    print(f"HATA: '{DATA_FILE}' bulunamadı!")
    print("Lütfen önce 'python race_data_gen.py' çalıştırın.")
    exit(1)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

NUM_CANDIDATES = data["num_candidates"]
NUM_DEMANDS = data["num_demands"]
NUM_SHOPS = data["num_shops"]
distance_matrix = data["distance_matrix"]

print(f"Veri Yüklendi: {DATA_FILE}")

print("=" * 60)
print("BRUTE FORCE TESTİ BAŞLADI")
print("=" * 60)
print(f"Kombinasyon: C(25,10) = 3,268,760")
print(f"Başlangıç: {time.strftime('%H:%M:%S')}")
print("=" * 60)

start_time = time.perf_counter()

best_total = float('inf')
best_combo = None
checked = 0
last_print = 0

for combo in combinations(range(NUM_CANDIDATES), NUM_SHOPS):
    total = sum(min(distance_matrix[i][j] for i in combo) for j in range(NUM_DEMANDS))
    checked += 1
    
    if total < best_total:
        best_total = total
        best_combo = combo
    
    # Her 100,000 kombinasyonda durum yazdır
    elapsed = time.perf_counter() - start_time
    if checked - last_print >= 100000:
        progress = (checked / 3268760) * 100
        remaining = (elapsed / checked) * (3268760 - checked)
        print(f"   [{time.strftime('%H:%M:%S')}] {checked:,} / 3,268,760 ({progress:.1f}%) - Kalan: {remaining:.0f} sn")
        last_print = checked

elapsed = time.perf_counter() - start_time

print("\n" + "=" * 60)
print("BRUTE FORCE TAMAMLANDI!")
print("=" * 60)
print(f"Seçilen: Aday-{', Aday-'.join(str(i+1) for i in best_combo)}")
print(f"Toplam mesafe: {best_total:.2f} km")
print(f"Süre: {elapsed:.2f} saniye")
print(f"Bitiş: {time.strftime('%H:%M:%S')}")
