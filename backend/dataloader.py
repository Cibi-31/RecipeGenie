import pandas as pd
from langchain_core.documents import Document

def load_recipes(csv_path):

    # Use the path provided by vector_store.py
    df = pd.read_csv(r"C:\Users\T9960\Downloads\archive\recipe.csv")

    documents = []

    for _, row in df.iterrows():

        title = str(row["Title"])
        ingredients = str(row["Ingredients"])
        instructions = str(row["Instructions"])

        content = f"""
Recipe Name: {title}

Ingredients:
{ingredients}

Cooking Instructions:
{instructions}
"""

        document = Document(
            page_content=content,
            metadata={
                "title": title,
                "ingredients": ingredients,
                "instructions": instructions
            }
        )

        documents.append(document)

    return documents