# AI Code Reviewer Frontend

Modern React frontend for the AI Code Reviewer multi-agent code analysis platform.

## Features

- **Scan Management**: Browse and manage code analysis scans
- **Report Viewing**: Detailed scan reports with static analysis findings
- **LLM Insights**: AI-powered code analysis and recommendations
- **Diagram Visualization**: Interactive PlantUML and Mermaid diagrams
- **Responsive Design**: Modern, clean UI with mobile support
- **Real-time Updates**: Live scan status and progress tracking

## Tech Stack

- **React 18** with TypeScript
- **React Router** for client-side routing
- **Vite** for fast development and building
- **Mermaid** for diagram rendering
- **Modern CSS** with responsive design

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend API server running on port 8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Environment Variables

Create a `.env` file in the frontend directory:

```bash
# Backend API URL (optional, defaults to http://localhost:8000)
REACT_APP_API_BASE_URL=http://localhost:8000
```

## Project Structure

```
src/
├── components/          # Reusable React components
│   └── DiagramDisplay.tsx   # Diagram rendering component
├── pages/              # Page components
│   ├── ScanList.tsx       # Scans listing page
│   └── ReportView.tsx     # Report details page
├── services/           # API services
│   └── api.ts             # Backend API client
├── hooks/              # Custom React hooks
│   └── useApi.ts          # API state management hooks
├── types/              # TypeScript type definitions
│   └── index.ts           # All type definitions
├── App.tsx             # Main app component with routing
└── index.tsx           # Application entry point
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript type checking

## API Integration

The frontend integrates with the FastAPI backend through:

- **RESTful APIs**: Standard REST endpoints for CRUD operations
- **Type Safety**: TypeScript interfaces matching backend Pydantic models
- **Error Handling**: Comprehensive error handling and user feedback
- **Loading States**: Progressive loading and skeleton screens

### Key API Endpoints

- `GET /api/scans` - List all scans
- `GET /api/scans/{scan_id}/report` - Get detailed scan report
- `POST /api/scans` - Create new scan
- `DELETE /api/scans/{scan_id}` - Delete scan

## Components

### ScanList
- Displays paginated list of scans
- Filtering and sorting capabilities
- Navigation to individual reports
- Scan management actions

### ReportView
- Comprehensive scan report display
- Tabbed interface for different sections
- Static analysis findings with filtering
- LLM insights and recommendations
- Interactive diagram rendering

### DiagramDisplay
- Supports PlantUML and Mermaid formats
- Auto-detection of diagram types
- Error handling and fallbacks
- Responsive rendering

## Development

### Code Style

- TypeScript strict mode enabled
- ESLint with React and TypeScript rules
- Consistent naming conventions
- Comprehensive JSDoc documentation

### Testing

```bash
# Run tests (when test framework is set up)
npm test

# Run tests with coverage
npm run test:coverage
```

### Build Optimization

- Code splitting by route and vendor
- Tree shaking for minimal bundle size
- Source maps for debugging
- Optimized asset loading

## Deployment

The frontend is a static SPA that can be deployed to:

- Static hosting services (Netlify, Vercel, GitHub Pages)
- CDN with proper routing configuration
- Docker containers with nginx
- Traditional web servers

### Build for Production

```bash
npm run build
```

The `dist/` directory contains the production-ready files.

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Contributing

1. Follow the existing code style and patterns
2. Add TypeScript types for all new interfaces
3. Include comprehensive JSDoc documentation
4. Test components thoroughly
5. Ensure responsive design compliance

## Architecture Notes

- **State Management**: React hooks with custom API hooks
- **Routing**: React Router with nested layouts
- **API Layer**: Centralized service with error handling
- **Component Design**: Functional components with hooks
- **Type Safety**: Full TypeScript coverage 