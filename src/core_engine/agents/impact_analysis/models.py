from typing import List, Dict, Optional
from pydantic import BaseModel

class ImpactAnalysisInput(BaseModel):
    """
    Input cho ImpactAnalysisAgent.

    Attributes:
        diff (str): Nội dung diff (unified diff hoặc git diff).
        dependency_graph (Dict[str, List[str]]): Đồ thị phụ thuộc (key: entity, value: list các entity phụ thuộc).
        changed_files (Optional[List[str]]): Danh sách file thay đổi (nếu có).
        extra (Optional[Dict]): Thông tin bổ sung (nếu cần).
    """
    diff: str
    dependency_graph: Dict[str, List[str]]
    changed_files: Optional[List[str]] = None
    extra: Optional[Dict] = None

class ImpactedEntity(BaseModel):
    """
    Thực thể bị ảnh hưởng bởi thay đổi.

    Attributes:
        name (str): Tên thực thể (file/class/function).
        type (str): Loại thực thể (file/class/function).
        impact_level (str): Mức độ ảnh hưởng (direct/indirect/none).
        propagation_path (Optional[List[str]]): Đường lan truyền tác động.
    """
    name: str
    type: str
    impact_level: str
    propagation_path: Optional[List[str]] = None

class ImpactAnalysisResult(BaseModel):
    """
    Kết quả phân tích tác động.

    Attributes:
        impacted_entities (List[ImpactedEntity]): Danh sách thực thể bị ảnh hưởng.
        summary (Optional[str]): Tóm tắt kết quả.
        details (Optional[Dict]): Thông tin chi tiết (nếu có).
    """
    impacted_entities: List[ImpactedEntity]
    summary: Optional[str] = None
    details: Optional[Dict] = None 