Predicates
==========

``Pred`` builds filter conditions for XPath predicates.

Attribute Operations
--------------------

.. code-block:: python

   from xpath_builder import Pred

   Pred.attr("class").contains.any_of("btn", "button")
   Pred.attr("id").startswith.any_of("vue-", "react-")
   Pred.attr("disabled").exists()
   Pred.attr("hidden").missing()

Text Content
------------

.. code-block:: python

   Pred.text_contains("Hello")
   Pred.text_matches(r"^\d+$")  # regex match

String Matching
---------------

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
-------------------

.. code-block:: python

   Pred.attr("data-count").as_num.gt(10)
   Pred.attr("data-count").as_num.between(5, 15)
   Pred.attr("price").as_num.le(99.99)

Case Insensitivity
------------------

.. code-block:: python

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
