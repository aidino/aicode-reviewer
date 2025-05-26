"""
Unit tests for SequenceDiagramViewer component.

This module contains comprehensive tests for the sequence diagram viewer component
including rendering, interaction handling, and timeline navigation.
"""

import pytest
from unittest.mock import Mock, patch
from src.webapp.frontend.src.components.SequenceDiagramViewer import SequenceDiagramViewer


class TestSequenceDiagramViewer:
    """Test cases for SequenceDiagramViewer component."""

    @pytest.fixture
    def mock_diagram_data(self):
        """
        Create mock diagram data for testing.
        
        Returns:
            dict: Mock diagram data with sequence diagram content
        """
        return {
            'type': 'sequence',
            'content': '''
                @startuml
                Alice -> Bob: Authentication Request
                Bob --> Alice: Authentication Response
                Alice -> Bob: Another authentication Request
                Alice <-- Bob: Another authentication Response
                @enduml
            ''',
            'title': 'Authentication Sequence',
            'metadata': {
                'actors': ['Alice', 'Bob'],
                'interactions': [
                    'Authentication Request',
                    'Authentication Response',
                    'Another authentication Request',
                    'Another authentication Response'
                ]
            }
        }

    @pytest.fixture
    def component_props(self, mock_diagram_data):
        """
        Create component props for testing.
        
        Args:
            mock_diagram_data: Mock diagram data fixture
            
        Returns:
            dict: Component props for testing
        """
        return {
            'diagram': mock_diagram_data,
            'className': 'test-sequence-viewer',
            'onActorClick': Mock(),
            'onInteractionClick': Mock(),
            'showTimeline': True,
            'showActorHighlights': True
        }

    def test_component_initialization(self, component_props):
        """
        Test that SequenceDiagramViewer initializes correctly.
        
        Args:
            component_props: Component props fixture
        """
        # Test basic initialization
        viewer = SequenceDiagramViewer(component_props)
        assert viewer is not None
        assert viewer.props['diagram'] == component_props['diagram']
        assert viewer.props['className'] == 'test-sequence-viewer'

    def test_sequence_parsing(self, component_props):
        """
        Test sequence diagram parsing functionality.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test actor extraction
        actors = viewer.extract_actors()
        assert 'Alice' in actors
        assert 'Bob' in actors
        assert len(actors) == 2

        # Test interaction extraction
        interactions = viewer.extract_interactions()
        assert len(interactions) >= 4
        assert any('Authentication Request' in interaction for interaction in interactions)

    def test_timeline_functionality(self, component_props):
        """
        Test timeline navigation functionality.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test timeline item generation
        timeline_items = viewer.generate_timeline()
        assert len(timeline_items) > 0
        assert all('index' in item for item in timeline_items)
        assert all('description' in item for item in timeline_items)

    def test_actor_highlighting(self, component_props):
        """
        Test actor highlighting functionality.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test actor click handling
        with patch.object(viewer, 'highlight_actor') as mock_highlight:
            viewer.handle_actor_click('Alice')
            mock_highlight.assert_called_once_with('Alice')

        # Test actor highlighting state
        viewer.set_highlighted_actor('Bob')
        assert viewer.get_highlighted_actor() == 'Bob'

    def test_interaction_handling(self, component_props):
        """
        Test interaction click handling.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test interaction click callback
        viewer.handle_interaction_click('Authentication Request')
        component_props['onInteractionClick'].assert_called_once_with('Authentication Request')

    def test_zoom_and_pan_integration(self, component_props):
        """
        Test zoom and pan functionality integration.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test zoom controls presence
        zoom_controls = viewer.get_zoom_controls()
        assert zoom_controls is not None
        assert 'zoomIn' in zoom_controls
        assert 'zoomOut' in zoom_controls
        assert 'resetTransform' in zoom_controls

    def test_plantuml_rendering(self, component_props):
        """
        Test PlantUML diagram rendering.
        
        Args:
            component_props: Component props fixture
        """
        with patch('plantuml.PlantUML') as mock_plantuml:
            mock_instance = Mock()
            mock_plantuml.return_value = mock_instance
            mock_instance.processes.return_value = b'<svg>test</svg>'
            
            viewer = SequenceDiagramViewer(component_props)
            rendered_content = viewer.render_diagram()
            
            assert rendered_content is not None
            mock_plantuml.assert_called_once()

    def test_error_handling(self, component_props):
        """
        Test error handling in diagram rendering.
        
        Args:
            component_props: Component props fixture
        """
        # Test with invalid diagram content
        invalid_props = component_props.copy()
        invalid_props['diagram']['content'] = 'invalid content'
        
        viewer = SequenceDiagramViewer(invalid_props)
        
        # Should handle error gracefully
        with patch.object(viewer, 'handle_rendering_error') as mock_error_handler:
            viewer.render_diagram()
            mock_error_handler.assert_called_once()

    def test_timeline_navigation(self, component_props):
        """
        Test timeline navigation controls.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test navigation to specific timeline item
        viewer.navigate_to_timeline_item(1)
        assert viewer.get_current_timeline_index() == 1

        # Test next/previous navigation
        viewer.navigate_next()
        assert viewer.get_current_timeline_index() == 2

        viewer.navigate_previous()
        assert viewer.get_current_timeline_index() == 1

    def test_actor_filtering(self, component_props):
        """
        Test actor-based filtering functionality.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test filtering by actor
        viewer.filter_by_actor('Alice')
        filtered_interactions = viewer.get_filtered_interactions()
        
        # All interactions should involve Alice
        assert all('Alice' in interaction for interaction in filtered_interactions)

    def test_export_functionality(self, component_props):
        """
        Test diagram export functionality.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test SVG export
        with patch.object(viewer, 'export_as_svg') as mock_export:
            viewer.export_diagram('svg')
            mock_export.assert_called_once()

        # Test PNG export
        with patch.object(viewer, 'export_as_png') as mock_export:
            viewer.export_diagram('png')
            mock_export.assert_called_once()

    def test_performance_optimization(self, component_props):
        """
        Test performance optimization features.
        
        Args:
            component_props: Component props fixture
        """
        # Test with large diagram
        large_diagram = component_props['diagram'].copy()
        large_diagram['content'] = self.generate_large_sequence_diagram()
        large_props = component_props.copy()
        large_props['diagram'] = large_diagram
        
        viewer = SequenceDiagramViewer(large_props)
        
        # Test lazy loading
        with patch.object(viewer, 'enable_lazy_loading') as mock_lazy:
            viewer.optimize_for_large_diagram()
            mock_lazy.assert_called_once()

    def test_accessibility_features(self, component_props):
        """
        Test accessibility features.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test keyboard navigation
        keyboard_handlers = viewer.get_keyboard_handlers()
        assert 'onKeyDown' in keyboard_handlers
        assert 'onKeyUp' in keyboard_handlers

        # Test aria labels
        aria_labels = viewer.get_aria_labels()
        assert len(aria_labels) > 0

    def test_responsive_design(self, component_props):
        """
        Test responsive design adaptations.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test mobile layout
        viewer.set_viewport_size(400, 600)  # Mobile size
        mobile_layout = viewer.get_responsive_layout()
        assert mobile_layout['compact'] is True

        # Test desktop layout
        viewer.set_viewport_size(1200, 800)  # Desktop size
        desktop_layout = viewer.get_responsive_layout()
        assert desktop_layout['compact'] is False

    def generate_large_sequence_diagram(self):
        """
        Generate a large sequence diagram for performance testing.
        
        Returns:
            str: Large PlantUML sequence diagram content
        """
        content = "@startuml\n"
        actors = [f"Actor{i}" for i in range(10)]
        
        for i in range(100):
            actor1 = actors[i % len(actors)]
            actor2 = actors[(i + 1) % len(actors)]
            content += f"{actor1} -> {actor2}: Message {i}\n"
            content += f"{actor2} --> {actor1}: Response {i}\n"
        
        content += "@enduml"
        return content

    def test_custom_styling(self, component_props):
        """
        Test custom styling options.
        
        Args:
            component_props: Component props fixture
        """
        viewer = SequenceDiagramViewer(component_props)
        
        # Test theme application
        viewer.apply_theme('dark')
        assert viewer.get_current_theme() == 'dark'

        # Test custom colors
        custom_colors = {
            'actor_color': '#ff0000',
            'message_color': '#00ff00',
            'background_color': '#0000ff'
        }
        viewer.apply_custom_colors(custom_colors)
        assert viewer.get_custom_colors() == custom_colors

    def test_integration_with_transform_wrapper(self, component_props):
        """
        Test integration with react-zoom-pan-pinch TransformWrapper.
        
        Args:
            component_props: Component props fixture
        """
        with patch('react-zoom-pan-pinch.TransformWrapper') as mock_wrapper:
            viewer = SequenceDiagramViewer(component_props)
            viewer.render()
            
            # Verify TransformWrapper is used
            mock_wrapper.assert_called_once()
            
            # Check wrapper configuration
            call_args = mock_wrapper.call_args
            assert 'initialScale' in call_args[1]
            assert 'minScale' in call_args[1]
            assert 'maxScale' in call_args[1]


# Fixtures for pytest
@pytest.fixture
def sequence_diagram_test_suite():
    """
    Create a test suite for sequence diagram viewer.
    
    Returns:
        TestSequenceDiagramViewer: Test suite instance
    """
    return TestSequenceDiagramViewer()


if __name__ == '__main__':
    pytest.main([__file__]) 