import json
import yaml

with open("intent.json") as f:
    intent = json.load(f)

namespace = intent["namespace"]

policies = []

for rule in intent["communication"]:
    policy = {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "NetworkPolicy",
        "metadata": {
            "name": f"{rule['from']}-to-{rule['to']}",
            "namespace": namespace
        },
        "spec": {
            "podSelector": {
                "matchLabels": { "app": rule["to"] }
            },
            "policyTypes": ["Ingress"],
            "ingress": [{
                "from": [{
                    "podSelector": {
                        "matchLabels": { "app": rule["from"] }
                    }
                }],
                "ports": [{
                    "protocol": "TCP",
                    "port": rule["port"]
                }]
            }]
        }
    }
    policies.append(policy)

with open("generated-policies.yaml", "w") as f:
    yaml.dump_all(policies, f)

print("✅ AI generated NetworkPolicies")
