python --version
python -m unittest -v
python -c "import hashlib; from pathlib import Path; \
files = ['spec.json', 'atlas.py', 'test_atlas.py']; \
[(print(f, hashlib.sha256(Path(f).read_bytes()).hexdigest())) \
 for f in files]"
