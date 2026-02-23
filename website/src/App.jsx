import { useState, useEffect, createContext, useContext } from 'react';
import { HashRouter as Router, Routes, Route, Link, useNavigate } from 'react-router-dom';
import HomePage from './pages/HomePage';
import CategoryPage from './pages/CategoryPage';
import SkillPage from './pages/SkillPage';
import AllSkillsPage from './pages/AllSkillsPage';
import BlogPage from './pages/BlogPage';
import SearchBar from './components/SearchBar';

export const SkillsContext = createContext(null);

export function useSkills() {
  return useContext(SkillsContext);
}

function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="navbar-brand">
          <span className="navbar-brand-icon">⚡</span>
          <span>Skills Directory</span>
        </Link>
        <div className="navbar-links">
          <Link to="/" className="navbar-link">Home</Link>
          <Link to="/blog" className="navbar-link">Blog</Link>
          <Link to="/skills" className="navbar-link">All Skills</Link>
          <a
            href="https://the-mehdi.com"
            target="_blank"
            rel="noopener noreferrer"
            className="navbar-link"
          >
            Portfolio
          </a>
          <a
            href="https://github.com/mxn2020/skills"
            target="_blank"
            rel="noopener noreferrer"
            className="github-btn"
          >
            <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
              <path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z" />
            </svg>
            GitHub
          </a>
          <a
            href="https://buymeacoffee.com/mxn2020"
            target="_blank"
            rel="noopener noreferrer"
            className="navbar-link"
            title="Buy me a coffee"
            style={{ display: 'flex', alignItems: 'center', padding: '0.4rem', marginLeft: '0.2rem' }}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 8h1a4 4 0 1 1 0 8h-1"></path>
              <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"></path>
              <line x1="6" y1="2" x2="6" y2="4"></line>
              <line x1="10" y1="2" x2="10" y2="4"></line>
              <line x1="14" y1="2" x2="14" y2="4"></line>
            </svg>
          </a>
        </div>
      </div>
    </nav>
  );
}

function Footer({ data }) {
  return (
    <footer className="footer">
      <div className="footer-inner">
        <p>
          {data ? `${data.totalSkills} skills` : '...'} · Built with ⚡ by{' '}
          <a href="https://the-mehdi.com" target="_blank" rel="noopener noreferrer">
            Mehdi Nabhani
          </a>{' '}
          ·{' '}
          <a href="https://github.com/mxn2020" target="_blank" rel="noopener noreferrer">
            GitHub
          </a>{' '}
          ·{' '}
          <a href="https://buymeacoffee.com/mxn2020" target="_blank" rel="noopener noreferrer">
            Buy me a coffee
          </a>{' '}
          · Apache 2.0 License
        </p>
      </div>
    </footer>
  );
}

function AppContent() {
  const data = useSkills();

  return (
    <div className="app">
      <div className="bg-glow" />
      <div className="bg-grid" />
      <Navbar />
      <main style={{ flex: 1, position: 'relative', zIndex: 1 }}>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/category/:slug" element={<CategoryPage />} />
          <Route path="/category/:slug/:subSlug" element={<CategoryPage />} />
          <Route path="/skill/*" element={<SkillPage />} />
          <Route path="/skills" element={<AllSkillsPage />} />
          <Route path="/blog" element={<BlogPage />} />
          <Route path="/blog/:slug" element={<BlogPage />} />
        </Routes>
      </main>
      <Footer data={data} />
    </div>
  );
}

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch(`${import.meta.env.BASE_URL}skills-index.json`)
      .then(r => r.json())
      .then(setData)
      .catch(console.error);
  }, []);

  return (
    <SkillsContext.Provider value={data}>
      <Router>
        <AppContent />
      </Router>
    </SkillsContext.Provider>
  );
}

export default App;
