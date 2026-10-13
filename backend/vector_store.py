from langchain_community.vectorstores import FAISS
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document

import pandas as pd
import os


# ============================================================
# DATASET PATH
# ============================================================

CSV_PATH = r"C:\Users\T9960\Downloads\archive\recipe.csv"


# ============================================================
# FAISS INDEX LOCATION
# ============================================================

FAISS_PATH = "./faiss_index"


# ============================================================
# CREATE VECTOR STORE
# ============================================================

def create_vector_store():

    print("Loading recipe dataset...")

    df = pd.read_csv(CSV_PATH)

    print(f"Loaded {len(df)} recipes.")

    embedding_documents = []


    # ========================================================
    # CREATE DOCUMENTS
    # ========================================================

    for _, row in df.iterrows():

        title = str(row["Title"])

        ingredients = str(
            row["Ingredients"]
        )

        instructions = str(
            row["Instructions"]
        )

        image_name = str(
            row["Image_Name"]
        )


        # ====================================================
        # TEXT USED FOR EMBEDDINGS
        # ====================================================

        retrieval_text = f"""
Recipe Name: {title}

Ingredients:
{ingredients}
"""


        # ====================================================
        # DOCUMENT
        # ====================================================

        document = Document(

            page_content=retrieval_text,

            metadata={

                "title": title,

                "ingredients": ingredients,

                "instructions": instructions,

                # NEW:
                # Store the dataset image filename
                "image_name": image_name
            }
        )


        embedding_documents.append(
            document
        )


    # ========================================================
    # LOAD EMBEDDING MODEL
    # ========================================================

    print("Loading embedding model...")

    embeddings = OllamaEmbeddings(
        model="nomic-embed-text"
    )


    # ========================================================
    # CREATE FAISS INDEX
    # ========================================================

    print("Creating FAISS index...")

    print("Embedding recipes...")


    batch_size = 100


    # ========================================================
    # FIRST BATCH
    # ========================================================

    first_batch = embedding_documents[
        :batch_size
    ]


    vector_store = FAISS.from_documents(

        first_batch,

        embeddings
    )


    print(
        f"Embedded "
        f"{len(first_batch)}/"
        f"{len(embedding_documents)} recipes"
    )


    # ========================================================
    # ADD REMAINING RECIPES
    # ========================================================

    for i in range(

        batch_size,

        len(embedding_documents),

        batch_size
    ):

        batch = embedding_documents[
            i:i + batch_size
        ]


        vector_store.add_documents(
            batch
        )


        current = min(

            i + batch_size,

            len(embedding_documents)
        )


        print(
            f"Embedded "
            f"{current}/"
            f"{len(embedding_documents)} recipes"
        )


    # ========================================================
    # SAVE FAISS INDEX
    # ========================================================

    print("\nSaving FAISS index...")


    os.makedirs(
        FAISS_PATH,
        exist_ok=True
    )


    vector_store.save_local(
        FAISS_PATH
    )


    print(
        "\n==================================="
    )

    print(
        "FAISS index created successfully!"
    )

    print(
        "==================================="
    )

    print(
        f"Saved at: {FAISS_PATH}"
    )


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    create_vector_store()