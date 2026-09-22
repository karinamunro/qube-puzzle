"""Enumerate symbolic commutators of the three half-turn generators.

Run: python universality.py
     python universality.py --mode brackets --rounds 3 --output commutators.txt

Default: three rounds. A round uses all earlier A's and includes each new
unordered pair once. Thus round 2 includes [commutator, commutator].
With --mode brackets, instead limit the total number of bracket operations.

Products are reduced using the involution, braid, and four-move relations
in the paper's first appendix, to canonical words of at most four moves.
This enumerates expressions, not an independent basis or a universality test.
Uses only the Python standard library.
Dependent results are displayed as exact combinations of earlier independent As.
"""

import argparse
from dataclasses import dataclass
from fractions import Fraction
from functools import lru_cache, reduce
from itertools import combinations, permutations
from math import gcd
from pathlib import Path


# A polynomial maps operator words to integer coefficients. () is identity.
# Its overall scalar is (-i*pi/2)**degree, kept exact separately.
@dataclass
class Expression:
    index: int
    terms: dict[tuple[str, ...], int]
    degree: int
    level: int = 0
    parents: tuple[int, int] | None = None


MOVES = ('r', 'u', 'f')
MOVE_ORDER = {move: index for index, move in enumerate(MOVES)}


def word_key(word):
    return len(word), tuple(MOVE_ORDER[move] for move in word)


def appendix_rules():
    """Length-preserving identities from Appendix A, in both directions."""
    rules = set()
    for a, b in permutations(MOVES, 2):
        rules.add(((a, b, a), (b, a, b)))
    for a, b, c in permutations(MOVES):
        cyclic = ((a, b, c, a), (b, c, a, b), (c, a, b, c))
        rules.update(permutations(cyclic, 2))
        lhs, rhs = (a, b, a, c), (c, a, b, a)
        rules.update(((lhs, rhs), (rhs, lhs)))
    return tuple(sorted(rules))


APPENDIX_RULES = appendix_rules()


@lru_cache(maxsize=None)
def canonical_short_word(word):
    """Explore equal-length rewrites AND cancellations, avoiding greedy traps.

    The input is at most five moves: a canonical prefix plus one new move.
    Exploring both directions allows a braid/cyclic rewrite to expose a
    cancellation. Ties use the fixed order r, u, f for reproducible output.
    """
    seen = {word}
    pending = [word]
    while pending:
        current = pending.pop()
        neighbours = []
        for position in range(len(current) - 1):
            if current[position] == current[position + 1]:
                neighbours.append(current[:position] + current[position + 2:])
        for lhs, rhs in APPENDIX_RULES:
            for position in range(len(current) - len(lhs) + 1):
                if current[position:position + len(lhs)] == lhs:
                    neighbours.append(current[:position] + rhs + current[position + len(lhs):])
        for neighbour in neighbours:
            if neighbour not in seen:
                seen.add(neighbour)
                pending.append(neighbour)
    return min(seen, key=word_key)


def reduce_word(word):
    """Reduce an arbitrarily long ordered product using Appendix A."""
    canonical = ()
    for letter in word:
        if letter not in MOVE_ORDER:
            raise ValueError(f'Unknown classical move: {letter!r}')
        canonical = canonical_short_word(canonical + (letter,))
        if len(canonical) > 4:
            raise RuntimeError('Appendix reduction failed to reach four moves.')
    return canonical


def commutator(left, right):
    """Return the integer polynomial for XY - YX."""
    result = {}
    for first, second, sign in ((left, right, 1), (right, left, -1)):
        for word1, coefficient1 in first.items():
            for word2, coefficient2 in second.items():
                word = reduce_word(word1 + word2)
                result[word] = result.get(word, 0) + sign * coefficient1 * coefficient2
    return {word: coefficient for word, coefficient in result.items() if coefficient}


def generators():
    # A_1 = A_r = -i H_r = (-i*pi/2)(r-I), similarly for u and f.
    return [Expression(index, {(move,): 1, (): -1}, 1)
            for index, move in enumerate(('r', 'u', 'f'), start=1)]


def enumerate_commutators(rounds=3, mode='rounds'):
    expressions = generators()
    for level in range(1, rounds + 1):
        new = []
        # Snapshot: expressions created in this round enter the NEXT round.
        for left, right in combinations(expressions, 2):
            target_level = (1 + max(left.level, right.level) if mode == 'rounds'
                            else left.degree + right.degree - 1)
            if target_level != level:
                continue
            new.append(Expression(
                len(expressions) + len(new) + 1,
                commutator(left.terms, right.terms),
                left.degree + right.degree,
                level,
                (left.index, right.index),
            ))
        expressions.extend(new)
    return expressions


def format_expression(expression):
    """Render an exact scalar times an ordered noncommutative polynomial."""
    if not expression.terms:
        return '0'
    common = reduce(gcd, (abs(value) for value in expression.terms.values()))
    magnitude = Fraction(common, 2 ** expression.degree)
    # (-i)**degree cycles through 1, -i, -1, i.
    phase = expression.degree % 4
    sign = '-' if phase in (1, 2) else ''
    factors = []
    if magnitude.numerator != 1:
        factors.append(str(magnitude.numerator))
    if phase in (1, 3):
        factors.append('i')
    factors.append('pi' if expression.degree == 1 else f'pi^{expression.degree}')
    scalar = sign + '*'.join(factors)
    if magnitude.denominator != 1:
        scalar += f'/{magnitude.denominator}'
    pieces = []
    for word, value in sorted(expression.terms.items(), key=lambda item: (len(item[0]), item[0])):
        coefficient = value // common
        operator = '*'.join(word) if word else 'I'
        term = (f'{abs(coefficient)}*' if abs(coefficient) != 1 else '') + operator
        if not pieces:
            pieces.append(('-' if coefficient < 0 else '') + term)
        else:
            pieces.append((' - ' if coefficient < 0 else ' + ') + term)
    return f'({scalar}) * ({"".join(pieces)})'


def find_proportional(expression, previous):
    """Return (earliest A, rational ratio, degree difference), or None.

    The full multiplier is ratio * (-i*pi/2)**degree_difference.
    Zero is printed directly, never used as a proportional representative.
    """
    if not expression.terms:
        return None
    for original in previous:
        if not original.terms or expression.terms.keys() != original.terms.keys():
            continue
        word = next(iter(expression.terms))
        ratio = Fraction(expression.terms[word], original.terms[word])
        if all(value == ratio * original.terms[word]
               for word, value in expression.terms.items()):
            return original, ratio, expression.degree - original.degree
    return None


def format_reference(original, ratio, degree_difference):
    """Format an exact multiple, including signs, fractions and powers of pi."""
    coefficient = ratio * Fraction(2) ** (-degree_difference)
    phase = degree_difference % 4
    if phase in (1, 2):
        coefficient = -coefficient
    numerator = []
    denominator = []
    if abs(coefficient.numerator) != 1:
        numerator.append(str(abs(coefficient.numerator)))
    if phase in (1, 3):
        numerator.append('i')
    if degree_difference:
        power = abs(degree_difference)
        (numerator if degree_difference > 0 else denominator).append(
            'pi' if power == 1 else f'pi^{power}')
    if coefficient.denominator != 1:
        denominator.insert(0, str(coefficient.denominator))
    scalar = ('-' if coefficient < 0 else '') + ('*'.join(numerator) or '1')
    if denominator:
        divisor = '*'.join(denominator)
        scalar += '/' + (f'({divisor})' if len(denominator) > 1 else divisor)
    if scalar == '1':
        return f'A_{original.index}'
    if scalar == '-1':
        return f'-A_{original.index}'
    return f'{scalar}*A_{original.index}'


class LinearDecomposition:
    """Exact elimination retaining each pivot's expansion in original As.

    Coordinates omit (-i*pi/2)**degree, but keep degree parity so that
    elimination is over the reals. Display restores every scalar exactly.
    """

    def __init__(self):
        self.pivots = []
        self.basis = {}

    def add(self, expression):
        """Return None for a new independent A, otherwise its coefficient map.

        Coefficients refer to the unscaled integer polynomials. The actual
        coefficient of A_j is c_j*(-i*pi/2)**(degree-degree_j).
        An empty map denotes zero.
        """
        row = {(expression.degree % 2, word): Fraction(value)
               for word, value in expression.terms.items() if value}
        combination = {}
        for pivot, pivot_row, expansion in self.pivots:
            factor = row.get(pivot, 0)
            if not factor:
                continue
            for key, value in pivot_row.items():
                row[key] = row.get(key, 0) - factor * value
                if not row[key]:
                    del row[key]
            for index, value in expansion.items():
                combination[index] = combination.get(index, 0) + factor * value
                if not combination[index]:
                    del combination[index]
        if not row:
            return combination
        pivot = min(row)
        scale = row[pivot]
        expansion = {index: -value / scale for index, value in combination.items()}
        expansion[expression.index] = 1 / scale
        self.pivots.append((pivot, {key: value / scale for key, value in row.items()}, expansion))
        self.basis[expression.index] = expression
        return None

    def format_combination(self, expression, combination):
        pieces = []
        for index, coefficient in sorted(combination.items()):
            original = self.basis[index]
            term = format_reference(original, coefficient, expression.degree - original.degree)
            if not pieces:
                pieces.append(term)
            elif term.startswith('-'):
                pieces.append(' - ' + term[1:])
            else:
                pieces.append(' + ' + term)
        return ''.join(pieces) or '0'


def make_report(expressions, rounds, mode):
    lines = [
        '[X,Y] = X*Y - Y*X; i is the imaginary unit; I is the identity.',
        'Products use Appendix A: involution, braid, cyclic four-move,',
        'and four-move commutation relations. Canonical words have <= 4 moves.',
        'Equal-length representatives are chosen in the fixed order r, u, f.',
        'Each pair is listed once: [A_j,A_i] = -[A_i,A_j]; [A_i,A_i] = 0.',
        'Zero and dependent results are retained; A labels are not a basis.',
        'Dependent results are exact linear combinations of earlier independent As.',
        'New independent results show their operator expression and [independent].',
        '',
        'A_1 := A_r = -i*H_r = (-i*pi/2)*(r-I)',
        'A_2 := A_u = -i*H_u = (-i*pi/2)*(u-I)',
        'A_3 := A_f = -i*H_f = (-i*pi/2)*(f-I)',
    ]
    decomposition = LinearDecomposition()
    for item in expressions:
        if item.level == 0:
            decomposition.add(item)
    for level in range(1, rounds + 1):
        group = [item for item in expressions if item.level == level]
        title = f'Round {level}' if mode == 'rounds' else f'{level} bracket operation(s)'
        lines.extend(['', f'{title}: {len(group)} commutators'])
        for item in group:
            left, right = item.parents
            combination = decomposition.add(item)
            result = (format_expression(item) + '  [independent]' if combination is None
                      else decomposition.format_combination(item, combination))
            lines.append(f'A_{item.index} := [A_{left}, A_{right}] = {result}')
    lines.extend(['', f'Total: {len(expressions) - 3} commutators.'])
    lines.append('Independent As (including initial generators): ' +
                 ', '.join(f'A_{index}' for index in decomposition.basis))
    return '\n'.join(lines) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, default=3)
    parser.add_argument('--mode', choices=('rounds', 'brackets'), default='rounds')
    parser.add_argument('--output', type=Path, help='Also save the printed report to this file.')
    args = parser.parse_args()
    if not 1 <= args.rounds <= 3:
        parser.error('--rounds must be 1, 2, or 3 (all-pairs enumeration grows rapidly).')
    expressions = enumerate_commutators(args.rounds, args.mode)
    report = make_report(expressions, args.rounds, args.mode)
    print(report, end='')
    if args.output:
        args.output.write_text(report, encoding='utf-8')


if __name__ == '__main__':
    main()
