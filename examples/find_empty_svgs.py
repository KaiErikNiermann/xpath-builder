from xpath_builder import Pred, E

# fmt: off 
empty_svg_selector = (
    E("svg")
    .any()
    .where(
        Pred.attr("width").as_str.eq("0") |
        Pred.attr("height").as_str.eq("0") | 
        Pred.attr("aria-hidden").as_str.eq("true") |
        Pred.attr("role").missing() 
    )
)
# fmt: on