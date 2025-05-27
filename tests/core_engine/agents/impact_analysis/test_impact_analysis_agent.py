import pytest
from pydantic import ValidationError
from src.core_engine.agents.impact_analysis.impact_analysis_agent import ImpactAnalysisAgent
from src.core_engine.agents.impact_analysis.models import ImpactAnalysisInput, ImpactedEntity, ImpactAnalysisResult

import copy

def make_basic_input():
    return ImpactAnalysisInput(
        diff="""diff --git a/foo.py b/foo.py\n@@ -1,4 +1,5 @@\n def foo():\n     pass\n+def bar():\n+    return 1\n""",
        dependency_graph={
            "foo.py": ["bar.py"],
            "bar.py": []
        },
        changed_files=["foo.py"]
    )

def test_analyze_impact_basic():
    agent = ImpactAnalysisAgent()
    input_data = make_basic_input()
    result = agent.analyze_impact(input_data)
    # Phải có foo.py (direct) và bar.py (indirect)
    names = {e.name: e for e in result.impacted_entities}
    assert "foo.py" in names
    assert "bar.py" in names
    assert names["foo.py"].impact_level == "direct"
    assert names["bar.py"].impact_level == "indirect"
    # Kiểm tra propagation path
    assert names["foo.py"].propagation_path == ["foo.py"]
    assert names["bar.py"].propagation_path == ["foo.py", "bar.py"]
    assert result.summary.startswith("Tổng cộng")
    assert "foo.py" in result.details["changed_files"]

def test_input_model_validation():
    # Thiếu trường bắt buộc
    with pytest.raises(ValidationError):
        ImpactAnalysisInput()
    # Truyền sai kiểu
    with pytest.raises(ValueError):
        ImpactAnalysisInput(diff=123, dependency_graph={})

def test_impacted_entity_model():
    entity = ImpactedEntity(name="foo.py", type="file", impact_level="direct")
    assert entity.name == "foo.py"
    assert entity.impact_level == "direct"
    assert entity.propagation_path is None

def test_result_model():
    entity = ImpactedEntity(name="foo.py", type="file", impact_level="direct")
    result = ImpactAnalysisResult(impacted_entities=[entity], summary="Tác động trực tiếp", details={"foo": "bar"})
    assert result.summary == "Tác động trực tiếp"
    assert result.details["foo"] == "bar"

def test_edge_case_empty_diff():
    agent = ImpactAnalysisAgent()
    input_data = ImpactAnalysisInput(diff="", dependency_graph={}, changed_files=[])
    result = agent.analyze_impact(input_data)
    # Không có thực thể nào bị ảnh hưởng
    assert result.impacted_entities == []
    assert result.summary.startswith("Tổng cộng 0") 