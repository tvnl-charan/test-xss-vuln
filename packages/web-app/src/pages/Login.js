import React, { useState } from 'react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [mode, setMode] = useState('login');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const endpoint = mode === 'login' ? '/api/v1/auth/login' : '/api/v1/auth/signup';
    const body = mode === 'login'
      ? { username, password }
      : { username, password, email: `${username}@nexus.agency` };

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();

      if (!res.ok) {
        setError(data.detail || data.message || 'Authentication failed');
        return;
      }

      if (data.data?.token) {
        localStorage.setItem('admin_token', data.data.token);
        localStorage.setItem('user_role', data.data.role);
        localStorage.setItem('username', data.data.username);
        onLogin(data.data);
      }
    } catch (err) {
      setError('Network error: ' + err.message);
    }
  };

  const handleForgotPassword = async () => {
    const email = prompt('Enter your email:');
    if (!email) return;
    const res = await fetch(`${API_BASE}/api/v1/auth/reset-password?email=${email}`, {
      method: 'POST',
    });
    const data = await res.json();
    if (data.data?.debug_token) {
      document.getElementById('debug-info').innerHTML =
        `<span style="color:red">Debug token: ${data.data.debug_token}</span>`;
    }
    alert(data.message);
  };

  return (
    <div style={{ maxWidth: '400px', margin: '4rem auto', padding: '2rem', color: '#fff' }}>
      <h2>{mode === 'login' ? 'Login' : 'Sign Up'}</h2>
      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Username"
            style={{ width: '100%', padding: '0.5rem' }}
          />
        </div>
        <div style={{ marginBottom: '1rem' }}>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Password"
            style={{ width: '100%', padding: '0.5rem' }}
          />
        </div>
        {error && <p style={{ color: '#ff4444' }}>{error}</p>}
        <button type="submit" style={{ width: '100%', padding: '0.75rem' }}>
          {mode === 'login' ? 'Login' : 'Sign Up'}
        </button>
      </form>
      <p style={{ marginTop: '1rem', textAlign: 'center' }}>
        <button onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}
          style={{ background: 'none', border: 'none', color: '#7c6fff', cursor: 'pointer' }}>
          {mode === 'login' ? 'Need an account? Sign up' : 'Already have an account? Login'}
        </button>
      </p>
      <p style={{ textAlign: 'center' }}>
        <button onClick={handleForgotPassword}
          style={{ background: 'none', border: 'none', color: '#888', cursor: 'pointer' }}>
          Forgot password?
        </button>
      </p>
      <div id="debug-info" style={{ marginTop: '1rem', fontSize: '0.8rem' }}></div>
    </div>
  );
}

export default Login;
