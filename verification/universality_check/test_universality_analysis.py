import unittest

import universality as u
import universality_analysis as analysis


class AnalysisTests(unittest.TestCase):
    def test_relative_coefficients_and_phase_matter_for_rank(self):
        span = analysis.ExactSpan()
        self.assertTrue(span.add(u.Expression(1, {('r',): 1, ('u',): 1}, 2)))
        self.assertTrue(span.add(u.Expression(2, {('r',): 1, ('u',): -1}, 2)))
        # A sum is dependent even though not proportional to either row.
        self.assertFalse(span.add(u.Expression(3, {('r',): 2}, 4)))
        # Imaginary and real copies are independent over R.
        self.assertTrue(span.add(u.Expression(4, {('r',): 2}, 3)))
        self.assertFalse(span.add(u.Expression(5, {}, 2)))

    def test_three_round_result_and_closure(self):
        result = analysis.analyse(u.enumerate_commutators())
        self.assertEqual(result['ranks'], {0: 3, 1: 6, 2: 12, 3: 12})
        self.assertEqual(len(result['proportional_groups']), 100)
        self.assertEqual(len(result['support_groups']), 56)
        self.assertEqual(result['outside_span'], [])
        # Rank and closure do not depend on which independent rows come first.
        reversed_result = analysis.analyse(list(reversed(u.enumerate_commutators())))
        self.assertEqual(len(reversed_result['basis']), 12)
        self.assertEqual(reversed_result['outside_span'], [])


if __name__ == '__main__':
    unittest.main()
