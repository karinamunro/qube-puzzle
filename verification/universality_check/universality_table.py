"""Create a separate commutator table with consecutive independent A labels.

Run: python universality_table.py
Writes universality_table.html and universality_table.csv beside this script.
Rows are the left operand: cell (i,j) is [A_i,A_j] = A_i A_j - A_j A_i.
Original enumeration and reports are not modified.
"""

import ast
import csv
from dataclasses import replace
from html import escape
from pathlib import Path

import universality as u


def build_table():
    selection = u.LinearDecomposition()
    originals = []
    for expression in u.enumerate_commutators():
        if selection.add(expression) is None:
            originals.append(expression)
    basis = [replace(expression, index=index)
             for index, expression in enumerate(originals, start=1)]
    decomposition = u.LinearDecomposition()
    for expression in basis:
        if decomposition.add(expression) is not None:
            raise RuntimeError('Selected basis contains a dependent expression.')
    cells = []
    coefficients = []
    for left in basis:
        row = []
        coefficient_row = []
        for right in basis:
            bracket = u.Expression(0, u.commutator(left.terms, right.terms),
                                   left.degree + right.degree)
            combination = decomposition.add(bracket)
            if combination is None:
                raise RuntimeError('The selected basis is not closed under commutation.')
            row.append(decomposition.format_combination(bracket, combination))
            coefficient_row.append(combination)
        cells.append(row)
        coefficients.append(coefficient_row)
    return originals, basis, cells, coefficients


def math_html(expression):
    """Render our arithmetic expressions as native MathML, including fractions."""
    def render(node):
        if isinstance(node, ast.Name):
            if node.id.startswith('A_'):
                return f'<msub><mi>A</mi><mn>{int(node.id[2:])}</mn></msub>'
            return f'<mi>{"&#960;" if node.id == "pi" else escape(node.id)}</mi>'
        if isinstance(node, ast.Constant) and isinstance(node.value, int):
            return f'<mn>{node.value}</mn>'
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return '<mrow><mo>&#8722;</mo>' + render(node.operand) + '</mrow>'
        if isinstance(node, ast.BinOp):
            left, right = render(node.left), render(node.right)
            if isinstance(node.op, ast.Div):
                return f'<mfrac>{left}{right}</mfrac>'
            if isinstance(node.op, ast.Pow):
                return f'<msup>{left}{right}</msup>'
            if isinstance(node.op, ast.Mult):
                if isinstance(node.left, ast.BinOp) and isinstance(node.left.op, (ast.Add, ast.Sub)):
                    left = f'<mrow><mo>(</mo>{left}<mo>)</mo></mrow>'
                if isinstance(node.right, ast.BinOp) and isinstance(node.right.op, (ast.Add, ast.Sub)):
                    right = f'<mrow><mo>(</mo>{right}<mo>)</mo></mrow>'
                operator = '&#8290;'
            elif isinstance(node.op, ast.Add):
                operator = '+'
            elif isinstance(node.op, ast.Sub):
                operator = '&#8722;'
            else:
                raise ValueError('Unsupported mathematical operator')
            return f'<mrow>{left}<mo>{operator}</mo>{right}</mrow>'
        raise ValueError('Unsupported mathematical expression')
    body = render(ast.parse(expression.replace('^', '**'), mode='eval').body)
    return f'<math xmlns="http://www.w3.org/1998/Math/MathML" aria-label="{escape(expression)}">{body}</math>'


def make_html(originals, basis, cells):
    new_labels = {old.index: new.index for old, new in zip(originals, basis)}
    introductions = {tuple(new_labels[parent] for parent in old.parents): new.index
                     for old, new in zip(originals, basis) if old.parents}
    mapping_rows = ''.join(
        f'<tr><th>{math_html(f"A_{new.index}")}</th><td>{math_html(f"A_{old.index}")}</td>'
        f'<td class="expression">{math_html(u.format_expression(new))}</td></tr>'
        for old, new in zip(originals, basis))
    header = '<tr><th scope="col">[row, column]</th>' + ''.join(
        f'<th scope="col">{math_html(f"A_{item.index}")}</th>' for item in basis) + '</tr>'
    rows = ''.join(
        f'<tr><th scope="row">{math_html(f"A_{item.index}")}</th>' + ''.join(
            f'<td class="{"zero" if cell == "0" else "expression"}'
            f'{" new-generator" if (item.index, column) in introductions else ""}" '
            f'title="[A_{item.index}, A_{column}]">{math_html(cell)}'
            + ('<span class="badge">New independent generator</span>'
               if (item.index, column) in introductions else '') + '</td>'
            for column, cell in enumerate(row, start=1)) + '</tr>'
        for item, row in zip(basis, cells))
    return '''<!doctype html>
<html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Independent A commutator table</title>
<style>
body {font:16px/1.5 system-ui,sans-serif; margin:24px; color:#182330; background:#fafbfc}
h1 {font-size:26px} h2 {font-size:20px}
table {border-collapse:separate; border-spacing:0; background:white}
th,td {padding:12px; border-right:1px solid #dce2e8; border-bottom:1px solid #dce2e8; text-align:left}
th {background:#eaf0f6} .expression {min-width:220px}
math {font-size:1.15em; font-family:"Cambria Math", "STIX Two Math", math}
.badge {display:block; font:11px/1.4 system-ui,sans-serif; color:#654b00; margin-top:8px}
.scroll td.new-generator, .scroll tbody tr:hover td.new-generator {background:#fff0b3; box-shadow:inset 0 0 0 2px #c49318}
.legend {background:#fff0b3; padding:2px 7px; border:1px solid #c49318}
.zero {color:#7c8794; text-align:center}
.scroll {overflow:auto; max-height:72vh; border:1px solid #dce2e8}
.scroll thead th {position:sticky; top:0; z-index:2}
.scroll tbody th {position:sticky; left:0; z-index:1; white-space:nowrap}
.scroll thead th:first-child {left:0; z-index:3}
.scroll tbody tr:hover td {background:#f1f7fc}
</style>
<h1>Commutators of the 12 independent As</h1>
<p>Only independent generators receive labels <i>A</i><sub>1</sub> through <i>A</i><sub>12</sub> in this table.
Each cell is <strong>[row A, column A] = row A · column A − column A · row A</strong>.
Dependent results are combinations of these generators and receive no new number.</p>
<p><span class="legend">Gold cells</span> mark the defining commutators that introduce
the nine new independent generators after the initial three. Repeated appearances
and the reversed commutators are not new generators.</p>
<p>The original generator scales are retained. Thus factors of &pi; appear in the cells.
The diagonal is zero; entries across the diagonal have opposite signs.
Scroll horizontally to see all columns. Row and column headers stay visible.</p>
<div class="scroll"><table><thead>''' + header + '</thead><tbody>' + rows + '''</tbody></table></div>
<h2>Label mapping and definitions</h2>
<p>“Original label” refers to universality_commutators.txt. All labels inside the table
use the new numbering below. Products r, u, f use the paper’s appendix relations.</p>
<table><thead><tr><th>Table label</th><th>Original label</th><th>Operator expression</th></tr></thead>
<tbody>''' + mapping_rows + '</tbody></table></html>\n'


def main():
    originals, basis, cells, _ = build_table()
    directory = Path(__file__).resolve().parent
    html_path = directory / 'universality_table.html'
    csv_path = directory / 'universality_table.csv'
    html_path.write_text(make_html(originals, basis, cells), encoding='utf-8')
    with csv_path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.writer(stream)
        writer.writerow(['[row, column]'] + [f'A_{item.index}' for item in basis])
        for item, row in zip(basis, cells):
            writer.writerow([f'A_{item.index}'] + row)
    print(f'Wrote {html_path}\nWrote {csv_path}')
    print('New -> original labels: ' + ', '.join(
        f'A_{new.index} -> A_{old.index}' for old, new in zip(originals, basis)))


if __name__ == '__main__':
    main()
