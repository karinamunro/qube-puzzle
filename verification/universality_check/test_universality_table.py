import unittest

import universality as u
import universality_table as table


class TableTests(unittest.TestCase):
    def test_all_cells_reconstruct_and_are_antisymmetric(self):
        originals, basis, cells, coefficients = table.build_table()
        self.assertEqual([a.index for a in originals], [1,2,3,4,5,6,7,8,9,11,12,16])
        self.assertEqual([a.index for a in basis], list(range(1,13)))
        self.assertEqual(cells[0][1], 'A_4')
        self.assertEqual(cells[1][0], '-A_4')
        self.assertEqual(cells[2][3], '-A_9 + A_10')
        for i, left in enumerate(basis):
            self.assertEqual(cells[i][i], '0')
            for j, right in enumerate(basis):
                combination = coefficients[i][j]
                self.assertEqual(combination, {k: -v for k,v in coefficients[j][i].items()})
                reconstructed = {}
                for index, coefficient in combination.items():
                    for word, value in basis[index-1].terms.items():
                        reconstructed[word] = reconstructed.get(word,0) + coefficient*value
                self.assertEqual({w:v for w,v in reconstructed.items() if v},
                                 u.commutator(left.terms, right.terms))


if __name__ == '__main__':
    unittest.main()
