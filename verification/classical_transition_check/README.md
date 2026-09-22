# Classical transition verification

Checks the qudit and qubit implementations of r, u, and f against the classical transition rules for all 24 states. Each encoding has 72 directed transitions. It also checks unitarity, involutions on the classical subspace, Nauru graph structure, and agreement between the two encodings.

Run from this folder with Python 3:

```bash
python -m pip install -r requirements.txt
python check_nauru_encoding.py
```

To print individual checks and save the transitions:

```bash
python check_nauru_encoding.py --verbose --csv transitions.csv
```

Use `--encoding qudit` or `--encoding qubit` to check one encoding. The default checks both. Exit status is 0 for success and 1 for failed checks.

- `check_nauru_encoding.py`: verification and optional CSV output.
- `perm_matrices_MQT.py`: qudit permutation matrices.
- `perm_matrices.py`: qubit permutation matrices.
- `requirements.txt`: Python dependencies.

Keep the three Python files together. No GUI or universality scripts are required. The reference to `main.tex` documents the source of the classical rules; that file is not read at runtime. This verifies the encoded rules and graph structure, not an independent physical sticker/corner model.
