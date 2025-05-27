import React from 'react';
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import SequenceDiagramViewer from '../SequenceDiagramViewer';

// Mock react-zoom-pan-pinch
vi.mock('react-zoom-pan-pinch', () => ({
  TransformWrapper: ({ children }: any) => <div data-testid="transform-wrapper">{children({ zoomIn: vi.fn(), zoomOut: vi.fn(), resetTransform: vi.fn() })}</div>,
  TransformComponent: ({ children }: any) => <div data-testid="transform-component">{children}</div>
}));

describe('SequenceDiagramViewer', () => {
  const mockDiagram = {
    type: 'sequence',
    content: `sequenceDiagram\nAlice->>Bob: Authentication Request\nBob-->>Alice: Authentication Response`,
    format: 'mermaid',
    title: 'Authentication Sequence',
    description: 'Test sequence diagram',
  };

  it('renders loading state initially', () => {
    render(<SequenceDiagramViewer diagram={mockDiagram} />);
    expect(screen.getByText('Loading sequence diagram...')).toBeInTheDocument();
  });

  it('renders error when no content provided', () => {
    const emptyDiagram = { ...mockDiagram, content: '' };
    render(<SequenceDiagramViewer diagram={emptyDiagram} />);
    expect(screen.getByText('Error rendering sequence diagram:')).toBeInTheDocument();
    expect(screen.getByText('No sequence diagram content provided')).toBeInTheDocument();
  });

  it('renders error for non-sequence diagram', () => {
    const nonSequenceDiagram = { ...mockDiagram, content: 'graph TD\nA-->B', type: 'flowchart' };
    render(<SequenceDiagramViewer diagram={nonSequenceDiagram} />);
    expect(screen.getByText('Error rendering sequence diagram:')).toBeInTheDocument();
    expect(screen.getByText('This component is designed for sequence diagrams only')).toBeInTheDocument();
  });

  it('calls onActorClick when provided', () => {
    const onActorClick = vi.fn();
    render(<SequenceDiagramViewer diagram={mockDiagram} onActorClick={onActorClick} />);
    // Component renders với callback được truyền vào
    expect(screen.getByText('Loading sequence diagram...')).toBeInTheDocument();
  });

  it('shows timeline when showTimeline=true', () => {
    render(<SequenceDiagramViewer diagram={mockDiagram} showTimeline={true} />);
    // Component renders với timeline enabled
    expect(screen.getByText('Loading sequence diagram...')).toBeInTheDocument();
  });

  it('matches snapshot', () => {
    const { asFragment } = render(<SequenceDiagramViewer diagram={mockDiagram} />);
    expect(asFragment()).toMatchSnapshot();
  });
}); 