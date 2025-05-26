/**
 * DiagramDisplay component for rendering PlantUML and Mermaid diagrams.
 * 
 * This component accepts diagram content and renders it using appropriate
 * libraries based on the diagram format.
 */

import React, { useEffect, useRef, useState } from 'react';
import { DiagramData } from '../types';

interface DiagramDisplayProps {
  diagram: DiagramData;
  className?: string;
  style?: React.CSSProperties;
}

interface DiagramDisplayState {
  loading: boolean;
  error: string | null;
  rendered: boolean;
}

/**
 * Component to display diagrams from PlantUML or Mermaid content.
 * 
 * Args:
 *   diagram: Diagram data containing content and format information
 *   className: Additional CSS classes
 *   style: Inline styles
 * 
 * Returns:
 *   JSX.Element: Rendered diagram component
 */
const DiagramDisplay: React.FC<DiagramDisplayProps> = ({
  diagram,
  className = '',
  style = {},
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [state, setState] = useState<DiagramDisplayState>({
    loading: true,
    error: null,
    rendered: false,
  });

  // Function to render Mermaid diagrams
  const renderMermaid = async (content: string) => {
    try {
      // Dynamically import mermaid to avoid SSR issues
      const mermaid = await import('mermaid');
      
      // Initialize mermaid with configuration
      mermaid.default.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'strict',
        flowchart: {
          useMaxWidth: true,
          htmlLabels: true,
        },
      });

      if (containerRef.current) {
        // Clear previous content
        containerRef.current.innerHTML = '';
        
        // Generate unique ID for this diagram
        const id = `mermaid-diagram-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Create element for mermaid to render into
        const element = document.createElement('div');
        element.id = id;
        containerRef.current.appendChild(element);

        // Render the diagram
        const { svg } = await mermaid.default.render(id, content);
        element.innerHTML = svg;
        
        setState({
          loading: false,
          error: null,
          rendered: true,
        });
      }
    } catch (error) {
      console.error('Error rendering Mermaid diagram:', error);
      setState({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to render Mermaid diagram',
        rendered: false,
      });
    }
  };

  // Function to render PlantUML diagrams using PlantUML server
  const renderPlantUML = async (content: string) => {
    try {
      // Encode the PlantUML content for the server
      const encoded = await encodePlantUML(content);
      
      // Use PlantUML server to generate SVG
      const plantUMLServer = 'https://www.plantuml.com/plantuml/svg/';
      const imageUrl = `${plantUMLServer}${encoded}`;
      
      if (containerRef.current) {
        // Clear previous content
        containerRef.current.innerHTML = '';
        
        // Create image element
        const img = document.createElement('img');
        img.src = imageUrl;
        img.alt = 'PlantUML Diagram';
        img.style.maxWidth = '100%';
        img.style.height = 'auto';
        
        img.onload = () => {
          setState({
            loading: false,
            error: null,
            rendered: true,
          });
        };
        
        img.onerror = () => {
          setState({
            loading: false,
            error: 'Failed to load PlantUML diagram from server',
            rendered: false,
          });
        };
        
        containerRef.current.appendChild(img);
      }
    } catch (error) {
      console.error('Error rendering PlantUML diagram:', error);
      setState({
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to render PlantUML diagram',
        rendered: false,
      });
    }
  };

  // Function to encode PlantUML content for the server
  const encodePlantUML = async (content: string): Promise<string> => {
    // Simple base64 encoding for PlantUML server
    // In a real implementation, you might want to use the official PlantUML encoding
    try {
      const encoded = btoa(unescape(encodeURIComponent(content)));
      return encoded;
    } catch (error) {
      throw new Error('Failed to encode PlantUML content');
    }
  };

  // Effect to render diagram when content changes
  useEffect(() => {
    if (!diagram || !diagram.diagram_content) {
      setState({
        loading: false,
        error: 'No diagram content provided',
        rendered: false,
      });
      return;
    }

    setState({
      loading: true,
      error: null,
      rendered: false,
    });

    // Determine diagram type and render accordingly
    const format = diagram.format?.toLowerCase() || '';
    const diagramType = diagram.diagram_type?.toLowerCase() || '';
    
    // Check if it's a Mermaid diagram
    if (format.includes('mermaid') || diagramType.includes('mermaid') || 
        diagram.diagram_content.includes('graph') || 
        diagram.diagram_content.includes('flowchart') ||
        diagram.diagram_content.includes('classDiagram') ||
        diagram.diagram_content.includes('sequenceDiagram')) {
      renderMermaid(diagram.diagram_content);
    }
    // Check if it's a PlantUML diagram
    else if (format.includes('plantuml') || diagramType.includes('plantuml') || 
             diagram.diagram_content.includes('@startuml') || 
             diagram.diagram_content.includes('@startclass')) {
      renderPlantUML(diagram.diagram_content);
    }
    // Default to PlantUML for class diagrams
    else if (diagramType.includes('class')) {
      renderPlantUML(diagram.diagram_content);
    }
    // Default to Mermaid for sequence diagrams
    else if (diagramType.includes('sequence')) {
      renderMermaid(diagram.diagram_content);
    }
    // Fallback: try to detect from content
    else {
      renderMermaid(diagram.diagram_content);
    }
  }, [diagram]);

  // Render loading state
  if (state.loading) {
    return (
      <div 
        className={`diagram-display diagram-loading ${className}`}
        style={{
          padding: '20px',
          textAlign: 'center',
          border: '1px solid #e0e0e0',
          borderRadius: '4px',
          ...style,
        }}
      >
        <div>Loading diagram...</div>
      </div>
    );
  }

  // Render error state
  if (state.error) {
    return (
      <div 
        className={`diagram-display diagram-error ${className}`}
        style={{
          padding: '20px',
          textAlign: 'center',
          border: '1px solid #f44336',
          borderRadius: '4px',
          backgroundColor: '#ffebee',
          color: '#c62828',
          ...style,
        }}
      >
        <div>Error rendering diagram:</div>
        <div style={{ fontSize: '0.9em', marginTop: '8px' }}>{state.error}</div>
        <details style={{ marginTop: '12px', textAlign: 'left' }}>
          <summary style={{ cursor: 'pointer' }}>Show diagram content</summary>
          <pre style={{ 
            fontSize: '0.8em', 
            backgroundColor: '#f5f5f5', 
            padding: '8px', 
            borderRadius: '4px',
            marginTop: '8px',
            overflow: 'auto' 
          }}>
            {diagram.diagram_content}
          </pre>
        </details>
      </div>
    );
  }

  // Render diagram
  return (
    <div 
      className={`diagram-display diagram-rendered ${className}`}
      data-testid="diagram-display"
      style={{
        border: '1px solid #e0e0e0',
        borderRadius: '4px',
        padding: '16px',
        textAlign: 'center',
        ...style,
      }}
    >
      <div 
        ref={containerRef}
        data-testid="diagram-container"
        style={{
          minHeight: '200px',
          width: '100%',
        }}
      />
      {diagram.diagram_type && (
        <div style={{
          fontSize: '0.9em',
          color: '#666',
          marginTop: '8px',
          fontStyle: 'italic',
        }}>
          {diagram.diagram_type} diagram
        </div>
      )}
    </div>
  );
};

export default DiagramDisplay; 