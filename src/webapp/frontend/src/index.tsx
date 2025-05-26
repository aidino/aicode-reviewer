/**
 * Entry point for AI Code Reviewer React frontend application.
 * 
 * This file initializes and renders the React application into the DOM.
 */

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
// import SimpleApp from './App.simple'; // For debugging

// Get the root element
const container = document.getElementById('root');

console.log('Container found:', container);

if (!container) {
  console.error('Root element not found!');
  throw new Error('Root element not found. Make sure you have a div with id="root" in your HTML.');
}

// Create the root and render the app
const root = ReactDOM.createRoot(container);

console.log('About to render App...');

root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

console.log('App rendered!'); 