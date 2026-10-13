# ============================================================
# RecipeGenie - Retriever
# FAISS + Ingredient Matching + Recipe Ranking
# ============================================================

import ast
import re

from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings


# ============================================================
# FAISS INDEX
# ============================================================

FAISS_PATH = "./faiss_index"


def get_vector_store():
    """
    Load the existing FAISS vector store.

    The FAISS index is NOT rebuilt here.
    """

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )

    vector_store = FAISS.load_local(
        FAISS_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )

    return vector_store


# ============================================================
# BASIC WORD NORMALIZATION
# ============================================================

SPECIAL_CASES = {

    # Vegetables
    "tomatoes": "tomato",
    "tomato": "tomato",

    "potatoes": "potato",
    "potato": "potato",

    "onions": "onion",
    "onion": "onion",

    "carrots": "carrot",
    "carrot": "carrot",

    "peppers": "pepper",
    "pepper": "pepper",

    "chillies": "chilli",
    "chilies": "chilli",
    "chilis": "chilli",
    "chilli": "chilli",
    "chili": "chilli",

    "capsicums": "capsicum",
    "capsicum": "capsicum",

    "eggplants": "eggplant",
    "aubergines": "eggplant",
    "aubergine": "eggplant",

    # Meat
    "chickens": "chicken",
    "chicken": "chicken",

    "muttons": "mutton",
    "mutton": "mutton",

    "beefs": "beef",
    "beef": "beef",

    "porks": "pork",
    "pork": "pork",

    "fishes": "fish",
    "fish": "fish",

    "prawns": "prawn",
    "prawn": "prawn",

    "shrimps": "shrimp",
    "shrimp": "shrimp",

    # Eggs
    "eggs": "egg",
    "egg": "egg",

    # Rice
    "rices": "rice",
    "rice": "rice",

    # Gelatin spelling variants
    "gelatine": "gelatin",
    "gelatin": "gelatin",

    # Fruits
    "oranges": "orange",
    "orange": "orange",

    "apples": "apple",
    "apple": "apple",

    "bananas": "banana",
    "banana": "banana",

    "mangoes": "mango",
    "mangos": "mango",
    "mango": "mango",

    # Common dish terms
    "briyani": "biryani",
    "biriyani": "biryani",
    "briani": "biryani",
    "biryani": "biryani",

    "noodles": "noodle",
    "noodle": "noodle",

    "pastas": "pasta",
    "pasta": "pasta",

    "curries": "curry",
    "curry": "curry",

    "dosas": "dosa",
    "dosa": "dosa",

    "idlis": "idli",
    "idli": "idli",

    "rotis": "roti",
    "roti": "roti",

    "chapatis": "chapati",
    "chapati": "chapati",

    "parathas": "paratha",
    "paratha": "paratha",
}


def normalize_word(word):
    """
    Normalize one word conservatively.
    """

    if not word:
        return ""

    word = str(word).lower().strip()

    word = word.strip(
        ".,!?;:()[]{}\"'"
    )

    if word in SPECIAL_CASES:
        return SPECIAL_CASES[word]

    # Conservative plural handling
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"

    if len(word) > 5 and word.endswith("oes"):
        return word[:-2]

    if len(word) > 4 and word.endswith("s"):
        return word[:-1]

    return word


# ============================================================
# INGREDIENT VARIANTS
# ============================================================

INGREDIENT_VARIANTS = {

    "chicken": {
        "chicken",
        "chicken breast",
        "chicken thigh",
        "chicken leg",
        "chicken drumstick",
    },

    "rice": {
        "rice",
        "basmati rice",
        "white rice",
        "long grain rice",
        "short grain rice",
    },

    "onion": {
        "onion",
        "red onion",
        "yellow onion",
        "white onion",
        "sweet onion",
    },

    "tomato": {
        "tomato",
        "diced tomato",
        "whole tomato",
        "fresh tomato",
        "cherry tomato",
    },

    "potato": {
        "potato",
        "russet potato",
        "red potato",
        "yukon gold potato",
    },

    "carrot": {
        "carrot",
        "baby carrot",
    },

    "pepper": {
        "pepper",
        "bell pepper",
        "red pepper",
        "green pepper",
        "yellow pepper",
    },

    "egg": {
        "egg",
        "large egg",
        "medium egg",
    },

    "orange": {
        "orange",
        "navel orange",
        "blood orange",
    },

    "milk": {
        "milk",
        "whole milk",
        "skim milk",
        "low fat milk",
        "2 percent milk",
    },

    "gelatin": {
        "gelatin",
        "unflavored gelatin",
        "gelatin powder",
    },
}


# ============================================================
# USER INPUT STOPWORDS
# ============================================================

INGREDIENT_STOPWORDS = {
    "i",
    "ive",
    "i've",
    "got",
    "have",
    "has",
    "had",
    "am",
    "im",
    "i'm",
    "having",
    "my",
    "the",
    "a",
    "an",
    "some",
    "few",
    "little",
    "lot",
    "lots",
    "of",
    "and",
    "or",
    "with",
    "without",
    "these",
    "those",
    "ingredient",
    "ingredients",
    "available",
    "leftover",
    "leftovers",
    "please",
    "give",
    "show",
    "me",
    "what",
    "can",
    "could",
    "make",
    "cook",
    "prepare",
    "recipe",
    "recipes",
    "using",
    "use",
    "from",
}


# ============================================================
# MEASUREMENT UNITS
# ============================================================

UNITS = {
    "cup",
    "cups",
    "tablespoon",
    "tablespoons",
    "tbsp",
    "tbs",
    "teaspoon",
    "teaspoons",
    "tsp",
    "gram",
    "grams",
    "g",
    "kilogram",
    "kilograms",
    "kg",
    "milligram",
    "milligrams",
    "mg",
    "milliliter",
    "milliliters",
    "ml",
    "liter",
    "liters",
    "litre",
    "litres",
    "l",
    "ounce",
    "ounces",
    "oz",
    "pound",
    "pounds",
    "lb",
    "lbs",
    "piece",
    "pieces",
    "slice",
    "slices",
    "sprig",
    "sprigs",
    "packet",
    "packets",
    "package",
    "packages",
    "jar",
    "jars",
    "bottle",
    "bottles",
    "box",
    "boxes",
    "bunch",
    "bunches",
    "pinch",
    "pinches",
}


# ============================================================
# QUANTITY / SIZE WORDS
# ============================================================

QUANTITY_WORDS = {
    "small",
    "medium",
    "large",
    "extra",
    "about",
    "approximately",
    "heaping",
    "level",
    "scant",
}


# ============================================================
# PREPARATION WORDS
# ============================================================

PREPARATION_WORDS = {
    "chopped",
    "finely",
    "roughly",
    "diced",
    "sliced",
    "minced",
    "crushed",
    "grated",
    "peeled",
    "fresh",
    "freshly",
    "ground",
    "roasted",
    "cooked",
    "boiled",
    "fried",
    "thinly",
    "thickly",
    "softened",
    "melted",
    "drained",
    "rinsed",
    "thawed",
    "quartered",
    "halved",
    "smashed",
    "torn",
    "shaved",
    "coarsely",
    "beaten",
    "seeded",
    "cored",
    "trimmed",
    "divided",
    "cracked",
    "cubed",
    "shredded",
    "julienned",
    "pitted",
    "deveined",
    "boneless",
    "skinless",
}


# ============================================================
# DERIVED INGREDIENTS
# ============================================================

# These must NOT be considered equivalent.
#
# chicken != chicken broth
# tomato != tomato paste
# rice != rice flour
# ============================================================

BLOCKED_DERIVATIVES = {

    "chicken": {
        "chicken broth",
        "chicken stock",
        "chicken bouillon",
        "chicken soup",
    },

    "beef": {
        "beef broth",
        "beef stock",
        "beef bouillon",
    },

    "vegetable": {
        "vegetable broth",
        "vegetable stock",
    },

    "tomato": {
        "tomato paste",
        "tomato sauce",
        "tomato puree",
        "tomato ketchup",
        "tomato juice",
    },

    "potato": {
        "potato starch",
        "potato flour",
    },

    "rice": {
        "rice flour",
        "rice vinegar",
        "rice wine",
        "rice syrup",
        "rice milk",
    },

    "corn": {
        "corn starch",
        "cornstarch",
        "corn syrup",
        "corn flour",
    },

    "apple": {
        "apple juice",
        "apple cider",
        "apple vinegar",
        "apple cider vinegar",
    },
}


# ============================================================
# REMOVE QUANTITIES
# ============================================================

def remove_quantities(text):

    if not text:
        return ""

    # Unicode fractions
    text = re.sub(
        r"[¼½¾⅓⅔⅛⅜⅝⅞]",
        " ",
        text
    )

    # Fractions such as 1/2
    text = re.sub(
        r"\b\d+\s*/\s*\d+\b",
        " ",
        text
    )

    # Mixed / normal numbers
    text = re.sub(
        r"\b\d+(?:\.\d+)?\b",
        " ",
        text
    )

    return text


# ============================================================
# NORMALIZE TEXT
# ============================================================

def basic_normalize(text):

    if not text:
        return ""

    text = str(text).lower()

    text = text.replace(
        "’",
        "'"
    )

    text = text.replace(
        "&",
        " and "
    )

    text = re.sub(
        r"[^a-z0-9\s\-']",
        " ",
        text
    )

    text = text.replace(
        "-",
        " "
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# CLEAN ONE RECIPE INGREDIENT
# ============================================================

def clean_recipe_ingredient(ingredient):

    if not ingredient:
        return ""

    text = str(ingredient).lower().strip()

    # --------------------------------------------------------
    # Remove parenthetical notes
    # --------------------------------------------------------

    text = re.sub(
        r"\([^)]*\)",
        " ",
        text
    )

    # --------------------------------------------------------
    # Remove labels
    # --------------------------------------------------------

    text = re.sub(
        r"^(?:garnish|accompaniment|for serving)\s*:\s*",
        "",
        text,
        flags=re.I
    )

    # --------------------------------------------------------
    # Keep ingredient portion before comma.
    #
    # Examples:
    # chicken breast, boneless and skinless
    # onion, chopped
    # tomato, diced
    # --------------------------------------------------------

    if "," in text:
        text = text.split(",", 1)[0]

    # --------------------------------------------------------
    # Remove optional / serving phrases
    # --------------------------------------------------------

    text = re.sub(
        r"\bplus\s+(?:more|additional).*$",
        " ",
        text
    )

    text = re.sub(
        r"\bfor\s+(?:serving|garnish|garnishing|drizzling).*$",
        " ",
        text
    )

    text = re.sub(
        r"\bas\s+needed\b",
        " ",
        text
    )

    text = re.sub(
        r"\bto\s+taste\b",
        " ",
        text
    )

    text = re.sub(
        r"\bif\s+using\b",
        " ",
        text
    )

    text = re.sub(
        r"\boptional\b",
        " ",
        text
    )

    # --------------------------------------------------------
    # Remove quantities
    # --------------------------------------------------------

    text = remove_quantities(text)

    # --------------------------------------------------------
    # Normalize punctuation
    # --------------------------------------------------------

    text = basic_normalize(text)

    if not text:
        return ""

    words = text.split()

    cleaned_words = []

    for word in words:

        normalized = normalize_word(word)

        if not normalized:
            continue

        if normalized in UNITS:
            continue

        if normalized in QUANTITY_WORDS:
            continue

        if normalized in PREPARATION_WORDS:
            continue

        # Packaging words
        if normalized in {
            "can",
            "cans",
            "clove",
            "cloves",
            "envelope",
            "envelopes",
            "packet",
            "packets",
        }:
            continue

        cleaned_words.append(
            normalized
        )

    text = " ".join(
        cleaned_words
    )

    # --------------------------------------------------------
    # Remove common remaining descriptive phrases
    # --------------------------------------------------------

    descriptive_patterns = [
        r"\bcut into.*$",
        r"\bcut in.*$",
        r"\bcut lengthwise.*$",
        r"\bcut crosswise.*$",
        r"\bplus.*$",
        r"\bmore for.*$",
        r"\bpreferably.*$",
        r"\bsuch as.*$",
        r"\bor another.*$",
    ]

    for pattern in descriptive_patterns:

        text = re.sub(
            pattern,
            "",
            text
        )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# NORMALIZE USER INGREDIENT
# ============================================================

def clean_user_ingredient(text):

    if not text:
        return ""

    text = basic_normalize(
        text
    )

    words = []

    for word in text.split():

        word = normalize_word(
            word
        )

        if not word:
            continue

        if word in INGREDIENT_STOPWORDS:
            continue

        words.append(
            word
        )

    return " ".join(
        words
    ).strip()


# ============================================================
# PARSE USER INGREDIENTS
# ============================================================

def parse_user_ingredients(text):

    if not text:
        return []

    text = str(
        text
    ).lower().strip()

    # --------------------------------------------------------
    # Remove conversational prefixes
    # --------------------------------------------------------

    prefixes = [
        "i have got ",
        "i've got ",
        "i have ",
        "i got ",
        "i currently have ",
        "i currently got ",
        "i am having ",
        "i'm having ",
        "my ingredients are ",
        "my ingredients include ",
        "ingredients are ",
        "ingredients include ",
        "available ingredients are ",
        "available ingredients include ",
        "leftover ingredients are ",
        "leftover ingredients include ",
        "what can i make with ",
        "what can i cook with ",
        "what can i prepare with ",
        "what recipe can i make with ",
        "what recipes can i make with ",
        "what recipe can i cook with ",
        "what recipes can i cook with ",
        "what can i make using ",
        "what can i cook using ",
        "what can i prepare using ",
        "recipes using ",
        "recipes with ",
        "recipe using ",
        "recipe with ",
    ]

    for prefix in prefixes:

        if text.startswith(prefix):

            text = text[
                len(prefix):
            ]

            break

    # --------------------------------------------------------
    # Convert AND / & to separators
    # --------------------------------------------------------

    text = re.sub(
        r"\s+\band\b\s+",
        ",",
        text,
        flags=re.I
    )

    text = text.replace(
        "&",
        ","
    )

    # --------------------------------------------------------
    # Split ingredients
    # --------------------------------------------------------

    raw_items = text.split(
        ","
    )

    ingredients = []

    seen = set()

    for item in raw_items:

        ingredient = clean_user_ingredient(
            item
        )

        if not ingredient:
            continue

        if ingredient not in seen:

            ingredients.append(
                ingredient
            )

            seen.add(
                ingredient
            )

    print(
        "[DEBUG] Parsed ingredients:",
        ingredients
    )

    return ingredients


# ============================================================
# PARSE DATASET INGREDIENT LIST
# ============================================================

def parse_raw_recipe_list(ingredient_text):

    if ingredient_text is None:
        return []

    # Already a Python list
    if isinstance(
        ingredient_text,
        (list, tuple)
    ):

        return [
            str(item)
            for item in ingredient_text
            if item
        ]

    text = str(
        ingredient_text
    ).strip()

    if not text:
        return []

    # Dataset normally stores Python lists as strings.
    #
    # Example:
    # ['1 onion, diced', '1 pound chicken breast']
    #
    # literal_eval preserves individual entries correctly.

    try:

        parsed = ast.literal_eval(
            text
        )

        if isinstance(
            parsed,
            (list, tuple)
        ):

            return [
                str(item)
                for item in parsed
                if item
            ]

    except (
        ValueError,
        SyntaxError
    ):

        pass

    # Fallback
    if "\n" in text:

        return [
            item.strip(" -•")
            for item in text.splitlines()
            if item.strip(" -•")
        ]

    # Last-resort fallback
    return [
        text
    ]


# ============================================================
# GET CLEAN RECIPE INGREDIENTS
# ============================================================

def get_recipe_ingredients(
    ingredient_text
):

    raw_ingredients = parse_raw_recipe_list(
        ingredient_text
    )

    cleaned = []

    seen = set()

    for raw in raw_ingredients:

        ingredient = clean_recipe_ingredient(
            raw
        )

        if not ingredient:
            continue

        if ingredient not in seen:

            cleaned.append(
                ingredient
            )

            seen.add(
                ingredient
            )

    return cleaned


# ============================================================
# PHRASE UTILITIES
# ============================================================

def contains_phrase(
    text,
    phrase
):

    text_words = text.split()
    phrase_words = phrase.split()

    if not text_words or not phrase_words:
        return False

    length = len(
        phrase_words
    )

    for i in range(
        len(text_words) - length + 1
    ):

        if (
            text_words[
                i:i + length
            ]
            ==
            phrase_words
        ):

            return True

    return False


# ============================================================
# CHECK WHETHER RECIPE INGREDIENT IS BLOCKED
# ============================================================

def is_blocked_derivative(
    user,
    recipe
):

    blocked_phrases = (
        BLOCKED_DERIVATIVES.get(
            user,
            set()
        )
    )

    for blocked in blocked_phrases:

        if contains_phrase(
            recipe,
            blocked
        ):

            return True

    return False


# ============================================================
# INGREDIENT VARIANT CHECK
# ============================================================

def is_variant_match(
    user,
    recipe
):

    """
    Check known ingredient variants.

    Example:
        chicken -> chicken breast
        rice -> basmati rice
        onion -> red onion
    """

    for base, variants in INGREDIENT_VARIANTS.items():

        if user == base and recipe in variants:
            return True

        if recipe == base and user in variants:
            return True

        if user in variants and recipe in variants:
            return True

    return False


# ============================================================
# CORE INGREDIENT MATCHER
# ============================================================

def ingredient_matches(
    user_ingredient,
    recipe_ingredient
):

    user = clean_user_ingredient(
        user_ingredient
    )

    recipe = clean_recipe_ingredient(
        recipe_ingredient
    )

    if not user or not recipe:
        return False

    # --------------------------------------------------------
    # 1. Exact match
    # --------------------------------------------------------

    if user == recipe:
        return True

    # --------------------------------------------------------
    # 2. Block transformed / derived ingredients
    # --------------------------------------------------------

    if is_blocked_derivative(
        user,
        recipe
    ):

        return False

    # --------------------------------------------------------
    # 3. Known ingredient variants
    # --------------------------------------------------------

    if is_variant_match(
        user,
        recipe
    ):

        return True

    # --------------------------------------------------------
    # 4. Single basic ingredient
    #
    # chicken -> chicken breast
    # rice -> basmati rice
    # tomato -> whole tomato
    # onion -> red onion
    # --------------------------------------------------------

    user_words = user.split()
    recipe_words = recipe.split()

    if len(user_words) == 1:

        target = user_words[0]

        if target in recipe_words:
            return True

    # --------------------------------------------------------
    # 5. Multi-word user ingredient
    #
    # bell pepper -> red bell pepper
    # chicken breast -> skinless chicken breast
    # --------------------------------------------------------

    if contains_phrase(
        recipe,
        user
    ):

        return True

    # --------------------------------------------------------
    # 6. Reverse phrase
    #
    # User:
    # red onion
    #
    # Recipe:
    # onion
    # --------------------------------------------------------

    if contains_phrase(
        user,
        recipe
    ):

        if not is_blocked_derivative(
            recipe,
            user
        ):

            return True

    return False


# ============================================================
# CALCULATE RECIPE MATCH
# ============================================================

def calculate_recipe_match(
    user_ingredients,
    recipe_ingredients
):

    matched = []
    missing = []

    # ========================================================
    # USER -> RECIPE
    #
    # Which ingredients supplied by the user are present
    # in the recipe?
    # ========================================================

    for user_ingredient in user_ingredients:

        found = False

        for recipe_ingredient in recipe_ingredients:

            if ingredient_matches(
                user_ingredient,
                recipe_ingredient
            ):

                found = True
                break

        if found:
            matched.append(
                user_ingredient
            )

    # ========================================================
    # RECIPE -> USER
    #
    # Which recipe ingredients are NOT available?
    # ========================================================

    for recipe_ingredient in recipe_ingredients:

        found = False

        for user_ingredient in user_ingredients:

            if ingredient_matches(
                user_ingredient,
                recipe_ingredient
            ):

                found = True
                break

        if not found:

            missing.append(
                recipe_ingredient
            )

    # Remove duplicates
    matched = list(
        dict.fromkeys(
            matched
        )
    )

    missing = list(
        dict.fromkeys(
            missing
        )
    )

    # ========================================================
    # INGREDIENT MATCH %
    #
    # Percentage of USER ingredients found in recipe.
    #
    # User:
    #   orange, milk
    #
    # Recipe:
    #   orange, milk, sugar, egg
    #
    # Match = 2 / 2 = 100%
    # ========================================================

    total_user = len(
        user_ingredients
    )

    match_count = len(
        matched
    )

    if total_user:

        match_percentage = round(
            (
                match_count /
                total_user
            ) * 100,
            1
        )

    else:

        match_percentage = 0.0

    # ========================================================
    # RECIPE COVERAGE %
    #
    # Percentage of the COMPLETE RECIPE ingredients
    # that the user already has.
    #
    # User:
    #   orange, milk
    #
    # Recipe:
    #   orange, milk, sugar, egg
    #
    # Coverage = 2 / 4 = 50%
    # ========================================================

    total_recipe = len(
        recipe_ingredients
    )

    if total_recipe:

        recipe_coverage = round(
            (
                match_count /
                total_recipe
            ) * 100,
            1
        )

    else:

        recipe_coverage = 0.0

    return (
        matched,
        missing,
        match_count,
        match_percentage,
        recipe_coverage
    )


# ============================================================
# INGREDIENT RECIPE SEARCH
# ============================================================

def search_recipes(
    query,
    k=10
):

    vector_store = get_vector_store()

    # ========================================================
    # PARSE USER INPUT
    # ========================================================

    user_ingredients = (
        parse_user_ingredients(
            query
        )
    )

    print(
        "[SEARCH] User ingredients:",
        user_ingredients
    )

    if not user_ingredients:
        return []

    # ========================================================
    # SEMANTIC QUERY
    # ========================================================

    search_query = " ".join(
        user_ingredients
    )

    # ========================================================
    # FAISS CANDIDATE GENERATION
    #
    # FAISS performs semantic retrieval.
    # Structured ingredient matching performs final ranking.
    # ========================================================

    candidate_count = max(
        k * 30,
        300
    )

    documents = (
        vector_store.similarity_search(
            search_query,
            k=candidate_count
        )
    )

    results = []

    # ========================================================
    # SCORE CANDIDATES
    # ========================================================

    for document in documents:

        recipe_ingredient_text = (
            document.metadata.get(
                "ingredients",
                ""
            )
        )

        recipe_ingredients = (
            get_recipe_ingredients(
                recipe_ingredient_text
            )
        )

        if not recipe_ingredients:
            continue

        (
            matched,
            missing,
            match_count,
            match_percentage,
            recipe_coverage
        ) = calculate_recipe_match(
            user_ingredients,
            recipe_ingredients
        )

        # Ignore recipes that don't contain any
        # of the user's ingredients.
        if match_count == 0:
            continue

        missing_count = len(
            missing
        )

        # ====================================================
        # RANKING
        #
        # Primary:
        #   Number of user's ingredients used.
        #
        # Secondary:
        #   Percentage of user's ingredients matched.
        #
        # Third:
        #   Percentage of recipe already covered.
        #
        # Fourth:
        #   Fewer missing ingredients.
        # ====================================================

        final_score = (
            match_count * 100000
            + match_percentage * 1000
            + recipe_coverage * 100
            - missing_count * 25
        )

        # Strong preference for recipes
        # using ALL user ingredients.
        if match_percentage == 100:
            final_score += 50000

        # Prefer recipes where user already has
        # most of the required ingredients.
        if recipe_coverage >= 75:

            final_score += 10000

        elif recipe_coverage >= 50:

            final_score += 5000

        # Penalize recipes with too many extras.
        if missing_count > 10:

            final_score -= (
                missing_count * 100
            )

        results.append({

            "document":
                document,

            "matched":
                matched,

            "missing":
                missing,

            "match_count":
                match_count,

            "match_percentage":
                match_percentage,

            "recipe_coverage":
                recipe_coverage,

            "missing_count":
                missing_count,

            "semantic_score":
                0,

            "final_score":
                final_score
        })

    # ========================================================
    # SORT
    # ========================================================

    results.sort(
        key=lambda x: (
            x["match_count"],
            x["match_percentage"],
            x["recipe_coverage"],
            -x["missing_count"],
            x["final_score"]
        ),
        reverse=True
    )

    # ========================================================
    # REMOVE DUPLICATE TITLES
    # ========================================================

    unique_results = []

    seen_titles = set()

    for result in results:

        document = result[
            "document"
        ]

        title = document.metadata.get(
            "title",
            ""
        )

        title_key = (
            str(title)
            .lower()
            .strip()
        )

        if not title_key:
            continue

        if title_key in seen_titles:
            continue

        seen_titles.add(
            title_key
        )

        unique_results.append(
            result
        )

        if len(
            unique_results
        ) >= k:

            break

    # ========================================================
    # DEBUG OUTPUT
    # ========================================================

    print(
        "\n[SEARCH RESULTS]"
    )

    for result in unique_results:

        document = result[
            "document"
        ]

        title = document.metadata.get(
            "title",
            ""
        )

        print(
            f"\n{title}"
        )

        print(
            "Matched:",
            result["matched"]
        )

        print(
            "Missing:",
            result["missing"]
        )

        print(
            "Match:",
            f'{result["match_percentage"]}%'
        )

        print(
            "Recipe coverage:",
            f'{result["recipe_coverage"]}%'
        )

        print(
            "Missing count:",
            result["missing_count"]
        )

        print(
            "Final score:",
            result["final_score"]
        )

    return unique_results


# ============================================================
# DISH NORMALIZATION
# ============================================================

def normalize_dish_text(
    text
):

    if not text:
        return []

    text = str(
        text
    ).lower()

    text = re.sub(
        r"[^a-zA-Z0-9\s]",
        " ",
        text
    )

    words = []

    for word in text.split():

        normalized = normalize_word(
            word
        )

        if normalized:

            words.append(
                normalized
            )

    return words


# ============================================================
# SPECIFIC DISH SEARCH
# ============================================================

def search_dishes(
    query,
    k=10
):

    vector_store = get_vector_store()

    query_words = normalize_dish_text(
        query
    )

    if not query_words:
        return []

    query_set = set(
        query_words
    )

    query_text = " ".join(
        query_words
    )

    results = []

    # ========================================================
    # TITLE SEARCH
    # ========================================================

    for document in (
        vector_store.docstore._dict.values()
    ):

        title = document.metadata.get(
            "title",
            ""
        )

        if not title:
            continue

        title_words = normalize_dish_text(
            title
        )

        if not title_words:
            continue

        title_set = set(
            title_words
        )

        title_text = " ".join(
            title_words
        )

        matched_words = (
            query_set.intersection(
                title_set
            )
        )

        if not matched_words:
            continue

        # ====================================================
        # SCORE TITLE
        # ====================================================

        score = 0

        # Exact title match
        if query_text == title_text:

            score += 2000

        # Query phrase inside title
        elif query_text in title_text:

            score += 1500

        # All query words are in title
        if query_set.issubset(
            title_set
        ):

            score += 1000

        # Number of matched words
        score += (
            len(matched_words)
            * 200
        )

        # Penalize excessive extra words
        extra_words = (
            title_set -
            query_set
        )

        score -= (
            len(extra_words)
            * 5
        )

        results.append({

            "document":
                document,

            "title_score":
                score,

            "final_score":
                score
        })

    results.sort(
        key=lambda x:
            x["final_score"],
        reverse=True
    )

    return results[:k]


# ============================================================
# DIRECT TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n========== RETRIEVER TEST =========="
    )

    # --------------------------------------------------------
    # User input parsing test
    # --------------------------------------------------------

    test_query = (
        "I have chicken, rice, onion and tomato"
    )

    print(
        "\nInput:",
        test_query
    )

    parsed = parse_user_ingredients(
        test_query
    )

    print(
        "Parsed:",
        parsed
    )

    # --------------------------------------------------------
    # Ingredient matching tests
    # --------------------------------------------------------

    print(
        "\n--- MATCH TESTS ---"
    )

    tests = [

        ("chicken", "chicken breast", True),

        ("chicken", "chicken thigh", True),

        ("chicken", "chicken broth", False),

        ("tomato", "diced tomato", True),

        ("tomato", "tomato paste", False),

        ("rice", "short grain white rice", True),

        ("rice", "basmati rice", True),

        ("rice", "rice flour", False),

        ("onion", "medium onion", True),

        ("onion", "red onion", True),

        ("gelatine", "unflavored gelatin", True),

        ("gelatine", "gelatin", True),

        ("orange", "navel orange", True),

        ("milk", "whole milk", True),

        ("milk", "almond milk", False),
    ]

    for user, recipe, expected in tests:

        result = ingredient_matches(
            user,
            recipe
        )

        print(
            f"{user:15} <-> "
            f"{recipe:30} "
            f"result={result} "
            f"expected={expected}"
        )

    # --------------------------------------------------------
    # Coverage test
    # --------------------------------------------------------

    print(
        "\n--- COVERAGE TEST ---"
    )

    test_user = [
        "orange",
        "milk"
    ]

    test_recipe = [
        "orange",
        "milk",
        "sugar",
        "egg yolk"
    ]

    coverage_result = calculate_recipe_match(
        test_user,
        test_recipe
    )

    print(
        "User ingredients:",
        test_user
    )

    print(
        "Recipe ingredients:",
        test_recipe
    )

    print(
        "Result:",
        coverage_result
    )

    print(
        "\nExpected:"
    )

    print(
        "Matched: ['orange', 'milk']"
    )

    print(
        "Missing: ['sugar', 'egg yolk']"
    )

    print(
        "Match percentage: 100.0%"
    )

    print(
        "Recipe coverage: 50.0%"
    )