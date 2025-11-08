from __future__ import annotations

_elementpath_available = False
_lxml_available = False

try:
    # pip install elementpath
    import elementpath  # type: ignore[import]

    _elementpath_available = True
except Exception:
    pass

try:
    # pip install lxml
    from lxml.etree import XPath as _XPath  # type: ignore[import]

    _lxml_available = True
except Exception:
    pass


def validate_xpath(expr: str) -> None:
    if _elementpath_available:
        try:
            parser = elementpath.XPath2Parser()  # type: ignore[call-arg]
            parser.parse(expr)  # type: ignore
            return
        except Exception as e:
            raise SyntaxError(f"XPath (elementpath) syntax error: {e}") from e

    if _lxml_available:
        try:
            _XPath(expr)  # type: ignore[call-arg]
            return
        except Exception as e:
            # Note: lxml is 1.0-only, so 2.0 featurs may fail here spuriously.
            # We still surface the error to catch obvious typos.
            raise SyntaxError(f"XPath (lxml) syntax error: {e}") from e


def quote(s: str) -> str:
    """Quote as XPath literal; uses concat() if both quote types appear."""
    if "'" not in s:
        return f"'{s}'"
    if '"' not in s:
        return f'"{s}"'
    parts: list[str] = [f'"{chunk}"' for chunk in s.split("'")]
    glued = ",'\"',".join(parts)
    return f"concat({glued})"


def re_escape_xsd(lit: str) -> str:
    """Escape for XML Schema regex (close enough for literals)."""
    specials = r".^$|?*+()[]{}\-\\"
    out: list[str] = []
    for ch in lit:
        if ch in specials:
            out.append("\\" + ch)
        else:
            out.append(ch)
    return "".join(out)
