from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate

from backend.retriever import search_recipes


def create_rag_system():

    llm = ChatOllama(
        model="llama3.2",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template("""
You are an AI Kitchen Waste and Recipe Assistant.

The user has these ingredients:

{question}

The Python program has retrieved the BEST matching recipe
from the recipe database.

Use ONLY the information provided below.

IMPORTANT RULES:

1. Do NOT invent ingredients.
2. Do NOT invent recipes.
3. Do NOT invent cooking instructions.
4. Do NOT add health claims.
5. Do NOT add unsupported claims.
6. Do NOT change the Available Ingredients Used.
7. Do NOT change the Missing Ingredients.
8. The Available Ingredients Used and Missing Ingredients
   were calculated by Python and must be treated as facts.
9. You may make the answer easier to read, but do not
   change the meaning of the recipe.
10. Explain briefly how using the available ingredients
    can help reduce kitchen waste.

Return the answer using EXACTLY this structure:

Recipe Name:
[recipe name]

Ingredient Match:
[available ingredients used]

Missing Ingredients:
[missing ingredients]

Why Recommended:
[brief explanation based only on the provided information]

Cooking Instructions:
[provided cooking instructions]

RECIPE INFORMATION:

{context}
""")

    return llm, prompt


def run_rag(question):

    print("\nSearching recipe database...")

    # Search and rank recipes
    results = search_recipes(
        question,
        k=10
    )

    if not results:

        return (
            "Sorry, I could not find any "
            "suitable recipes."
        )

    # Select the best matching recipe
    best_result = results[0]

    document = best_result["document"]

    # Get recipe information
    title = document.metadata.get(
        "title",
        ""
    )

    ingredients = document.metadata.get(
        "ingredients",
        ""
    )

    instructions = document.metadata.get(
        "instructions",
        ""
    )

    matched = best_result["matched"]

    missing = best_result["missing"]

    # Create grounded context
    context = f"""
Recipe Name:
{title}

Recipe Ingredients:
{ingredients}

Available Ingredients Used:
{", ".join(matched) if matched else "None"}

Missing Ingredients:
{", ".join(missing) if missing else "None"}

Cooking Instructions:
{instructions}
"""

    llm, prompt = create_rag_system()

    messages = prompt.format_messages(
        question=question,
        context=context
    )

    print(
        "Generating recommendation using Llama 3.2..."
    )

    response = llm.invoke(messages)

    return response.content


if __name__ == "__main__":

    print("=" * 60)
    print("AI KITCHEN WASTE & RECIPE ASSISTANT")
    print("=" * 60)

    question = input(
        "\nEnter the ingredients you have: "
    )

    answer = run_rag(question)

    print("\n" + "=" * 60)
    print("AI RECIPE RECOMMENDATION")
    print("=" * 60)

    print("\n" + answer)