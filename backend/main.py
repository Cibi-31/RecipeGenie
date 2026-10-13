# ============================================================
# RecipeGenie - FastAPI Backend
# Agentic AI + RAG + FAISS
# ============================================================

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException
)
from io import BytesIO
import ollama
from PIL import Image
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import os
import json
import re
import base64
from difflib import SequenceMatcher

from dotenv import load_dotenv
from openai import OpenAI

from backend.retriever import (
    search_recipes,
    search_dishes
)

# ============================================================
# AGENTIC AI
# ============================================================

from backend.agent import run_agent

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

# ============================================================
# AI INGREDIENT IMAGE RECOGNITION
# ============================================================

# ============================================================
# AI INGREDIENT IMAGE RECOGNITION
# USING OLLAMA MOONDREAM
# ============================================================

VISION_MODEL = "qwen2.5vl:3b"


# ============================================================
# INGREDIENT VOCABULARY
# ============================================================

IMAGE_INGREDIENTS = [
    "tomato",
    "onion",
    "red onion",
    "potato",
    "carrot",

    "bell pepper",
    "capsicum",

    "green chilli",
    "chilli",

    "egg",

    "milk",
    "cheese",
    "butter",

    "bread",

    "rice",
    "basmati rice",

    "chicken",
    "fish",
    "prawn",
    "shrimp",

    "paneer",
    "mushroom",

    "garlic",
    "ginger",

    "lemon",
    "lime",

    "orange",
    "apple",
    "banana",
    "mango",
    "avocado",

    "cucumber",
    "spinach",
    "broccoli",
    "cauliflower",

    "peas",
    "corn",
    "beans",
    "cabbage",

    "beetroot",
    "sweet potato",

    "yogurt",
    "curd",

    "flour",
    "sugar"
]


# ============================================================
# DETECT INGREDIENTS USING QWEN2.5-VL
# ============================================================

def detect_ingredients_from_image(image_bytes):

    print("[IMAGE AI] Preparing image...")

    try:

        # ----------------------------------------------------
        # OPEN IMAGE
        # ----------------------------------------------------

        image = Image.open(
            BytesIO(image_bytes)
        ).convert("RGB")

        print(
            f"[IMAGE AI] Original size: "
            f"{image.width}x{image.height}"
        )

        # ----------------------------------------------------
        # RESIZE IMAGE
        # ----------------------------------------------------

        max_size = 512

        image.thumbnail(
            (max_size, max_size)
        )

        # ----------------------------------------------------
        # COMPRESS IMAGE
        # ----------------------------------------------------

        buffer = BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=75,
            optimize=True
        )

        optimized_bytes = buffer.getvalue()

        print(
            f"[IMAGE AI] Optimized size: "
            f"{len(optimized_bytes) / 1024:.1f} KB"
        )

        # ----------------------------------------------------
        # BASE64
        # ----------------------------------------------------

        image_base64 = base64.b64encode(
            optimized_bytes
        ).decode("utf-8")

        # ----------------------------------------------------
        # STRICT PROMPT
        # ----------------------------------------------------

        prompt = f"""
You are an ingredient recognition system.

Look carefully at the image.

Identify ONLY food ingredients that are
clearly visible in the image.

IMPORTANT RULES:

1. Do NOT guess.
2. Do NOT infer hidden ingredients.
3. Do NOT list ingredients that are not clearly visible.
4. If only one ingredient is visible, return only one ingredient.
5. Do not generate recipes.
6. Do not generate explanations.
7. Do not generate quantities.
8. Do not generate cooking instructions.
9. Choose ONLY from the allowed ingredient list below.
10. Return ONLY comma-separated ingredient names.

Allowed ingredients:

{", ".join(IMAGE_INGREDIENTS)}

Examples:

If the image contains only rice:
rice

If the image contains rice and onion:
rice, onion

If the image contains tomato, onion and potato:
tomato, onion, potato
"""

        print(
            "[IMAGE AI] Sending image to "
            f"{VISION_MODEL}..."
        )

        # ----------------------------------------------------
        # VISION MODEL
        # ----------------------------------------------------

        response = ollama.chat(
            model=VISION_MODEL,

            messages=[
                {
                    "role": "user",
                    "content": prompt,
                    "images": [image_base64]
                }
            ],

            options={
                "temperature": 0,
                "num_predict": 30
            },

            keep_alive="10m"
        )

        # ----------------------------------------------------
        # GET MODEL RESPONSE
        # ----------------------------------------------------

        result = (
            response
            .get("message", {})
            .get("content", "")
            .strip()
        )

        print(
            "[IMAGE AI] Raw response:",
            result
        )

        # ----------------------------------------------------
        # CLEAN RESPONSE
        # ----------------------------------------------------

        result = result.replace(
            "\n",
            ","
        )

        result = result.replace(
            "`",
            ""
        )

        result = result.replace(
            "[",
            ""
        )

        result = result.replace(
            "]",
            ""
        )

        # ----------------------------------------------------
        # SPLIT MODEL RESPONSE
        # ----------------------------------------------------

        candidates = [
            item.strip().lower()
            for item in result.split(",")
            if item.strip()
        ]

        # ----------------------------------------------------
        # NORMALIZATION
        # ----------------------------------------------------

        aliases = {

            "capsicum":
                "bell pepper",

            "red onion":
                "red onion",

            "green chili":
                "green chilli",

            "green chile":
                "green chilli",

            "chili":
                "chilli",

            "basmati":
                "basmati rice",

            "yoghurt":
                "yogurt"
        }

        normalized_candidates = []

        for candidate in candidates:

            # Remove numbering such as:
            # 1. rice
            # 2) onion

            candidate = re.sub(
                r"^\s*\d+[\.\)\-:]\s*",
                "",
                candidate
            )

            candidate = candidate.strip(
                " .,:;-"
            )

            candidate = aliases.get(
                candidate,
                candidate
            )

            if candidate:
                normalized_candidates.append(
                    candidate
                )

        # ----------------------------------------------------
        # EXACT MATCH ONLY
        # ----------------------------------------------------

        valid_ingredients = {
            ingredient.lower(): ingredient
            for ingredient in IMAGE_INGREDIENTS
        }

        detected = []

        for candidate in normalized_candidates:

            # Exact match only.
            # This prevents:
            #
            # rice
            # matching inside
            # basmati rice
            #
            # and prevents arbitrary substring matches.

            if candidate in valid_ingredients:

                ingredient = valid_ingredients[
                    candidate
                ]

                if ingredient not in detected:

                    detected.append(
                        ingredient
                    )

        # ----------------------------------------------------
        # LIMIT RESULTS
        # ----------------------------------------------------

        detected = detected[:10]

        print(
            "[IMAGE AI] Parsed candidates:",
            normalized_candidates
        )

        print(
            "[IMAGE AI] Detected ingredients:",
            detected
        )

        return detected

    except Exception as e:

        print(
            "[IMAGE AI ERROR]",
            str(e)
        )

        raise
# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("WARNING: OPENAI_API_KEY not found in .env")


# ============================================================
# OPENAI CLIENT
# ============================================================

openai_client = (
    OpenAI(api_key=OPENAI_API_KEY)
    if OPENAI_API_KEY
    else None
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="RecipeGenie",
    description=(
        "AI-powered kitchen waste and recipe recommendation "
        "system using Agentic AI, RAG and FAISS"
    ),
    version="2.0"
)
# ============================================================
# DETECT INGREDIENTS FROM UPLOADED IMAGE
# ============================================================

@app.post("/detect-ingredients")
async def detect_ingredients(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # VALIDATE FILE TYPE
    # --------------------------------------------------------

    if (
        not file.content_type
        or not file.content_type.startswith(
            "image/"
        )
    ):

        raise HTTPException(
            status_code=400,
            detail="Please upload an image file."
        )


    try:

        # ----------------------------------------------------
        # READ IMAGE
        # ----------------------------------------------------

        image_bytes = await file.read()


        if not image_bytes:

            raise HTTPException(
                status_code=400,
                detail="Uploaded image is empty."
            )


        # ----------------------------------------------------
        # VALIDATE IMAGE
        # ----------------------------------------------------

        try:

            Image.open(
                BytesIO(image_bytes)
            ).verify()

        except Exception:

            raise HTTPException(
                status_code=400,
                detail="Invalid image file."
            )


        # ----------------------------------------------------
        # DETECT INGREDIENTS
        # ----------------------------------------------------

        detected = (
            detect_ingredients_from_image(
                image_bytes
            )
        )


        # ----------------------------------------------------
        # RETURN RESULT
        # ----------------------------------------------------

        return {

            "success": True,

            "ingredients": detected,

            "detections": [
                {
                    "ingredient": ingredient
                }

                for ingredient in detected
            ]

        }


    except HTTPException:

        raise


    except Exception as e:

        print(
            "[IMAGE AI ERROR]",
            str(e)
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Ingredient detection failed: "
                f"{str(e)}"
            )
        )
    
# ============================================================
# CORS
# ============================================================

# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# DATASET FOOD IMAGE FOLDER
# ============================================================

IMAGE_FOLDER = (
    r"C:\Users\T9960\Downloads\archive"
    r"\Food Images\Food Images"
)


# ============================================================
# AI GENERATED IMAGE FOLDER
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
# SERVE DATASET IMAGES
# ============================================================

app.mount(
    "/recipe-images",
    StaticFiles(
        directory=IMAGE_FOLDER
    ),
    name="recipe-images"
)


# ============================================================
# SERVE GENERATED IMAGES
# ============================================================

app.mount(
    "/generated-images",
    StaticFiles(
        directory=GENERATED_IMAGE_FOLDER
    ),
    name="generated-images"
)


# ============================================================
# IMAGE URL HELPER
# ============================================================

def get_image_url(image_name):

    if not image_name:
        return ""

    image_name = str(
        image_name
    ).strip()

    if image_name.lower().endswith(
        (
            ".jpg",
            ".jpeg",
            ".png",
            ".webp"
        )
    ):
        return (
            f"/recipe-images/{image_name}"
        )

    return (
        f"/recipe-images/{image_name}.jpg"
    )


# ============================================================
# DISH NAME NORMALIZATION
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
# SAFE FILENAME FOR GENERATED IMAGES
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

    return (
        f"{normalized}.png"
    )


# ============================================================
# GET CACHED AI IMAGE
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
    # CHECK CACHE FIRST
    # --------------------------------------------------------

    cached_image = get_cached_image(
        dish_name
    )

    if cached_image:

        print(
            f"Using cached image for: {dish_name}"
        )

        return cached_image

    # --------------------------------------------------------
    # CHECK API KEY
    # --------------------------------------------------------

    if not openai_client:

        print(
            "OpenAI API key is missing."
        )

        return ""

    # --------------------------------------------------------
    # IMAGE PROMPT
    # --------------------------------------------------------

    image_prompt = f"""
Create a realistic professional food photograph
of {dish_name}.

The dish should look freshly prepared and appetizing.

Show the complete dish clearly on a plate or suitable
serving bowl.

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
            f"Generating new GPT image for: {dish_name}"
        )

        response = openai_client.images.generate(
            model="gpt-image-1",
            prompt=image_prompt,
            size="1024x1024",
            quality="low",
            n=1
        )

        # ----------------------------------------------------
        # GET BASE64 IMAGE
        # ----------------------------------------------------

        image_base64 = response.data[0].b64_json

        if not image_base64:

            print(
                "GPT did not return image data."
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
            f"Image saved: {filepath}"
        )

        # ----------------------------------------------------
        # RETURN FRONTEND URL
        # ----------------------------------------------------

        return (
            f"/generated-images/{filename}"
        )

    except Exception as e:

        print(
            "GPT image generation error:",
            str(e)
        )

        return ""


# ============================================================
# CHECK REASONABLE DISH MATCH
# ============================================================

# ============================================================
# CHECK EXACT DISH MATCH
# ============================================================

def is_reasonable_dish_match(
    query,
    title
):

    normalized_query = (
        normalize_dish_name(query)
    )

    normalized_title = (
        normalize_dish_name(title)
    )

    if not normalized_query:
        return False

    if not normalized_title:
        return False

    # --------------------------------------------------------
    # ONLY ACCEPT EXACT NORMALIZED TITLE MATCH
    # --------------------------------------------------------
    #
    # Example:
    #
    # chicken fried rice
    #        ↓
    # Chicken Fried Rice
    #
    # = VALID
    #
    # chicken fried rice
    #        ↓
    # Easy Fried Rice with Chicken and Broccolini
    #
    # = INVALID
    #
    # --------------------------------------------------------

    if normalized_query == normalized_title:
        return True

    return False

# ============================================================
# REQUEST MODELS
# ============================================================

class RecipeRequest(BaseModel):

    ingredients: str


class SelectedRecipeRequest(BaseModel):

    ingredients: str
    recipe_title: str


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {

        "message":
            "RecipeGenie API is running",

        "architecture":
            "Agentic AI + RAG + FAISS",

        "agent":
            "Llama 3.2 via Ollama"
    }


# ============================================================
# AGENTIC INGREDIENT / DISH SEARCH
# ============================================================

@app.post("/recommend")
def recommend_recipe(
    request: RecipeRequest
):

    query = request.ingredients.strip()

    # --------------------------------------------------------
    # VALIDATE INPUT
    # --------------------------------------------------------

    if not query:

        return {

            "ingredients": "",

            "top_recipes": [],

            "recommendation":
                "Please enter at least one ingredient or dish."
        }

    try:

        print("\n")
        print("=" * 60)
        print("GUI → AGENTIC AI")
        print("=" * 60)

        print(
            f"User request: {query}"
        )

        # ----------------------------------------------------
        # RUN AGENT
        # ----------------------------------------------------

        agent_result = run_agent(
            query
        )

        print(
            "\n[AGENT RESULT]"
        )

        print(
            agent_result
        )

        if not agent_result.get(
            "success",
            False
        ):

            return {

                "ingredients":
                    query,

                "top_recipes":
                    [],

                "recommendation":
                    agent_result.get(
                        "response",
                        "Unable to find recipes."
                    )
            }

        # ----------------------------------------------------
        # GET AGENT HISTORY
        # ----------------------------------------------------

        history = agent_result.get(
            "history",
            []
        )

        recipe_tool_result = None
        dish_tool_result = None

        # ----------------------------------------------------
        # CHECK WHICH TOOL WAS USED
        # ----------------------------------------------------

        for item in history:

            tool_name = item.get(
                "tool"
            )

            if tool_name == "recipe_search":

                recipe_tool_result = (
                    item.get(
                        "result"
                    )
                )

            elif tool_name == "dish_search":

                dish_tool_result = (
                    item.get(
                        "result"
                    )
                )

        # ====================================================
        # CASE 1:
        # INGREDIENT SEARCH
        # ====================================================

        if recipe_tool_result is not None:

            recipes = recipe_tool_result.get(
                "recipes",
                []
            )

            top_recipes = []

            for recipe in recipes[:3]:

                image_name = recipe.get(
                    "image_name",
                    ""
                )

                image_url = recipe.get(
                    "image",
                    ""
                )

                if not image_url:

                    image_url = get_image_url(
                        image_name
                    )

                top_recipes.append({

                    "title":
                        recipe.get(
                            "title",
                            "Unknown Recipe"
                        ),

                    "image":
                        image_url,

                    "matched":
                        recipe.get(
                            "matched",
                            []
                        ),

                    "missing":
                        recipe.get(
                            "missing",
                            []
                        ),

                    "match_count":
                        recipe.get(
                            "match_count",
                            0
                        ),

                    "match_percentage":
                        recipe.get(
                            "match_percentage",
                            0
                        ),

                    "recipe_coverage":
                        recipe.get(
                            "recipe_coverage",
                            0
                        ),

                    "missing_count":
                        recipe.get(
                            "missing_count",
                            len(
                                recipe.get(
                                    "missing",
                                    []
                                )
                            )
                        ),

                    "ingredients":
                        recipe.get(
                            "ingredients",
                            ""
                        ),

                    "instructions":
                        recipe.get(
                            "instructions",
                            ""
                        ),

                    "source":
                        "dataset"
                })

            return {

                "ingredients":
                    query,

                "top_recipes":
                    top_recipes,

                "recommendation":
                    agent_result.get(
                        "response",
                        ""
                    )
            }

        # ====================================================
        # CASE 2:
        # SPECIFIC DISH SEARCH
        # ====================================================

        if dish_tool_result is not None:

            print(
                "\n[BACKEND] Dish search result detected."
            )

            found = dish_tool_result.get(
                "found",
                False
            )

            recipe = dish_tool_result.get(
                "recipe"
            )

            # ------------------------------------------------
            # DATASET DISH FOUND
            # ------------------------------------------------

            if found and recipe:

                print(
                    "[BACKEND] Dataset dish found:",
                    recipe.get(
                        "title",
                        "Unknown Recipe"
                    )
                )

                # ------------------------------------------------
                # GET IMAGE
                # ------------------------------------------------

                image_url = recipe.get(
                    "image",
                    ""
                )

                if image_url:

                    if image_url.startswith(
                        "/"
                    ):

                        final_image = image_url

                    elif (
                        image_url.startswith(
                            "http://"
                        )
                        or
                        image_url.startswith(
                            "https://"
                        )
                    ):

                        final_image = image_url

                    else:

                        final_image = get_image_url(
                            image_url
                        )

                else:

                    final_image = get_image_url(
                        recipe.get(
                            "image_name",
                            ""
                        )
                    )

                # ------------------------------------------------
                # CREATE GUI RECIPE
                # ------------------------------------------------

                dataset_recipe = {

                    "title":
                        recipe.get(
                            "title",
                            "Unknown Recipe"
                        ),

                    "image":
                        final_image,

                    "image_name":
                        recipe.get(
                            "image_name",
                            ""
                        ),

                    "matched":
                        recipe.get(
                            "matched",
                            []
                        ),

                    "missing":
                        recipe.get(
                            "missing",
                            []
                        ),

                    "match_count":
                        recipe.get(
                            "match_count",
                            0
                        ),

                    "match_percentage":
                        recipe.get(
                            "match_percentage",
                            0
                        ),

                    "recipe_coverage":
                        recipe.get(
                            "recipe_coverage",
                            0
                        ),

                    "missing_count":
                        recipe.get(
                            "missing_count",
                            len(
                                recipe.get(
                                    "missing",
                                    []
                                )
                            )
                        ),

                    "ingredients":
                        recipe.get(
                            "ingredients",
                            ""
                        ),

                    "instructions":
                        recipe.get(
                            "instructions",
                            ""
                        ),

                    "source":
                        "dataset"
                }

                print(
                    "\n[BACKEND] Sending recipe to GUI:"
                )

                print(
                    dataset_recipe
                )

                return {

                    "ingredients":
                        query,

                    "top_recipes":
                        [
                            dataset_recipe
                        ],

                    "recommendation":
                        agent_result.get(
                            "response",
                            ""
                        )
                }

            # ------------------------------------------------
            # DATASET DISH NOT FOUND
            # ------------------------------------------------

            print(
                f"\n[BACKEND] '{query}' not found in dataset."
            )

            print(
                "[BACKEND] Falling back to Llama 3.2 AI recipe generation."
            )

            ai_recipe = generate_dish_recipe(
                query
            )

            if ai_recipe:

                return {

                    "ingredients":
                        query,

                    "top_recipes":
                        [
                            ai_recipe
                        ],

                    "recommendation":
                        (
                            f"'{query}' was not found "
                            "in the RecipeGenie dataset, "
                            "so an AI-generated recipe "
                            "was created."
                        )
                }

        # ====================================================
        # NOTHING FOUND
        # ====================================================

        return {

            "ingredients":
                query,

            "top_recipes":
                [],

            "recommendation":
                agent_result.get(
                    "response",
                    "No suitable recipe found."
                )
        }

    except Exception as e:

        print(
            "\nAgent recommendation error:",
            str(e)
        )

        return {

            "ingredients":
                query,

            "top_recipes":
                [],

            "recommendation":
                f"Error finding recipes: {str(e)}"
        }


# ============================================================
# GENERATE RECIPE USING LLAMA 3.2 + GPT IMAGE
# ============================================================

def generate_dish_recipe(dish_name):

    try:

        llm = ChatOllama(
            model="llama3.2",
            temperature=0
        )

        prompt = f"""
You are RecipeGenie, an AI recipe assistant.

Create ONE practical recipe for:

{dish_name}

Return ONLY JSON.

Example:

{{
    "title": "{dish_name}",
    "ingredients": [
        "2 cups rice",
        "1 onion",
        "2 tomatoes"
    ],
    "instructions": "Step 1: Prepare the ingredients. Step 2: Cook the dish. Step 3: Serve hot."
}}

Rules:

- Return ONLY one JSON object.
- No markdown.
- No ```json.
- No explanation outside JSON.
- Keep the title as {dish_name}.
- Give realistic ingredients.
- Give clear cooking instructions.
"""

        response = llm.invoke(
            prompt
        )

        content = response.content

        if isinstance(
            content,
            list
        ):

            content = " ".join(
                str(item)
                for item in content
            )

        content = str(
            content
        ).strip()

        print(
            "Llama response:",
            content
        )

        # ----------------------------------------------------
        # REMOVE MARKDOWN
        # ----------------------------------------------------

        content = re.sub(
            r"```json",
            "",
            content,
            flags=re.IGNORECASE
        )

        content = re.sub(
            r"```",
            "",
            content
        )

        content = content.strip()

        # ----------------------------------------------------
        # FIND JSON
        # ----------------------------------------------------

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1:

            print(
                "No JSON object found in Llama response."
            )

            return create_fallback_recipe(
                dish_name
            )

        json_text = content[
            start:end + 1
        ]

        # ----------------------------------------------------
        # PARSE JSON
        # ----------------------------------------------------

        try:

            data = json.loads(
                json_text
            )

        except json.JSONDecodeError as e:

            print(
                "JSON parsing error:",
                str(e)
            )

            return create_fallback_recipe(
                dish_name
            )

        # ----------------------------------------------------
        # GET DATA
        # ----------------------------------------------------

        title = data.get(
            "title",
            dish_name
        )

        ingredients = data.get(
            "ingredients",
            []
        )

        instructions = data.get(
            "instructions",
            ""
        )

        # ----------------------------------------------------
        # NORMALIZE INGREDIENTS
        # ----------------------------------------------------

        if isinstance(
            ingredients,
            str
        ):

            ingredients = [
                item.strip()
                for item in ingredients.split(",")
                if item.strip()
            ]

        elif not isinstance(
            ingredients,
            list
        ):

            ingredients = []

        # ----------------------------------------------------
        # NORMALIZE INSTRUCTIONS
        # ----------------------------------------------------

        if isinstance(
            instructions,
            list
        ):

            instructions = "\n".join(
                str(step)
                for step in instructions
            )

        else:

            instructions = str(
                instructions
            )

        # ----------------------------------------------------
        # GENERATE / RETRIEVE IMAGE
        # ----------------------------------------------------

        print(
            f"Getting image for: {title}"
        )

        image_url = generate_food_image(
            title
        )

        # ----------------------------------------------------
        # RETURN RECIPE
        # ----------------------------------------------------

        return {

            "title":
                title,

            "image":
                image_url,

            "matched":
                [],

            "missing":
                [],

            "match_count":
                0,

            "match_percentage":
                0,

            "recipe_coverage":
                0,

            "missing_count":
                0,

            "ingredients":
                ingredients,

            "instructions":
                instructions,

            "source":
                "ai_generated"
        }

    except Exception as e:

        print(
            "Recipe generation error:",
            str(e)
        )

        return create_fallback_recipe(
            dish_name
        )


# ============================================================
# FALLBACK RECIPE
# ============================================================

def create_fallback_recipe(dish_name):

    return {

        "title":
            dish_name,

        "image":
            "",

        "matched":
            [],

        "missing":
            [],

        "match_count":
            0,

        "match_percentage":
            0,

        "recipe_coverage":
            0,

        "missing_count":
            0,

        "ingredients":
            [],

        "instructions":
            (
                "The AI recipe could not be "
                "generated correctly. "
                "Please try again."
            ),

        "source":
            "ai_generated"
    }


# ============================================================
# AGENTIC SPECIFIC DISH SEARCH
# ============================================================

@app.post("/search-dish")
def search_dish(
    request: RecipeRequest
):

    dish_name = (
        request.ingredients.strip()
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if not dish_name:

        return {

            "query": "",

            "top_recipes": []
        }

    try:

        print("\n")
        print("=" * 60)
        print("GUI → AGENTIC AI → DISH SEARCH")
        print("=" * 60)

        print(
            f"Requested dish: {dish_name}"
        )

        # ----------------------------------------------------
        # RUN AGENT
        # ----------------------------------------------------

        agent_result = run_agent(
            dish_name
        )

        print(
            "\n[AGENT RESULT]"
        )

        print(
            agent_result
        )

        # ----------------------------------------------------
        # GET DISH SEARCH RESULT
        # ----------------------------------------------------

        history = agent_result.get(
            "history",
            []
        )

        dish_tool_result = None

        for item in history:

            if item.get(
                "tool"
            ) == "dish_search":

                dish_tool_result = (
                    item.get(
                        "result"
                    )
                )

                break

        # ----------------------------------------------------
        # NOT FOUND
        # ----------------------------------------------------

        if not dish_tool_result:

            return {

                "query":
                    dish_name,

                "top_recipes":
                    []
            }

        # ----------------------------------------------------
        # DATASET DISH FOUND
        # ----------------------------------------------------

        if not dish_tool_result.get(
            "found",
            False
        ):

            print(
                f"[BACKEND] '{dish_name}' not found."
            )

            print(
                "[BACKEND] Falling back to Llama 3.2."
            )

            ai_recipe = generate_dish_recipe(
                dish_name
            )

            if ai_recipe:

                return {

                    "query":
                        dish_name,

                    "top_recipes":
                        [
                            ai_recipe
                        ]
                }

            return {

                "query":
                    dish_name,

                "top_recipes":
                    []
            }

        recipe = dish_tool_result.get(
            "recipe",
            {}
        )

        if not recipe:

            return {

                "query":
                    dish_name,

                "top_recipes":
                    []
            }

        # ----------------------------------------------------
        # IMAGE
        # ----------------------------------------------------

        image_url = recipe.get(
            "image",
            ""
        )

        if image_url:

            if image_url.startswith(
                "/"
            ):

                final_image = image_url

            elif (
                image_url.startswith(
                    "http://"
                )
                or
                image_url.startswith(
                    "https://"
                )
            ):

                final_image = image_url

            else:

                final_image = get_image_url(
                    image_url
                )

        else:

            final_image = get_image_url(
                recipe.get(
                    "image_name",
                    ""
                )
            )

        # ----------------------------------------------------
        # CONVERT TO GUI FORMAT
        # ----------------------------------------------------

        dataset_recipe = {

            "title":
                recipe.get(
                    "title",
                    "Unknown Recipe"
                ),

            "image":
                final_image,

            "image_name":
                recipe.get(
                    "image_name",
                    ""
                ),

            "matched":
                recipe.get(
                    "matched",
                    []
                ),

            "missing":
                recipe.get(
                    "missing",
                    []
                ),

            "match_count":
                recipe.get(
                    "match_count",
                    0
                ),

            "match_percentage":
                recipe.get(
                    "match_percentage",
                    0
                ),

            "recipe_coverage":
                recipe.get(
                    "recipe_coverage",
                    0
                ),

            "missing_count":
                recipe.get(
                    "missing_count",
                    len(
                        recipe.get(
                            "missing",
                            []
                        )
                    )
                ),

            "ingredients":
                recipe.get(
                    "ingredients",
                    ""
                ),

            "instructions":
                recipe.get(
                    "instructions",
                    ""
                ),

            "source":
                "dataset"
        }

        return {

            "query":
                dish_name,

            "top_recipes":
                [
                    dataset_recipe
                ]
        }

    except Exception as e:

        print(
            "Agent dish search error:",
            str(e)
        )

        return {

            "query":
                dish_name,

            "top_recipes":
                []
        }
    # ============================================================
# SELECTED RECIPE + AI RECOMMENDATION
# ============================================================

@app.post("/recommend-selected")
def recommend_selected_recipe(
    request: SelectedRecipeRequest
):

    user_ingredients = (
        request.ingredients.strip()
    )

    selected_title = (
        request.recipe_title.strip()
    )

    # --------------------------------------------------------
    # VALIDATE
    # --------------------------------------------------------

    if (
        not user_ingredients
        or not selected_title
    ):

        return {

            "recommendation":
                "Invalid recipe selection."
        }

    try:

        # ====================================================
        # SEARCH RECIPES FROM USER INGREDIENTS
        # ====================================================

        results = search_recipes(
            user_ingredients,
            k=10
        )

        selected_result = None

        # ====================================================
        # FIND SELECTED DATASET RECIPE
        # ====================================================

        for result in results:

            document = result[
                "document"
            ]

            title = document.metadata.get(
                "title",
                ""
            )

            if is_reasonable_dish_match(
                selected_title,
                title
            ):

                selected_result = result

                break

        # ====================================================
        # DIRECT DISH SEARCH
        # ====================================================

        if selected_result is None:

            dish_results = search_dishes(
                selected_title,
                k=10
            )

            for result in dish_results:

                document = result[
                    "document"
                ]

                title = document.metadata.get(
                    "title",
                    ""
                )

                if is_reasonable_dish_match(
                    selected_title,
                    title
                ):

                    selected_result = result

                    break

        # ====================================================
        # AI GENERATED DISH
        # ====================================================

        if selected_result is None:

            llm = ChatOllama(
                model="llama3.2",
                temperature=0
            )

            prompt = ChatPromptTemplate.from_template(
                """
You are RecipeGenie, an AI Kitchen Waste
and Recipe Assistant.

The user searched for this dish:

{dish_name}

The requested dish was not available
in the local recipe dataset.

The recipe was generated using AI.

The user has these available ingredients:

{question}

Briefly explain why this generated recipe
is relevant to the user's request.

IMPORTANT:

- Do not claim the user has ingredients
  that they did not provide.
- Do not create another recipe.
- Do not rewrite the recipe.
- Do not provide cooking instructions.
- Do not make health claims.
- Keep the explanation concise.
- Return ONLY natural language.
"""
            )

            response = llm.invoke(
                prompt.format_messages(
                    dish_name=selected_title,
                    question=user_ingredients
                )
            )

            return {

                "recommendation":
                    response.content
            }

        # ====================================================
        # DATASET RECIPE
        # ====================================================

        document = selected_result[
            "document"
        ]

        title = document.metadata.get(
            "title",
            "Unknown Recipe"
        )

        recipe_ingredients = (
            document.metadata.get(
                "ingredients",
                ""
            )
        )

        matched = selected_result.get(
            "matched",
            []
        )

        missing = selected_result.get(
            "missing",
            []
        )

        # ====================================================
        # BUILD RECIPE CONTEXT
        # ====================================================

        context = f"""

Recipe Name:
{title}

Recipe Ingredients:
{recipe_ingredients}

Available Ingredients Used:
{
    ", ".join(matched)
    if matched
    else "None"
}

Missing Ingredients:
{
    ", ".join(missing)
    if missing
    else "None"
}
"""

        # ====================================================
        # LLAMA 3.2
        # ====================================================

        llm = ChatOllama(
            model="llama3.2",
            temperature=0
        )

        prompt = ChatPromptTemplate.from_template(
            """
You are RecipeGenie, an AI Kitchen Waste
and Recipe Assistant.

The user has these available ingredients:

{question}

The user selected this recipe:

{context}

Explain briefly why this selected recipe
is suitable for the user's available ingredients.

IMPORTANT RULES:

- Recommend ONLY the selected recipe.
- Do NOT create a new recipe.
- Do NOT invent ingredients.
- Do NOT change ingredient information.
- Do NOT change matched ingredients.
- Do NOT change missing ingredients.
- Do NOT rewrite the recipe.
- Do NOT generate cooking instructions.
- Do NOT make health claims.
- Do NOT assume that an ingredient is spoiled.
- Do NOT assume that an ingredient is expired.
- Do NOT assume that an ingredient is past its prime.
- Do NOT assume why the user has the ingredient.
- Keep the explanation concise.
- Focus on the available ingredients.
- Explain how using available ingredients
  can help reduce potential kitchen food waste.

Return ONLY a natural-language explanation.

Do NOT return:

Recipe Name:
Ingredient Match:
Missing Ingredients:
Cooking Instructions:
"""
        )

        messages = prompt.format_messages(
            question=user_ingredients,
            context=context
        )

        response = llm.invoke(
            messages
        )

        return {

            "recommendation":
                response.content
        }

    except Exception as e:

        return {

            "recommendation":
                (
                    "Error generating AI "
                    f"recommendation: {str(e)}"
                )
        }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    return {

        "status":
            "healthy",

        "service":
            "RecipeGenie",

        "architecture":
            "Agentic AI + RAG + FAISS",

        "llm":
            "Llama 3.2 via Ollama"
    }


# ============================================================
# DEBUG / DATASET IMAGE CHECK
# ============================================================

@app.get("/check-image/{image_name}")
def check_image(
    image_name: str
):

    try:

        image_name = str(
            image_name
        ).strip()

        if not image_name:

            return {

                "found":
                    False,

                "image":
                    ""
            }

        # ----------------------------------------------------
        # REMOVE EXTENSION IF PRESENT
        # ----------------------------------------------------

        clean_name = re.sub(
            r"\.(jpg|jpeg|png|webp)$",
            "",
            image_name,
            flags=re.IGNORECASE
        )

        possible_files = [

            f"{clean_name}.jpg",

            f"{clean_name}.jpeg",

            f"{clean_name}.png",

            f"{clean_name}.webp"
        ]

        for filename in possible_files:

            filepath = os.path.join(
                IMAGE_FOLDER,
                filename
            )

            if os.path.exists(
                filepath
            ):

                return {

                    "found":
                        True,

                    "filename":
                        filename,

                    "image":
                        f"/recipe-images/{filename}"
                }

        return {

            "found":
                False,

            "filename":
                clean_name,

            "image":
                ""
        }

    except Exception as e:

        return {

            "found":
                False,

            "error":
                str(e)
        }


# ============================================================
# DATASET IMAGE INFORMATION
# ============================================================

@app.get("/image-info/{image_name}")
def image_info(
    image_name: str
):

    try:

        image_name = str(
            image_name
        ).strip()

        clean_name = re.sub(
            r"\.(jpg|jpeg|png|webp)$",
            "",
            image_name,
            flags=re.IGNORECASE
        )

        possible_files = [

            f"{clean_name}.jpg",

            f"{clean_name}.jpeg",

            f"{clean_name}.png",

            f"{clean_name}.webp"
        ]

        for filename in possible_files:

            filepath = os.path.join(
                IMAGE_FOLDER,
                filename
            )

            if os.path.exists(
                filepath
            ):

                return {

                    "exists":
                        True,

                    "filename":
                        filename,

                    "path":
                        filepath,

                    "url":
                        f"/recipe-images/{filename}",

                    "size":
                        os.path.getsize(
                            filepath
                        )
                }

        return {

            "exists":
                False,

            "filename":
                clean_name
        }

    except Exception as e:

        return {

            "exists":
                False,

            "error":
                str(e)
        }


# ============================================================
# TEST RECIPE SEARCH
# ============================================================

@app.get("/test-search")
def test_search(
    q: str
):

    try:

        results = search_recipes(
            q,
            k=3
        )

        output = []

        for result in results:

            document = result[
                "document"
            ]

            output.append({

                "title":
                    document.metadata.get(
                        "title",
                        ""
                    ),

                "matched":
                    result.get(
                        "matched",
                        []
                    ),

                "missing":
                    result.get(
                        "missing",
                        []
                    ),

                "match_percentage":
                    result.get(
                        "match_percentage",
                        0
                    ),

                "recipe_coverage":
                    result.get(
                        "recipe_coverage",
                        0
                    ),

                "missing_count":
                    result.get(
                        "missing_count",
                        0
                    )
            })

        return {

            "query":
                q,

            "results":
                output
        }

    except Exception as e:

        return {

            "query":
                q,

            "results":
                [],

            "error":
                str(e)
        }


# ============================================================
# TEST DISH SEARCH
# ============================================================

@app.get("/test-dish")
def test_dish(
    q: str
):

    try:

        results = search_dishes(
            q,
            k=5
        )

        output = []

        for result in results:

            document = result[
                "document"
            ]

            output.append({

                "title":
                    document.metadata.get(
                        "title",
                        ""
                    ),

                "ingredients":
                    document.metadata.get(
                        "ingredients",
                        ""
                    ),

                "image_name":
                    document.metadata.get(
                        "image_name",
                        ""
                    )
            })

        return {

            "query":
                q,

            "results":
                output
        }

    except Exception as e:

        return {

            "query":
                q,

            "results":
                [],

            "error":
                str(e)
        }


# ============================================================
# TEST AGENT
# ============================================================

@app.get("/test-agent")
def test_agent(
    q: str
):

    try:

        result = run_agent(
            q
        )

        return result

    except Exception as e:

        return {

            "success":
                False,

            "error":
                str(e)
        }


# ============================================================
# RECIPE IMAGE URL
# ============================================================

@app.get("/recipe-image-url/{image_name}")
def recipe_image_url(
    image_name: str
):

    try:

        url = get_image_url(
            image_name
        )

        return {

            "image_name":
                image_name,

            "url":
                url
        }

    except Exception as e:

        return {

            "image_name":
                image_name,

            "url":
                "",

            "error":
                str(e)
        }


# ============================================================
# GENERATED IMAGE URL
# ============================================================

@app.get("/generated-image-url/{dish_name}")
def generated_image_url(
    dish_name: str
):

    try:

        cached = get_cached_image(
            dish_name
        )

        if cached:

            return {

                "exists":
                    True,

                "url":
                    cached
            }

        return {

            "exists":
                False,

            "url":
                ""
        }

    except Exception as e:

        return {

            "exists":
                False,

            "url":
                "",

            "error":
                str(e)
        }


# ============================================================
# NORMALIZE DISH API
# ============================================================

@app.get("/normalize-dish")
def normalize_dish(
    q: str
):

    return {

        "original":
            q,

        "normalized":
            normalize_dish_name(q)
    }


# ============================================================
# MATCH CHECK API
# ============================================================

@app.get("/dish-match")
def dish_match(
    query: str,
    title: str
):

    return {

        "query":
            query,

        "title":
            title,

        "match":
            is_reasonable_dish_match(
                query,
                title
            )
    }
 # ============================================================
# FINAL API STATUS
# ============================================================

@app.get("/")
def root():

    return {

        "message":
            "RecipeGenie Backend is Running",

        "service":
            "AI Kitchen Waste & Recipe Assistant",

        "architecture":
            "Agentic AI + RAG",

        "llm":
            "Llama 3.2",

        "embedding":
            "Nomic Embed Text",

        "vector_database":
            "FAISS",

        "status":
            "online"
    }


# ============================================================
# API INFORMATION
# ============================================================

@app.get("/api-info")
def api_info():

    return {

        "application":
            "RecipeGenie",

        "description":
            "AI Kitchen Waste and Recipe Assistant",

        "features": [

            "Ingredient-based recipe recommendation",

            "Dish search",

            "Agentic AI",

            "RAG",

            "FAISS semantic retrieval",

            "Ingredient matching",

            "Missing ingredient detection",

            "Recipe coverage calculation",

            "Dataset recipe images",

            "AI-generated fallback recipes",

            "Selected recipe explanation"
        ],

        "models": {

            "llm":
                "llama3.2",

            "embedding":
                "nomic-embed-text"
        }
    }


# ============================================================
# ERROR HANDLER
# ============================================================

@app.exception_handler(
    Exception
)
async def global_exception_handler(
    request,
    exc
):

    return JSONResponse(

        status_code=500,

        content={

            "success":
                False,

            "error":
                str(exc),

            "message":
                "An unexpected backend error occurred."
        }
    )


# ============================================================
# RUN FASTAPI
# ============================================================

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(

        "backend.main:app",

        host="127.0.0.1",

        port=8000,

        reload=True
    )