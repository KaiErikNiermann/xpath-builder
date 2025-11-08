from xpath_builder import STAR, Pred

# fmt: off 
ad_class_selector = (
    STAR.any()
    .where(
        Pred.attr("class")
        .contains.any_of(
            "ads",
            "ad",
            "advert",
            "advertisement",
            "sponsored",
            "promo",
            "affiliate",
            "tracking",
            "analytics",
        )
    )
)
# fmt: on