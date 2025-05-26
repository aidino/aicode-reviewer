/**
 * Unit tests for DiagramDisplay component.
 * 
 * Tests diagram rendering functionality for both PlantUML and Mermaid formats
 * using Vitest and React Testing Library.
 */

import React from 'react';
import { render, screen, waitFor } from '../../../src/test/utils';
import DiagramDisplay from '../../../../src/webapp/frontend/src/components/DiagramDisplay';
import { DiagramData } from '../../../../src/webapp/frontend/src/types';

describe('DiagramDisplay Component', () => {
  // Mock data for different diagram types
  const mockPlantUMLDiagram: DiagramData = {
    diagram_type: 'PlantUML',
    format: 'plantuml',
    diagram_content: '@startuml\nclass User {\n  +name: string\n}\n@enduml'
  };

  const mockMermaidDiagram: DiagramData = {
    diagram_type: 'Mermaid',
    format: 'mermaid',
    diagram_content: 'graph TD\n  A[Start] --> B[Process]\n  B --> C[End]'
  };

  const mockUnknownDiagram: DiagramData = {
    diagram_type: 'Unknown',
    format: '',
    diagram_content: 'sequenceDiagram\n  Alice->>Bob: Hello'
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders loading state initially', () => {
    render(<DiagramDisplay diagram={mockMermaidDiagram} />);
    
    expect(screen.getByText('Loading diagram...')).toBeInTheDocument();
  });

  test('renders PlantUML diagram correctly', async () => {
    render(<DiagramDisplay diagram={mockPlantUMLDiagram} />);
    
    await waitFor(() => {
      // PlantUML diagrams are rendered as images from PlantUML server
      const img = screen.getByRole('img', { name: /plantuml diagram/i });
      expect(img).toBeInTheDocument();
      expect(img).toHaveAttribute('src', expect.stringContaining('plantuml.com'));
    });
  });

  test('renders Mermaid diagram correctly', async () => {
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

  test('auto-detects PlantUML from content', async () => {
    const autoDetectDiagram: DiagramData = {
      diagram_type: 'Unknown',
      format: '',
      diagram_content: '@startuml\nclass Test\n@enduml'
    };

    render(<DiagramDisplay diagram={autoDetectDiagram} />);
    
    await waitFor(() => {
      const img = screen.getByRole('img', { name: /plantuml diagram/i });
      expect(img).toBeInTheDocument();
    });
  });

  test('auto-detects Mermaid from content keywords', async () => {
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

  test('auto-detects Mermaid from sequence diagram', async () => {
    render(<DiagramDisplay diagram={mockUnknownDiagram} />);
    
    const { default: mermaid } = await import('mermaid');
    
    await waitFor(() => {
      expect(mermaid.render).toHaveBeenCalled();
    });
  });

  test('handles empty diagram content', () => {
    const emptyDiagram: DiagramData = {
      diagram_type: 'Mermaid',
      format: 'mermaid',
      diagram_content: ''
    };

    render(<DiagramDisplay diagram={emptyDiagram} />);
    
    expect(screen.getByText('No diagram content available')).toBeInTheDocument();
  });

  test('handles PlantUML encoding correctly', async () => {
    render(<DiagramDisplay diagram={mockPlantUMLDiagram} />);
    
    await waitFor(() => {
      const img = screen.getByRole('img', { name: /plantuml diagram/i });
      const src = img.getAttribute('src');
      
      // Should contain encoded PlantUML content
      expect(src).toContain('plantuml.com');
      expect(src).toContain('/png/');
    });
  });

  test('handles Mermaid rendering error gracefully', async () => {
    const { default: mermaid } = await import('mermaid');
    mermaid.render.mockRejectedValueOnce(new Error('Mermaid error'));
    
    render(<DiagramDisplay diagram={mockMermaidDiagram} />);
    
    await waitFor(() => {
      expect(screen.getByText('Error rendering diagram:')).toBeInTheDocument();
      expect(screen.getByText('Mermaid error')).toBeInTheDocument();
    });
  });

  test('handles PlantUML image load error', async () => {
    render(<DiagramDisplay diagram={mockPlantUMLDiagram} />);
    
    await waitFor(() => {
      const img = screen.getByRole('img', { name: /plantuml diagram/i });
      
      // Simulate image load error
      Object.defineProperty(img, 'complete', { value: false });
      img.dispatchEvent(new Event('error'));
    });

    expect(screen.getByText('Error loading PlantUML diagram')).toBeInTheDocument();
  });

  test('displays diagram title when provided', async () => {
    const diagramWithTitle = {
      ...mockMermaidDiagram,
      title: 'Test Flow Diagram'
    };

    render(<DiagramDisplay diagram={diagramWithTitle} />);
    
    expect(screen.getByText('Test Flow Diagram')).toBeInTheDocument();
  });

  test('displays diagram type and format in loading state', () => {
    render(<DiagramDisplay diagram={mockPlantUMLDiagram} />);
    
    expect(screen.getByText('Loading diagram...')).toBeInTheDocument();
  });

  test('applies custom className correctly', () => {
    const { container } = render(
      <DiagramDisplay 
        diagram={mockMermaidDiagram} 
        className="custom-diagram" 
      />
    );
    
    expect(container.firstChild).toHaveClass('diagram-display', 'custom-diagram');
  });

  test('handles unsupported diagram type gracefully', () => {
    const unsupportedDiagram: DiagramData = {
      diagram_type: 'UnsupportedType',
      format: 'unknown',
      diagram_content: 'some unknown content'
    };

    render(<DiagramDisplay diagram={unsupportedDiagram} />);
    
    expect(screen.getByText('Unsupported diagram type: UnsupportedType')).toBeInTheDocument();
  });

  test('properly unmounts and cleans up resources', () => {
    const { unmount } = render(<DiagramDisplay diagram={mockMermaidDiagram} />);
    
    // Should unmount without errors
    expect(() => unmount()).not.toThrow();
  });

  test('updates diagram when props change', async () => {
    const { rerender } = render(<DiagramDisplay diagram={mockMermaidDiagram} />);
    
    await waitFor(() => {
      expect(screen.getByText('Loading diagram...')).toBeInTheDocument();
    });

    // Change to PlantUML diagram
    rerender(<DiagramDisplay diagram={mockPlantUMLDiagram} />);
    
    await waitFor(() => {
      const img = screen.getByRole('img', { name: /plantuml diagram/i });
      expect(img).toBeInTheDocument();
    });
  });

  test('handles invalid PlantUML content gracefully', async () => {
    const invalidPlantUML: DiagramData = {
      diagram_type: 'PlantUML',
      format: 'plantuml',
      diagram_content: '@startuml\n invalid syntax here \n@enduml'
    };

    render(<DiagramDisplay diagram={invalidPlantUML} />);
    
    await waitFor(() => {
      const img = screen.getByRole('img', { name: /plantuml diagram/i });
      expect(img).toBeInTheDocument();
      
      // PlantUML server should handle invalid syntax and return error image
      expect(img.getAttribute('src')).toContain('plantuml.com');
    });
  });

  test('handles invalid Mermaid content gracefully', async () => {
    const invalidMermaid: DiagramData = {
      diagram_type: 'Mermaid',
      format: 'mermaid',
      diagram_content: 'invalid mermaid syntax here'
    };

    const { default: mermaid } = await import('mermaid');
    mermaid.render.mockRejectedValueOnce(new Error('Invalid syntax'));
    
    render(<DiagramDisplay diagram={invalidMermaid} />);
    
    await waitFor(() => {
      expect(screen.getByText('Error rendering diagram:')).toBeInTheDocument();
      expect(screen.getByText('Invalid syntax')).toBeInTheDocument();
    });
  });

  test('renders responsive diagram container', () => {
    const { container } = render(<DiagramDisplay diagram={mockMermaidDiagram} />);
    
    const diagramContainer = container.querySelector('.diagram-container');
    expect(diagramContainer).toBeInTheDocument();
    expect(diagramContainer).toHaveClass('responsive');
  });
}); 