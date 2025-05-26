/**
 * Unit tests for DiagramDisplay component.
 * 
 * Tests diagram rendering functionality for both PlantUML and Mermaid formats.
 */

import React from 'react';
import { render, screen, waitFor } from '../../../src/test/utils';
import DiagramDisplay from '../../../../src/webapp/frontend/src/components/DiagramDisplay';
import { DiagramData } from '../../../../src/webapp/frontend/src/types';

describe('DiagramDisplay Component', () => {
  const mockMermaidDiagram: DiagramData = {
    diagram_type: 'Class Diagram',
    format: 'mermaid',
    diagram_content: `
      classDiagram
        class User {
          +String name
          +String email
          +login()
        }
        class Admin {
          +String permissions
          +manage()
        }
        User <|-- Admin
    `
  };

  const mockPlantUMLDiagram: DiagramData = {
    diagram_type: 'Class Diagram',
    format: 'plantuml',
    diagram_content: `
      @startuml
      class User {
        +String name
        +String email
        +login()
      }
      class Admin {
        +String permissions
        +manage()
      }
      User <|-- Admin
      @enduml
    `
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders loading state initially', () => {
    render(<DiagramDisplay diagram={mockMermaidDiagram} />);
    
    expect(screen.getByText('Loading diagram...')).toBeInTheDocument();
  });

  test('renders error state for invalid diagram content', async () => {
    const invalidDiagram: DiagramData = {
      diagram_type: 'Invalid',
      format: 'invalid',
      diagram_content: ''
    };

    render(<DiagramDisplay diagram={invalidDiagram} />);
    
    await waitFor(() => {
      expect(screen.getByText('Error rendering diagram:')).toBeInTheDocument();
      expect(screen.getByText('No diagram content provided')).toBeInTheDocument();
    });
  });

  test('renders mermaid diagram correctly', async () => {
    const { default: mermaid } = await import('mermaid');
    
    render(<DiagramDisplay diagram={mockMermaidDiagram} />);
    
    await waitFor(() => {
      expect(mermaid.initialize).toHaveBeenCalledWith({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'strict',
        flowchart: {
          useMaxWidth: true,
          htmlLabels: true,
        },
      });
      expect(mermaid.render).toHaveBeenCalled();
    });
  });

  test('detects PlantUML format correctly', async () => {
    render(<DiagramDisplay diagram={mockPlantUMLDiagram} />);
    
    // Should attempt to render as PlantUML (will use image approach)
    await waitFor(() => {
      const container = screen.getByText('Class Diagram diagram').parentElement;
      expect(container).toBeInTheDocument();
    });
  });

  test('applies custom className and style', () => {
    const customProps = {
      className: 'custom-diagram',
      style: { backgroundColor: 'red' }
    };
    
    render(<DiagramDisplay diagram={mockMermaidDiagram} {...customProps} />);
    
    const container = document.querySelector('.custom-diagram');
    expect(container).toBeInTheDocument();
  });

  test('shows diagram type label', async () => {
    render(<DiagramDisplay diagram={mockMermaidDiagram} />);
    
    await waitFor(() => {
      expect(screen.getByText('Class Diagram diagram')).toBeInTheDocument();
    });
  });

  test('handles mermaid rendering error gracefully', async () => {
    const { default: mermaid } = await import('mermaid');
    mermaid.render.mockRejectedValueOnce(new Error('Mermaid error'));
    
    render(<DiagramDisplay diagram={mockMermaidDiagram} />);
    
    await waitFor(() => {
      expect(screen.getByText('Error rendering diagram:')).toBeInTheDocument();
      expect(screen.getByText('Mermaid error')).toBeInTheDocument();
    });
  });

  test('provides diagram content in error details', async () => {
    const invalidDiagram: DiagramData = {
      diagram_type: 'Test',
      format: 'test',
      diagram_content: 'invalid content'
    };

    render(<DiagramDisplay diagram={invalidDiagram} />);
    
    await waitFor(() => {
      const detailsElement = screen.getByText('Show diagram content');
      expect(detailsElement).toBeInTheDocument();
    });
  });

  test('auto-detects mermaid from content keywords', async () => {
    const autoDetectDiagram: DiagramData = {
      diagram_type: 'Unknown',
      format: '',
      diagram_content: 'graph TD\n  A --> B'
    };

    const { default: mermaid } = await import('mermaid');
    
    render(<DiagramDisplay diagram={autoDetectDiagram} />);
    
    await waitFor(() => {
      expect(mermaid.render).toHaveBeenCalled();
    });
  });
}); 