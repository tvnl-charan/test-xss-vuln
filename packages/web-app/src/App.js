import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import About from './pages/About';
import Services from './pages/Services';
import Work from './pages/Work';
import Contact from './pages/Contact';
import Admin from './pages/Admin';
import Login from './pages/Login';
import './App.css';

function App() {
  const [currentPage, setCurrentPage] = useState('home');
  const [user, setUser] = useState(null);

  useEffect(() => {
    const token = localStorage.getItem('admin_token');
    const role = localStorage.getItem('user_role');
    const username = localStorage.getItem('username');
    if (token && username) {
      setUser({ username, role, token });
    }
  }, []);

  const navigate = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleLogin = (userData) => {
    setUser(userData);
    setCurrentPage('admin');
  };

  const handleLogout = () => {
    localStorage.removeItem('admin_token');
    localStorage.removeItem('user_role');
    localStorage.removeItem('username');
    setUser(null);
    setCurrentPage('home');
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'home':     return <Home navigate={navigate} />;
      case 'about':    return <About />;
      case 'services': return <Services navigate={navigate} />;
      case 'work':     return <Work />;
      case 'contact':  return <Contact />;
      case 'login':    return <Login onLogin={handleLogin} />;
      case 'admin':    return user ? <Admin /> : <Login onLogin={handleLogin} />;
      default:         return <Home navigate={navigate} />;
    }
  };

  return (
    <div className="app">
      <Navbar
        currentPage={currentPage}
        navigate={navigate}
        user={user}
        onLogout={handleLogout}
      />
      <main className="main">{renderPage()}</main>
      <Footer navigate={navigate} />
    </div>
  );
}

export default App;
