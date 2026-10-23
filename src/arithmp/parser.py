"""Arithmetic expression parser and evaluator."""

from __future__ import annotations

import operator
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NoReturn, cast

from lark import Lark, LarkError, Token, Transformer, Tree

from arithmp.exceptions import (
    ParserException,
    ParserExceptionContext,
    SyntaxException,
    ZeroDivisionException,
)
from arithmp.variables import Variables, VariableType

_UNARY_OPERATORS: dict[str, Callable[[Any], VariableType]] = {
    "pos": operator.pos,
    "neg": operator.neg,
    "not": operator.not_,
}

_BINARY_OPERATORS: dict[str, Callable[[Any, Any], VariableType]] = {
    "add": operator.add,
    "sub": operator.sub,
    "mul": operator.mul,
    "div": operator.truediv,
    "pow": operator.pow,
    "mod": operator.mod,
    "equal": operator.eq,
    "not_equal": operator.ne,
    "less": operator.lt,
    "less_equal": operator.le,
    "greater": operator.gt,
    "greater_equal": operator.ge,
    "and": operator.and_,
    "or": operator.or_,
}


def _exit() -> NoReturn:
    raise SystemExit


_BUILTINS: dict[str, VariableType] = {}


class _Transformer(Transformer[Tree[Token] | Token, str]):
    """
    Simple transformer that generate full names from sequences of identifiers.
    """

    def dotted_name(self, items: Sequence[str]) -> str:
        return ".".join(str(item) for item in items)

    def QUOTED_FILEPATH(self, token: str) -> str:
        return str(token)[1:-1]

    def unquoted_filepath(self, items: Sequence[str]) -> str:
        return "/".join(str(item) for item in items)


@dataclass(frozen=True)
class Context:
    """
    Small dataclass holding context (current file, source) for the parser.
    """

    file: Path | None
    source: str

    def exception(self, tree: Tree[Token] | Token) -> ParserExceptionContext:
        """
        Generate a ParserExceptionContext for the given tree or token using this
        context.
        """
        if isinstance(tree, Token):
            line, column, start_pos, end_pos = (
                tree.line or -1,
                tree.column or -1,
                tree.start_pos or 0,
                tree.end_pos or len(self.source),
            )
        else:
            line, column, start_pos, end_pos = (
                tree.meta.line,
                tree.meta.column,
                tree.meta.start_pos,
                tree.meta.end_pos,
            )
        return ParserExceptionContext(
            filepath=self.file,
            line=line,
            column=column,
            source=self.source[start_pos:end_pos],
        )


class Parser:
    """
    Parser for arithmetic expressions, supporting variables, functions, and basic
    arithmetic operations.
    """

    def __init__(self) -> None:
        """
        Initialize the parser and set up built-in variables and functions.
        """
        self.parser = Lark(
            Path(__file__).parent.joinpath("arithmp.lark").read_text(),
            parser="lalr",
            transformer=_Transformer(),
            propagate_positions=True,
        )

        self._globals: dict[str, VariableType] = {}

    @property
    def globals(self) -> Mapping[str, VariableType]:
        """Global variables and functions currently defined."""
        return self._globals

    def _eval_as_int(
        self, tree: Tree[Token] | Token, variables: Variables, context: Context
    ) -> int:
        result = self._eval(tree, variables, context)
        if not isinstance(result, (bool, int)):
            raise TypeError(f"expected an integer value, got {type(result).__name__}")
        return result

    def _eval_as_number(
        self, tree: Tree[Token] | Token, variables: Variables, context: Context
    ) -> complex:
        result = self._eval(tree, variables, context)
        if not isinstance(result, (bool, int, float, complex)):
            raise TypeError(f"expected a numeric value, got {type(result).__name__}")
        return result

    def _eval_token(
        self, token: Token, variables: Variables, context: Context
    ) -> VariableType:
        if token.type.endswith("_NUMBER"):
            if token.type.endswith("_NUMBER"):
                for type in (int, float, complex):
                    try:
                        return type(token.value)
                    except ValueError:
                        pass
                raise TypeError(
                    f"expected a numeric value, got {token.value}"
                ) from None
        elif token.type == "STRING":
            return cast(str, token.value)[1:-1]
        elif token.type == "LONG_STRING":
            return cast(str, token.value)[3:-3]
        else:
            # should never occur, there are no other token types in the grammar
            raise ParserException(
                f"unexpected token type: {token.type}", context.exception(token)
            )

    def _eval_tree(
        self, tree: Tree[Token], variables: Variables, context: Context
    ) -> VariableType:

        match tree.data:
            case "const_true":
                return True
            case "const_false":
                return False
            case "const_none":
                return None
            case "string":
                return self._eval(tree.children[0], variables, context)
            case "number":
                return self._eval_as_number(tree.children[0], variables, context)
            case "ternary":
                condition = self._eval(tree.children[0], variables, context)
                if condition:
                    return self._eval(tree.children[1], variables, context)
                else:
                    return self._eval(tree.children[2], variables, context)
            case "add":
                lhs, rhs = (
                    self._eval(tree.children[0], variables, context),
                    self._eval(tree.children[1], variables, context),
                )
                if isinstance(lhs, str) or isinstance(rhs, str):
                    lhs, rhs = str(lhs), str(rhs)
                return _BINARY_OPERATORS["add"](lhs, rhs)
            case (
                "sub"
                | "mul"
                | "div"
                | "mod"
                | "equal"
                | "not_equal"
                | "less"
                | "less_equal"
                | "greater"
                | "greater_equal"
                | "pow"
            ):
                try:
                    return _BINARY_OPERATORS[tree.data](
                        self._eval(tree.children[0], variables, context),
                        self._eval(tree.children[1], variables, context),
                    )
                except ZeroDivisionError as e:
                    raise ZeroDivisionException(
                        "division by zero", context.exception(tree)
                    ) from e

            # special handling for and/or for short-circuit
            case "or":
                return self._eval(tree.children[0], variables, context) or self._eval(
                    tree.children[1], variables, context
                )
            case "and":
                return self._eval(tree.children[0], variables, context) and self._eval(
                    tree.children[1], variables, context
                )
            case "pos" | "neg" | "not":
                return _UNARY_OPERATORS[tree.data](
                    self._eval(tree.children[0], variables, context)
                )
            case "variable_assignment":
                var_name=str(tree.children[0])
                var_value = self._eval(tree.children[1], variables, context)
                variables[var_name] = var_value
                return var_value
            case "variable":
                var_name = str(tree.children[0])
                try:
                    return variables[var_name]
                except KeyError:
                    raise ParserException(
                        f"undefined variable '{var_name}'",context.exception(tree)
                    )
            
            case "body":
                result: VariableType = None
                for child in tree.children:
                    result = self._eval(child, variables, context)
                return result
            case _:
                raise ParserException(
                    f"unexpected tree data: {tree.data}", context.exception(tree)
                )
            

    def _eval(
        self, tree: Tree[Token] | Token, variables: Variables, context: Context
    ) -> VariableType:
        try:
            if isinstance(tree, Token):
                return self._eval_token(tree, variables, context)
            else:
                return self._eval_tree(tree, variables, context)
        except ParserException:
            raise
        except Exception as e:
            raise ParserException(
                f"unexpected error evaluating expression: {e}", context.exception(tree)
            ) from e

    def parse(self, filepath: Path | None, expression: str) -> VariableType:
        """
        Parse and evaluate an arithmetic expression.

        Args:
            filepath: The path to the file containing the expression, or None
                if the expression does not come from a script.
            expression: The arithmetic expression to parse and evaluate.

        Returns:
            The result of the evaluated expression, or None if no expressions were
            provided.
        """
        context = Context(filepath, expression)
        try:
            return self._eval(
                self.parser.parse(expression), Variables(self._globals), context
            )
        except ParserException:
            raise
        except LarkError as e:
            raise SyntaxException(
                f"syntax error parsing expression '{expression}': {e}",
                ParserExceptionContext(filepath, -1, -1, expression),
            ) from e
