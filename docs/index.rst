xpath-builder
=============

A fluent, type-safe Python DSL for building XPath 2.0 expressions.

**xpath-builder** helps you construct complex XPath queries programmatically
without string concatenation, reducing errors and improving readability.

.. code-block:: python

   from xpath_builder import E, Pred

   xpath = E("div").any().where(
       Pred.attr("class").contains.any_of("container")
   )
   print(xpath.compile())
   # //div[contains(@class, 'container')]

.. toctree::
   :maxdepth: 2
   :caption: Getting Started

   installation
   quickstart

.. toctree::
   :maxdepth: 2
   :caption: User Guide

   core-concepts
   predicates
   chaining
   examples

.. toctree::
   :maxdepth: 2
   :caption: Reference

   api
