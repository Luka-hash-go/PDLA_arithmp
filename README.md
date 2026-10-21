# ArithmP

ArithmP is a small expression parser and evaluator written in Python. test ahhhhh

## Requirements and installation

- Python 3.13 or newer

Install the project with your preferred Python package manager. For example,
with [uv](https://docs.astral.sh/uv/):

```bash
uv sync
```

## Command-line usage

Run a script file by passing its path as the first argument:

```bash
arithmp calculations.arithmp
```

## Language

Statements can be separated by newlines or semicolons. Blank lines and `#`
comments are ignored. Parentheses can be used to group expressions.

### Values and operators

Numbers include decimal, floating-point, and imaginary literals. Strings can
use single, double, or triple quotes.
`True`, `False`, and `None` are also available.
The operators, from lower to higher precedence, are:

| Operators | Operation |
| --- | --- |
| `? :` | Conditional expression |
| `or` | `or` operation |
| `and` | `and` operation |
| `not` | Unary `not` |
| `==`, `!=`, `<`, `<=`, `>`, `>=` | Comparisons |
| `+`, `-` | Addition and subtraction |
| `*`, `/`, `%` | Multiplication, division, and remainder |
| Unary `+`, unary `-` | Sign |
| `^` | Exponentiation |

Exponentiation associates from right to left. `and` and `or` short-circuit and
return one of their operands, as in Python. Addition concatenates values as
strings if either operand is a string.

```text
2 + 3 * 4
(2 + 3) * 4
age >= 18 ? "adult" : "child"
```
