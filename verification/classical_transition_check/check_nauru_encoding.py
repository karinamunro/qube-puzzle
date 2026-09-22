"""Check both existing r,u,f implementations on all 24 classical states.

Run from this directory:
    .venv\Scripts\python.exe check_nauru_encoding.py
    .venv\Scripts\python.exe check_nauru_encoding.py --verbose --csv transitions.csv

Requires numpy, sympy, pennylane and networkx (available in the project venv).
Expected labelled transitions come from the classical rules in main.tex,
tab:summary_op_encoding and eq. d_operator_g, independently of the matrices.
An additional unlabelled isomorphism check uses the Nauru graph G(12,5).
This verifies those rules and graph structure, not an independent physical
sticker/corner model of the cube. There are 72 directed transitions per
encoding, or 36 undirected edges. Matrix columns are input basis states.
"""

import argparse
import csv
from itertools import product
from pathlib import Path

import networkx as nx
import numpy as np


STATES = tuple(product(range(2), range(2), range(3), range(2)))
MOVES = ('r', 'u', 'f')
Y_BITS = ('00', '10', '11')
ATOL = 1e-12


def label(state):
    return ''.join(map(str, state))


def qubit_label(state):
    w, x, y, z = state
    return f'{w}{x}{Y_BITS[y]}{z}'


def classical_move(state, move):
    """Independent scalar rules; operator products act right to left."""
    w, x, y, z = state
    if move == 'r':
        return w, x, y, 1-z
    if move == 'u':  # a b
        return w, x, (y + (-1)**z) % 3, 1-z
    if move == 'f':  # b a d
        g = 1 + (y + z - 1) % 3
        return w ^ int(g in (1, 2)), x ^ int(g in (1, 3)), (y - (-1)**z) % 3, 1-z
    raise ValueError(move)


def nauru_graph():
    """Generalized Petersen graph G(12,5), with independent numbering."""
    graph = nx.Graph()
    for i in range(12):
        graph.add_edges_from(((i, (i+1) % 12), (i, i+12),
                              (i+12, (i+5) % 12 + 12)))
    return graph


def check_encoding(name, matrices, verbose=False):
    size = 24 if name == 'qudit' else 32
    indices = list(range(24)) if size == 24 else [int(qubit_label(s), 2) for s in STATES]
    unused = sorted(set(range(size)) - set(indices))
    lookup = {state: i for state, i in zip(STATES, indices)}
    graph = nx.Graph()
    graph.add_nodes_from(STATES)
    errors, rows = [], []
    passed = 0
    restricted = []
    for move, matrix in zip(MOVES, matrices):
        matrix = np.asarray(matrix, dtype=complex)
        if matrix.shape != (size, size) or not np.isfinite(matrix).all():
            raise ValueError(f'{name}/{move}: invalid matrix shape or nonfinite entries')
        if not np.allclose(matrix.conj().T @ matrix, np.eye(size), atol=ATOL, rtol=0):
            errors.append(f'{name}/{move}: matrix is not unitary')
        block = matrix[np.ix_(indices, indices)]
        restricted.append(block)
        if not np.allclose(block @ block, np.eye(24), atol=ATOL, rtol=0):
            errors.append(f'{name}/{move}: not an involution on classical subspace')
        for state in STATES:
            expected = classical_move(state, move)
            column = matrix[:, lookup[state]]
            target = np.zeros(size, dtype=complex)
            target[lookup[expected]] = 1
            error = float(np.max(np.abs(column-target)))
            leakage = float(np.sum(np.abs(column[unused])**2))
            ok = error <= ATOL
            passed += int(ok)
            support = np.flatnonzero(np.abs(column) > ATOL)
            actual = int(support[0]) if len(support) == 1 else None
            if actual in indices:
                graph.add_edge(state, STATES[indices.index(actual)])
            if not ok:
                errors.append(f'{name}/{move} |{label(state)}> -> expected |{label(expected)}>: '
                              f'max error={error:.3g}, leakage={leakage:.3g}')
            row = dict(encoding=name, source=label(state), generator=move,
                       expected=label(expected), source_index=lookup[state],
                       expected_index=lookup[expected], actual_index=actual,
                       source_bits=qubit_label(state) if size == 32 else '',
                       expected_bits=qubit_label(expected) if size == 32 else '',
                       max_amplitude_error=error, leakage_probability=leakage, passed=ok)
            rows.append(row)
            if verbose:
                print(f"{name:5} {label(state)} --{move}--> {label(expected)} "
                      f"{'PASS' if ok else 'FAIL'}")
    graph_ok = (graph.number_of_edges() == 36 and
                all(degree == 3 for _, degree in graph.degree()) and
                nx.is_connected(graph) and nx.is_isomorphic(graph, nauru_graph()))
    if not graph_ok:
        errors.append(f'{name}: actual transition graph is not the Nauru graph')
    print(f'{name}: {passed}/72 transitions correct; '
          f'Nauru graph: {"PASS" if graph_ok else "FAIL"}; '
          f'max leakage probability: {max(row["leakage_probability"] for row in rows):.3g}')
    return errors, rows, restricted


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--encoding', choices=('both', 'qudit', 'qubit'), default='both')
    parser.add_argument('--verbose', action='store_true', help='Print every transition')
    parser.add_argument('--csv', type=Path, help='Write all transition results to this CSV')
    args = parser.parse_args()
    errors, rows, blocks = [], [], {}
    for name in ('qudit', 'qubit'):
        if args.encoding not in ('both', name):
            continue
        try:
            if name == 'qudit':
                from perm_matrices_MQT import perm_matrix
            else:
                from perm_matrices import perm_matrix
            matrices = perm_matrix()
            if len(matrices) != 3:
                raise ValueError('Expected exactly three matrices: r, u, f')
            failures, results, blocks[name] = check_encoding(name, matrices, args.verbose)
            errors.extend(failures)
            rows.extend(results)
        except Exception as exc:
            errors.append(f'{name}: {type(exc).__name__}: {exc}')
    if len(blocks) == 2:
        agree = all(np.allclose(a, b, atol=ATOL, rtol=0)
                    for a, b in zip(blocks['qudit'], blocks['qubit']))
        print(f'Qudit/qubit restricted matrices agree: {"PASS" if agree else "FAIL"}')
        if not agree:
            errors.append('Encodings disagree on the classical subspace')
    if args.csv and rows:
        with args.csv.open('w', newline='', encoding='utf-8') as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f'Transition report: {args.csv.resolve()}')
    for error in errors:
        print(f'FAIL: {error}')
    print('FAIL' if errors else 'PASS: all requested encodings verified.')
    return 1 if errors else 0


if __name__ == '__main__':
    raise SystemExit(main())
