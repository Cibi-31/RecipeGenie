import { BrowserRouter, Routes, Route } from "react-router-dom";

import Home from "./Home";
import RecipeFinder from "./RecipeFinder";
import HowItWorks from "./HowItWorks";
import About from "./About";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/recipes" element={<RecipeFinder />} />
        <Route path="/how-it-works" element={<HowItWorks />} />
        <Route path="/about" element={<About />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;