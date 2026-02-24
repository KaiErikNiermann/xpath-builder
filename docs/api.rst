API Reference
=============

Shortcuts
---------

- ``E(tag)`` -- Create a Node for the given element tag
- ``STAR`` -- Matches any element (``*``)
- ``TEXT`` -- Matches text nodes (``text()``)
- ``COMMENT`` -- Matches comment nodes (``comment()``)
- ``NODE`` -- Matches any node (``node()``)
- ``ATTR(name)`` -- Matches an attribute (``@name``)

Node Methods
------------

- ``.any()`` → Path -- Match anywhere (``//node``)
- ``.root()`` → Path -- Match at root (``/node``)
- ``.where(pred)`` → Path -- Add predicate filter
- ``.child(node)`` → Path -- Direct child axis
- ``.desc(node)`` → Path -- Descendant axis

Path Methods
------------

- ``.where(pred)`` → Path -- Add predicate filter
- ``.child(node)`` → Path -- Direct child axis
- ``.desc(node)`` → Path -- Descendant axis
- ``.first()`` → Path -- First match
- ``.nth(n)`` → Path -- Nth match
- ``.compile()`` → str -- Get the XPath string
- ``.validate()`` -- Validate XPath syntax (requires ``elementpath`` or ``lxml``)

Pred Class Methods
------------------

- ``Pred.attr(name, case_insensitive=False)`` -- Attribute operations
- ``Pred.text_contains(needle)`` -- Text content contains
- ``Pred.text_matches(pattern)`` -- Text content regex match
- ``Pred.union(*preds)`` -- OR multiple predicates
