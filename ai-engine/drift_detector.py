import json

with open("intent.json") as f:
    intent = json.load(f)

with open("runtime_events.json") as f:
    runtime = json.load(f)

allowed = {(x["from"], x["to"]) for x in intent["allowed_flows"]}
observed = {(x["from"], x["to"]) for x in runtime["observed_flows"]}

print("🔍 Checking for policy drift...\n")

for flow in observed:
    if flow not in allowed:
        print(f"🚨 DRIFT DETECTED: {flow[0]} → {flow[1]}")
    else:
        print(f"✅ Allowed: {flow[0]} → {flow[1]}")
