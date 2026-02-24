Examples
========

Finding Ad Elements
-------------------

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
------------------

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
--------------------------------

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
