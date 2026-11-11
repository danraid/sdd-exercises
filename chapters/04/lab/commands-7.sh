python -c "import hashlib,pathlib; [(print(p, hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest())) for p in ('spec.json','atlas.py','test_atlas.py','validate.py')]"
