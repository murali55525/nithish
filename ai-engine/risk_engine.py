import json
from collections import defaultdict

with open("service_weights.json") as f:
    weights = json.load(f)

with open("drift_output.json") as f:
    drift = json.load(f)

risk = defaultdict(int)

# Base risk
for service, base in weights.items():
    risk[service] += base

# Add drift penalties
for v in drift["violations"]:
    risk[v["from"]] += 20
    risk[v["to"]] += 30

print("\n📊 SERVICE RISK SCORES\n")

for service, score in risk.items():
    final = min(score, 100)
    level = "LOW" if final < 30 else "MEDIUM" if final < 70 else "HIGH"
    print(f"{service.upper():10} → {final:3} ({level})")
