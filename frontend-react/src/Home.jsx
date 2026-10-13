import { Link } from "react-router-dom";
import "./Home.css";

function Home() {
  return (
    <div className="home-page">

      {/* ==================== NAVBAR ==================== */}
      <nav className="home-navbar">

        <Link to="/" className="home-logo">
          <div className="logo-icon">🧞‍♀️</div>

          <div>
            <div className="logo-title">RecipeGenie</div>
            <div className="logo-subtitle">
              AI-Powered Recipe Assistant
            </div>
          </div>
        </Link>

        <div className="nav-links">

          <Link to="/" className="nav-link active">
            Home
          </Link>

          <Link to="/recipes" className="nav-link">
            Find Recipes
          </Link>

          <Link to="/how-it-works" className="nav-link">
            How It Works
          </Link>

          <Link to="/about" className="nav-link">
            About
          </Link>

        </div>

        <Link to="/recipes" className="get-started-btn">
          Get Started →
        </Link>

      </nav>


      {/* ==================== HERO SECTION ==================== */}
      <section className="hero">

        <div className="hero-content">

          <div className="hero-label">
            SMART INGREDIENTS. BRIGHTER MEALS.
          </div>

          <h1>
            Turn Your
            <br />
            Leftovers into
            <br />
            <span>Delicious Meals</span>
          </h1>

          <p className="hero-description">
            Have extra ingredients in your kitchen?
            Discover delicious recipes using what
            you already have, powered by AI.
            Reduce food waste, save money, and
            enjoy home cooking!
          </p>

          <div className="hero-buttons">

            <Link
              to="/recipes"
              className="primary-hero-btn"
            >
              🔍 Start Finding Recipes →
            </Link>

            <Link
              to="/how-it-works"
              className="secondary-hero-btn"
            >
              ▶ How It Works
            </Link>

          </div>

          <div className="hero-note">
            🍃 Reduce waste. Cook smarter. Live better.
          </div>

        </div>


        {/* ==================== FOOD VISUAL ==================== */}
        <div className="hero-food">

          <div className="food-circle">

            <div className="food-item tomato">
              🍅
            </div>

            <div className="food-item onion">
              🧅
            </div>

            <div className="food-item pepper">
              🫑
            </div>

            <div className="food-item garlic">
              🧄
            </div>

            <div className="food-item carrot">
              🥕
            </div>

            <div className="food-item greens">
              🥬
            </div>

            <div className="cutting-board">

              <div>
                Good Ingredients
              </div>

              <div>
                Brighter Meals
              </div>

              <div>
                Less Waste ♡
              </div>

            </div>

          </div>


          <div className="waste-message">

            <strong>
              Reduce
              <br />
              Food Waste
            </strong>

            <span>
              One Meal
              <br />
              at a Time 🌿
            </span>

          </div>

        </div>

      </section>

    </div>
  );
}

export default Home;