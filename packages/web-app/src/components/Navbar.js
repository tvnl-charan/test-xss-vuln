import React, { useState, useEffect } from 'react';
import './Navbar.css';

const NAV_LINKS = [
  { label: 'Home',     page: 'home' },
  { label: 'About',    page: 'about' },
  { label: 'Services', page: 'services' },
  { label: 'Work',     page: 'work' },
  { label: 'Contact',  page: 'contact' },
];

function Navbar({ currentPage, navigate, user, onLogout }) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll);
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const handleNav = (page) => {
    navigate(page);
    setMenuOpen(false);
  };

  return (
    <nav className={`navbar ${scrolled ? 'scrolled' : ''}`}>
      <div className="container navbar-inner">
        <button className="logo" onClick={() => handleNav('home')} aria-label="Go home">
          <span className="logo-mark" />
          <span className="logo-text">Nexus</span>
        </button>

        <ul className={`nav-links ${menuOpen ? 'open' : ''}`} role="list">
          {NAV_LINKS.map(({ label, page }) => (
            <li key={page}>
              <button
                className={`nav-link ${currentPage === page ? 'active' : ''}`}
                onClick={() => handleNav(page)}
              >
                {label}
              </button>
            </li>
          ))}
          <li className="mobile-cta">
            <button className="btn btn-primary" onClick={() => handleNav('contact')}>
              Get Started
            </button>
          </li>
        </ul>

        <div className="nav-actions" style={{ display: 'flex', gap: '0.5rem' }}>
          {user ? (
            <>
              <button className="btn" onClick={() => handleNav('admin')}>
                Dashboard
              </button>
              <button className="btn" onClick={onLogout}>
                Logout
              </button>
            </>
          ) : (
            <>
              <button className="btn" onClick={() => handleNav('login')}>
                Login
              </button>
              <button className="btn btn-primary" onClick={() => handleNav('contact')}>
                Get Started
              </button>
            </>
          )}
        </div>

        <button
          className={`hamburger ${menuOpen ? 'open' : ''}`}
          onClick={() => setMenuOpen(!menuOpen)}
          aria-label={menuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={menuOpen}
        >
          <span />
          <span />
          <span />
        </button>
      </div>
    </nav>
  );
}

export default Navbar;
