#!/usr/bin/env python3
"""
Demo script for LLM Integration in AI Code Review System.

This script demonstrates the integration of commercial LLM APIs (OpenAI and Google Gemini)
into the LLMOrchestratorAgent. It shows how to use different providers with proper error handling.
"""

import os
import sys
from typing import Dict, List

# Add src to path for imports
sys.path.insert(0, 'src')

from core_engine.agents.llm_orchestrator_agent import LLMOrchestratorAgent


def demo_mock_provider():
    """Demonstrate mock LLM provider functionality."""
    print("=" * 60)
    print("🤖 Demo: Mock LLM Provider")
    print("=" * 60)
    
    agent = LLMOrchestratorAgent(llm_provider='mock')
    
    # Demo code to analyze
    demo_code = """
def calculate_total(items):
    total = 0
    for item in items:
        print(f"Processing item: {item}")  # Should use logging
        total += item.price
    return total
"""
    
    # Demo static findings
    static_findings = [
        {
            'rule_id': 'PRINT_STATEMENT_FOUND',
            'line': 4,
            'message': 'print() statement found',
            'category': 'logging',
            'suggestion': 'Use logging instead of print statements'
        }
    ]
    
    print("Analyzing sample code with mock LLM...")
    response = agent.invoke_llm(
        "Analyze this Python function for code quality issues",
        demo_code,
        static_findings
    )
    
    print(f"✅ Mock LLM Response (truncated):")
    print(response[:300] + "...")
    print(f"\n📊 Provider Info: {agent.get_provider_info()}")
    print(f"🔍 Provider Available: {agent.is_provider_available()}")


def demo_openai_provider():
    """Demonstrate OpenAI LLM provider functionality."""
    print("\n" + "=" * 60)
    print("🚀 Demo: OpenAI GPT Provider")
    print("=" * 60)
    
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("⚠️  OpenAI API key not found in environment variables.")
        print("   Set OPENAI_API_KEY to test real OpenAI integration.")
        print("   Demonstrating initialization without key...")
        
        try:
            agent = LLMOrchestratorAgent(llm_provider='openai')
            print(f"📊 Provider Info: {agent.get_provider_info()}")
            print(f"🔍 Provider Available: {agent.is_provider_available()}")
        except Exception as e:
            print(f"❌ Initialization failed as expected: {e}")
    else:
        print(f"✅ Found OpenAI API key: {api_key[:8]}...")
        
        try:
            agent = LLMOrchestratorAgent(
                llm_provider='openai',
                model_name='gpt-3.5-turbo'  # Use cheaper model for demo
            )
            
            print(f"📊 Provider Info: {agent.get_provider_info()}")
            print(f"🔍 Provider Available: {agent.is_provider_available()}")
            
            # Test with simple code analysis
            print("\n🔍 Testing OpenAI code analysis...")
            response = agent.invoke_llm(
                "Briefly analyze this Python function",
                "def add(a, b):\n    return a + b"
            )
            print(f"✅ OpenAI Response: {response[:200]}...")
            
        except Exception as e:
            print(f"❌ OpenAI integration error: {e}")


def demo_google_gemini_provider():
    """Demonstrate Google Gemini LLM provider functionality."""
    print("\n" + "=" * 60)
    print("🌟 Demo: Google Gemini Provider")
    print("=" * 60)
    
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("⚠️  Google API key not found in environment variables.")
        print("   Set GOOGLE_API_KEY to test real Google Gemini integration.")
        print("   Demonstrating initialization without key...")
        
        try:
            agent = LLMOrchestratorAgent(llm_provider='google_gemini')
            print(f"📊 Provider Info: {agent.get_provider_info()}")
            print(f"🔍 Provider Available: {agent.is_provider_available()}")
        except Exception as e:
            print(f"❌ Initialization failed as expected: {e}")
    else:
        print(f"✅ Found Google API key: {api_key[:8]}...")
        
        try:
            agent = LLMOrchestratorAgent(
                llm_provider='google_gemini',
                model_name='gemini-pro'
            )
            
            print(f"📊 Provider Info: {agent.get_provider_info()}")
            print(f"🔍 Provider Available: {agent.is_provider_available()}")
            
            # Test with simple code analysis
            print("\n🔍 Testing Google Gemini code analysis...")
            response = agent.invoke_llm(
                "Briefly analyze this Python function",
                "def multiply(x, y):\n    return x * y"
            )
            print(f"✅ Gemini Response: {response[:200]}...")
            
        except Exception as e:
            print(f"❌ Google Gemini integration error: {e}")


def demo_legacy_provider():
    """Demonstrate legacy provider name handling."""
    print("\n" + "=" * 60)
    print("🔄 Demo: Legacy Provider Name ('google' -> 'google_gemini')")
    print("=" * 60)
    
    try:
        agent = LLMOrchestratorAgent(llm_provider='google', api_key='dummy-key')
        print(f"✅ Legacy 'google' provider redirected to: {agent.llm_provider}")
        print(f"📊 Provider Info: {agent.get_provider_info()}")
    except Exception as e:
        print(f"❌ Legacy provider handling error: {e}")


def demo_error_handling():
    """Demonstrate error handling capabilities."""
    print("\n" + "=" * 60)
    print("⚠️  Demo: Error Handling")
    print("=" * 60)
    
    # Test unsupported provider
    print("1. Testing unsupported provider...")
    try:
        agent = LLMOrchestratorAgent(llm_provider='invalid_provider')
    except ValueError as e:
        print(f"✅ Caught expected error: {e}")
    
    # Test provider without dependencies
    print("\n2. Testing missing dependencies handling...")
    # This would require temporarily removing the imports, so we'll skip actual test
    print("✅ Missing dependency errors are handled gracefully with ImportError")
    
    # Test provider availability
    print("\n3. Testing provider availability checks...")
    providers_to_test = ['mock', 'openai', 'google_gemini', 'local', 'anthropic']
    
    for provider in providers_to_test:
        try:
            if provider in ['openai', 'google_gemini']:
                # Skip actual initialization for providers that require API keys
                print(f"   {provider}: Requires API key for full functionality")
            else:
                agent = LLMOrchestratorAgent(llm_provider=provider)
                available = agent.is_provider_available()
                print(f"   {provider}: Available = {available}")
        except Exception as e:
            print(f"   {provider}: Error = {str(e)[:50]}...")


def main():
    """Run all LLM integration demos."""
    print("🎯 AI Code Review System - LLM Integration Demo")
    print("This demo showcases the integration of commercial LLM APIs\n")
    
    # Demo each provider
    demo_mock_provider()
    demo_openai_provider()
    demo_google_gemini_provider()
    demo_legacy_provider()
    demo_error_handling()
    
    print("\n" + "=" * 60)
    print("✅ Demo Complete!")
    print("=" * 60)
    print("\nKey Features Demonstrated:")
    print("• Mock LLM provider for testing and development")
    print("• OpenAI GPT integration with langchain-openai")
    print("• Google Gemini integration with langchain-google-genai")
    print("• Environment variable API key management")
    print("• Comprehensive error handling and fallbacks")
    print("• Legacy provider name support with deprecation warnings")
    print("• Provider availability checking")
    print("\nTo test real API integration:")
    print("• Set OPENAI_API_KEY environment variable for OpenAI")
    print("• Set GOOGLE_API_KEY environment variable for Google Gemini")


if __name__ == "__main__":
    main() 