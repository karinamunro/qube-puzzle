"""Separate exact analysis; leaves universality_commutators.txt unchanged.

Run: python universality_analysis.py
     python universality_analysis.py --output universality_analysis.txt

Counts nonzero expressions three ways: proportionality, support (ignoring
all nonzero coefficients), and real linear independence. Rank uses the
formal group algebra of the 24 canonical moves, with separate real and
imaginary coordinates. No floating-point tolerance or extra dependencies.
"""

import argparse
from fractions import Fraction
from itertools import combinations
from pathlib import Path

import universality as u


def real_coordinates(expression):
    # Each expression is (-i*pi/2)**degree times an integer polynomial.
    # Discard its nonzero REAL scalar, but retain whether its phase is real
    # or imaginary. This preserves rank over R, the Lie-algebra base field.
    return {(expression.degree % 2, word): Fraction(value)
            for word, value in expression.terms.items() if value}


class ExactSpan:
    """Incremental Gaussian elimination using exact rational arithmetic."""

    def __init__(self):
        self.pivots = {}

    def remainder(self, coordinates):
        row = dict(coordinates)
        for pivot, basis_row in self.pivots.items():
            scale = row.get(pivot, 0)
            if not scale:
                continue
            for key, value in basis_row.items():
                updated = row.get(key, 0) - scale * value
                if updated:
                    row[key] = updated
                else:
                    row.pop(key, None)
        return row

    def add(self, expression):
        row = self.remainder(real_coordinates(expression))
        if not row:
            return False
        pivot = min(row)
        scale = row[pivot]
        self.pivots[pivot] = {key: value / scale for key, value in row.items()}
        return True


def analyse(expressions):
    span = ExactSpan()
    basis = []
    proportional_groups = []
    support_groups = {}
    zero_labels = []
    ranks = {}
    for expression in expressions:
        if not expression.terms:
            zero_labels.append(expression.index)
        else:
            representatives = [group[0] for group in proportional_groups]
            match = u.find_proportional(expression, representatives)
            if match:
                group = next(group for group in proportional_groups if group[0] is match[0])
                group.append(expression)
            else:
                proportional_groups.append([expression])
            support_groups.setdefault(frozenset(expression.terms), []).append(expression)
        if span.add(expression):
            basis.append(expression)
        ranks[expression.level] = len(basis)

    # A basis whose every pairwise bracket lies in its span is closed.
    # Since it contains the initial generators and consists of their Lie
    # words, closure certifies that later rounds cannot increase the rank.
    outside_span = []
    for left, right in combinations(basis, 2):
        bracket = u.Expression(0, u.commutator(left.terms, right.terms),
                               left.degree + right.degree)
        if span.remainder(real_coordinates(bracket)):
            outside_span.append((left.index, right.index))
    return {
        'basis': basis,
        'ranks': ranks,
        'proportional_groups': proportional_groups,
        'support_groups': list(support_groups.values()),
        'zero_labels': zero_labels,
        'outside_span': outside_span,
    }


def labels(expressions):
    return ', '.join(f'A_{expression.index}' for expression in expressions)


def make_report(expressions, result):
    basis = result['basis']
    lines = [
        'SEPARATE UNIQUENESS AND LINEAR-INDEPENDENCE ANALYSIS',
        'Input: the original three generators plus three rounds of commutators.',
        f'Total A labels: {len(expressions)} (including zero results).',
        'Zero expressions are excluded from all uniqueness counts.',
        '',
        f"Distinct up to an overall nonzero factor: {len(result['proportional_groups'])}",
        f"Distinct supports, ignoring relative coefficients too: {len(result['support_groups'])}",
        f'Real linear dimension: {len(basis)}',
        '',
        'Ignoring relative coefficients counts sets of terms only; it does not',
        'test operator equivalence or Lie-algebra dimension. For example,',
        'r+u and r-u have the same support but are not proportional.',
        '',
        'Cumulative real dimension (including A_1, A_2, A_3):',
    ]
    for level, rank in result['ranks'].items():
        title = 'Initial generators' if level == 0 else f'After round {level}'
        lines.append(f'  {title}: {rank}')
    lines.extend(['', 'Earliest independent A labels:', labels(basis), ''])
    pairs = len(basis) * (len(basis) - 1) // 2
    if not result['outside_span']:
        lines.extend([
            f'Closure verified: all {pairs} distinct basis-pair commutators lie in this span.',
            f'Further rounds cannot increase the dimension beyond {len(basis)} under these relations.',
        ])
    else:
        lines.append(f"Not closed: {len(result['outside_span'])} basis-pair brackets lie outside the span.")
    lines.extend([
        '',
        'Method: exact rational elimination; retain relative coefficients and',
        'separate real/imaginary coordinates, discarding only overall real scales.',
        'The 24 group elements are treated as independent formal coordinates.',
        'This is exact for the regular representation. A different matrix',
        'representation may introduce additional linear dependencies.',
        '',
        'Independent expressions:',
    ])
    for expression in basis:
        lines.append(f'A_{expression.index} = {u.format_expression(expression)}')
    lines.extend(['', 'Groups equivalent up to an overall factor (first label is representative):'])
    lines.extend(labels(group) for group in result['proportional_groups'])
    lines.extend(['', 'Groups with the same terms, ignoring all relative coefficients:'])
    lines.extend(labels(group) for group in result['support_groups'])
    lines.extend(['', 'Zero labels: ' + ', '.join(f'A_{index}' for index in result['zero_labels'])])
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Save this separate report to a file.')
    args = parser.parse_args()
    expressions = u.enumerate_commutators()
    report = make_report(expressions, analyse(expressions))
    print(report, end='')
    if args.output:
        if args.output.resolve() == Path(u.__file__).with_name('universality_commutators.txt').resolve():
            parser.error('Choose a separate output file to preserve the commutator report.')
        args.output.write_text(report, encoding='utf-8')


if __name__ == '__main__':
    main()
