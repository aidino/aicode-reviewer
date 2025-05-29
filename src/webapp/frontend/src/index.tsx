/**
 * Entry point for AI Code Reviewer React frontend application.
 * 
 * This file initializes and renders the React application into the DOM.
 */

import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';
// import SimpleApp from './App.simple';
// import AppDebug from './App.debug';

console.log('🚀 AI Code Reviewer starting...');

const container = document.getElementById('root');

if (container) {
  const root = createRoot(container);
  root.render(<App />);
  console.log('✅ React app mounted successfully');
} else {
  console.error('❌ Root container not found');
}