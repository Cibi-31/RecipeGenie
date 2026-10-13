import { Link } from "react-router-dom";
import "./HowItWorks.css";

function HowItWorks() {
  return (
    <div className="how-page">

      {/* NAVBAR */}
      <nav className="how-navbar">

        <Link to="/" className="how-logo">
          <div className="how-logo-icon">🧞‍♀️</div>

          <div>
            <div className="how-logo-title">RecipeGenie</div>
            <div className="how-logo-subtitle">
              AI-Powered Recipe Assistant
            </div>
          </div>
        </Link>

        <div className="how-nav-links">
          <Link to="/" className="how-nav-link">
            Home
          </Link>

          <Link to="/recipes" className="how-nav-link">
            Find Recipes
          </Link>

          <Link to="/how-it-works" className="how-nav-link active">
            How It Works
          </Link>

          <Link to="/about" className="how-nav-link">
            About
          </Link>
        </div>

        <Link to="/recipes" className="how-start-btn">
          Get Started →
        </Link>

      </nav>


      {/* HERO */}
      <section className="how-hero">

        <div className="how-hero-content">

          <div className="how-label">
            HOW RECIPEGENIE WORKS
          </div>

          <h1>
            From Your Ingredients
            <br />
            to <span>Delicious Recipes</span>
          </h1>

          <p>
            RecipeGenie combines recipe data, semantic search,
            Retrieval-Augmented Generation, and AI to help you
            discover recipes using ingredients already available
            in your kitchen.
          </p>

          <Link to="/recipes" className="how-hero-btn">
            Try RecipeGenie →
          </Link>

        </div>

        <div className="how-hero-visual">
          <div className="how-big-icon">🧞‍♀️</div>
          <div className="how-floating-icon icon-one">🥕</div>
          <div className="how-floating-icon icon-two">🍅</div>
          <div className="how-floating-icon icon-three">🧅</div>
          <div className="how-floating-icon icon-four">🥬</div>
        </div>

      </section>


      {/* STEPS */}
      <section className="how-steps-section">

        <div className="how-section-label">
          THE PROCESS
        </div>

        <h2>
          How <span>RecipeGenie</span> Finds Your Recipe
        </h2>

        <p className="how-intro">
          The system follows a simple AI-powered pipeline to
          transform your available ingredients into useful
          recipe recommendations.
        </p>


        <div className="how-process">

          {/* STEP 1 */}
          <div className="how-process-card">

            <div className="process-number">
              01
            </div>

            <div className="process-icon">
              🥕
            </div>

            <h3>
              Enter Your Ingredients
            </h3>

            <p>
              Enter the ingredients that are currently
              available in your kitchen, such as tomato,
              onion, potato or paneer.
            </p>

          </div>


          <div className="process-arrow">
            →
          </div>


          {/* STEP 2 */}
          <div className="how-process-card">

            <div className="process-number">
              02
            </div>

            <div className="process-icon">
              🔎
            </div>

            <h3>
              Recipe Retrieval
            </h3>

            <p>
              FAISS performs semantic similarity search
              to retrieve recipes that are relevant to
              the ingredients provided by the user.
            </p>

          </div>


          <div className="process-arrow">
            →
          </div>


          {/* STEP 3 */}
          <div className="how-process-card">

            <div className="process-number">
              03
            </div>

            <div className="process-icon">
              📊
            </div>

            <h3>
              Ingredient Matching
            </h3>

            <p>
              RecipeGenie compares the user's available
              ingredients with the ingredients required
              by the retrieved recipes.
            </p>

          </div>


          <div className="process-arrow">
            →
          </div>


          {/* STEP 4 */}
          <div className="how-process-card">

            <div className="process-number">
              04
            </div>

            <div className="process-icon">
              🤖
            </div>

            <h3>
              AI Recommendation
            </h3>

            <p>
              Llama 3.2 analyzes the selected recipe and
              generates a concise explanation of why it
              is suitable for the user's ingredients.
            </p>

          </div>

        </div>

      </section>


      {/* RAG SECTION */}
      <section className="rag-section">

        <div className="rag-content">

          <div className="rag-text">

            <div className="how-section-label">
              RAG PIPELINE
            </div>

            <h2>
              Retrieval-Augmented
              <br />
              <span>Generation</span>
            </h2>

            <p>
              RecipeGenie uses a Retrieval-Augmented Generation
              approach. Instead of asking the language model to
              create recipes from scratch, relevant recipe
              information is first retrieved from the recipe
              dataset.
            </p>

            <p>
              The retrieved recipe context is then provided to
              Llama 3.2, which generates an explanation for the
              selected recipe.
            </p>

          </div>


          <div className="rag-flow">

            <div className="rag-box">
              <span>📚</span>
              <strong>Recipe Dataset</strong>
              <small>Recipe knowledge</small>
            </div>

            <div className="rag-line">↓</div>

            <div className="rag-box">
              <span>🧠</span>
              <strong>FAISS</strong>
              <small>Semantic retrieval</small>
            </div>

            <div className="rag-line">↓</div>

            <div className="rag-box">
              <span>🔗</span>
              <strong>LangChain</strong>
              <small>RAG orchestration</small>
            </div>

            <div className="rag-line">↓</div>

            <div className="rag-box">
              <span>🤖</span>
              <strong>Llama 3.2</strong>
              <small>AI explanation</small>
            </div>

          </div>

        </div>

      </section>


      {/* TECHNOLOGY */}
      <section className="technology-section">

        <div className="how-section-label">
          TECHNOLOGY STACK
        </div>

        <h2>
          Technologies Behind <span>RecipeGenie</span>
        </h2>

        <div className="technology-grid">

          <div className="technology-card">
            <div>🗄️</div>
            <h3>Recipe Dataset</h3>
            <p>
              Provides the recipe names, ingredients and
              cooking instructions used by the system.
            </p>
          </div>

          <div className="technology-card">
            <div>🔍</div>
            <h3>FAISS</h3>
            <p>
              Performs efficient vector similarity search
              to retrieve relevant recipes.
            </p>
          </div>

          <div className="technology-card">
            <div>🧩</div>
            <h3>LangChain</h3>
            <p>
              Connects the retrieval and language model
              components in the RAG pipeline.
            </p>
          </div>

          <div className="technology-card">
            <div>🤖</div>
            <h3>Llama 3.2</h3>
            <p>
              Generates the natural-language explanation
              for the selected recipe.
            </p>
          </div>

          <div className="technology-card">
            <div>🧠</div>
            <h3>Nomic Embed Text</h3>
            <p>
              Converts recipe information into vector
              embeddings for semantic search.
            </p>
          </div>

          <div className="technology-card">
            <div>⚡</div>
            <h3>FastAPI</h3>
            <p>
              Provides the backend API connecting the
              frontend with the AI pipeline.
            </p>
          </div>

        </div>

      </section>


      {/* CTA */}
      <section className="how-final-cta">

        <h2>
          Ready to Find Your Next Meal?
        </h2>

        <p>
          Tell RecipeGenie what you have and discover
          what you can cook.
        </p>

        <Link to="/recipes" className="how-hero-btn">
          Find My Recipe →
        </Link>

      </section>


      {/* FOOTER */}
      <footer className="how-footer">

        <div>
          <strong>🧞‍♀️ RecipeGenie</strong>
          <p>
            Smart ingredients. Brighter meals.
          </p>
        </div>

        <div className="footer-links">

          <Link to="/">
            Home
          </Link>

          <Link to="/recipes">
            Find Recipes
          </Link>

          <Link to="/how-it-works">
            How It Works
          </Link>

          <Link to="/about">
            About
          </Link>

        </div>

      </footer>

    </div>
  );
}

export default HowItWorks;