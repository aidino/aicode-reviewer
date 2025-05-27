#!/usr/bin/env python3
"""
Demo script for Flutter/Dart support in AI Code Review system.

This script demonstrates the comprehensive Dart/Flutter analysis capabilities
including AST parsing, static analysis, and diagram generation.
"""

import tempfile
import os
from pathlib import Path

from src.core_engine.agents.ast_parsing_agent import ASTParsingAgent
from src.core_engine.agents.static_analysis_agent import StaticAnalysisAgent
from src.core_engine.diagramming_engine import DiagrammingEngine


def create_sample_dart_project():
    """Create a sample Flutter/Dart project for demonstration."""
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix="dart_demo_")
    
    # Sample Dart files with various patterns
    files = {
        "main.dart": '''
import 'package:flutter/material.dart';

void main() {
  print('Starting Flutter app');  // Should be flagged
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Demo',
      home: MyHomePage(title: 'Flutter Demo Home Page'),
    );
  }
}
''',
        
        "models/user_model.dart": '''
class User {
  final String id;
  final String name;
  final String email;
  
  const User({
    required this.id,
    required this.name,
    required this.email,
  });
  
  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'] as String,
      name: json['name'] as String,
      email: json['email'] as String,
    );
  }
}
'''
    }
    
    # Write files to temporary directory
    for file_path, content in files.items():
        full_path = Path(temp_dir) / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content)
    
    return temp_dir, files


def demo_dart_support():
    """Demonstrate Dart support capabilities."""
    print("🚀 AI CODE REVIEW - FLUTTER/DART SUPPORT DEMO")
    print("=" * 60)
    
    # Get engine information
    diagram_engine = DiagrammingEngine()
    engine_info = diagram_engine.get_engine_info()
    
    print(f"🏗️  Engine: {engine_info['engine_name']}")
    print(f"📦 Version: {engine_info['version']}")
    print(f"🌐 Supported Languages: {', '.join(engine_info['supported_languages'])}")
    
    print(f"\n🎯 Dart/Flutter Capabilities:")
    for capability in engine_info['capabilities']:
        if "dart" in capability or "flutter" in capability:
            print(f"  🎨 {capability}")
    
    # Check individual agent support
    print(f"\n🤖 Agent Support Status:")
    
    ast_agent = ASTParsingAgent()
    print(f"  📝 ASTParsingAgent: {'✅' if ast_agent.is_language_supported('dart') else '❌'}")
    
    static_agent = StaticAnalysisAgent()
    print(f"  🔍 StaticAnalysisAgent: {'✅' if static_agent.is_language_supported('dart') else '❌'}")
    
    print(f"  📊 DiagrammingEngine: {'✅' if 'dart' in diagram_engine.supported_languages else '❌'}")
    
    # Create sample project
    temp_dir, files = create_sample_dart_project()
    
    try:
        print(f"\n📄 Testing Dart file parsing:")
        
        # Test AST parsing
        for file_path, content in files.items():
            print(f"\n  🔍 Parsing: {file_path}")
            full_path = os.path.join(temp_dir, file_path)
            
            try:
                # Parse file to AST
                ast_result = ast_agent.parse_file_to_ast(full_path)
                
                if ast_result:
                    # Extract structural information
                    structure = ast_agent.extract_structural_info(ast_result, 'dart')
                    
                    print(f"    ✅ Successfully parsed")
                    print(f"    📦 Imports: {len(structure.get('imports', []))}")
                    print(f"    🏛️  Classes: {len(structure.get('classes', []))}")
                    print(f"    ⚙️  Functions: {len(structure.get('functions', []))}")
                    print(f"    🔢 Total nodes: {structure.get('node_count', 0)}")
                    
                    # Test static analysis
                    findings = static_agent.analyze_ast(ast_result, full_path, 'dart')
                    
                    if findings:
                        print(f"    🚨 Found {len(findings)} issues:")
                        for finding in findings:
                            severity_icon = {
                                'Error': '🔴',
                                'Warning': '🟡', 
                                'Info': '🔵'
                            }.get(finding.get('severity', 'Info'), '⚪')
                            
                            print(f"      {severity_icon} Line {finding.get('line', '?')}: {finding.get('message', 'No message')}")
                    else:
                        print(f"    ✅ No issues found")
                else:
                    print(f"    ❌ Failed to parse")
                    
            except Exception as e:
                print(f"    ⚠️  Error: {str(e)}")
    
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
    
    print(f"\n✅ DART SUPPORT DEMONSTRATION COMPLETED!")
    print("🎯 Key Features Demonstrated:")
    print("  • Dart file parsing and AST generation")
    print("  • Static analysis with Dart-specific rules")
    print("  • Flutter widget detection capabilities")
    print("  • Comprehensive error handling")


if __name__ == "__main__":
    demo_dart_support() 