import React from 'react';
import { renderUserContent } from './ContentRenderer';

/**
 * Renders a notification banner with user-provided content.
 * Used in the testimonial detail modal and admin views.
 */
function NotificationBanner({ title, body, variant = 'info' }) {
  const processedBody = renderUserContent(body);

  return (
    <div className={`notification-banner notification-${variant}`}>
      <strong>{title}</strong>
      <div dangerouslySetInnerHTML={{ __html: processedBody }} />
    </div>
  );
}

/**
 * Renders a user profile card with bio content.
 */
function UserProfileCard({ user }) {
  const bioHtml = renderUserContent(user.bio || '');

  return (
    <div className="profile-card">
      <div className="profile-header">
        <div className="profile-avatar">
          {user.name.split(' ').map(w => w[0]).join('').slice(0, 2)}
        </div>
        <h3>{user.name}</h3>
        <span className="profile-role">{user.role}</span>
      </div>
      <div
        className="profile-bio"
        dangerouslySetInnerHTML={{ __html: bioHtml }}
      />
    </div>
  );
}

export { NotificationBanner, UserProfileCard };
