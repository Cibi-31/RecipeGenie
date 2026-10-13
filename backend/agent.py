# ============================================================
# RecipeGenie - Agentic AI
# ============================================================

import json

from langchain_ollama import ChatOllama

from backend.agent_tools import (
    recipe_search_tool,
    dish_search_tool,
    image_cache_tool,
    image_generation_tool,
)


# ============================================================
# LLM
# ============================================================

llm = ChatOllama(
    model="llama3.2",
    temperature=0
)


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are RecipeGenie, an Agentic AI Recipe Assistant.

Your main goal is to help users reduce kitchen food waste.

============================================================
INTENT 1 - LEFTOVER / AVAILABLE INGREDIENTS
============================================================

Examples:

"I have chicken, rice and onion"

"I have tomato, potato and egg"

"What can I make with chicken and rice?"

"I have leftover vegetables"

"What can I cook using these ingredients?"

"chicken,rice,onion,tomato"

"tomato,onion,chicken"

For these requests:

USE:

recipe_search

The recipe_search tool searches the RecipeGenie
recipe dataset using FAISS/RAG.

It returns:

- title
- ingredients
- instructions
- matched ingredients
- missing ingredients
- match count
- match percentage
- recipe coverage
- missing count
- image information

IMPORTANT:

Do NOT generate a new recipe.

Do NOT use dish_search.

Use the dataset results.

============================================================
INTENT 2 - SPECIFIC DISH
============================================================

Examples:

"I want chicken biryani"

"Show me a pizza recipe"

"Give me chicken fried rice"

"How do I make pasta?"

"chicken biryani"

"pizza"

For these requests:

USE:

dish_search

If found:

Return the dataset recipe.

If not found:

Tell the user that the dish was not found
in the RecipeGenie dataset.

Do NOT automatically generate a recipe.

============================================================
IMAGE TOOLS
============================================================

Image tools are optional.

image_cache checks whether an image exists.

image_generation can generate an image if needed.

If image generation fails, the recipe is still valid.

============================================================
IMPORTANT AGENT RULES
============================================================

1. Leftover / available ingredients -> recipe_search.

2. Specific dish -> dish_search.

3. Never use dish_search for ingredient requests.

4. Never generate recipes for leftover ingredients.

5. Never invent dataset results.

6. Use tool results as facts.

7. Do not call the same primary tool twice
   for the same request.

8. Once recipe_search has returned a result,
   do NOT call recipe_search again.

9. Once dish_search has returned a result,
   do NOT call dish_search again.

10. After a successful primary tool result,
    the next action should be final.

11. Never modify the original user request.

12. Never change ingredient text.

13. For ingredient requests, use only the
    recipe_search result as the factual source.

14. For specific dish requests, use only the
    dish_search result as the factual source.

15. Prioritize recipes that use the ingredients
    already available to the user.

16. The purpose is to reduce kitchen food waste.

============================================================
OUTPUT FORMAT
============================================================

When a tool is required:

{
    "action": "tool",
    "tool": "tool_name",
    "input": "tool input"
}

When a tool result already exists:

{
    "action": "final",
    "response": "..."
}

Return ONLY valid JSON.
"""


# ============================================================
# PARSE LLM RESPONSE
# ============================================================

def parse_agent_response(content):

    if isinstance(content, list):
        content = " ".join(
            str(item)
            for item in content
        )

    content = str(content).strip()

    # Remove markdown JSON fences
    content = content.replace(
        "```json",
        ""
    )

    content = content.replace(
        "```",
        ""
    )

    start = content.find("{")
    end = content.rfind("}")

    if start == -1 or end == -1:
        return None

    try:
        return json.loads(
            content[start:end + 1]
        )

    except json.JSONDecodeError:
        return None


# ============================================================
# EXECUTE TOOL
# ============================================================

def execute_tool(
    tool_name,
    tool_input
):

    if tool_name == "recipe_search":

        return recipe_search_tool(
            tool_input
        )

    if tool_name == "dish_search":

        return dish_search_tool(
            tool_input
        )

    if tool_name == "image_cache":

        return image_cache_tool(
            tool_input
        )

    if tool_name == "image_generation":

        return image_generation_tool(
            tool_input
        )

    return {
        "error":
            f"Unknown tool: {tool_name}"
    }


# ============================================================
# GET TOOL RESULT
# ============================================================

def get_tool_result(
    history,
    tool_name
):

    for item in history:

        if item.get("tool") == tool_name:

            return item.get(
                "result"
            )

    return None


# ============================================================
# CHECK WHETHER TOOL WAS ALREADY CALLED
# ============================================================

def tool_was_called(
    history,
    tool_name,
    tool_input
):

    for item in history:

        if (
            item.get("tool") == tool_name
            and
            item.get("input") == tool_input
        ):

            return True

    return False


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(user_query):

    if not user_query:
        return "dish"

    query = str(
        user_query
    ).lower().strip()

    # ========================================================
    # INGREDIENT REQUEST PHRASES
    # ========================================================

    ingredient_phrases = [

        "i have",

        "i've got",

        "i got",

        "i currently have",

        "leftover",

        "left overs",

        "left-over",

        "leftovers",

        "available ingredients",

        "ingredients available",

        "ingredients i have",

        "what can i make",

        "what can i cook",

        "what can i prepare",

        "what recipe can i make",

        "what recipes can i make",

        "what should i make",

        "what should i cook",

        "using these ingredients",

        "with these ingredients",

        "using my ingredients",

        "with my ingredients",

        "use these ingredients",

        "use my ingredients",

    ]

    # ========================================================
    # CHECK INGREDIENT PHRASES
    # ========================================================

    for phrase in ingredient_phrases:

        if phrase in query:

            print(
                "[INTENT DETECTOR] "
                f"Ingredient phrase detected: {phrase}"
            )

            return "ingredients"

    # ========================================================
    # COMMA-SEPARATED INGREDIENT LIST
    # ========================================================

    if "," in query:

        parts = [
            part.strip()
            for part in query.split(",")
            if part.strip()
        ]

        if len(parts) >= 2:

            print(
                "[INTENT DETECTOR] "
                "Comma-separated ingredients"
            )

            return "ingredients"

    # ========================================================
    # AND-SEPARATED INGREDIENT LIST
    # ========================================================

    if " and " in query:

        parts = [
            part.strip()
            for part in query.split(" and ")
            if part.strip()
        ]

        if len(parts) >= 2:

            print(
                "[INTENT DETECTOR] "
                "AND-separated ingredients"
            )

            return "ingredients"

    # ========================================================
    # DEFAULT
    # ========================================================

    print(
        "[INTENT DETECTOR] "
        "Specific dish request"
    )

    return "dish"


# ============================================================
# BUILD INGREDIENT RESPONSE
# ============================================================

def build_ingredient_response(
    recipe_result
):

    if not recipe_result:

        return (
            "I couldn't find a suitable recipe "
            "for your available ingredients."
        )

    recipes = recipe_result.get(
        "recipes",
        []
    )

    if not recipes:

        return (
            "I couldn't find a suitable recipe "
            "for your available ingredients."
        )

    response = (
        "Here are recipes you can make "
        "with your available ingredients:\n\n"
    )

    # ========================================================
    # SHOW TOP 3
    # ========================================================

    for index, recipe in enumerate(
        recipes[:3],
        start=1
    ):

        title = recipe.get(
            "title",
            "Unknown Recipe"
        )

        matched = recipe.get(
            "matched",
            []
        )

        missing = recipe.get(
            "missing",
            []
        )

        # ====================================================
        # IMPORTANT
        #
        # match_percentage means:
        #
        # How many of the USER'S ingredients
        # can be used by this recipe.
        #
        # Example:
        #
        # User:
        # chicken,onion,tomato,garlic
        #
        # Recipe matches all 4:
        #
        # 4 / 4 = 100%
        #
        # recipe_coverage is different:
        #
        # How much of the RECIPE is already
        # available to the user.
        # ====================================================

        percentage = recipe.get(
            "match_percentage",
            0
        )

        recipe_coverage = recipe.get(
            "recipe_coverage",
            0
        )

        missing_count = recipe.get(
            "missing_count",
            len(missing)
        )

        # ----------------------------------------------------
        # Defensive conversion
        # ----------------------------------------------------

        try:
            percentage = float(
                percentage
            )
        except (
            TypeError,
            ValueError
        ):
            percentage = 0

        try:
            recipe_coverage = float(
                recipe_coverage
            )
        except (
            TypeError,
            ValueError
        ):
            recipe_coverage = 0

        # ----------------------------------------------------
        # Make whole numbers display nicely
        # ----------------------------------------------------

        if percentage.is_integer():
            percentage_text = str(
                int(percentage)
            )
        else:
            percentage_text = str(
                percentage
            )

        if recipe_coverage.is_integer():
            coverage_text = str(
                int(recipe_coverage)
            )
        else:
            coverage_text = str(
                recipe_coverage
            )

        # ====================================================
        # RESPONSE
        # ====================================================

        response += (
            f"{index}. {title}\n"
        )

        response += (
            f"   Ingredient match: "
            f"{percentage_text}%\n"
        )

        response += (
            f"   Recipe coverage: "
            f"{coverage_text}%\n"
        )

        if matched:

            response += (
                "   Matched: "
                + ", ".join(
                    str(x)
                    for x in matched
                )
                + "\n"
            )

        else:

            response += (
                "   Matched: None\n"
            )

        if missing:

            response += (
                "   Missing: "
                + ", ".join(
                    str(x)
                    for x in missing
                )
                + "\n"
            )

        else:

            response += (
                "   Missing: None\n"
            )

        response += (
            f"   Missing ingredient count: "
            f"{missing_count}\n"
        )

        response += "\n"

    response += (
        "These recommendations prioritize "
        "recipes that use the ingredients "
        "you already have, helping reduce "
        "food waste."
    )

    return response


# ============================================================
# BUILD DISH RESPONSE
# ============================================================

def build_dish_response(
    recipe
):

    if not recipe:

        return (
            "I couldn't find that recipe "
            "in the RecipeGenie dataset."
        )

    title = recipe.get(
        "title",
        "Recipe"
    )

    ingredients = recipe.get(
        "ingredients",
        ""
    )

    instructions = recipe.get(
        "instructions",
        ""
    )

    return (
        f"{title}\n\n"
        f"Ingredients:\n"
        f"{ingredients}\n\n"
        f"Instructions:\n"
        f"{instructions}"
    )


# ============================================================
# CONTROLLER
# ============================================================

def controller_override(
    decision,
    history,
    user_query,
    intent
):

    recipe_result = get_tool_result(
        history,
        "recipe_search"
    )

    dish_result = get_tool_result(
        history,
        "dish_search"
    )

    # ========================================================
    # INGREDIENT FLOW
    # ========================================================

    if intent == "ingredients":

        # Recipe search has not happened yet

        if recipe_result is None:

            return {
                "action": "tool",

                "tool": "recipe_search",

                "input": user_query
            }

        # Recipe search already completed.
        # Never call it again.

        return {
            "action": "final",

            "response":
                build_ingredient_response(
                    recipe_result
                )
        }

    # ========================================================
    # SPECIFIC DISH FLOW
    # ========================================================

    if intent == "dish":

        # Dish search has not happened yet

        if dish_result is None:

            return {
                "action": "tool",

                "tool": "dish_search",

                "input": user_query
            }

        # Dish found

        if dish_result.get(
            "found"
        ) is True:

            recipe = dish_result.get(
                "recipe",
                {}
            )

            return {
                "action": "final",

                "response":
                    build_dish_response(
                        recipe
                    )
            }

        # Dish not found

        return {
            "action": "final",

            "response":
                (
                    f"I couldn't find "
                    f"'{user_query}' in the "
                    f"RecipeGenie recipe dataset."
                )
        }

    # ========================================================
    # FALLBACK
    # ========================================================

    return decision


# ============================================================
# MAIN AGENT - FAST ROUTING
# ============================================================

def run_agent(
    user_query
):

    print("\n")
    print("=" * 60)
    print("🤖 RECIPEGENIE AGENT")
    print("=" * 60)

    print(
        f"\nUser request: {user_query}"
    )

    # ========================================================
    # FAST INTENT DETECTION
    # ========================================================

    intent = detect_intent(
        user_query
    )

    print(
        f"\n[AGENT] Detected intent: {intent}"
    )

    history = []

    # ========================================================
    # INGREDIENT / LEFTOVER FLOW
    # ========================================================

    if intent == "ingredients":

        print(
            "\n[AGENT] "
            "Fast route → recipe_search"
        )

        print(
            "[AGENT] "
            "Skipping unnecessary LLM call "
            "for initial retrieval."
        )

        # ----------------------------------------------------
        # Execute recipe search exactly once
        # ----------------------------------------------------

        tool_result = execute_tool(
            "recipe_search",
            user_query
        )

        print(
            "\n[TOOL RESULT]"
        )

        print(
            json.dumps(
                tool_result,
                indent=2,
                ensure_ascii=False
            )
        )

        history.append({

            "tool":
                "recipe_search",

            "input":
                user_query,

            "result":
                tool_result

        })

        # ----------------------------------------------------
        # Final response
        # ----------------------------------------------------

        return {

            "success":
                True,

            "response":
                build_ingredient_response(
                    tool_result
                ),

            "history":
                history

        }

    # ========================================================
    # SPECIFIC DISH FLOW
    # ========================================================

    if intent == "dish":

        print(
            "\n[AGENT] "
            "Fast route → dish_search"
        )

        print(
            "[AGENT] "
            "Skipping unnecessary LLM call "
            "for initial retrieval."
        )

        # ----------------------------------------------------
        # Execute dish search exactly once
        # ----------------------------------------------------

        tool_result = execute_tool(
            "dish_search",
            user_query
        )

        print(
            "\n[TOOL RESULT]"
        )

        print(
            json.dumps(
                tool_result,
                indent=2,
                ensure_ascii=False
            )
        )

        history.append({

            "tool":
                "dish_search",

            "input":
                user_query,

            "result":
                tool_result

        })

        # ----------------------------------------------------
        # Dish found
        # ----------------------------------------------------

        if tool_result.get(
            "found"
        ) is True:

            recipe = tool_result.get(
                "recipe",
                {}
            )

            return {

                "success":
                    True,

                "response":
                    build_dish_response(
                        recipe
                    ),

                "history":
                    history

            }

        # ----------------------------------------------------
        # Dish not found
        # ----------------------------------------------------

        return {

            "success":
                True,

            "response":
                (
                    f"I couldn't find "
                    f"'{user_query}' in the "
                    f"RecipeGenie recipe dataset."
                ),

            "history":
                history

        }

    # ========================================================
    # FALLBACK
    # ========================================================

    return {

        "success":
            False,

        "response":
            "Unable to determine the search intent.",

        "history":
            history

    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "=" * 60
    )

    print(
        "RecipeGenie Agent Test"
    )

    print(
        "=" * 60
    )

    query = input(
        "\nWhat would you like to cook? "
    )

    result = run_agent(
        query
    )

    print("\n")

    print(
        "=" * 60
    )

    print(
        "FINAL RESULT"
    )

    print(
        "=" * 60
    )

    print(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        )
    )