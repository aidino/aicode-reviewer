/**
 * Entry point for AI Code Reviewer React frontend application.
 * 
 * This file initializes and renders the React application into the DOM.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Get the root element
const container = document.getElementById('root');

if (!container) {
  throw new Error('Root element not found. Make sure you have a div with id="root" in your HTML.');
}

// Create the root and render the app
const root = ReactDOM.createRoot(container);

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
); 