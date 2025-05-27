"""
ImpactAnalysisAgent cho hệ thống AI Code Reviewer.

Agent này chịu trách nhiệm phân tích tác động của thay đổi mã nguồn (diff), xác định các thành phần bị ảnh hưởng dựa trên dependency graph, và lan truyền tác động (propagation).
"""
import re
from typing import Set, List
from .models import ImpactAnalysisInput, ImpactAnalysisResult, ImpactedEntity

class ImpactAnalysisAgent:
    """
    Agent phân tích tác động thay đổi mã nguồn (impact analysis).
    """
    def __init__(self):
        """
        Khởi tạo ImpactAnalysisAgent.
        """
        pass

    def _parse_changed_files_from_diff(self, diff: str) -> Set[str]:
        """
        Parse diff để lấy danh sách file bị thay đổi.
        Args:
            diff (str): Nội dung diff (unified diff)
        Returns:
            Set[str]: Tên file bị thay đổi
        """
        changed_files = set()
        for line in diff.splitlines():
            if line.startswith('diff --git'):
                parts = line.split(' ')
                if len(parts) >= 3:
                    # diff --git a/foo.py b/foo.py
                    file_b = parts[3][2:] if parts[3].startswith('b/') else parts[3]
                    changed_files.add(file_b)
        return changed_files

    def _propagate_impact(self, changed: Set[str], dependency_graph: dict) -> List[ImpactedEntity]:
        """
        Lan truyền tác động qua dependency graph.
        Args:
            changed (Set[str]): Các file bị thay đổi trực tiếp
            dependency_graph (dict): Đồ thị phụ thuộc
        Returns:
            List[ImpactedEntity]: Danh sách thực thể bị ảnh hưởng
        """
        impacted = []
        visited = set()
        stack = []
        # Đầu tiên: các file bị thay đổi trực tiếp
        for file in changed:
            impacted.append(
                ImpactedEntity(name=file, type="file", impact_level="direct", propagation_path=[file])
            )
            visited.add(file)
            stack.append((file, [file]))
        # Lan truyền tác động (BFS)
        while stack:
            current, path = stack.pop(0)
            for dependent in dependency_graph.get(current, []):
                if dependent not in visited:
                    impacted.append(
                        ImpactedEntity(name=dependent, type="file", impact_level="indirect", propagation_path=path + [dependent])
                    )
                    visited.add(dependent)
                    stack.append((dependent, path + [dependent]))
        return impacted

    def analyze_impact(self, input_data: ImpactAnalysisInput) -> ImpactAnalysisResult:
        """
        Phân tích tác động của thay đổi mã nguồn dựa trên diff và dependency graph.

        Args:
            input_data (ImpactAnalysisInput): Thông tin diff, dependency graph, v.v.

        Returns:
            ImpactAnalysisResult: Kết quả phân tích tác động (các thành phần bị ảnh hưởng, mức độ, propagation path).
        """
        # 1. Xác định file bị thay đổi
        if input_data.changed_files:
            changed = set(input_data.changed_files)
        else:
            changed = self._parse_changed_files_from_diff(input_data.diff)
        # 2. Phân tích propagation qua dependency graph
        impacted_entities = self._propagate_impact(changed, input_data.dependency_graph)
        # 3. Tóm tắt
        summary = f"Tổng cộng {len(impacted_entities)} thực thể bị ảnh hưởng."
        return ImpactAnalysisResult(
            impacted_entities=impacted_entities,
            summary=summary,
            details={"changed_files": list(changed)}
        ) 