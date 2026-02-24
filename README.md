# xpath-builder

A fluent, type-safe Python DSL for building XPath 2.0 expressions without string concatenation.

## Installation

```bash
pip install xpath-builder
```

## Quick Start

```python
from xpath_builder import E, STAR, Pred

# Find all divs with class containing "container"
xpath = E("div").any().where(
    Pred.attr("class").contains.any_of("container")
)
print(xpath.compile())
# //div[contains(@class, 'container')]
```

## Features

- **Fluent API** — chain methods to build complex XPath expressions naturally
- **Zero dependencies** — pure Python, no runtime dependencies
- **Type-safe comparisons** — generic `Ops[T]` for numeric and string comparisons
- **XPath 2.0** — full support including `matches()`, token matching, and more
- **Optional validation** — validate expressions with `elementpath` or `lxml`

## Usage

### Nodes and Paths

```python
from xpath_builder import E, STAR, TEXT, COMMENT

E("div").any()            # //div
E("div").root()           # /div
E("ul").child(E("li"))    # ul/li
E("div").desc(E("span"))  # div//span
STAR.any()                # //*
```

### Predicates

```python
from xpath_builder import Pred

# Attribute checks
Pred.attr("class").contains.any_of("btn", "button")
Pred.attr("id").startswith.any_of("vue-", "react-")
Pred.attr("disabled").exists()
Pred.attr("hidden").missing()

# Text content
Pred.text_contains("Hello")
Pred.text_matches(r"^\d+$")

# Numeric comparisons
Pred.attr("data-count").as_num.gt(10)
Pred.attr("price").as_num.between(5, 99)

# Case-insensitive matching
Pred.attr("type", case_insensitive=True).as_str.eq("submit")
```

### Combining Predicates

```python
# AND / OR / NOT
visible = Pred.attr("hidden").missing() & Pred.attr("display").as_str.ne("none")
clickable = Pred.attr("href").exists() | Pred.attr("onclick").exists()
not_disabled = Pred.attr("disabled").exists().neg()
```

### Chaining

```python
selector = (
    E("div")
    .any()
    .where(Pred.attr("class").contains_tokens.any_of("card"))
    .child(E("a"))
    .where(Pred.attr("href").startswith.any_of("https://"))
    .first()
)
```

### Positional Filtering

```python
E("li").any().first()    # //li[position() = 1]
E("li").any().nth(3)     # //li[position() = 3]
```

## Example: Finding Ad Elements

```python
from xpath_builder import STAR, Pred

ad_selector = (
    STAR.any()
    .where(
        Pred.attr("class").contains.any_of(
            "ads", "ad", "advert", "sponsored", "promo"
        )
    )
)
```

## Documentation

Full documentation is available at [xpath-builder.readthedocs.io](https://kaierikniermann.github.io/xpath-builder/).

## License

MIT
