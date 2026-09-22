# The Qube Puzzle

Welcome!

Code for Karina Munro's 2025 Honours thesis at RMIT University and 2026 research paper (TBA).


Contact:
- Karina Munro
- karina.munro@rmit.edu.au

## Choose a version

| Folder | Contents | Status |
| --- | --- | --- |
| [Qubit encoding](qubit-encoding/) | PennyLane qubit program, dependencies, images, and instructions | Available |
| [Qudit encoding](qudit-encoding/) | MQT qudit program, dependencies, images, and instructions | Available |
| [Quick start](quick-start/) | Windows executables for both encodings | Available |

## Quick start on Windows

Download one of the executables from [quick-start](quick-start/):

- [Qubit version](quick-start/qubits_qube_puzzle.exe) — PennyLane encoding.
- [Qudit version](quick-start/qudits_qube_puzzle.exe) — MQT encoding.

On the file's GitHub page, choose **Download raw file**, then double-click the downloaded `.exe`. These packages bundle Python and the game images; you do not need to install Python or Conda separately. See the [quick-start instructions](quick-start/README.md) for details.

## Run from source

For macOS, Linux, or working with the Python code, follow the [qubit instructions](qubit-encoding/README.md) or [qudit instructions](qudit-encoding/README.md). Each version has its own dependencies and image folder. The `.exe` downloads are Windows applications.

## Playing

Press **Scramble** to begin. Use classical and quantum **R2**, **U2**, and **F2** moves, adjust the quantum step size, then **Measure** to try to reach the solved state marked by the star. Open **Help → Keyboard Shortcuts** for controls.

The repository-wide license is in [LICENSE](LICENSE).
