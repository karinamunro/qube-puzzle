"""Check Appendix A reduction against an independent S4 representation."""

from itertools import permutations, product
from fractions import Fraction
import unittest

import universality as u


def permutation_of(word):
    # The three star transpositions satisfy the appendix presentation of S4.
    result = list(range(4))
    for move in word:
        other = {'r': 1, 'u': 2, 'f': 3}[move]
        result[0], result[other] = result[other], result[0]
    return tuple(result)


def multiply(left, right):
    return tuple(left[right[i]] for i in range(4))


def direct_bracket(left, right):
    result = {}
    for first, second, sign in ((left, right, 1), (right, left, -1)):
        for a, ca in first.items():
            for b, cb in second.items():
                key = multiply(a, b)
                result[key] = result.get(key, 0) + sign * ca * cb
    return {key: value for key, value in result.items() if value}


class ReductionTests(unittest.TestCase):
    def test_linear_decompositions_reconstruct_every_expression(self):
        for mode in ('rounds', 'brackets'):
            decomposition = u.LinearDecomposition()
            for expression in u.enumerate_commutators(3, mode):
                combination = decomposition.add(expression)
                if combination is None:
                    continue
                reconstructed = {}
                for index, coefficient in combination.items():
                    original = decomposition.basis[index]
                    self.assertLess(index, expression.index)
                    self.assertEqual((expression.degree - original.degree) % 2, 0)
                    for word, value in original.terms.items():
                        reconstructed[word] = reconstructed.get(word, 0) + coefficient * value
                self.assertEqual({word: value for word, value in reconstructed.items() if value},
                                 expression.terms)
            self.assertEqual(len(decomposition.basis), 12)
        report = u.make_report(u.enumerate_commutators(), 3, 'rounds')
        self.assertIn('A_14 := [A_3, A_5] = pi^2/2*A_1 - pi^2/2*A_3 - A_8', report)
        self.assertIn('A_13 := [A_3, A_4] = -A_9 + A_11', report)

    def test_proportional_references(self):
        expressions = u.enumerate_commutators()
        report = u.make_report(expressions, 3, 'rounds')
        self.assertIn('A_19 := [A_1, A_7] = -pi^2*A_4', report)
        for position, expression in enumerate(expressions):
            match = u.find_proportional(expression, expressions[:position])
            if match:
                original, ratio, power = match
                self.assertLess(original.index, expression.index)
                self.assertEqual(expression.degree, original.degree + power)
                self.assertEqual(expression.terms,
                                 {word: ratio * value for word, value in original.terms.items()})

    def test_proportional_edge_cases(self):
        first = u.Expression(1, {('r',): 2, ('u',): -4}, 2)
        duplicate = u.Expression(2, dict(first.terms), 2)
        scaled = u.Expression(3, {('u',): 2, ('r',): -1}, 4)
        match = u.find_proportional(scaled, [first, duplicate])
        self.assertIs(match[0], first)
        self.assertEqual(u.format_reference(*match), 'pi^2/8*A_1')
        self.assertEqual(u.format_reference(first, Fraction(1), 0), 'A_1')
        self.assertEqual(u.format_reference(first, Fraction(-1), 0), '-A_1')
        self.assertEqual(u.format_reference(first, Fraction(1), -2), '-4/pi^2*A_1')
        self.assertEqual(u.format_reference(first, Fraction(1), 1), '-i*pi/2*A_1')
        self.assertIsNone(u.find_proportional(u.Expression(4, {}, 4), [first]))
        self.assertIsNone(u.find_proportional(first, [u.Expression(4, {}, 4)]))
        self.assertIsNone(u.find_proportional(
            u.Expression(4, {('r',): 2, ('u',): -3}, 2), [first]))

    def test_all_words_through_length_eight(self):
        representatives = {}
        for length in range(9):
            for word in product(u.MOVES, repeat=length):
                reduced = u.reduce_word(word)
                permutation = permutation_of(word)
                self.assertEqual(permutation_of(reduced), permutation)
                self.assertLessEqual(len(reduced), 4)
                self.assertEqual(representatives.setdefault(permutation, reduced), reduced)
        self.assertEqual(len(representatives), 24)
        # Independently enumerate shortest representatives, including tie order.
        shortest = {}
        for length in range(5):
            for word in product(u.MOVES, repeat=length):
                shortest.setdefault(permutation_of(word), word)
        self.assertEqual(representatives, shortest)

    def test_appendix_relations(self):
        for a, b, c in permutations(u.MOVES):
            for lhs, rhs in (
                (a+a, ''), (a+b+a, b+a+b), ((a+b)*3, ''),
                (a+b+c+a, b+c+a+b), (a+b+c+a, c+a+b+c),
                (a+b+a+c, c+a+b+a), ((a+b+c)*4, ''),
            ):
                self.assertEqual(u.reduce_word(lhs), u.reduce_word(rhs))
        self.assertEqual(u.reduce_word('rfurf'), tuple('fur'))

    def test_every_commutator_against_permutation_algebra(self):
        for mode, counts in [('rounds', [3, 12, 138]), ('brackets', [3, 9, 30])]:
            expressions = u.enumerate_commutators(3, mode)
            self.assertEqual([sum(e.level == k for e in expressions) for k in (1, 2, 3)], counts)
            direct = {}
            for expression in expressions:
                actual = {permutation_of(word): value for word, value in expression.terms.items()}
                if expression.parents:
                    a, b = expression.parents
                    expected = direct_bracket(direct[a], direct[b])
                    self.assertEqual(actual, expected)
                    direct[expression.index] = expected
                else:
                    direct[expression.index] = actual


if __name__ == '__main__':
    unittest.main()
