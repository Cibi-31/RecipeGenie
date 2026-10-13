# ============================================================
# RecipeGenie - Agent Tools
# ============================================================

from backend.retriever import (
    search_recipes,
    search_dishes
)

from backend.image_service import (
    generate_food_image,
    get_cached_image
)


# ============================================================
# TOOL 1 - SEARCH RECIPES FROM LEFTOVER INGREDIENTS
# ============================================================

def recipe_search_tool(ingredients: str):

    print("\n[AGENT TOOL] Recipe Search")

    print(
        f"Ingredients: {ingredients}"
    )

    # --------------------------------------------------------
    # Search recipes
    # --------------------------------------------------------

    results = search_recipes(
        ingredients,
        k=10
    )

    if not results:

        print(
            "[AGENT TOOL] No recipes found."
        )

        return {
            "found": False,
            "recipes": []
        }

    recipes = []

    # --------------------------------------------------------
    # Use top 5 results from retriever
    # --------------------------------------------------------

    for result in results[:5]:

        document = result.get(
            "document"
        )

        if document is None:
            continue

        # ----------------------------------------------------
        # Recipe information
        # ----------------------------------------------------

        title = document.metadata.get(
            "title",
            ""
        )

        recipe_ingredients = document.metadata.get(
            "ingredients",
            ""
        )

        instructions = document.metadata.get(
            "instructions",
            ""
        )

        # ----------------------------------------------------
        # Dataset image
        # ----------------------------------------------------

        image_name = document.metadata.get(
            "image_name",
            ""
        )

        # ----------------------------------------------------
        # Matching information
        # ----------------------------------------------------

        matched = result.get(
            "matched",
            []
        )

        missing = result.get(
            "missing",
            []
        )

        match_count = result.get(
            "match_count",
            len(matched)
        )

        match_percentage = result.get(
            "match_percentage",
            0
        )

        # NEW:
        # Percentage of recipe ingredients that
        # are already available to the user.

        recipe_coverage = result.get(
            "recipe_coverage",
            0
        )

        # NEW:
        # Number of recipe ingredients that
        # are missing.

        missing_count = result.get(
            "missing_count",
            len(missing)
        )

        semantic_score = result.get(
            "semantic_score",
            0
        )

        final_score = result.get(
            "final_score",
            0
        )

        # ----------------------------------------------------
        # Debug information
        # ----------------------------------------------------

        print(
            f"[AGENT TOOL] Recipe: {title}"
        )

        print(
            f"[AGENT TOOL] Image: {image_name}"
        )

        print(
            f"[AGENT TOOL] Matched: {matched}"
        )

        print(
            f"[AGENT TOOL] Missing: {missing}"
        )

        print(
            f"[AGENT TOOL] Match: "
            f"{match_percentage}%"
        )

        print(
            f"[AGENT TOOL] Recipe coverage: "
            f"{recipe_coverage}%"
        )

        print(
            f"[AGENT TOOL] Missing count: "
            f"{missing_count}"
        )

        print(
            f"[AGENT TOOL] Final score: "
            f"{final_score}"
        )

        # ----------------------------------------------------
        # Add recipe
        # ----------------------------------------------------

        recipes.append({

            "title":
                title,

            "ingredients":
                recipe_ingredients,

            "instructions":
                instructions,

            # Dataset image name
            "image_name":
                image_name,

            # Frontend compatibility
            "image":
                image_name,

            # Ingredient matching
            "matched":
                matched,

            "missing":
                missing,

            "match_count":
                match_count,

            "match_percentage":
                match_percentage,

            # NEW ranking information
            "recipe_coverage":
                recipe_coverage,

            "missing_count":
                missing_count,

            "semantic_score":
                semantic_score,

            "final_score":
                final_score,

            # Source information
            "source":
                "dataset"
        })

    # --------------------------------------------------------
    # Final result
    # --------------------------------------------------------

    if not recipes:

        return {
            "found": False,
            "recipes": []
        }

    return {

        "found":
            True,

        "recipes":
            recipes
    }


# ============================================================
# TOOL 2 - SEARCH SPECIFIC DISH
# ============================================================

def dish_search_tool(dish_name: str):

    print("\n[AGENT TOOL] Dish Search")

    print(
        f"Dish: {dish_name}"
    )

    results = search_dishes(
        dish_name,
        k=10
    )

    if not results:

        return {

            "found":
                False,

            "recipe":
                None
        }

    # --------------------------------------------------------
    # Import only when called.
    #
    # This prevents circular import problems during startup.
    # --------------------------------------------------------

    from backend.main import (
        is_reasonable_dish_match
    )

    # --------------------------------------------------------
    # Validate dataset results
    # --------------------------------------------------------

    for result in results:

        document = result.get(
            "document"
        )

        if document is None:
            continue

        title = document.metadata.get(
            "title",
            ""
        )

        # ----------------------------------------------------
        # Make sure title is actually related to query
        # ----------------------------------------------------

        if not is_reasonable_dish_match(
            dish_name,
            title
        ):

            continue

        ingredients = document.metadata.get(
            "ingredients",
            ""
        )

        instructions = document.metadata.get(
            "instructions",
            ""
        )

        image_name = document.metadata.get(
            "image_name",
            ""
        )

        print(
            f"[AGENT TOOL] "
            f"Valid dataset match: {title}"
        )

        print(
            f"[AGENT TOOL] "
            f"Image: {image_name}"
        )

        return {

            "found":
                True,

            "recipe": {

                "title":
                    title,

                "ingredients":
                    ingredients,

                "instructions":
                    instructions,

                "image_name":
                    image_name,

                "image":
                    image_name,

                "source":
                    "dataset"
            }
        }

    # --------------------------------------------------------
    # No valid dish found
    # --------------------------------------------------------

    print(
        "[AGENT TOOL] "
        "No valid dataset dish found."
    )

    return {

        "found":
            False,

        "recipe":
            None
    }


# ============================================================
# TOOL 3 - IMAGE CACHE
# ============================================================

def image_cache_tool(
    dish_name: str
):

    print("\n[AGENT TOOL] Image Cache")

    print(
        f"Dish: {dish_name}"
    )

    image = get_cached_image(
        dish_name
    )

    if image:

        print(
            "[AGENT TOOL] "
            "Cached image found."
        )

        return {

            "exists":
                True,

            "image":
                image,

            "dish":
                dish_name
        }

    print(
        "[AGENT TOOL] "
        "No cached image."
    )

    return {

        "exists":
            False,

        "image":
            "",

        "dish":
            dish_name
    }


# ============================================================
# TOOL 4 - IMAGE GENERATION
# ============================================================

def image_generation_tool(
    dish_name: str
):

    print("\n[AGENT TOOL] Image Generation")

    print(
        f"Dish: {dish_name}"
    )

    try:

        image = generate_food_image(
            dish_name
        )

    except Exception as e:

        print(
            "[AGENT TOOL] "
            f"Image generation error: {e}"
        )

        return {

            "success":
                False,

            "image":
                "",

            "dish":
                dish_name,

            "error":
                str(e)
        }

    if image:

        print(
            "[AGENT TOOL] "
            "Image generated successfully."
        )

        return {

            "success":
                True,

            "image":
                image,

            "dish":
                dish_name
        }

    print(
        "[AGENT TOOL] "
        "Image generation failed."
    )

    return {

        "success":
            False,

        "image":
            "",

        "dish":
            dish_name,

        "error":
            "Image generation unavailable"
    }