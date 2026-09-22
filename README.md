# The Qube Puzzle

Welcome!

Code for Karina Munro's 2025 Honours thesis at RMIT University and 2026 research paper (TBA).


Contact:
- Karina Munro
- karina.munro@rmit.edu.au

## Repository contents

| Folder | Contents | Status |
| --- | --- | --- |
| [Qubit encoding](qubit-encoding/) | PennyLane qubit program, dependencies, images, and instructions | Available |
| [Qudit encoding](qudit-encoding/) | MQT qudit program, dependencies, images, and instructions | Available |
| [Quick start](quick-start/) | Windows executables for both encodings | Available |
| [Classical transition checks](verification/classical_transition_check/) | Verify both encodings against the 24-state classical rules and Nauru graph | Available |
| [Universality algebra checks](verification/universality_check/) | Exact commutator decompositions, dimension, closure, and tables | Available |

## Quick start on Windows

Download one of the executables from [quick-start](quick-start/):

- [Qubit version](quick-start/qubits_qube_puzzle.exe) — PennyLane encoding.
- [Qudit version](quick-start/qudits_qube_puzzle.exe) — MQT encoding.

On the file's GitHub page, choose **Download raw file**, then double-click the downloaded `.exe`. These packages bundle Python and the game images; you do not need to install Python or Conda separately. See the [quick-start instructions](quick-start/README.md) for details.

## Run from source

For macOS, Linux, or working with the Python code, follow the [qubit instructions](qubit-encoding/README.md) or [qudit instructions](qudit-encoding/README.md). Each version has its own dependencies and image folder. The `.exe` downloads are Windows applications.

## Reproduce the verification results

The verification scripts run separately from the games and do not need the GUI or image files.

### Classical transitions

From the repository root:

```bash
python -m pip install -r verification/classical_transition_check/requirements.txt
python verification/classical_transition_check/check_nauru_encoding.py
```

A successful run reports 72/72 transitions for each encoding, passing Nauru graph checks, and agreement between the restricted qudit and qubit matrices. See the [classical transition README](verification/classical_transition_check/README.md) for individual checks and CSV output.

### Commutator algebra

Requires Python 3.10 or newer; no third-party packages are needed. From the repository root:

```bash
python verification/universality_check/universality_analysis.py
python verification/universality_check/universality_table.py
python -m unittest discover -s verification/universality_check -p "test_*.py"
```

The analysis finds 12 real linearly independent generators and verifies closure under the implemented appendix relations in the formal group algebra. The [universality README](verification/universality_check/README.md) explains the assumptions, exact decompositions, and output commands. The table uses consecutive basis labels and includes a mapping to the original enumeration.

View the [CSV table](verification/universality_check/universality_table.csv) on GitHub, or download the [HTML table](verification/universality_check/universality_table.html) and open it in a browser for formatted mathematics.

## Playing

Press **Scramble** to begin. Use classical and quantum **R2**, **U2**, and **F2** moves, adjust the quantum step size, then **Measure** to try to reach the solved state marked by the star. Open **Help → Keyboard Shortcuts** for controls.

The repository-wide license is in [LICENSE](LICENSE).
