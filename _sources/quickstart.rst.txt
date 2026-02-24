Quick Start
===========

Build your first XPath expression in three steps.

1. Import the essentials
------------------------

.. code-block:: python

   from xpath_builder import E, STAR, Pred

2. Build an expression
----------------------

.. code-block:: python

   # Find all divs with class containing "container"
   xpath = E("div").any().where(
       Pred.attr("class").contains.any_of("container")
   )

3. Compile to a string
----------------------

.. code-block:: python

   print(xpath.compile())
   # //div[contains(@class, 'container')]

The general pattern is: **create a node** → **set an axis** → **add predicates** → **compile**.
