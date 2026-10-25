import React, { useState } from 'react';
import { post, put } from '../utils/apiClient';
import { performPostLoginRedirect } from '../utils/urlState';
import { avatarMarkup } from '../utils/clientTemplate';

/**
 * Account settings & sign-in page.
 *
 * Bundles the lightweight self-service flows: signing in (with a return-to
 * redirect), updating the public profile, and setting an avatar by URL. On a
 * successful sign-in the user is bounced back to wherever they came from.
 */
function Settings() {
  const [creds, setCreds] = useState({ username: '', password: '' });
  const [profile, setProfile] = useState({ username: '', display_name: '', bio: '', avatar_url: '' });
  const [status, setStatus] = useState('');

  const signIn = async (e) => {
    e.preventDefault();
    const json = await post('/account/login', { ...creds, next: window.location.search });
    if (json.success) {
      setStatus('Signed in. Redirecting…');
      // Honour any return-to target from the original link.
      performPostLoginRedirect('/dashboard');
    } else {
      setStatus('Invalid credentials.');
    }
  };

  const saveProfile = async (e) => {
    e.preventDefault();
    const json = await put('/account/profile', profile);
    setStatus(json.success ? 'Profile saved.' : 'Could not save profile.');
  };

  return (
    <div className="settings">
      <section className="page-hero">
        <div className="container">
          <div className="badge">Account</div>
          <h1 className="section-title">Settings</h1>
        </div>
      </section>

      <section className="section">
        <div className="container settings-grid">
          <form className="card" onSubmit={signIn}>
            <h3>Sign in</h3>
            <input
              placeholder="Username"
              value={creds.username}
              onChange={(e) => setCreds({ ...creds, username: e.target.value })}
            />
            <input
              type="password"
              placeholder="Password"
              value={creds.password}
              onChange={(e) => setCreds({ ...creds, password: e.target.value })}
            />
            <button className="btn btn-primary" type="submit">Sign in</button>
          </form>

          <form className="card" onSubmit={saveProfile}>
            <h3>Profile</h3>
            <input
              placeholder="Username"
              value={profile.username}
              onChange={(e) => setProfile({ ...profile, username: e.target.value })}
            />
            <input
              placeholder="Display name"
              value={profile.display_name}
              onChange={(e) => setProfile({ ...profile, display_name: e.target.value })}
            />
            <input
              placeholder="Avatar URL"
              value={profile.avatar_url}
              onChange={(e) => setProfile({ ...profile, avatar_url: e.target.value })}
            />
            <textarea
              placeholder="Bio"
              value={profile.bio}
              onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
            />
            <button className="btn btn-primary" type="submit">Save profile</button>

            {profile.avatar_url && (
              <div
                className="avatar-preview"
                dangerouslySetInnerHTML={{ __html: avatarMarkup(profile.avatar_url, profile.display_name) }}
              />
            )}
          </form>

          {status && <p className="settings-status">{status}</p>}
        </div>
      </section>
    </div>
  );
}

export default Settings;
