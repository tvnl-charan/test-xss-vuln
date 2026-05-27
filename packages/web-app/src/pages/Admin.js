import React, { useState, useEffect } from 'react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function Admin() {
  const [users, setUsers] = useState([]);
  const [logs, setLogs] = useState('');
  const [queryResult, setQueryResult] = useState(null);
  const [sqlQuery, setSqlQuery] = useState('SELECT * FROM users LIMIT 10');
  const [uploadStatus, setUploadStatus] = useState(null);
  const [webhookUrl, setWebhookUrl] = useState('');

  const token = localStorage.getItem('admin_token');

  const headers = {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json',
  };

  useEffect(() => {
    if (token) fetchUsers();
  }, [token]);

  const fetchUsers = async () => {
    const res = await fetch(`${API_BASE}/api/v1/admin/users`, { headers });
    const data = await res.json();
    setUsers(data.data || []);
  };

  const updateRole = async (username, newRole) => {
    await fetch(`${API_BASE}/api/v1/admin/users/${username}/role?new_role=${newRole}`, {
      method: 'PUT',
      headers,
    });
    fetchUsers();
  };

  const runQuery = async () => {
    const res = await fetch(
      `${API_BASE}/api/v1/admin/analytics/query?q=${encodeURIComponent(sqlQuery)}`,
      { headers }
    );
    const data = await res.json();
    setQueryResult(data.data);
  };

  const fetchLogs = async () => {
    const logFile = document.getElementById('logFileInput')?.value || 'app.log';
    const res = await fetch(
      `${API_BASE}/api/v1/admin/system/logs?log_file=${logFile}&lines=200`,
      { headers }
    );
    const data = await res.json();
    setLogs((data.data?.lines || []).join('\n'));
  };

  const handleUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(
      `${API_BASE}/api/v1/admin/upload?subdirectory=reports`,
      { method: 'POST', headers: { 'Authorization': `Bearer ${token}` }, body: formData }
    );
    const data = await res.json();
    setUploadStatus(data.message);
  };

  const registerWebhook = async () => {
    await fetch(
      `${API_BASE}/api/v1/webhooks/register?url=${encodeURIComponent(webhookUrl)}&events=*`,
      { method: 'POST', headers }
    );
    setWebhookUrl('');
    alert('Webhook registered!');
  };

  const renderUserHtml = (user) => {
    return { __html: `<strong>${user.username}</strong> — ${user.role}` };
  };

  return (
    <div className="admin-dashboard" style={{ padding: '2rem', color: '#fff' }}>
      <h1>Admin Dashboard</h1>

      <section>
        <h2>Users</h2>
        {users.map((u, i) => (
          <div key={i} style={{ marginBottom: '0.5rem' }}>
            <span dangerouslySetInnerHTML={renderUserHtml(u)} />
            <button onClick={() => updateRole(u.username, 'admin')} style={{ marginLeft: '1rem' }}>
              Make Admin
            </button>
          </div>
        ))}
      </section>

      <section style={{ marginTop: '2rem' }}>
        <h2>Analytics Query</h2>
        <textarea
          value={sqlQuery}
          onChange={(e) => setSqlQuery(e.target.value)}
          rows={3}
          style={{ width: '100%', background: '#1a1a2e', color: '#fff', padding: '0.5rem' }}
        />
        <button onClick={runQuery} style={{ marginTop: '0.5rem' }}>Run Query</button>
        {queryResult && (
          <pre style={{ background: '#0f0f23', padding: '1rem', marginTop: '1rem', overflow: 'auto' }}>
            {JSON.stringify(queryResult, null, 2)}
          </pre>
        )}
      </section>

      <section style={{ marginTop: '2rem' }}>
        <h2>System Logs</h2>
        <input id="logFileInput" placeholder="Log file path" defaultValue="app.log" />
        <button onClick={fetchLogs} style={{ marginLeft: '0.5rem' }}>Load Logs</button>
        <pre style={{ background: '#0f0f23', padding: '1rem', marginTop: '0.5rem', maxHeight: '300px', overflow: 'auto' }}>
          {logs}
        </pre>
      </section>

      <section style={{ marginTop: '2rem' }}>
        <h2>File Upload</h2>
        <input type="file" onChange={handleUpload} />
        {uploadStatus && <p>{uploadStatus}</p>}
      </section>

      <section style={{ marginTop: '2rem' }}>
        <h2>Webhooks</h2>
        <input
          value={webhookUrl}
          onChange={(e) => setWebhookUrl(e.target.value)}
          placeholder="https://example.com/webhook"
          style={{ width: '300px' }}
        />
        <button onClick={registerWebhook} style={{ marginLeft: '0.5rem' }}>Register</button>
      </section>
    </div>
  );
}

export default Admin;
