/**
 * SequenceDiagramViewer component for displaying sequence diagrams with enhanced features.
 * 
 * This component provides specialized functionality for sequence diagrams including
 * timeline navigation, actor highlighting, and interaction flow analysis.
 */

import React, { useState, useEffect, useRef } from 'react';
import { TransformWrapper, TransformComponent } from 'react-zoom-pan-pinch';
import { DiagramData } from '../types';

interface SequenceDiagramViewerProps {
  diagram: DiagramData;
  className?: string;
  onActorClick?: (actor: string) => void;
  onInteractionClick?: (interaction: string) => void;
  showTimeline?: boolean;
  showActorHighlights?: boolean;
}

interface SequenceTimelineItem {
  index: number;
  description: string;
  actors: string[];
  timestamp?: string;
}

/**
 * Specialized component for viewing sequence diagrams with interactive features.
 * 
 * Args:
 *   diagram: Sequence diagram data
 *   className: Additional CSS classes
 *   onActorClick: Callback when an actor is clicked
 *   onInteractionClick: Callback when an interaction is clicked
 *   showTimeline: Whether to show interaction timeline (default: true)
 *   showActorHighlights: Whether to highlight actors on hover (default: true)
 * 
 * Returns:
 *   JSX.Element: Rendered sequence diagram viewer with interactive features
 */
const SequenceDiagramViewer: React.FC<SequenceDiagramViewerProps> = ({
  diagram,
  className = '',
  onActorClick,
  onInteractionClick,
  showTimeline = true,
  showActorHighlights = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actors, setActors] = useState<string[]>([]);
  const [timeline, setTimeline] = useState<SequenceTimelineItem[]>([]);
  const [highlightedActor, setHighlightedActor] = useState<string | null>(null);
  const [selectedInteraction, setSelectedInteraction] = useState<number | null>(null);

  // Extract actors and timeline from diagram content
  const parseSequenceDiagram = (content: string) => {
    const actorSet = new Set<string>();
    const timelineItems: SequenceTimelineItem[] = [];
    
    const lines = content.split('\n');
    let interactionIndex = 0;
    
    lines.forEach((line, index) => {
      const trimmed = line.trim();
      
      // Extract actors from participant declarations
      if (trimmed.startsWith('participant ') || trimmed.startsWith('actor ')) {
        const actor = trimmed.split(' ')[1]?.replace(/[:"]/g, '');
        if (actor) actorSet.add(actor);
      }
      
      // Extract interactions (arrows between actors)
      if (trimmed.includes('->') || trimmed.includes('-->') || trimmed.includes('->>')) {
        const parts = trimmed.split(/->|-->|->>/).map(p => p.trim());
        if (parts.length >= 2) {
          const fromActor = parts[0];
          const toActor = parts[1].split(':')[0].trim();
          const message = parts[1].split(':')[1]?.trim() || 'Interaction';
          
          actorSet.add(fromActor);
          actorSet.add(toActor);
          
          timelineItems.push({
            index: interactionIndex++,
            description: `${fromActor} → ${toActor}: ${message}`,
            actors: [fromActor, toActor],
          });
        }
      }
    });
    
    setActors(Array.from(actorSet));
    setTimeline(timelineItems);
  };

  // Render sequence diagram using Mermaid
  const renderSequenceDiagram = async (content: string) => {
    try {
      // Parse diagram content first
      parseSequenceDiagram(content);
      
      // Dynamically import mermaid
      const mermaid = await import('mermaid');
      
      // Initialize mermaid with sequence-specific configuration
      mermaid.default.initialize({
        startOnLoad: false,
        theme: 'default',
        securityLevel: 'strict',
        sequence: {
          diagramMarginX: 50,
          diagramMarginY: 10,
          actorMargin: 50,
          width: 150,
          height: 65,
          boxMargin: 10,
          boxTextMargin: 5,
          noteMargin: 10,
          messageMargin: 35,
          mirrorActors: true,
          bottomMarginAdj: 1,
          useMaxWidth: true,
          rightAngles: false,
          showSequenceNumbers: true,
        },
      });

      if (containerRef.current) {
        // Clear previous content
        containerRef.current.innerHTML = '';
        
        // Generate unique ID
        const id = `sequence-diagram-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        // Create container element
        const element = document.createElement('div');
        element.id = id;
        element.style.width = '100%';
        element.style.height = 'auto';
        containerRef.current.appendChild(element);

        // Render the diagram
        const { svg } = await mermaid.default.render(id, content);
        element.innerHTML = svg;
        
        // Add interactive features
        if (showActorHighlights) {
          addSequenceInteractivity(element);
        }
        
        setLoading(false);
        setError(null);
      }
    } catch (error) {
      console.error('Error rendering sequence diagram:', error);
      setError(error instanceof Error ? error.message : 'Failed to render sequence diagram');
      setLoading(false);
    }
  };

  // Add interactivity to sequence diagram elements
  const addSequenceInteractivity = (element: HTMLElement) => {
    // Add hover effects to actors
    const actorElements = element.querySelectorAll('g.actor, rect.actor');
    actorElements.forEach((actorEl, index) => {
      actorEl.addEventListener('mouseenter', () => {
        (actorEl as HTMLElement).style.opacity = '0.8';
        (actorEl as HTMLElement).style.cursor = 'pointer';
        
        // Highlight related interactions
        if (actors[index]) {
          setHighlightedActor(actors[index]);
        }
      });
      
      actorEl.addEventListener('mouseleave', () => {
        (actorEl as HTMLElement).style.opacity = '1';
        setHighlightedActor(null);
      });
      
      actorEl.addEventListener('click', (event) => {
        event.stopPropagation();
        if (actors[index] && onActorClick) {
          onActorClick(actors[index]);
        }
      });
    });

    // Add hover effects to message lines
    const messageElements = element.querySelectorAll('g.messageText, line.messageLine0, line.messageLine1');
    messageElements.forEach((msgEl, index) => {
      msgEl.addEventListener('mouseenter', () => {
        (msgEl as HTMLElement).style.opacity = '0.8';
        (msgEl as HTMLElement).style.cursor = 'pointer';
      });
      
      msgEl.addEventListener('mouseleave', () => {
        (msgEl as HTMLElement).style.opacity = '1';
      });
      
      msgEl.addEventListener('click', (event) => {
        event.stopPropagation();
        setSelectedInteraction(index);
        if (timeline[index] && onInteractionClick) {
          onInteractionClick(timeline[index].description);
        }
      });
    });
  };

  // Initialize diagram rendering
  useEffect(() => {
    if (!diagram || !diagram.diagram_content) {
      setError('No sequence diagram content provided');
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);
    
    // Ensure it's a sequence diagram
    const content = diagram.diagram_content;
    if (content.includes('sequenceDiagram') || diagram.diagram_type?.toLowerCase().includes('sequence')) {
      renderSequenceDiagram(content);
    } else {
      setError('This component is designed for sequence diagrams only');
      setLoading(false);
    }
  }, [diagram]);

  // Render actor list
  const renderActorList = () => {
    if (!showActorHighlights || actors.length === 0) return null;
    
    return (
      <div style={{
        marginBottom: '16px',
        padding: '12px',
        backgroundColor: '#f8f9fa',
        borderRadius: '4px',
        border: '1px solid #e9ecef',
      }}>
        <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#495057' }}>
          Actors ({actors.length})
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {actors.map((actor, index) => (
            <span
              key={index}
              onClick={() => onActorClick && onActorClick(actor)}
              style={{
                padding: '4px 8px',
                backgroundColor: highlightedActor === actor ? '#007bff' : '#ffffff',
                color: highlightedActor === actor ? 'white' : '#495057',
                border: '1px solid #dee2e6',
                borderRadius: '12px',
                fontSize: '12px',
                cursor: onActorClick ? 'pointer' : 'default',
                transition: 'all 0.2s ease',
              }}
            >
              {actor}
            </span>
          ))}
        </div>
      </div>
    );
  };

  // Render interaction timeline
  const renderTimeline = () => {
    if (!showTimeline || timeline.length === 0) return null;
    
    return (
      <div style={{
        marginTop: '16px',
        padding: '12px',
        backgroundColor: '#f8f9fa',
        borderRadius: '4px',
        border: '1px solid #e9ecef',
        maxHeight: '200px',
        overflowY: 'auto',
      }}>
        <h4 style={{ margin: '0 0 8px 0', fontSize: '14px', color: '#495057' }}>
          Interaction Timeline ({timeline.length} interactions)
        </h4>
        <div style={{ fontSize: '12px' }}>
          {timeline.map((item, index) => (
            <div
              key={index}
              onClick={() => {
                setSelectedInteraction(index);
                if (onInteractionClick) {
                  onInteractionClick(item.description);
                }
              }}
              style={{
                padding: '6px 8px',
                marginBottom: '4px',
                backgroundColor: selectedInteraction === index ? '#e3f2fd' : 'white',
                border: '1px solid #dee2e6',
                borderRadius: '4px',
                cursor: 'pointer',
                transition: 'background-color 0.2s ease',
              }}
            >
              <strong>#{index + 1}</strong> {item.description}
            </div>
          ))}
        </div>
      </div>
    );
  };

  // Render loading state
  if (loading) {
    return (
      <div className={`sequence-diagram-viewer sequence-loading ${className}`}>
        <div style={{
          padding: '20px',
          textAlign: 'center',
          border: '1px solid #e0e0e0',
          borderRadius: '4px',
        }}>
          <div>Loading sequence diagram...</div>
        </div>
      </div>
    );
  }

  // Render error state
  if (error) {
    return (
      <div className={`sequence-diagram-viewer sequence-error ${className}`}>
        <div style={{
          padding: '20px',
          textAlign: 'center',
          border: '1px solid #f44336',
          borderRadius: '4px',
          backgroundColor: '#ffebee',
          color: '#c62828',
        }}>
          <div>Error rendering sequence diagram:</div>
          <div style={{ fontSize: '0.9em', marginTop: '8px' }}>{error}</div>
        </div>
      </div>
    );
  }

  return (
    <div className={`sequence-diagram-viewer ${className}`}>
      {renderActorList()}
      
      <div style={{
        border: '1px solid #e0e0e0',
        borderRadius: '4px',
        padding: '16px',
        backgroundColor: 'white',
      }}>
        <TransformWrapper
          initialScale={1}
          minScale={0.3}
          maxScale={3}
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
              {/* Zoom Controls */}
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
                <div 
                  ref={containerRef}
                  style={{
                    minHeight: '300px',
                    width: '100%',
                    textAlign: 'center',
                  }}
                />
              </TransformComponent>
            </>
          )}
        </TransformWrapper>
      </div>

      {renderTimeline()}
    </div>
  );
};

export default SequenceDiagramViewer; 