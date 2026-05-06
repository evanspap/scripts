# Extract Column By Header

Μικρό Python script που διαβάζει ένα CSV ή TSV αρχείο και τυπώνει στο standard output
τη στήλη που αντιστοιχεί σε ένα συγκεκριμένο header.

## Εγκατάσταση

```bash
pip install -r requirements.txt
```

## Χρήση

```bash
python3 column_by_header.py input.csv header_name
```

Για TSV:

```bash
python3 column_by_header.py input.tsv header_name
```

Για custom separator:

```bash
python3 column_by_header.py input.txt header_name --separator ';'
```
