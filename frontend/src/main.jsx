import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App.jsx';

if (window.location.hostname === '127.0.0.1') {
  const { port, pathname, search, hash } = window.location;
  window.location.replace(`http://localhost:${port}${pathname}${search}${hash}`);
} else {
  createRoot(document.getElementById('root')).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}
