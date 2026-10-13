import os
import re
import base64

from dotenv import load_dotenv
from openai import OpenAI


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# ============================================================
# OPENAI CLIENT
# ============================================================

openai_client = (
    OpenAI(api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)


# ============================================================
# GENERATED IMAGE FOLDER
# ============================================================

GENERATED_IMAGE_FOLDER = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "generated-images"
)

os.makedirs(
    GENERATED_IMAGE_FOLDER,
    exist_ok=True
)


# ============================================================
# NORMALIZE DISH NAME
# ============================================================

def normalize_dish_name(name):

    if not name:
        return ""

    name = str(name).lower().strip()

    replacements = {

        "briyani": "biryani",
        "biriyani": "biryani",
        "briani": "biryani",

        "chillies": "chilli",
        "chilies": "chilli",

        "capsicums": "capsicum",

        "aubergine": "eggplant",
        "aubergines": "eggplant",

        "potatoes": "potato",
        "tomatoes": "tomato",
        "onions": "onion",
        "carrots": "carrot"
    }

    name = re.sub(
        r"[^a-z0-9\s]",
        " ",
        name
    )

    name = re.sub(
        r"\s+",
        " ",
        name
    ).strip()

    words = []

    for word in name.split():

        word = replacements.get(
            word,
            word
        )

        words.append(word)

    return " ".join(words)


# ============================================================
# IMAGE FILENAME
# ============================================================

def make_image_filename(dish_name):

    normalized = normalize_dish_name(
        dish_name
    )

    normalized = re.sub(
        r"[^a-z0-9]+",
        "-",
        normalized
    ).strip("-")

    if not normalized:
        normalized = "recipe"

    return f"{normalized}.png"


# ============================================================
# CHECK IMAGE CACHE
# ============================================================

def get_cached_image(dish_name):

    filename = make_image_filename(
        dish_name
    )

    filepath = os.path.join(
        GENERATED_IMAGE_FOLDER,
        filename
    )

    if os.path.exists(filepath):

        return (
            f"/generated-images/{filename}"
        )

    return None


# ============================================================
# GENERATE FOOD IMAGE USING GPT
# ============================================================

def generate_food_image(dish_name):

    # --------------------------------------------------------
    # CACHE FIRST
    # --------------------------------------------------------

    cached_image = get_cached_image(
        dish_name
    )

    if cached_image:

        print(
            f"[IMAGE] Using cached image: {dish_name}"
        )

        return cached_image


    # --------------------------------------------------------
    # API KEY CHECK
    # --------------------------------------------------------

    if not openai_client:

        print(
            "[IMAGE ERROR] OPENAI_API_KEY missing."
        )

        return ""


    # --------------------------------------------------------
    # IMAGE PROMPT
    # --------------------------------------------------------

    image_prompt = f"""
Create a realistic professional food photograph
of {dish_name}.

The dish should look freshly prepared and appetizing.

Show the complete dish clearly on a plate or
suitable serving bowl.

Natural restaurant-style food photography.

Realistic food texture.

Soft natural lighting.

Clean background.

No people.

No text.

No labels.

No logos.

No watermark.

The image should look like a real photograph,
not an illustration or cartoon.
"""


    try:

        print(
            f"[IMAGE] Generating GPT image: {dish_name}"
        )


        # ----------------------------------------------------
        # GPT IMAGE API
        # ----------------------------------------------------

        response = openai_client.images.generate(
            model="gpt-image-1",
            prompt=image_prompt,
            size="1024x1024",
            quality="low",
            n=1
        )


        # ----------------------------------------------------
        # GET BASE64
        # ----------------------------------------------------

        image_base64 = response.data[0].b64_json

        if not image_base64:

            print(
                "[IMAGE ERROR] GPT returned no image data."
            )

            return ""


        # ----------------------------------------------------
        # SAVE IMAGE
        # ----------------------------------------------------

        filename = make_image_filename(
            dish_name
        )

        filepath = os.path.join(
            GENERATED_IMAGE_FOLDER,
            filename
        )

        image_bytes = base64.b64decode(
            image_base64
        )

        with open(
            filepath,
            "wb"
        ) as image_file:

            image_file.write(
                image_bytes
            )


        print(
            f"[IMAGE] Saved successfully: {filepath}"
        )


        # ----------------------------------------------------
        # RETURN FRONTEND URL
        # ----------------------------------------------------

        return (
            f"/generated-images/{filename}"
        )


    except Exception as e:

        print(
            "[IMAGE ERROR]",
            type(e).__name__,
            str(e)
        )

        return ""