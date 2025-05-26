/**
 * MSW server setup for testing environment.
 * 
 * This file configures Mock Service Worker for use in Node.js testing environment.
 */

import { setupServer } from 'msw/node';
import { handlers } from './handlers';

// Setup MSW server with handlers
export const server = setupServer(...handlers); 