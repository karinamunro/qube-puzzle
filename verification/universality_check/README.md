# Universality algebra checks

Requires Python 3.10 or newer and only the Python standard library. Keep the three scripts together; no installation or requirements.txt is needed.

Run from this folder:

```bash
python universality.py --output universality_commutators.txt
python universality_analysis.py --output universality_analysis.txt
python universality_table.py
```

- `universality.py` enumerates commutators and expresses dependent results using earlier independent As. Its command-line interface permits at most three rounds.
- `universality_analysis.py` uses three rounds to count proportionality classes, supports and real linear dimension, then checks closure under all independent basis-pair commutators.
- `universality_table.py` generates `universality_table.html` and `universality_table.csv` beside itself. It renumbers the independent As consecutively from 1 to 12; the HTML includes the mapping to the original labels.

The analysis finds real dimension 12 and verifies closure under the implemented appendix relations. It treats the 24 group elements as independent formal coordinates, so the result is exact for the regular representation. Other matrix representations may introduce further dependencies. These scripts report the generated algebra; they do not by themselves establish universality for an unspecified target space.

The checked-in HTML and CSV can be regenerated with the table command. No personal directory paths or external data files are required.

## Tests

Run the included regression tests from this folder:

```bash
python -m unittest discover -s . -p "test_*.py"
```

They check word reduction against an independent permutation representation, exact decompositions, dimension and closure, and reconstruction and antisymmetry of every table entry.
