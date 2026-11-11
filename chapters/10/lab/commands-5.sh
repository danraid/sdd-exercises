python --version > environment.txt 2>&1
python -m unittest -v > run-record.txt 2>&1
status=$?
printf 'test exit status: %s\n' "$status" >> run-record.txt
cat run-record.txt
sha256sum spec.json atlas.py test_atlas.py > input-hashes.txt
cat input-hashes.txt
