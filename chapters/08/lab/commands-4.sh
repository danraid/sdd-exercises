sha256sum spec.json atlas_lab.py > run-record.txt
python -VV >> run-record.txt 2>&1
python -m unittest -v atlas_lab >> run-record.txt 2>&1
status=$?
echo "test exit status: $status" >> run-record.txt
sha256sum spec.json atlas_lab.py >> run-record.txt
cat run-record.txt
