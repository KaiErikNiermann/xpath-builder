Core Concepts
=============

Node
----

A ``Node`` represents an element or node test in XPath. Use the ``E()`` shortcut to create nodes:

.. code-block:: python

   from xpath_builder import E, STAR, TEXT, COMMENT

   E("div")      # div element
   E("*")        # any element (or use STAR)
   TEXT          # text() node
   COMMENT       # comment() node

Path
----

A ``Path`` represents a complete XPath expression. Nodes become paths via axis methods:

.. code-block:: python

   E("div").any()            # //div - anywhere in document
   E("div").root()           # /div - at document root
   E("ul").child(E("li"))    # ul/li - direct child
   E("div").desc(E("span"))  # div//span - any descendant

Positional Filtering
--------------------

.. code-block:: python

   E("li").any().first()           # //li[position() = 1]
   E("li").any().nth(3)            # //li[position() = 3]
   E("tr").any().where(
       position_ops().between(2, 5)
   )
