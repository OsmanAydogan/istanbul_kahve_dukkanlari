"""
MILP TESTİ
==========
25 aday, 50 talep, 10 seçim
C(25,10) = 3,268,760 kombinasyon (ama MILP hepsini denemez!)

Bu scripti BRUTE FORCE scripti ile aynı anda çalıştırın!
"""

import pulp
import time
import json
import os

# Veri dosyasını yükle
DATA_FILE = "race_data.json"

if not os.path.exists(DATA_FILE):
    print(f"HATA: '{DATA_FILE}' bulunamadı!")
    print("   Lütfen önce 'python race_data_gen.py' çalıştırın.")
    exit(1)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

NUM_CANDIDATES = data["num_candidates"]
NUM_DEMANDS = data["num_demands"]
NUM_SHOPS = data["num_shops"]
distance_matrix = data["distance_matrix"]

print(f"Veri Yüklendi: {DATA_FILE}")

print("=" * 60)
print("MILP TESTİ BAŞLADI")
print("=" * 60)
print(f"Kombinasyon: C(25,10) = 3,268,760")
print(f"Başlangıç: {time.strftime('%H:%M:%S')}")
print("=" * 60)

start_time = time.perf_counter()

# Model oluştur
print(f"\n   [{time.strftime('%H:%M:%S')}] Model oluşturuluyor...")
mdl = pulp.LpProblem("race_test", pulp.LpMinimize)

shop_vars = pulp.LpVariable.dicts("shop", range(NUM_CANDIDATES), cat="Binary")
link_vars = {
    (i, j): pulp.LpVariable(f"link_{i}_{j}", cat="Binary")
    for i in range(NUM_CANDIDATES)
    for j in range(NUM_DEMANDS)
}

print(f"   [{time.strftime('%H:%M:%S')}] Kısıtlar ekleniyor...")

for j in range(NUM_DEMANDS):
    mdl += pulp.lpSum(link_vars[i, j] for i in range(NUM_CANDIDATES)) == 1

for i in range(NUM_CANDIDATES):
    for j in range(NUM_DEMANDS):
        mdl += link_vars[i, j] <= shop_vars[i]

mdl += pulp.lpSum(shop_vars[i] for i in range(NUM_CANDIDATES)) == NUM_SHOPS

mdl += pulp.lpSum(
    link_vars[i, j] * distance_matrix[i][j]
    for i in range(NUM_CANDIDATES)
    for j in range(NUM_DEMANDS)
)

print(f"   [{time.strftime('%H:%M:%S')}] Çözülüyor...")
mdl.solve(pulp.PULP_CBC_CMD(msg=0))

elapsed = time.perf_counter() - start_time

selected = [i for i in range(NUM_CANDIDATES) if pulp.value(shop_vars[i]) == 1]
total_distance = pulp.value(mdl.objective)

print("\n" + "=" * 60)
print("MILP TAMAMLANDI!")
print("=" * 60)
print(f"Seçilen: Aday-{', Aday-'.join(str(i+1) for i in selected)}")
print(f"Toplam mesafe: {total_distance:.2f} km")
print(f"Süre: {elapsed:.2f} saniye")
print(f"Bitiş: {time.strftime('%H:%M:%S')}")
print("\n Şimdi Brute Force'un bitip bitmediğine bakın!")
