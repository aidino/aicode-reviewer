"""
ReportingAgent for AI Code Review System.

This module implements the ReportingAgent responsible for generating structured
reports from static analysis findings and LLM insights. Supports both JSON
data structure and Markdown formatting for comprehensive code review reports.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from ..diagramming_engine import DiagrammingEngine

# Configure logging
logger = logging.getLogger(__name__)


class ReportingAgent:
    """
    Agent responsible for generating comprehensive code review reports.
    
    This agent handles:
    - Aggregating static analysis findings and LLM insights
    - Creating structured report data (JSON-like)
    - Formatting reports as Markdown for human readability
    - Generating summary statistics and metadata
    - Supporting future extensions for HTML/PDF output
    """
    
    def __init__(self, diagramming_engine: Optional[DiagrammingEngine] = None):
        """
        Initialize the ReportingAgent.
        
        Args:
            diagramming_engine (Optional[DiagrammingEngine]): Engine for diagram generation
        
        Sets up report generation capabilities and default configurations.
        """
        self.supported_formats = ['json', 'markdown', 'html']  # Future extension
        self.report_version = "1.0.0"
        self.diagramming_engine = diagramming_engine or DiagrammingEngine()
        
        logger.info("ReportingAgent initialized with diagram generation support")
    
    def generate_report_data(self, static_findings: List[Dict], llm_insights: str, 
                           scan_details: Dict, code_files: Optional[Dict[str, Any]] = None) -> Dict:
        """
        Generate structured report data from analysis results.
        
        Args:
            static_findings (List[Dict]): Static analysis findings from StaticAnalysisAgent
            llm_insights (str): LLM analysis insights from LLMOrchestratorAgent
            scan_details (Dict): Scan metadata (repo URL, PR ID, etc.)
            code_files (Optional[Dict[str, Any]]): AST data for diagram generation
            
        Returns:
            Dict: Structured report data ready for formatting
        """
        logger.info("Generating structured report data")
        
        try:
            # Calculate summary statistics
            total_findings = len(static_findings) if static_findings else 0
            
            # Categorize findings by severity
            severity_counts = self._calculate_severity_stats(static_findings)
            
            # Categorize findings by type/category
            category_counts = self._calculate_category_stats(static_findings)
            
            # Extract scan metadata
            scan_info = {
                "scan_id": scan_details.get("scan_id", f"scan_{int(datetime.now().timestamp())}"),
                "repository": scan_details.get("repo_url", "Unknown repository"),
                "pr_id": scan_details.get("pr_id"),
                "branch": scan_details.get("branch"),
                "scan_type": scan_details.get("scan_type", "project"),
                "timestamp": datetime.now().isoformat(),
                "report_version": self.report_version
            }
            
            # Process LLM insights
            llm_review = self._process_llm_insights(llm_insights)
            
            # Generate class diagrams if code files provided
            diagrams = self._generate_diagrams(code_files, static_findings)
            
            # Construct structured report data
            report_data = {
                "scan_info": scan_info,
                "summary": {
                    "total_findings": total_findings,
                    "severity_breakdown": severity_counts,
                    "category_breakdown": category_counts,
                    "scan_status": "completed",
                    "has_llm_analysis": bool(llm_insights and llm_insights.strip())
                },
                "static_analysis_findings": static_findings or [],
                "llm_review": llm_review,
                "diagrams": diagrams,
                "metadata": {
                    "agent_versions": {
                        "reporting_agent": self.report_version,
                        "static_analysis": "1.0.0",  # TODO: Get from agents
                        "llm_orchestrator": "1.0.0"
                    },
                    "generation_time": datetime.now().isoformat(),
                    "total_files_analyzed": scan_details.get("total_files", 0),
                    "successful_parses": scan_details.get("successful_parses", 0)
                }
            }
            
            logger.info(f"Generated report data with {total_findings} findings")
            return report_data
            
        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            # Return minimal report structure on error
            return self._generate_error_report(str(e), scan_details)
    
    def format_markdown_report(self, report_data: Dict) -> str:
        """
        Format structured report data as Markdown.
        
        Args:
            report_data (Dict): Structured report data from generate_report_data()
            
        Returns:
            str: Human-readable Markdown report
        """
        logger.info("Formatting report as Markdown")
        
        try:
            # Extract data sections
            scan_info = report_data.get("scan_info", {})
            summary = report_data.get("summary", {})
            static_findings = report_data.get("static_analysis_findings", [])
            llm_review = report_data.get("llm_review", {})
            metadata = report_data.get("metadata", {})
            
            # Build Markdown report
            markdown_parts = []
            
            # Header
            markdown_parts.append(self._format_header(scan_info))
            
            # Executive Summary
            markdown_parts.append(self._format_summary(summary, scan_info))
            
            # Static Analysis Results (always include, even if empty)
            markdown_parts.append(self._format_static_findings(static_findings, summary))
            
            # LLM Analysis Results
            if llm_review.get("insights"):
                markdown_parts.append(self._format_llm_insights(llm_review))
            
            # Recommendations
            markdown_parts.append(self._format_recommendations(static_findings, llm_review))
            
            # Technical Details
            markdown_parts.append(self._format_technical_details(metadata))
            
            # Footer
            markdown_parts.append(self._format_footer())
            
            # Combine all parts
            markdown_report = "\n\n".join(markdown_parts)
            
            logger.info(f"Generated Markdown report ({len(markdown_report)} characters)")
            return markdown_report
            
        except Exception as e:
            logger.error(f"Error formatting Markdown report: {str(e)}")
            return self._generate_error_markdown(str(e), report_data)
    
    def _calculate_severity_stats(self, findings: List[Dict]) -> Dict[str, int]:
        """Calculate statistics by severity level."""
        severity_counts = {"Error": 0, "Warning": 0, "Info": 0, "Unknown": 0}
        
        for finding in findings:
            severity = finding.get("severity", "Unknown")
            if severity in severity_counts:
                severity_counts[severity] += 1
            else:
                severity_counts["Unknown"] += 1
        
        return severity_counts
    
    def _calculate_category_stats(self, findings: List[Dict]) -> Dict[str, int]:
        """Calculate statistics by category/type."""
        category_counts = {}
        
        for finding in findings:
            category = finding.get("category", "uncategorized")
            category_counts[category] = category_counts.get(category, 0) + 1
        
        return category_counts
    
    def _process_llm_insights(self, llm_insights: str) -> Dict:
        """Process and structure LLM insights with XAI data extraction."""
        if not llm_insights or not llm_insights.strip():
            return {"insights": "", "has_content": False}
        
        # Extract sections from LLM insights if structured
        sections = {}
        current_section = "general"
        current_content = []
        
        # XAI data extraction
        import re
        xai_data = {
            "confidence_scores": [],
            "reasoning_points": [],
            "evidence_items": [],
            "alternatives": []
        }
        
        for line in llm_insights.split('\n'):
            line = line.strip()
            
            # Extract XAI components
            # Extract confidence scores
            confidence_match = re.search(r'\*\*Confidence:\*\*\s*(\d+\.?\d*)', line, re.IGNORECASE)
            if confidence_match:
                confidence_score = float(confidence_match.group(1))
                xai_data["confidence_scores"].append(confidence_score)
            
            # Extract reasoning
            reasoning_match = re.search(r'\*\*Reasoning:\*\*\s*(.*)', line, re.IGNORECASE)
            if reasoning_match:
                reasoning = reasoning_match.group(1).strip()
                if reasoning:
                    xai_data["reasoning_points"].append(reasoning)
            
            # Extract evidence
            evidence_match = re.search(r'\*\*Evidence:\*\*\s*(.*)', line, re.IGNORECASE)
            if evidence_match:
                evidence = evidence_match.group(1).strip()
                if evidence:
                    xai_data["evidence_items"].append(evidence)
            
            # Extract alternatives
            alternatives_match = re.search(r'\*\*Alternatives:\*\*\s*(.*)', line, re.IGNORECASE)
            if alternatives_match:
                alternatives = alternatives_match.group(1).strip()
                if alternatives:
                    xai_data["alternatives"].append(alternatives)
            
            # Section processing
            if line.startswith('##') and line.endswith(':'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line[2:].strip().rstrip(':').lower().replace(' ', '_')
                current_content = []
            elif line.startswith('##'):
                # Save previous section
                if current_content:
                    sections[current_section] = '\n'.join(current_content).strip()
                
                # Start new section
                current_section = line[2:].strip().lower().replace(' ', '_')
                current_content = []
            else:
                current_content.append(line)
        
        # Save final section
        if current_content:
            sections[current_section] = '\n'.join(current_content).strip()
        
        # Calculate XAI summary metrics
        avg_confidence = sum(xai_data["confidence_scores"]) / len(xai_data["confidence_scores"]) if xai_data["confidence_scores"] else None
        
        return {
            "insights": llm_insights,
            "has_content": True,
            "sections": sections,
            "word_count": len(llm_insights.split()),
            "line_count": len(llm_insights.split('\n')),
            # XAI specific fields
            "xai_data": xai_data,
            "xai_summary": {
                "total_confidence_scores": len(xai_data["confidence_scores"]),
                "average_confidence": round(avg_confidence, 2) if avg_confidence else None,
                "reasoning_points_count": len(xai_data["reasoning_points"]),
                "evidence_items_count": len(xai_data["evidence_items"]),
                "alternatives_count": len(xai_data["alternatives"])
            }
        }
    
    def _format_header(self, scan_info: Dict) -> str:
        """Format report header."""
        repo_name = scan_info.get("repository", "Unknown").split('/')[-1] if scan_info.get("repository") else "Unknown"
        pr_info = f" - PR #{scan_info.get('pr_id')}" if scan_info.get("pr_id") else ""
        
        header = f"""# Code Review Report: {repo_name}{pr_info}

**Scan ID:** `{scan_info.get('scan_id', 'unknown')}`  
**Repository:** {scan_info.get('repository', 'Unknown')}  
**Scan Type:** {scan_info.get('scan_type', 'project').title()}  
**Generated:** {self._format_timestamp(scan_info.get('timestamp'))}  
**Report Version:** {scan_info.get('report_version', '1.0.0')}"""

        if scan_info.get("pr_id"):
            header += f"\n**Pull Request:** #{scan_info['pr_id']}"
        
        if scan_info.get("branch"):
            header += f"\n**Branch:** `{scan_info['branch']}`"
        
        return header
    
    def _format_summary(self, summary: Dict, scan_info: Dict) -> str:
        """Format executive summary section."""
        total_findings = summary.get("total_findings", 0)
        severity_breakdown = summary.get("severity_breakdown", {})
        
        summary_md = "## 📋 Executive Summary\n\n"
        
        if total_findings == 0:
            summary_md += "✅ **No issues found!** This code appears to be in good shape.\n\n"
        else:
            summary_md += f"📊 **Total Issues Found:** {total_findings}\n\n"
            
            # Severity breakdown
            if severity_breakdown and any(severity_breakdown.values()):
                summary_md += "### Issue Severity Breakdown\n\n"
                for severity, count in severity_breakdown.items():
                    if count > 0:
                        icon = {"Error": "🔴", "Warning": "🟡", "Info": "🔵"}.get(severity, "⚫")
                        summary_md += f"- {icon} **{severity}:** {count}\n"
                summary_md += "\n"
        
        # Scan type information
        scan_type = scan_info.get("scan_type", "project")
        if scan_type == "pr":
            summary_md += "🔍 **Analysis Type:** Pull Request review\n"
        else:
            summary_md += "🔍 **Analysis Type:** Full project scan\n"
        
        if summary.get("has_llm_analysis"):
            summary_md += "🤖 **AI Analysis:** Included\n"
        
        return summary_md
    
    def _format_static_findings(self, findings: List[Dict], summary: Dict) -> str:
        """Format static analysis findings section."""
        findings_md = "## 🔍 Static Analysis Results\n\n"
        
        if not findings:
            findings_md += "No static analysis issues detected.\n"
            return findings_md
        
        # Group findings by category
        category_breakdown = summary.get("category_breakdown", {})
        
        if category_breakdown:
            findings_md += "### Findings by Category\n\n"
            for category, count in sorted(category_breakdown.items()):
                category_icon = {
                    "debugging": "🐛",
                    "logging": "📝",
                    "complexity": "⚡",
                    "imports": "📦",
                    "security": "🔒"
                }.get(category, "📋")
                findings_md += f"- {category_icon} **{category.title()}:** {count} issue(s)\n"
            findings_md += "\n"
        
        # Detailed findings
        findings_md += "### Detailed Findings\n\n"
        
        # Group by file for better organization
        files_dict = {}
        for finding in findings:
            file_path = finding.get("file", "Unknown file")
            if file_path not in files_dict:
                files_dict[file_path] = []
            files_dict[file_path].append(finding)
        
        for file_path, file_findings in sorted(files_dict.items()):
            findings_md += f"#### 📄 `{file_path}`\n\n"
            
            for finding in file_findings:
                severity = finding.get("severity", "Info")
                severity_icon = {"Error": "🔴", "Warning": "🟡", "Info": "🔵"}.get(severity, "⚫")
                
                findings_md += f"**{severity_icon} {finding.get('rule_id', 'Unknown Rule')}** "
                findings_md += f"(Line {finding.get('line', 'N/A')})\n\n"
                findings_md += f"**Issue:** {finding.get('message', 'No description')}\n\n"
                
                if finding.get("suggestion"):
                    findings_md += f"**Recommendation:** {finding['suggestion']}\n\n"
                
                findings_md += "---\n\n"
        
        return findings_md
    
    def _format_llm_insights(self, llm_review: Dict) -> str:
        """Format LLM analysis insights section with XAI data."""
        insights_md = "## 🤖 AI Analysis & Insights\n\n"
        
        insights = llm_review.get("insights", "")
        if not insights:
            insights_md += "No AI analysis available.\n"
            return insights_md
        
        # Add XAI summary if available
        xai_summary = llm_review.get("xai_summary", {})
        if xai_summary and xai_summary.get("total_confidence_scores", 0) > 0:
            insights_md += "### 🎯 Explainable AI (XAI) Summary\n\n"
            
            avg_confidence = xai_summary.get("average_confidence")
            if avg_confidence is not None:
                confidence_emoji = "🟢" if avg_confidence >= 0.8 else "🟡" if avg_confidence >= 0.6 else "🔴"
                insights_md += f"**Overall Confidence:** {confidence_emoji} {avg_confidence}/1.0\n\n"
            
            insights_md += f"**Analysis Depth:**\n"
            insights_md += f"- 🧠 {xai_summary.get('reasoning_points_count', 0)} reasoning explanations\n"
            insights_md += f"- 📊 {xai_summary.get('evidence_items_count', 0)} evidence citations\n"
            insights_md += f"- 🔄 {xai_summary.get('alternatives_count', 0)} alternative approaches\n"
            insights_md += f"- ✅ {xai_summary.get('total_confidence_scores', 0)} confidence assessments\n\n"
            
            insights_md += "---\n\n"
        
        # Add LLM analysis directly (it's already well-formatted)
        insights_md += insights
        
        # Add XAI details if available
        xai_data = llm_review.get("xai_data", {})
        if xai_data and any(xai_data.values()):
            insights_md += "\n\n---\n\n### 🔍 Explainability Details\n\n"
            
            # Confidence distribution
            confidence_scores = xai_data.get("confidence_scores", [])
            if confidence_scores:
                high_conf = sum(1 for c in confidence_scores if c >= 0.8)
                med_conf = sum(1 for c in confidence_scores if 0.6 <= c < 0.8)
                low_conf = sum(1 for c in confidence_scores if c < 0.6)
                
                insights_md += "**Confidence Distribution:**\n"
                if high_conf > 0:
                    insights_md += f"- 🟢 High (≥0.8): {high_conf} findings\n"
                if med_conf > 0:
                    insights_md += f"- 🟡 Medium (0.6-0.8): {med_conf} findings\n"
                if low_conf > 0:
                    insights_md += f"- 🔴 Low (<0.6): {low_conf} findings\n"
                insights_md += "\n"
        
        # Add metadata if available
        if llm_review.get("word_count"):
            insights_md += f"\n\n*Analysis contains {llm_review['word_count']} words with explainable AI enhancements.*"
        
        return insights_md
    
    def _format_recommendations(self, findings: List[Dict], llm_review: Dict) -> str:
        """Format recommendations section."""
        rec_md = "## 💡 Key Recommendations\n\n"
        
        recommendations = []
        
        # Extract recommendations from static findings
        for finding in findings:
            if finding.get("suggestion") and finding["suggestion"] not in recommendations:
                recommendations.append(finding["suggestion"])
        
        # Extract recommendations from LLM insights
        llm_sections = llm_review.get("sections", {})
        if "specific_recommendations" in llm_sections:
            rec_md += "### From AI Analysis\n\n"
            rec_content = llm_sections["specific_recommendations"]
            # Clean up the content
            for line in rec_content.split('\n'):
                if line.strip() and not line.strip().startswith('#'):
                    rec_md += f"{line}\n"
            rec_md += "\n"
        
        # Add static analysis recommendations
        if recommendations:
            rec_md += "### From Static Analysis\n\n"
            for i, rec in enumerate(recommendations[:5], 1):  # Limit to top 5
                rec_md += f"{i}. {rec}\n"
            
            if len(recommendations) > 5:
                rec_md += f"\n*... and {len(recommendations) - 5} more recommendations from detailed findings above.*\n"
        
        if not recommendations and not llm_sections.get("specific_recommendations"):
            rec_md += "✅ No specific recommendations - code quality appears good!\n"
        
        return rec_md
    
    def _format_technical_details(self, metadata: Dict) -> str:
        """Format technical details section."""
        tech_md = "## 🔧 Technical Details\n\n"
        
        tech_md += "### Analysis Configuration\n\n"
        tech_md += f"- **Files Analyzed:** {metadata.get('total_files_analyzed', 'Unknown')}\n"
        tech_md += f"- **Successfully Parsed:** {metadata.get('successful_parses', 'Unknown')}\n"
        tech_md += f"- **Generation Time:** {self._format_timestamp(metadata.get('generation_time'))}\n"
        
        agent_versions = metadata.get("agent_versions", {})
        if agent_versions:
            tech_md += "\n### Agent Versions\n\n"
            for agent, version in agent_versions.items():
                tech_md += f"- **{agent.replace('_', ' ').title()}:** {version}\n"
        
        return tech_md
    
    def _format_footer(self) -> str:
        """Format report footer."""
        footer = """---

## 📝 Notes

- This report was generated automatically by the AI Code Review System
- Static analysis findings are based on rule-based pattern matching
- AI insights are generated using Large Language Models and should be reviewed by humans
- For questions about this report, please refer to the documentation

**Generated by ReportingAgent** | *Making code reviews more comprehensive and actionable*"""
        
        return footer
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display."""
        if not timestamp:
            return "Unknown"
        
        try:
            # Parse ISO format timestamp
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
        except:
            return timestamp
    
    def _generate_error_report(self, error_message: str, scan_details: Dict) -> Dict:
        """Generate minimal report structure for error cases."""
        return {
            "scan_info": {
                "scan_id": f"error_{int(datetime.now().timestamp())}",
                "repository": scan_details.get("repo_url", "Unknown"),
                "scan_type": "error",
                "timestamp": datetime.now().isoformat(),
                "report_version": self.report_version
            },
            "summary": {
                "total_findings": 0,
                "severity_breakdown": {},
                "category_breakdown": {},
                "scan_status": "error",
                "error_message": error_message
            },
            "static_analysis_findings": [],
            "llm_review": {"insights": "", "has_content": False},
            "diagrams": [],
            "metadata": {
                "generation_time": datetime.now().isoformat(),
                "error": error_message
            }
        }
    
    def _generate_error_markdown(self, error_message: str, report_data: Dict) -> str:
        """Generate error Markdown report."""
        return f"""# Code Review Report - Error

## ❌ Report Generation Error

An error occurred while generating the code review report:

**Error:** {error_message}

**Timestamp:** {self._format_timestamp(datetime.now().isoformat())}

Please check the logs for more details and try again.

---
*Generated by ReportingAgent*"""
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported report formats."""
        return self.supported_formats.copy()
    
    def _generate_diagrams(self, code_files: Optional[Dict[str, Any]], 
                         static_findings: List[Dict]) -> List[Dict]:
        """
        Generate diagrams from code files and findings.
        
        Args:
            code_files (Optional[Dict[str, Any]]): AST data for diagram generation
            static_findings (List[Dict]): Static analysis findings for change highlighting
            
        Returns:
            List[Dict]: List of diagram data structures
        """
        diagrams = []
        
        if not code_files:
            logger.info("No code files provided for diagram generation")
            return diagrams
        
        try:
            # Extract modified classes and functions from static findings for highlighting
            modified_classes = set()
            modified_functions = set()
            modified_methods = set()
            
            for finding in static_findings:
                # Try to extract class/function names from file paths or findings
                file_path = finding.get("file", "")
                message = finding.get("message", "").lower()
                
                # Extract function names for sequence diagrams
                if "function" in message or "method" in message:
                    # Simple heuristic to extract function/method names
                    # This could be enhanced with more sophisticated parsing
                    words = message.split()
                    for i, word in enumerate(words):
                        if word in ["function", "method"] and i + 1 < len(words):
                            func_name = words[i + 1].strip("'\"(),:")
                            if file_path.endswith(".py"):
                                modified_functions.add(func_name)
                            elif file_path.endswith(".java"):
                                modified_methods.add(func_name)
                
                # Extract class names for class diagrams
                if "class" in message:
                    words = message.split()
                    for i, word in enumerate(words):
                        if word == "class" and i + 1 < len(words):
                            class_name = words[i + 1].strip("'\"(),:")
                            modified_classes.add(class_name)
            
            changes = {
                "modified_classes": list(modified_classes),
                "modified_functions": list(modified_functions),
                "added_functions": [],  # Could be enhanced to detect added functions
                "modified_methods": list(modified_methods),
                "added_methods": []  # Could be enhanced to detect added methods
            }
            
            # Generate diagrams for Python files
            python_files = {path: ast_data for path, ast_data in code_files.items() 
                           if path.endswith('.py')}
            
            if python_files:
                logger.info(f"Generating diagrams for {len(python_files)} Python files")
                
                # Generate class diagrams
                plantuml_class_diagram = self.diagramming_engine.generate_class_diagram(
                    python_files, 'python', changes
                )
                
                self.diagramming_engine.set_diagram_format('mermaid')
                mermaid_class_diagram = self.diagramming_engine.generate_class_diagram(
                    python_files, 'python', changes
                )
                
                # Generate sequence diagrams
                plantuml_sequence_diagram = self.diagramming_engine.generate_sequence_diagram(
                    python_files, 'python', changes
                )
                
                self.diagramming_engine.set_diagram_format('plantuml')  # Reset to default
                mermaid_sequence_diagram = self.diagramming_engine.generate_sequence_diagram(
                    python_files, 'python', changes
                )
                
                # Add class diagrams
                diagrams.append({
                    'type': 'class_diagram',
                    'language': 'python',
                    'format': 'plantuml',
                    'content': plantuml_class_diagram,
                    'files_included': list(python_files.keys()),
                    'generated_at': datetime.now().isoformat()
                })
                
                diagrams.append({
                    'type': 'class_diagram',
                    'language': 'python', 
                    'format': 'mermaid',
                    'content': mermaid_class_diagram,
                    'files_included': list(python_files.keys()),
                    'generated_at': datetime.now().isoformat()
                })
                
                # Add sequence diagrams
                diagrams.append({
                    'type': 'sequence_diagram',
                    'language': 'python',
                    'format': 'plantuml',
                    'content': plantuml_sequence_diagram,
                    'files_included': list(python_files.keys()),
                    'pr_changes': changes,
                    'generated_at': datetime.now().isoformat()
                })
                
                diagrams.append({
                    'type': 'sequence_diagram',
                    'language': 'python',
                    'format': 'mermaid',
                    'content': mermaid_sequence_diagram,
                    'files_included': list(python_files.keys()),
                    'pr_changes': changes,
                    'generated_at': datetime.now().isoformat()
                })
            
            # Generate diagrams for Java files
            java_files = {path: ast_data for path, ast_data in code_files.items() 
                         if path.endswith('.java')}
            
            if java_files:
                logger.info(f"Generating diagrams for {len(java_files)} Java files")
                
                # Generate class diagrams (if supported)
                try:
                    plantuml_java_class_diagram = self.diagramming_engine.generate_class_diagram(
                        java_files, 'java', changes
                    )
                    
                    diagrams.append({
                        'type': 'class_diagram',
                        'language': 'java',
                        'format': 'plantuml',
                        'content': plantuml_java_class_diagram,
                        'files_included': list(java_files.keys()),
                        'generated_at': datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Java class diagrams not yet supported: {str(e)}")
                
                # Generate sequence diagrams
                try:
                    plantuml_java_sequence_diagram = self.diagramming_engine.generate_sequence_diagram(
                        java_files, 'java', changes
                    )
                    
                    self.diagramming_engine.set_diagram_format('mermaid')
                    mermaid_java_sequence_diagram = self.diagramming_engine.generate_sequence_diagram(
                        java_files, 'java', changes
                    )
                    self.diagramming_engine.set_diagram_format('plantuml')  # Reset
                    
                    diagrams.append({
                        'type': 'sequence_diagram',
                        'language': 'java',
                        'format': 'plantuml',
                        'content': plantuml_java_sequence_diagram,
                        'files_included': list(java_files.keys()),
                        'pr_changes': changes,
                        'generated_at': datetime.now().isoformat()
                    })
                    
                    diagrams.append({
                        'type': 'sequence_diagram',
                        'language': 'java',
                        'format': 'mermaid',
                        'content': mermaid_java_sequence_diagram,
                        'files_included': list(java_files.keys()),
                        'pr_changes': changes,
                        'generated_at': datetime.now().isoformat()
                    })
                
                except Exception as e:
                    logger.error(f"Error generating Java sequence diagrams: {str(e)}")
                
            logger.info(f"Generated {len(diagrams)} diagrams total")
            
        except Exception as e:
            logger.error(f"Error generating diagrams: {str(e)}")
            # Add error diagram
            diagrams.append({
                'type': 'error',
                'format': 'text',
                'content': f"Error generating diagrams: {str(e)}",
                'generated_at': datetime.now().isoformat()
            })
        
        return diagrams
    
    def export_json(self, report_data: Dict) -> str:
        """Export report data as JSON string."""
        try:
            return json.dumps(report_data, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error exporting JSON: {str(e)}")
            return json.dumps({"error": str(e)}, indent=2) 