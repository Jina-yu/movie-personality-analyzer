import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './styles/globals.css';

// 페이지 컴포넌트 import
import Home from './pages/Home';
import MovieEvaluation from './pages/MovieEvaluation';
import PersonalityResults from './pages/PersonalityResults';

// 네비게이션 컴포넌트
const Navigation = () => {
  return (
    <nav style={{
      position: 'fixed',
      top: '20px',
      left: '20px',
      zIndex: 1000,
      display: 'flex',
      gap: 'var(--spacing-sm)'
    }}>
      <a
        href="/"
        style={{
          background: 'var(--color-bg-card)',
          color: 'var(--color-text-primary)',
          padding: 'var(--spacing-sm) var(--spacing-md)',
          borderRadius: 'var(--radius-medium)',
          fontSize: 'var(--font-size-sm)',
          textDecoration: 'none',
          border: '1px solid var(--color-text-secondary)'
        }}
      >
        🏠 홈
      </a>
    </nav>
  );
};

function App() {
  return (
    <Router>
      <div className="App">
        <Navigation />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/evaluate" element={<MovieEvaluation />} />
          <Route path="/results" element={<PersonalityResults />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
