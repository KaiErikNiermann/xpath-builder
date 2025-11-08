from xpath_builder import Pred, STAR

# fmt: off
id_str_selector = (
    STAR.any()
    .where(
        Pred.attr("id")
        .startswith.any_of(
            "vue-",
            "angular-",
            "svelte-",
            "lit-",
            "astro-",
            "preact-",
            "solid-",
        )
    )
)
# fmt: on