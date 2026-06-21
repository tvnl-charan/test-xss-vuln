import React, { useState, useEffect, useCallback } from 'react';
import { get, put, del } from '../utils/apiClient';
import { renderUserContent } from '../ContentRenderer';

/**
 * Admin user-management page.
 *
 * Lists users, lets an admin edit a user's role / display name / bio, and
 * delete users. The bio is rendered with the shared content renderer so admins
 * see it formatted exactly as it appears on the public profile card.
 */
function AdminUsers({ adminToken = '' }) {
  const [users, setUsers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [draft, setDraft] = useState({ role: '', display_name: '', bio: '' });
  const headers = adminToken ? { 'X-Admin-Token': adminToken } : {};

  const load = useCallback(() => {
    get('/admin/users').then((json) => {
      if (json.success) setUsers(json.data);
    });
  }, []);

  useEffect(() => { load(); }, [load]);

  const choose = (user) => {
    setSelected(user.username);
    setDraft({
      role: user.role || '',
      display_name: user.display_name || '',
      bio: user.bio || '',
    });
  };

  const save = async () => {
    if (!selected) return;
    const json = await put(`/admin/users/${selected}`, draft, headers);
    if (json.success) load();
  };

  const remove = async (username) => {
    await del(`/admin/users/${username}`, headers);
    load();
  };

  return (
    <div className="admin-users">
      <section className="page-hero">
        <div className="container">
          <div className="badge">Admin</div>
          <h1 className="section-title">User Management</h1>
        </div>
      </section>

      <section className="section">
        <div className="container admin-grid">
          <table className="admin-table">
            <thead>
              <tr><th>Username</th><th>Email</th><th>Role</th><th /></tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.username}>
                  <td>{u.username}</td>
                  <td>{u.email}</td>
                  <td>{u.role}</td>
                  <td>
                    <button className="btn btn-sm" onClick={() => choose(u)}>Edit</button>
                    <button className="btn btn-sm" onClick={() => remove(u.username)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {selected && (
            <div className="card admin-editor">
              <h3>Editing {selected}</h3>
              <label>Role
                <input
                  value={draft.role}
                  onChange={(e) => setDraft({ ...draft, role: e.target.value })}
                />
              </label>
              <label>Display name
                <input
                  value={draft.display_name}
                  onChange={(e) => setDraft({ ...draft, display_name: e.target.value })}
                />
              </label>
              <label>Bio
                <textarea
                  value={draft.bio}
                  onChange={(e) => setDraft({ ...draft, bio: e.target.value })}
                />
              </label>
              <button className="btn btn-primary" onClick={save}>Save</button>

              <div className="admin-bio-preview">
                <h4>Bio preview</h4>
                <div dangerouslySetInnerHTML={{ __html: renderUserContent(draft.bio) }} />
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}

export default AdminUsers;
