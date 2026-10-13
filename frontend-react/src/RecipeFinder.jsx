import { useState } from "react";
import axios from "axios";
import { Link } from "react-router-dom";
import "./RecipeFinder.css";


function RecipeFinder() {

  const [searchMode, setSearchMode] = useState("ingredients");

  const [ingredients, setIngredients] = useState("");
  const [dishName, setDishName] = useState("");

  // IMAGE INGREDIENT DETECTION
  const [ingredientImage, setIngredientImage] = useState(null);
  const [imageLoading, setImageLoading] = useState(false);

  const [recipes, setRecipes] = useState([]);
  const [selectedRecipe, setSelectedRecipe] = useState(null);

  const [recommendation, setRecommendation] = useState("");

  const [loading, setLoading] = useState(false);
  const [aiLoading, setAiLoading] = useState(false);

  const [error, setError] = useState("");


  // ============================================================
  // BACKEND URL
  // ============================================================

  const BACKEND_URL = "http://127.0.0.1:8001";


  // ============================================================
  // DETECT INGREDIENTS FROM IMAGE
  // ============================================================

  const detectIngredientsFromImage = async (file) => {

    if (!file) {
      return;
    }

    setError("");
    setImageLoading(true);

    try {

      const formData = new FormData();

      formData.append("file", file);

      const response = await axios.post(
        `${BACKEND_URL}/detect-ingredients`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data"
          }
        }
      );

      const detected =
        response.data.ingredients || [];


      if (detected.length === 0) {

        setError(
          "No ingredients could be detected. Try a clearer image."
        );

        return;
      }


      // Put detected ingredients into
      // the existing ingredient input box
      setIngredients(
        detected.join(", ")
      );

    }

    catch (err) {

      console.error(
        "Image detection error:",
        err
      );

      setError(
        err.response?.data?.detail ||
        "Could not detect ingredients from the image."
      );

    }

    finally {

      setImageLoading(false);

    }

  };


  // ============================================================
  // FIND RECIPES
  // ============================================================

  const findRecipe = async () => {

    const query =
      searchMode === "ingredients"
        ? ingredients.trim()
        : dishName.trim();


    if (!query) {

      setError(
        searchMode === "ingredients"
          ? "Please enter at least one ingredient."
          : "Please enter a dish name."
      );

      return;
    }


    setError("");
    setLoading(true);

    setRecipes([]);
    setSelectedRecipe(null);
    setRecommendation("");


    try {

      let response;


      // ========================================================
      // INGREDIENT SEARCH
      // ========================================================

      if (searchMode === "ingredients") {

        response = await axios.post(
          `${BACKEND_URL}/recommend`,
          {
            ingredients: query
          }
        );

      }


      // ========================================================
      // DISH SEARCH
      // ========================================================

      else {

        response = await axios.post(
          `${BACKEND_URL}/search-dish`,
          {
            ingredients: query
          }
        );

      }


      setRecipes(
        response.data.top_recipes || []
      );

    }

    catch (err) {

      console.error(err);

      setError(
        "Could not connect to the FastAPI backend. Please make sure FastAPI is running."
      );

    }

    finally {

      setLoading(false);

    }

  };


  // ============================================================
  // SELECT RECIPE
  // ============================================================

  const selectRecipe = async (recipe) => {

    setSelectedRecipe(recipe);

    setRecommendation("");

    setError("");

    setAiLoading(true);


    const userQuery =
      searchMode === "ingredients"
        ? ingredients.trim()
        : dishName.trim();


    try {

      const response = await axios.post(
        `${BACKEND_URL}/recommend-selected`,
        {
          ingredients: userQuery,
          recipe_title: recipe.title
        }
      );


      setRecommendation(
        response.data.recommendation || ""
      );

    }

    catch (err) {

      console.error(err);

      setError(
        "Could not generate AI recommendation."
      );

    }

    finally {

      setAiLoading(false);

    }

  };


  // ============================================================
  // CHANGE SEARCH MODE
  // ============================================================

  const changeMode = (mode) => {

    setSearchMode(mode);

    setRecipes([]);

    setSelectedRecipe(null);

    setRecommendation("");

    setError("");

  };


  // ============================================================
  // CLEAR
  // ============================================================

  const clearAll = () => {

    setIngredients("");

    setDishName("");

    setIngredientImage(null);

    setImageLoading(false);

    setRecipes([]);

    setSelectedRecipe(null);

    setRecommendation("");

    setError("");

  };


  // ============================================================
  // MATCH PERCENTAGE
  // ============================================================

  const getMatchPercentage = (recipe) => {

    if (searchMode === "dish") {
      return null;
    }

    return Math.round(
      recipe.match_percentage ?? 0
    );

  };


  // ============================================================
  // RECIPE COVERAGE
  // ============================================================

  const getRecipeCoverage = (recipe) => {

    if (searchMode === "dish") {
      return null;
    }

    return Math.round(
      recipe.recipe_coverage ?? 0
    );

  };


  // ============================================================
  // RANK
  // ============================================================

  const getRank = (index) => {

    const ranks = [
      "🥇",
      "🥈",
      "🥉"
    ];

    return (
      ranks[index] ||
      `#${index + 1}`
    );

  };


  // ============================================================
  // IMAGE URL
  // ============================================================

  const getImageUrl = (recipe) => {

    if (!recipe) {
      return "";
    }


    // Complete URL
    if (
      recipe.image &&
      (
        recipe.image.startsWith("http://") ||
        recipe.image.startsWith("https://")
      )
    ) {

      return recipe.image;

    }


    // Backend path
    if (
      recipe.image &&
      recipe.image.startsWith("/")
    ) {

      return `${BACKEND_URL}${recipe.image}`;

    }


    // image_name or image
    const imageName =
      recipe.image_name ||
      recipe.image ||
      "";


    if (!imageName) {
      return "";
    }


    const cleanImageName =
      imageName.replace(/^\/+/, "");


    const finalImageName =
      cleanImageName.toLowerCase().endsWith(".jpg") ||
      cleanImageName.toLowerCase().endsWith(".jpeg") ||
      cleanImageName.toLowerCase().endsWith(".png") ||
      cleanImageName.toLowerCase().endsWith(".webp")
        ? cleanImageName
        : `${cleanImageName}.jpg`;


    return `${BACKEND_URL}/recipe-images/${encodeURIComponent(finalImageName)}`;

  };


  // ============================================================
  // IMAGE ERROR HANDLER
  // ============================================================

  const handleImageError = (event) => {

    event.currentTarget.style.display = "none";

  };


  // ============================================================
  // UI
  // ============================================================

  return (

    <div className="recipe-page">


      {/* ======================================================
          NAVBAR
          ====================================================== */}

      <header className="recipe-header">

        <div className="recipe-header-content">


          {/* LOGO */}

          <Link
            to="/"
            className="recipe-brand"
          >

            <div className="recipe-brand-icon">
              🧞‍♀️
            </div>

            <div>

              <h1>
                RecipeGenie
              </h1>

              <p>
                AI-Powered Recipe Assistant
              </p>

            </div>

          </Link>


          {/* NAVIGATION */}

          <nav className="recipe-nav">

            <Link
              to="/"
              className="recipe-nav-link"
            >
              Home
            </Link>


            <Link
              to="/recipes"
              className="recipe-nav-link active"
            >
              Find Recipes
            </Link>


            <Link
              to="/how-it-works"
              className="recipe-nav-link"
            >
              How It Works
            </Link>


            <Link
              to="/about"
              className="recipe-nav-link"
            >
              About
            </Link>

          </nav>

        </div>

      </header>


      {/* ======================================================
          MAIN CONTENT
          ====================================================== */}

      <main className="recipe-main">


        {/* ====================================================
            HERO
            ==================================================== */}

        <section className="recipe-hero">

          <h2>
            Find Your Perfect Recipe
          </h2>

          <p>
            Turn your available ingredients into delicious
            meals while reducing kitchen waste.
          </p>

        </section>


        {/* ====================================================
            SEARCH CARD
            ==================================================== */}

        <section className="recipe-search-card">


          {/* SEARCH MODE */}

          <div className="search-mode-buttons">

            <button
              className={
                searchMode === "ingredients"
                  ? "mode-btn active"
                  : "mode-btn"
              }
              onClick={() =>
                changeMode("ingredients")
              }
            >
              🥕 Search by Ingredients
            </button>


            <button
              className={
                searchMode === "dish"
                  ? "mode-btn active"
                  : "mode-btn"
              }
              onClick={() =>
                changeMode("dish")
              }
            >
              🍽️ Search by Dish
            </button>

          </div>


          {/* ==================================================
              INGREDIENT SEARCH
              ================================================== */}

          {searchMode === "ingredients" && (

            <div className="ingredient-search-section">

              <label>
                What ingredients do you have?
              </label>


              <div className="search-input-row">

                <input
                  type="text"
                  className="recipe-search-input"
                  placeholder="e.g. tomato, onion, potato"
                  value={ingredients}
                  onChange={(e) =>
                    setIngredients(e.target.value)
                  }
                  onKeyDown={(e) => {

                    if (e.key === "Enter") {
                      findRecipe();
                    }

                  }}
                />


                <button
                  className="find-recipe-btn"
                  onClick={findRecipe}
                  disabled={loading || imageLoading}
                >

                  {loading
                    ? "Finding..."
                    : "Find Recipes"}

                </button>


                <button
                  className="clear-btn"
                  onClick={clearAll}
                >
                  Clear
                </button>

              </div>


              {/* ==================================================
                  IMAGE UPLOAD
                  ================================================== */}

              <div className="ingredient-image-section">

                <div className="image-upload-divider">
                  <span>OR</span>
                </div>


                <label
                  htmlFor="ingredient-image-upload"
                  className="ingredient-upload-btn"
                >
                  📷 Upload Ingredient Image
                </label>


                <input
                  id="ingredient-image-upload"
                  type="file"
                  accept="image/*"
                  style={{
                    display: "none"
                  }}
                  onChange={(e) => {

                    const file =
                      e.target.files?.[0];

                    if (!file) {
                      return;
                    }

                    setIngredientImage(file);

                    detectIngredientsFromImage(file);

                    // Allow selecting the same image again
                    e.target.value = "";

                  }}
                />


                {imageLoading && (

                  <p className="image-detection-loading">
                    🔄 Detecting ingredients...
                  </p>

                )}


                {ingredientImage &&
                  !imageLoading && (

                    <p className="image-selected-text">
                      📷 {ingredientImage.name}
                    </p>

                  )}

              </div>


              {/* ==================================================
                  DETECTED INGREDIENTS INFO
                  ================================================== */}

              {ingredients && ingredientImage &&
                !imageLoading && (

                  <div className="detected-ingredients-box">

                    <strong>
                      Detected ingredients:
                    </strong>

                    <p>
                      {ingredients}
                    </p>

                    <small>
                      You can edit the ingredients above
                      before finding recipes.
                    </small>

                  </div>

                )}

            </div>

          )}


          {/* ==================================================
              DISH SEARCH
              ================================================== */}

          {searchMode === "dish" && (

            <div className="dish-search-section">

              <label>
                What dish are you looking for?
              </label>


              <div className="search-input-row">

                <input
                  type="text"
                  className="recipe-search-input"
                  placeholder="e.g. Chicken Biryani"
                  value={dishName}
                  onChange={(e) =>
                    setDishName(e.target.value)
                  }
                  onKeyDown={(e) => {

                    if (e.key === "Enter") {
                      findRecipe();
                    }

                  }}
                />


                <button
                  className="find-recipe-btn"
                  onClick={findRecipe}
                  disabled={loading}
                >

                  {loading
                    ? "Searching..."
                    : "Search Dish"}

                </button>


                <button
                  className="clear-btn"
                  onClick={clearAll}
                >
                  Clear
                </button>

              </div>

            </div>

          )}


          {/* ERROR */}

          {error && (

            <div className="recipe-error">
              ⚠️ {error}
            </div>

          )}

        </section>


        {/* ====================================================
            LOADING
            ==================================================== */}

        {loading && (

          <div className="recipe-loading">

            <div className="loading-spinner"></div>

            <p>
              Finding the best recipes for you...
            </p>

          </div>

        )}


        {/* ====================================================
            RESULTS
            ==================================================== */}

        {!loading &&
          recipes.length > 0 && (

            <section className="recipe-results">


              <div className="results-header">

                <h3>
                  Recommended Recipes
                </h3>

                <p>
                  Based on your available ingredients
                </p>

              </div>


              <div className="recipe-grid">

                {recipes.map(
                  (recipe, index) => (

                    <div
                      className="recipe-card"
                      key={
                        recipe.title ||
                        index
                      }
                    >


                      {/* RANK */}

                      <div className="recipe-rank">
                        {getRank(index)}
                      </div>


                      {/* IMAGE */}

                      {getImageUrl(recipe) && (

                        <img
                          src={getImageUrl(recipe)}
                          alt={recipe.title}
                          className="recipe-image"
                          onError={handleImageError}
                        />

                      )}


                      {/* CONTENT */}

                      <div className="recipe-card-content">

                        <h4>
                          {recipe.title}
                        </h4>


                        {/* INGREDIENT SEARCH METRICS */}

                        {searchMode ===
                          "ingredients" && (

                          <div className="recipe-metrics">

                            <div className="metric">

                              <span>
                                Ingredient Match
                              </span>

                              <strong>
                                {getMatchPercentage(recipe)}%
                              </strong>

                            </div>


                            <div className="metric">

                              <span>
                                Recipe Coverage
                              </span>

                              <strong>
                                {getRecipeCoverage(recipe)}%
                              </strong>

                            </div>

                          </div>

                        )}


                        {/* MATCHED INGREDIENTS */}

                        {searchMode ===
                          "ingredients" &&
                          recipe.matched?.length > 0 && (

                          <div className="ingredient-info">

                            <strong>
                              ✓ You have:
                            </strong>

                            <p>
                              {recipe.matched.join(", ")}
                            </p>

                          </div>

                        )}


                        {/* MISSING INGREDIENTS */}

                        {searchMode ===
                          "ingredients" &&
                          recipe.missing?.length > 0 && (

                          <div className="ingredient-info missing">

                            <strong>
                              + You need:
                            </strong>

                            <p>
                              {recipe.missing.join(", ")}
                            </p>

                          </div>

                        )}


                        {/* VIEW RECIPE */}

                        <button
                          className="view-recipe-btn"
                          onClick={() =>
                            selectRecipe(recipe)
                          }
                        >
                          View Recipe
                        </button>

                      </div>

                    </div>

                  )
                )}

              </div>

            </section>

          )}


        {/* ====================================================
            NO RESULTS
            ==================================================== */}

        {!loading &&
          !error &&
          recipes.length === 0 &&
          (ingredients || dishName) && (

            <div className="no-results">

              <div className="no-results-icon">
                🍳
              </div>

              <h3>
                No recipes found
              </h3>

              <p>
                Try different ingredients or
                search for another dish.
              </p>

            </div>

          )}


        {/* ====================================================
            SELECTED RECIPE
            ==================================================== */}

        {selectedRecipe && (

          <section className="selected-recipe-section">


            <div className="selected-recipe-card">


              <div className="selected-recipe-header">

                <h3>
                  {selectedRecipe.title}
                </h3>

                <button
                  className="close-recipe-btn"
                  onClick={() =>
                    setSelectedRecipe(null)
                  }
                >
                  ✕
                </button>

              </div>


              {/* SELECTED RECIPE IMAGE */}

              {getImageUrl(selectedRecipe) && (

                <img
                  src={getImageUrl(selectedRecipe)}
                  alt={selectedRecipe.title}
                  className="selected-recipe-image"
                  onError={handleImageError}
                />

              )}


              {/* INGREDIENTS */}

              {selectedRecipe.ingredients && (

                <div className="selected-recipe-content">

                  <h4>
                    🥕 Ingredients
                  </h4>

                  <p>
                    {Array.isArray(
                      selectedRecipe.ingredients
                    )
                      ? selectedRecipe.ingredients.join(", ")
                      : selectedRecipe.ingredients}
                  </p>

                </div>

              )}


              {/* INSTRUCTIONS */}

              {selectedRecipe.instructions && (

                <div className="selected-recipe-content">

                  <h4>
                    👨‍🍳 Instructions
                  </h4>

                  <p>
                    {selectedRecipe.instructions}
                  </p>

                </div>

              )}


              {/* AI RECOMMENDATION */}

              <div className="ai-recommendation">

                <h4>
                  🤖 RecipeGenie AI
                </h4>


                {aiLoading ? (

                  <div className="ai-loading">

                    <div className="loading-spinner"></div>

                    <p>
                      Preparing your personalized recommendation...
                    </p>

                  </div>

                ) : (

                  <p>
                    {recommendation ||
                      "Select a recipe to get an AI-powered recommendation."}
                  </p>

                )}

              </div>

            </div>

          </section>

        )}

      </main>


      {/* ======================================================
          FOOTER
          ====================================================== */}

      <footer className="recipe-footer">

        <p>
          © 2026 RecipeGenie — Reduce Waste.
          Cook Smart. Eat Better.
        </p>

      </footer>

    </div>

  );

}


export default RecipeFinder;