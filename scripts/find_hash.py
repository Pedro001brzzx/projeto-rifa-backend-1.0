
import hashlib
import json

target_hash_compact = "301ed40a9cda6e64" # From server when sending compact
target_hash_spaced = "4dfe0d8e803c7220" # From server when sending spaced (partial)

payload = {
    "event": "billing.paid",
    "data": {
        "billing": {
            "id": f"bill_simulated_11",
            "status": "PAID",
            "products": [
                {
                    "externalId": "11",
                    "name": "Rifa Teste"
                }
            ]
        }
    }
}

candidates = []
candidates.append(json.dumps(payload, separators=(',', ':')).encode('utf-8')) # Compact
candidates.append(json.dumps(payload).encode('utf-8')) # Spaced
candidates.append((json.dumps(payload, separators=(',', ':')) + '\n').encode('utf-8')) # Compact + \n
candidates.append((json.dumps(payload) + '\n').encode('utf-8')) # Spaced + \n

for i, c in enumerate(candidates):
    h = hashlib.sha256(c).hexdigest()
    if h == target_hash_compact:
        print(f"MATCH_COMPACT_INDEX_{i}")
    if h == target_hash_spaced:
        print(f"MATCH_SPACED_INDEX_{i}")
    print(f"{i}:{h}")
