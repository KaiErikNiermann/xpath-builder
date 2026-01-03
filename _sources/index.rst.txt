.. xpath-builder documentation master file, created by
   sphinx-quickstart on Sat Nov  8 20:32:49 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

xpath-builder
=============

A fluent, type-safe Python DSL for building XPath 2.0 expressions.

**xpath-builder** helps you construct complex XPath queries programmatically without string concatenation, reducing errors and improving readability.

Installation
------------

.. code-block:: bash

   pip install xpath-builder

Quick Start
-----------

.. code-block:: python

   from xpath_builder import E, STAR, Pred

   # Find all divs with class containing "container"
   xpath = E("div").any().where(
       Pred.attr("class").contains.any_of("container")
   )
   print(xpath.compile())
   # Output: //div[contains(@class, 'container')]

Core Concepts
-------------

Node
^^^^

A ``Node`` represents an element or node test in XPath. Use the ``E()`` shortcut to create nodes:

.. code-block:: python

   from xpath_builder import E, STAR, TEXT, COMMENT

   E("div")      # div element
   E("*")        # any element (or use STAR)
   TEXT          # text() node
   COMMENT       # comment() node

Path
^^^^

A ``Path`` represents a complete XPath expression. Nodes become paths via axis methods:

.. code-block:: python

   E("div").any()      # //div - anywhere in document
   E("div").root()     # /div - at document root
   E("ul").child(E("li"))   # ul/li - direct child
   E("div").desc(E("span")) # div//span - any descendant

Pred (Predicate)
^^^^^^^^^^^^^^^^

``Pred`` builds filter conditions for XPath predicates:

.. code-block:: python

   from xpath_builder import Pred

   # Attribute operations
   Pred.attr("class").contains.any_of("btn", "button")
   Pred.attr("id").startswith.any_of("vue-", "react-")
   Pred.attr("disabled").exists()
   Pred.attr("hidden").missing()

   # Text content
   Pred.text_contains("Hello")
   Pred.text_matches(r"^\d+$")  # regex match

Attribute Operations
--------------------

String Matching
^^^^^^^^^^^^^^^

.. code-block:: python

   # Contains substring
   Pred.attr("class").contains.any_of("nav", "menu")
   Pred.attr("class").contains.all_of("btn", "primary")
   Pred.attr("class").contains.none_of("hidden", "disabled")

   # Token matching (space-separated, like CSS classes)
   Pred.attr("class").contains_tokens.any_of("active", "selected")

   # Starts/ends with
   Pred.attr("id").startswith.any_of("user-", "admin-")
   Pred.attr("href").endswith.any_of(".pdf", ".doc")

   # Regex matching
   Pred.attr("data-id").matches().any_of(r"^\d{4}-\d{2}$")

Numeric Comparisons
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   Pred.attr("data-count").as_num.gt(10)
   Pred.attr("data-count").as_num.between(5, 15)
   Pred.attr("price").as_num.le(99.99)

Case Insensitivity
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # Case-insensitive attribute matching
   Pred.attr("type", case_insensitive=True).as_str.eq("submit")

Combining Predicates
--------------------

Use Python operators to combine predicates:

.. code-block:: python

   # AND: &
   visible = Pred.attr("hidden").missing() & Pred.attr("display").as_str.ne("none")

   # OR: |
   clickable = Pred.attr("href").exists() | Pred.attr("onclick").exists()

   # NOT: .neg()
   not_disabled = Pred.attr("disabled").exists().neg()

Chaining
--------

Build complex selectors by chaining methods:

.. code-block:: python

   from xpath_builder import E, Pred

   selector = (
       E("div")
       .any()
       .where(Pred.attr("class").contains_tokens.any_of("card"))
       .child(E("a"))
       .where(Pred.attr("href").startswith.any_of("https://"))
       .first()
   )

Positional Filtering
--------------------

.. code-block:: python

   E("li").any().first()           # //li[position() = 1]
   E("li").any().nth(3)            # //li[position() = 3]
   E("tr").any().where(
       position_ops().between(2, 5)
   )

Complete Examples
-----------------

Finding Ad Elements
^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from xpath_builder import STAR, Pred

   ad_selector = (
       STAR.any()
       .where(
           Pred.attr("class").contains.any_of(
               "ads", "ad", "advert", "sponsored", "promo"
           )
       )
   )

Finding Empty SVGs
^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from xpath_builder import E, Pred

   empty_svg = (
       E("svg")
       .any()
       .where(
           Pred.attr("width").as_str.eq("0") |
           Pred.attr("height").as_str.eq("0") |
           Pred.attr("aria-hidden").as_str.eq("true")
       )
   )

Finding Framework-Generated IDs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   from xpath_builder import STAR, Pred

   framework_ids = (
       STAR.any()
       .where(
           Pred.attr("id").startswith.any_of(
               "vue-", "react-", "angular-", "svelte-"
           )
       )
   )

API Reference
-------------

Shortcuts
^^^^^^^^^

- ``E(tag)`` - Create a Node for the given element tag
- ``STAR`` - Matches any element (``*``)
- ``TEXT`` - Matches text nodes (``text()``)
- ``COMMENT`` - Matches comment nodes (``comment()``)
- ``NODE`` - Matches any node (``node()``)
- ``ATTR(name)`` - Matches an attribute (``@name``)

Node Methods
^^^^^^^^^^^^

- ``.any()`` → Path - Match anywhere (``//node``)
- ``.root()`` → Path - Match at root (``/node``)
- ``.where(pred)`` → Path - Add predicate filter
- ``.child(node)`` → Path - Direct child axis
- ``.desc(node)`` → Path - Descendant axis

Path Methods
^^^^^^^^^^^^

- ``.where(pred)`` → Path - Add predicate filter
- ``.child(node)`` → Path - Direct child axis
- ``.desc(node)`` → Path - Descendant axis
- ``.first()`` → Path - First match
- ``.nth(n)`` → Path - Nth match
- ``.compile()`` → str - Get the XPath string
- ``.validate()`` - Validate XPath syntax (requires ``elementpath`` or ``lxml``)

Pred Class Methods
^^^^^^^^^^^^^^^^^^

- ``Pred.attr(name, case_insensitive=False)`` - Attribute operations
- ``Pred.text_contains(needle)`` - Text content contains
- ``Pred.text_matches(pattern)`` - Text content regex match
- ``Pred.union(*preds)`` - OR multiple predicates


.. toctree::
   :maxdepth: 2
   :caption: Contents:

