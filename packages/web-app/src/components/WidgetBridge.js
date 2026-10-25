import React, { useEffect, useRef, useState } from 'react';
import { renderTemplate } from '../utils/clientTemplate';

/**
 * Cross-frame widget bridge.
 *
 * Partners embed the Nexus testimonial widget in an <iframe> and drive it via
 * postMessage: the host page can push a themed banner, update the displayed
 * quote, or hand the widget a small render context. This component listens for
 * those messages and reflects them into the widget UI.
 */
function WidgetBridge() {
  const [banner, setBanner] = useState('');
  const [settings, setSettings] = useState({ theme: 'light' });
  const bannerRef = useRef(null);

  useEffect(() => {
    function handleMessage(event) {
      const msg = event.data || {};
      if (msg.type === 'nexus:banner') {
        // Render the partner-supplied banner template with the widget context.
        setBanner(renderTemplate(msg.template || '', settings));
      } else if (msg.type === 'nexus:settings') {
        // Merge partner settings into the widget configuration.
        applySettings(settings, msg.patch || {});
        setSettings({ ...settings });
      }
    }

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [settings]);

  useEffect(() => {
    if (bannerRef.current) {
      bannerRef.current.innerHTML = banner;
    }
  }, [banner]);

  return (
    <div className={`widget-bridge widget-${settings.theme}`}>
      <div className="widget-banner" ref={bannerRef} />
      <p className="widget-hint">Embedded Nexus testimonial widget.</p>
    </div>
  );
}

/**
 * Deep-merge a settings patch into the widget configuration.
 * Supports nested keys so partners can tweak `display.density` etc.
 */
function applySettings(target, patch) {
  for (const key of Object.keys(patch)) {
    const value = patch[key];
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      if (!target[key]) target[key] = {};
      applySettings(target[key], value);
    } else {
      target[key] = value;
    }
  }
  return target;
}

export default WidgetBridge;
