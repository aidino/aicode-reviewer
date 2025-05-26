/**
 * DiagramDisplay component for rendering PlantUML and Mermaid diagrams with interactive features.
 * 
 * This component accepts diagram content and renders it using appropriate
 * libraries based on the diagram format. It includes zoom, pan, and other
 * interactive features for better diagram exploration.
 */

import React, { useEffect, useRef, useState } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { DiagramData } from '../types';

interface DiagramDisplayProps {
  diagram: DiagramData;
  className?: string;
  style?: React.CSSProperties;
  enableInteraction?: boolean;
  showControls?: boolean;
}

interface DiagramDisplayState {
  loading: boolean;
  error: string | null;
  rendered: boolean;
}

/**
 * Component to display diagrams from PlantUML or Mermaid content with interactive features.
 * 
 * Args:
 *   diagram: Diagram data containing content and format information
 *   className: Additional CSS classes
 *   style: Inline styles
 *   enableInteraction: Whether to enable zoom/pan interactions (default: true)
 *   showControls: Whether to show zoom controls (default: true)
 * 
 * Returns:
 *   JSX.Element: Rendered diagram component with interactive features
 */
const DiagramDisplay: React.FC<DiagramDisplayProps> = ({
  diagram,
  className = '',
  style = {},
  enableInteraction = true,
  showControls = true,
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
        sequence: {
          useMaxWidth: true,
          actorMargin: 50,
          boxMargin: 10,
          boxTextMargin: 5,
        },
        class: {
          useMaxWidth: true,
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
        element.style.width = '100%';
        element.style.height = 'auto';
        containerRef.current.appendChild(element);

        // Render the diagram
        const { svg } = await mermaid.default.render(id, content);
        element.innerHTML = svg;
        
        // Add click handlers for interactive elements if needed
        if (enableInteraction) {
          addDiagramInteractivity(element);
        }
        
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
        img.style.display = 'block';
        img.style.margin = '0 auto';
        
        img.onload = () => {
          // Add interactive features if enabled
          if (enableInteraction) {
            addDiagramInteractivity(containerRef.current!);
          }
          
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

  // Function to add interactivity to diagram elements
  const addDiagramInteractivity = (element: HTMLElement) => {
    // Add hover effects to diagram elements
    const svgElements = element.querySelectorAll('g, rect, circle, path');
    svgElements.forEach((el) => {
      el.addEventListener('mouseenter', () => {
        (el as HTMLElement).style.opacity = '0.8';
        (el as HTMLElement).style.cursor = 'pointer';
      });
      
      el.addEventListener('mouseleave', () => {
        (el as HTMLElement).style.opacity = '1';
      });
      
      // Add click handlers for potential future features
      el.addEventListener('click', (event) => {
        event.stopPropagation();
        console.log('Diagram element clicked:', el);
        // TODO: Add click-to-code navigation in future iterations
      });
    });
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
  }, [diagram, enableInteraction]);

  // Render controls for diagram interaction
  const renderControls = () => {
    if (!showControls || !state.rendered) return null;
    
    return (
      <div style={{
        position: 'absolute',
        top: '8px',
        right: '8px',
        display: 'flex',
        gap: '4px',
        zIndex: 10,
      }}>
        <button
          style={{
            padding: '4px 8px',
            fontSize: '12px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            backgroundColor: 'white',
            cursor: 'pointer',
          }}
          onClick={() => {
            // Will be handled by TransformWrapper
          }}
          title="Reset zoom"
        >
          Reset
        </button>
      </div>
    );
  };

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

  // Render diagram with or without interactive wrapper
  const diagramContent = (
    <div 
      className={`diagram-display diagram-rendered ${className}`}
      data-testid="diagram-display"
      style={{
        border: '1px solid #e0e0e0',
        borderRadius: '4px',
        padding: '16px',
        textAlign: 'center',
        position: 'relative',
        ...style,
      }}
    >
      {renderControls()}
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

  // Wrap with interactive features if enabled
  if (enableInteraction && state.rendered) {
    return (
      <TransformWrapper
        initialScale={1}
        minScale={0.1}
        maxScale={5}
        centerOnInit={true}
        limitToBounds={false}
        doubleClick={{
          disabled: false,
          mode: 'zoomIn',
          step: 0.7,
        }}
        wheel={{
          step: 0.1,
        }}
      >
        {({ zoomIn, zoomOut, resetTransform }) => (
          <>
            <div style={{ position: 'relative' }}>
              {showControls && (
                <div style={{
                  position: 'absolute',
                  top: '8px',
                  right: '8px',
                  display: 'flex',
                  gap: '4px',
                  zIndex: 10,
                }}>
                  <button
                    onClick={() => zoomIn()}
                    style={{
                      padding: '6px 10px',
                      fontSize: '14px',
                      border: '1px solid #ccc',
                      borderRadius: '4px',
                      backgroundColor: 'white',
                      cursor: 'pointer',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    }}
                    title="Zoom In"
                  >
                    +
                  </button>
                  <button
                    onClick={() => zoomOut()}
                    style={{
                      padding: '6px 12px',
                      fontSize: '14px',
                      border: '1px solid #ccc',
                      borderRadius: '4px',
                      backgroundColor: 'white',
                      cursor: 'pointer',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    }}
                    title="Zoom Out"
                  >
                    -
                  </button>
                  <button
                    onClick={() => resetTransform()}
                    style={{
                      padding: '6px 8px',
                      fontSize: '12px',
                      border: '1px solid #ccc',
                      borderRadius: '4px',
                      backgroundColor: 'white',
                      cursor: 'pointer',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                    }}
                    title="Reset Zoom"
                  >
                    Reset
                  </button>
                </div>
              )}
              <TransformComponent
                wrapperStyle={{
                  width: '100%',
                  height: '100%',
                }}
                contentStyle={{
                  width: '100%',
                  height: '100%',
                }}
              >
                {diagramContent}
              </TransformComponent>
            </div>
          </>
        )}
      </TransformWrapper>
    );
  }

  // Return non-interactive diagram
  return diagramContent;
};

export default DiagramDisplay; 