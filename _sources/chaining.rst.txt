Chaining
========

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

The chain reads naturally: *find any div with class "card", then its child anchor links starting with "https://", and take the first match*.
