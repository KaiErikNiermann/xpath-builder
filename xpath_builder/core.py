from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from typing import Callable, Literal

from xpath_builder.utils import quote, re_escape_xsd, validate_xpath


@dataclass(frozen=True)
class Ops[T]:
    """
    Generic comparator builder for an XPath LHS.
    - lhs: the left-hand XPath expression, e.g. '@price', 'number(@price)', 'position()'
    - to_lit: turns a Python value into an XPath literal (quotes, lowercasing, etc.)
    """

    lhs: str
    to_lit: Callable[[T], str]

    def cmp(self, op: Literal["=", "!=", "<", "<=", ">", ">="], value: T) -> "Pred":
        if op not in {"=", "!=", "<", "<=", ">", ">="}:
            raise ValueError("Invalid comparator")
        return Pred(f"{self.lhs} {op} {self.to_lit(value)}")

    def eq(self, value: T) -> "Pred":
        return self.cmp("=", value)

    def ne(self, value: T) -> "Pred":
        return self.cmp("!=", value)

    def lt(self, value: T) -> "Pred":
        return self.cmp("<", value)

    def le(self, value: T) -> "Pred":
        return self.cmp("<=", value)

    def gt(self, value: T) -> "Pred":
        return self.cmp(">", value)

    def ge(self, value: T) -> "Pred":
        return self.cmp(">=", value)

    def between(
        self, lo: T, hi: T, *, inclusive: tuple[bool, bool] = (True, True)
    ) -> "Pred":
        lop = ">=" if inclusive[0] else ">"
        hip = "<=" if inclusive[1] else "<"
        return Pred(
            f"({self.lhs} {lop} {self.to_lit(lo)}) and ({self.lhs} {hip} {self.to_lit(hi)})"
        )

    def in_(self, *values: T) -> "Pred":
        if not values:
            return Pred("false()")
        seq = "(" + ", ".join(self.to_lit(v) for v in values) + ")"
        return Pred(f"{self.lhs} = {seq}")

    def not_in(self, *values: T) -> "Pred":
        return self.in_(*values).neg()


def attr_str(name: str, *, ci: bool = False) -> Ops[str]:
    """String attribute ops (optionally case-insensitive)."""
    lhs = f"lower-case(@{name})" if ci else f"@{name}"

    def to_lit(v: str) -> str:
        return quote(v.lower() if ci else v)

    return Ops[str](lhs, to_lit)


def attr_num(name: str) -> Ops[float]:
    """Numeric compare on attribute by casting: number(@name)."""
    lhs = f"number(@{name})"

    def to_lit(v: float) -> str:
        return (
            "NaN"
            if v != v  # type: ignore[comparison-overlap]  # NaN check
            else (
                "Infinity"
                if v == float("inf")
                else "-Infinity" if v == float("-inf") else str(v)
            )
        )

    return Ops[float](lhs, to_lit)


def position_ops() -> Ops[int]:
    lhs = "position()"

    def to_lit(v: int) -> str:
        return str(int(v))

    return Ops[int](lhs, to_lit)


def bool_expr(expr: str) -> Ops[bool]:
    """Compare boolean expressions (rare)."""
    lhs = expr

    def to_lit(v: bool) -> str:
        return "true()" if v else "false()"

    return Ops[bool](lhs, to_lit)


def string_value(ci: bool = False) -> Ops[str]:
    """Compare node string-value: string(.) (optionally lower-cased)."""
    lhs = "lower-case(string(.))" if ci else "string(.)"

    def to_lit(v: str) -> str:
        return quote(v.lower() if ci else v)

    return Ops[str](lhs, to_lit)


@dataclass(frozen=True)
class _SetBuilder:
    """Implements .any_of/.all_of/.none_of for a given per-token predicate factory."""

    make_one: Callable[[str], str]  # (token: str) -> str

    def any_of(self, *tokens: str) -> "Pred":
        if not tokens:
            return Pred("false()")
        parts = [self.make_one(t) for t in tokens]
        return Pred(" or ".join(parts))

    def all_of(self, *tokens: str) -> "Pred":
        if not tokens:
            return Pred("true()")
        parts = [self.make_one(t) for t in tokens]
        return Pred(" and ".join(parts))

    def none_of(self, *tokens: str) -> "Pred":
        if not tokens:
            return Pred("true()")
        return self.any_of(*tokens).neg()


def _seq_literal_strs(items: list[str]) -> str:
    return "(" + ", ".join(quote(s) for s in items) + ")"


@dataclass(frozen=True)
class _AttrNameOps:
    """attr('*').name.{contains|startswith|endswith|matches}.set_op(...)"""

    ci: bool  # case-insensitive for NAME comparisons

    def _lname(self, var: str) -> str:
        # var is like "$a"
        return f"lower-case(local-name({var}))" if self.ci else f"local-name({var})"

    @property
    def contains(self) -> _SetBuilder:
        def one(substr: str) -> str:
            x = self._lname("$a")
            needle = substr.lower() if self.ci else substr
            return f"some $a in @* satisfies contains({x}, {quote(needle)})"

        return _SetBuilder(make_one=one)

    @property
    def equals(self) -> _SetBuilder:
        def one(name: str) -> str:
            x = self._lname("$a")
            target = name.lower() if self.ci else name
            return f"some $a in @* satisfies {x} = {quote(target)}"

        return _SetBuilder(make_one=one)

    # convenience aliases mapping to equals
    def any_of(self, *names: str) -> "Pred":
        return self.equals.any_of(*names)

    def all_of(self, *names: str) -> "Pred":
        # every $n in ('a','b') satisfies some $a in @* satisfies local-name($a)= $n
        if not names:
            return Pred("true()")
        seq = _seq_literal_strs([n.lower() if self.ci else n for n in names])
        x = "lower-case(local-name($a))" if self.ci else "local-name($a)"
        return Pred(f"every $n in {seq} satisfies some $a in @* satisfies {x} = $n")

    def none_of(self, *names: str) -> "Pred":
        if not names:
            return Pred("true()")
        return self.any_of(*names).neg()

    @property
    def startswith(self) -> _SetBuilder:
        def one(prefix: str) -> str:
            x = self._lname("$a")
            return f"some $a in @* satisfies starts-with({x}, {quote(prefix.lower() if self.ci else prefix)})"

        return _SetBuilder(make_one=one)

    @property
    def endswith(self) -> _SetBuilder:
        def one(suffix: str) -> str:
            x = self._lname("$a")
            return f"some $a in @* satisfies ends-with({x}, {quote(suffix.lower() if self.ci else suffix)})"

        return _SetBuilder(make_one=one)

    def matches(self, *, flags: str = "") -> _SetBuilder:
        fl = f", {quote(flags)}" if flags else ""

        def one(pattern: str) -> str:
            # Note: pattern is XML Schema regex; pass as-is
            lhs = f"lower-case(local-name($a))" if self.ci else f"local-name($a)"
            return f"some $a in @* satisfies matches({lhs}, {quote(pattern)}{fl})"

        return _SetBuilder(make_one=one)


@dataclass(frozen=True)
class _AttrOps:
    """Entry point: "Pred".attr(name, ci=...).op.set_op(...)"""

    name: str
    ci: bool

    @property
    def contains(self) -> _SetBuilder:
        base = f"lower-case(@{self.name})" if self.ci else f"@{self.name}"

        def one(tok: str) -> str:
            needle = tok.lower() if self.ci else tok
            return f"contains({base}, {quote(needle)})"

        return _SetBuilder(make_one=one)

    @property
    def contains_tokens(self) -> _SetBuilder:
        src = f"concat(' ', normalize-space(@{self.name}), ' ')"
        flags = ", 'i'" if self.ci else ""

        def one(tok: str) -> str:
            pat = rf"\s{re_escape_xsd(tok)}\s"
            return f"matches({src}, {quote(pat)}{flags})"

        return _SetBuilder(make_one=one)

    def none_of(self, *tokens: str) -> "Pred":
        return self.contains_tokens.none_of(*tokens)

    @property
    def startswith(self) -> _SetBuilder:
        left = f"lower-case(@{self.name})" if self.ci else f"@{self.name}"

        def one(prefix: str) -> str:
            right = quote(prefix.lower() if self.ci else prefix)
            return f"starts-with({left}, {right})"

        return _SetBuilder(make_one=one)

    @property
    def endswith(self) -> _SetBuilder:
        left = f"lower-case(@{self.name})" if self.ci else f"@{self.name}"

        def one(suffix: str) -> str:
            right = quote(suffix.lower() if self.ci else suffix)
            return f"ends-with({left}, {right})"

        return _SetBuilder(make_one=one)

    @property
    def has_name(self) -> _AttrNameOps:
        """
        Attribute NAME matching across the element's attributes.
        Only meaningful if self.name == '*'; otherwise this would be tautological.
        """
        if self.name != "*":
            # You *can* allow it, but it's effectively checking a constant.
            # Safer to nudge the caller:
            raise ValueError("attr(name).has_name is only meaningful for attr('*')")
        return _AttrNameOps(ci=self.ci)

    def matches(self, *, flags: str = "") -> _SetBuilder:
        fl = f", {quote(flags)}" if flags else ""

        def one(pattern: str) -> str:
            return f"matches(@{self.name}, {quote(pattern)}{fl})"

        return _SetBuilder(make_one=one)

    def missing(self) -> "Pred":
        """
        Attribute missing: not(@attr)
        """
        return Pred(f"not(@{self.name})")

    def exists(self) -> "Pred":
        """
        Attribute exists: @attr
        """
        return Pred(f"@{self.name}")

    @property
    def as_str(self) -> Ops[str]:
        """
        String attribute ops (optionally case-insensitive).
        """
        return attr_str(self.name, ci=self.ci)

    @property
    def as_num(self) -> Ops[float]:
        """
        Numeric attribute ops: number(@attr).
        """
        return attr_num(self.name)


@runtime_checkable
class Compilable(Protocol):
    def compile(self) -> str: ...


@dataclass(frozen=True)
class Pred(Compilable):
    expr: str

    def compile(self) -> str:
        return self.expr

    # Boolean ops
    def __and__(self, other: "Pred") -> "Pred":
        return Pred(f"({self.expr}) and ({other.expr})")

    def __or__(self, other: "Pred") -> "Pred":
        return Pred(f"({self.expr}) or ({other.expr})")

    def neg(self) -> "Pred":
        return Pred(f"not({self.expr})")

    @staticmethod
    def attr(name: str, *, case_insensitive: bool = False) -> _AttrOps:
        return _AttrOps(name=name, ci=case_insensitive)

    @staticmethod
    def attr_has_token(attr: str, token: str, case_insensitive: bool = False) -> "Pred":
        """
        Exact token match in space-separated lists (e.g., @class).
        In XPath 2.0 we can just regex with word-like boundaries.
        We normalize spaces to avoid duplicate-space issues.
        """
        # normalize-space collapses whitespace; add spaces to force token boundaries
        src = f"concat(' ', normalize-space(@{attr}), ' ')"
        pat = f"\\s{token}\\s"
        flags = "i" if case_insensitive else ""
        return Pred(
            f"matches({src}, {quote(pat)}{', ' + quote(flags) if flags else ''})"
        )

    # Text/string predicates (node string-value)
    @staticmethod
    def text_contains(
        needle: str, normalized: bool = True, case_insensitive: bool = False
    ) -> "Pred":
        base = "normalize-space()" if normalized else "string(.)"
        if case_insensitive:
            return Pred(f"contains(lower-case({base}), lower-case({quote(needle)}))")
        return Pred(f"contains({base}, {quote(needle)})")

    @staticmethod
    def text_matches(pattern: str, flags: str = "") -> "Pred":
        base = "string(.)"
        flags_arg = f", {quote(flags)}" if flags else ""
        return Pred(f"matches({base}, {quote(pattern)}{flags_arg})")

    @staticmethod
    def union(*preds: "Pred") -> "Pred":
        """
        Union of multiple predicates: (pred1) | (pred2) | ...
        """
        if not preds:
            return Pred("false()")
        return Pred(" or ".join(f"({p.compile()})" for p in preds))


# ----- Path / Node DSL -----

@dataclass(frozen=True)
class Path(Compilable):
    expr: str

    def compile(self) -> str:
        return self.expr

    def __str__(self) -> str:
        return self.expr

    # predicates
    def neg(self) -> "Pred":
        return Pred(f"not({self.expr})")

    def where(self, pred: "Pred") -> "Path":
        """
        Filter with a predicate: /node[pred]
        """
        return Path(f"{self.expr}[{pred.compile()}]")

    def child(self, node: "Node") -> "Path":
        """
        Child axis: /node
        """
        return Path(f"{self.expr}/{node.compile()}")

    def desc(self, node: "Node") -> "Path":
        """
        Descendant-or-self axis: //node
        """
        return Path(f"{self.expr}//{node.compile()}")

    def curr_desc(self) -> "Path":
        """
        Current + Descendant-or-self axis: .//node
        """
        return Path(f".//{self.expr}")

    def nth(self, n: int) -> "Path":
        return self.where(position_ops().eq(n))

    def first(self) -> "Path":
        return self.nth(1)

    def validate(self) -> None:
        validate_xpath(self.expr)

    @staticmethod
    def union(*paths: "Path") -> "Path":
        """
        Union of multiple paths: /path1 | /path2 | ...
        """
        if not paths:
            return Path("false()")
        return Path(" | ".join(f"({p.compile()})" for p in paths))


@dataclass(frozen=True)
class Node(Compilable):
    """
    Node test: element name (*, div), node(), text(), attribute (@href), etc.
    """
    test: str

    def __or__(self, other: "Node") -> "Path":
        """
        Union with another node test: node | other
        """
        return Path(f"{self.test} | {other.test}")

    def compile(self) -> str:
        return self.test

    def any(self) -> "Path":
        """
        Description: Match any in the document.
        """
        return Path(f"//{self.test}")

    def root(self) -> "Path":
        """
        Description: Match the root of the document.
        """
        return Path(f"/{self.test}")

    def where(self, pred: "Pred") -> "Path":
        """
        Filter with a predicate: /node[pred]
        """
        return Path(self.test).where(pred)

    def child(self, other: "Node") -> "Path":
        return Path(self.test).child(other)

    def desc(self, other: "Node") -> "Path":
        return Path(self.test).desc(other)

    def curr_desc(self) -> "Path":
        """
        Current + Descendant-or-self axis: .//node
        """
        return Path(self.test).curr_desc()
