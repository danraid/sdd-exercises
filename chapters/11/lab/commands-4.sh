python -c "import hashlib; from pathlib import Path; \
[(print(p, hashlib.sha256(Path(p).read_bytes()).hexdigest())) \
for p in ('spec.json', 'test_delivery.py')]"
