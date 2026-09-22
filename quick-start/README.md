# Quick Start — Windows

Choose the executable for the encoding you want:

| Download | Encoding | Approximate size |
| --- | --- | --- |
| [qubits_qube_puzzle.exe](qubits_qube_puzzle.exe) | Qubits, using PennyLane | 77 MB |
| [qudits_qube_puzzle.exe](qudits_qube_puzzle.exe) | Qudits, using MQT | 90 MB |

## Start the game

1. Open the file link above and select **Download raw file** on GitHub. If you downloaded the whole repository as a ZIP, extract it first and open the `quick-start` folder.
2. Double-click the chosen `.exe` on Windows. Allow time for the packaged program to unpack and start.
3. Press **Scramble** to begin. Use classical and quantum moves to change the state, and **Measure** to try to solve the puzzle.
4. Open **Help → Keyboard Shortcuts** for the controls.

Each executable bundles Python, libraries, and game images. No separate Python or Conda installation is needed, and the source folders do not need to be alongside the executable.

## Other operating systems and source code

These `.exe` files are Windows applications. For macOS or Linux, use the [qubit source instructions](../qubit-encoding/README.md) or [qudit source instructions](../qudit-encoding/README.md).

## Build and verification notes

The executables are separately packaged builds; editing the Python source or images in this repository does not update them. Rebuild an executable to include source changes.

The source image filenames and references are lowercase. The supplied executables still contain older bundled image names, including uppercase `.PNG` extensions; those packaged assets have not been renamed.

The source versions passed startup and image-path checks on Windows during the 22 September 2026 review, and the qudit circuit checks covered reset, moves and inverses, fractional moves, and measurement. Both executable packages contain Python and game images, but their interactive launch and gameplay have not been fully verified in this review.
