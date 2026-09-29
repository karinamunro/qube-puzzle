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

## Reference rules and scope

The expected transitions are calculated by `classical_move()` in [check_nauru_encoding.py](check_nauru_encoding.py). It contains explicit update rules for the state labels `(w, x, y, z)`, where `w`, `x`, and `z` are binary and `y` is ternary. These implement the classical move rules in **Table I** of the accompanying Qube Puzzle paper, with the group number `g` defined in **Eq. (20)** and the conditional action of `d` given in **Eq. (22)**. The rules are evaluated separately from the qubit and qudit permutation matrices being checked.

All rules needed to run the check are included in this folder. Keep the three Python files together and install the listed dependencies; the paper's source files and the game GUI are not required.

The checks establish agreement with the encoded classical rules and the Nauru graph structure. They do not provide an independent physical sticker/corner model of the cube.
