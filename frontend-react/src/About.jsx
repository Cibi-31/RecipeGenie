import { Link } from "react-router-dom";
import "./About.css";

function About() {
  return (
    <div className="about-page">

      {/* ================= NAVBAR ================= */}
      <nav className="about-navbar">

        <Link to="/" className="about-logo">
          <div className="about-logo-icon">🧞‍♀️</div>

          <div>
            <div className="about-logo-title">
              RecipeGenie
            </div>

            <div className="about-logo-subtitle">
              AI-Powered Recipe Assistant
            </div>
          </div>
        </Link>

        <div className="about-nav-links">

          <Link to="/" className="about-nav-link">
            Home
          </Link>

          <Link to="/recipes" className="about-nav-link">
            Find Recipes
          </Link>

          <Link to="/how-it-works" className="about-nav-link">
            How It Works
          </Link>

          <Link
            to="/about"
            className="about-nav-link active"
          >
            About
          </Link>

        </div>

        <Link
          to="/recipes"
          className="about-start-btn"
        >
          Get Started →
        </Link>

      </nav>


      {/* ================= HERO ================= */}
      <section className="about-hero">

        <div className="about-hero-icon">
          🧞‍♀️
        </div>

        <div className="about-label">
          ABOUT RECIPEGENIE
        </div>

        <h1>
          Cook More.
          <br />
          <span>Waste Less.</span>
        </h1>

        <p>
          RecipeGenie is an AI-powered recipe recommendation
          system that helps users discover delicious recipes
          using ingredients already available in their kitchen.
        </p>

      </section>


      {/* ================= PURPOSE ================= */}
      <section className="about-mission">

        <div className="mission-content">

          <div className="mission-text">

            <div className="about-section-label">
              OUR PURPOSE
            </div>

            <h2>
              Turning Kitchen Leftovers
              <br />
              into <span>Useful Meals</span>
            </h2>

            <p>
              Many ingredients are left unused because people
              are unsure what they can prepare with them.
              RecipeGenie helps solve this problem by connecting
              available ingredients with suitable recipes.
            </p>

            <p>
              Users simply enter the ingredients they have.
              The system searches its recipe knowledge base
              and retrieves recipes that are relevant to those
              ingredients.
            </p>

            <p>
              RecipeGenie also identifies the ingredients that
              are available and the ingredients that may still
              be required for the selected recipe.
            </p>

          </div>


          <div className="mission-visual">

            <div className="mission-circle">
              ♻️
            </div>

            <div className="mission-food food-a">
              🍅
            </div>

            <div className="mission-food food-b">
              🥕
            </div>

            <div className="mission-food food-c">
              🧅
            </div>

            <div className="mission-food food-d">
              🥬
            </div>

          </div>

        </div>

      </section>


      {/* ================= FEATURES ================= */}
      <section className="about-features">

        <div className="about-section-label">
          WHAT RECIPEGENIE OFFERS
        </div>

        <h2>
          Designed for <span>Smarter Cooking</span>
        </h2>


        <div className="about-feature-grid">

          <div className="about-feature-card">

            <div className="about-feature-icon">
              🥕
            </div>

            <h3>
              Ingredient-Based Search
            </h3>

            <p>
              Enter ingredients available in your kitchen
              and discover relevant recipes.
            </p>

          </div>


          <div className="about-feature-card">

            <div className="about-feature-icon">
              🔎
            </div>

            <h3>
              Smart Recipe Retrieval
            </h3>

            <p>
              RecipeGenie uses FAISS to retrieve recipes
              that are semantically relevant to the user's
              ingredients.
            </p>

          </div>


          <div className="about-feature-card">

            <div className="about-feature-icon">
              🤖
            </div>

            <h3>
              AI Recommendation
            </h3>

            <p>
              Llama 3.2 generates an explanation for why
              the selected recipe is suitable.
            </p>

          </div>


          <div className="about-feature-card">

            <div className="about-feature-icon">
              ♻️
            </div>

            <h3>
              Reduce Food Waste
            </h3>

            <p>
              Make better use of ingredients that are
              already available in your kitchen.
            </p>

          </div>

        </div>

      </section>


      {/* ================= TECHNOLOGY ================= */}
      <section className="about-tech">

        <div className="about-section-label">
          TECHNOLOGY
        </div>

        <h2>
          Powered by <span>AI & RAG</span>
        </h2>

        <p className="about-tech-intro">
          RecipeGenie combines retrieval technology and
          generative AI to provide context-aware recipe
          recommendations.
        </p>


        <div className="about-tech-flow">

          <div className="tech-flow-item">

            <div className="tech-flow-icon">
              📚
            </div>

            <strong>
              Recipe Dataset
            </strong>

            <span>
              Recipe knowledge
            </span>

          </div>


          <div className="tech-flow-arrow">
            →
          </div>


          <div className="tech-flow-item">

            <div className="tech-flow-icon">
              🔎
            </div>

            <strong>
              FAISS
            </strong>

            <span>
              Recipe retrieval
            </span>

          </div>


          <div className="tech-flow-arrow">
            →
          </div>


          <div className="tech-flow-item">

            <div className="tech-flow-icon">
              🔗
            </div>

            <strong>
              LangChain
            </strong>

            <span>
              RAG orchestration
            </span>

          </div>


          <div className="tech-flow-arrow">
            →
          </div>


          <div className="tech-flow-item">

            <div className="tech-flow-icon">
              🤖
            </div>

            <strong>
              Llama 3.2
            </strong>

            <span>
              AI explanation
            </span>

          </div>

        </div>

      </section>


      {/* ================= CTA ================= */}
      <section className="about-cta">

        <div className="about-cta-icon">
          🍽️
        </div>

        <h2>
          Have Ingredients?
        </h2>

        <p>
          Let RecipeGenie help you discover what you can cook.
        </p>

        <Link
          to="/recipes"
          className="about-cta-btn"
        >
          Find My Recipe →
        </Link>

      </section>


      {/* ================= FOOTER ================= */}
      <footer className="about-footer">

        <div>

          <strong>
            🧞‍♀️ RecipeGenie
          </strong>

          <p>
            Smart ingredients. Brighter meals.
          </p>

        </div>


        <div className="about-footer-links">

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

export default About;