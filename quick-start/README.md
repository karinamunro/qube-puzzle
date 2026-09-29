# Quick Start — Windows

Choose the executable for the encoding you want:

| Download | Encoding | Approximate size |
| --- | --- | --- |
| [qubits_qube_puzzle.exe](qubits_qube_puzzle.exe) | Qubits, using PennyLane | 95 MB |
| [qudits_qube_puzzle.exe](qudits_qube_puzzle.exe) | Qudits, using MQT | 86 MB |

## Start the game

1. Open the file link above and select **Download raw file** on GitHub. If you downloaded the whole repository as a ZIP, extract it first and open the `quick-start` folder.
2. Double-click the chosen `.exe` on Windows. Allow time for the packaged program to unpack and start.
3. Press **Scramble** to begin. Use classical and quantum moves to change the state, and **Measure** to try to solve the puzzle.
4. Open **Help → Keyboard Shortcuts** for the controls.

Each executable bundles Python, libraries, and game images. No separate Python or Conda installation is needed, and the source folders do not need to be alongside the executable.

## Playing

To start the game, press the **Scramble** button. The aim of the game is to **Measure** the Qube and collapse the state to the solved state marked by the star ⭐. To increase your chances of solving the Qube, combine the amplitudes by using quantum **R2**, **U2**, and **F2** moves dictated by the **step size** (the sliding bar). Use the classical **R2**, **U2**, and **F2** moves to move the locations of basis states without changing the amplitudes.

Note: Click **Help**&#8594;**Keyboard Shortcuts** for shortcuts on all the functionalities.

The qudit version also retains the supplied MQT program's warning when a measurement cannot be completed.

## Interface guide

The screenshots below show the qubit version to illustrate the shared controls and layout. The qudit version uses four-digit basis-state labels (for example, `0000` and `1121`) for its 2 × 2 × 3 × 2 encoding, instead of the five-bit labels shown in these screenshots.

<img src="../qubit-encoding/docs/pennylane_instructions.png" alt="Game controls illustrated using the qubit interface" width="60%">

## Example screens

### Windows

Initial and scrambled views of the shared game interface:

<img src="../qubit-encoding/docs/pennylane_initial.png" alt="Initial game view, shown in the qubit version on Windows" width="45.2%"> <img src="../qubit-encoding/docs/pennylane_random.png" alt="Scrambled game view, shown in the qubit version on Windows" width="44.7%">

## Other operating systems and source code

These `.exe` files are Windows applications. For macOS or Linux, use the [qubit source instructions](../qubit-encoding/README.md) or [qudit source instructions](../qudit-encoding/README.md).

## Build and verification notes

The executables are separately packaged builds; editing the Python source or images in this repository does not update them. Rebuild an executable to include source changes.
