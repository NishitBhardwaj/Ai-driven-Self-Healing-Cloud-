"""
Unit tests for Coding/Code-Fixer Agent
Tests code generation and code fixing functionality
"""

import unittest
import sys
import os

# Add parent directory to path to import agent
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from agents.coding.agent import CodingAgent


class TestCodingAgent(unittest.TestCase):
    """Test cases for Coding Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = CodingAgent()
        self.agent.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.agent.stop()
    
    def test_agent_health_check(self):
        """Test that agent health check works"""
        self.assertEqual(self.agent.status, "running", "Agent should be running")
        self.assertIsNotNone(self.agent.agent_id, "Agent should have ID")
        self.assertIsNotNone(self.agent.name, "Agent should have name")
    
    def test_code_generation(self):
        """Test the code generation function"""
        prompt = "Create a function that calculates the factorial of a number"
        
        result = self.agent.generate_code(
            prompt=prompt,
            language="python"
        )
        
        self.assertIsNotNone(result, "Code generation should return result")
        self.assertIn("code", result, "Result should contain generated code")
        self.assertIn("explanation", result, "Result should contain explanation")
    
    def test_code_fixing(self):
        """Test code fixing functionality"""
        broken_code = """
def calculate_sum(a, b):
    return a + c  # Error: 'c' is not defined
"""
        
        result = self.agent.debug_code(
            stacktrace="NameError: name 'c' is not defined",
            file_path="test.py",
            file_content=broken_code,
            error_logs="Error at line 2"
        )
        
        self.assertIsNotNone(result, "Code fixing should return result")
        self.assertIn("fix_suggestions", result, "Result should contain fix suggestions")
        self.assertIn("patch", result, "Result should contain patch")
        
        # Verify fix is correct
        if "patch" in result:
            fixed_code = result["patch"]
            self.assertNotIn("c", fixed_code, "Fixed code should not contain undefined variable")
            self.assertIn("b", fixed_code, "Fixed code should use correct variable")
    
    def test_code_fixing_with_stacktrace(self):
        """Test code fixing with stacktrace"""
        stacktrace = """
Traceback (most recent call last):
  File "app.py", line 10, in <module>
    result = divide(10, 0)
  File "app.py", line 5, in divide
    return a / b
ZeroDivisionError: division by zero
"""
        
        result = self.agent.debug_code(
            stacktrace=stacktrace,
            file_path="app.py",
            error_logs="Division by zero error"
        )
        
        self.assertIsNotNone(result, "Code fixing should return result")
        self.assertIn("fix_suggestions", result, "Result should contain fix suggestions")
        
        # Verify fix addresses the issue
        if "fix_suggestions" in result:
            suggestions = result["fix_suggestions"]
            self.assertIsInstance(suggestions, list, "Fix suggestions should be a list")
    
    def test_code_generation_with_language(self):
        """Test code generation for different languages"""
        languages = ["python", "javascript", "go"]
        
        for lang in languages:
            with self.subTest(language=lang):
                result = self.agent.generate_code(
                    prompt="Create a hello world function",
                    language=lang
                )
                
                self.assertIsNotNone(result, f"Code generation should work for {lang}")
                self.assertIn("code", result, f"Result should contain code for {lang}")
    
    def test_explain_action(self):
        """Test explanation generation"""
        input_data = {
            "stacktrace": "IndexError: list index out of range",
            "file_path": "app.py"
        }
        
        output_data = {
            "fix_suggestions": ["Add bounds checking"],
            "patch": "if index < len(items): return items[index]"
        }
        
        explanation = self.agent.explain_action(input_data, output_data)
        
        self.assertIsNotNone(explanation, "Explanation should be generated")
        self.assertIn("message", explanation, "Explanation should have message")
        self.assertIn("explanation", explanation, "Explanation should have explanation text")
        
        # Verify explanation format
        if "explanation" in explanation:
            exp_text = explanation["explanation"]
            self.assertIn("The agent detected that", exp_text, "Should follow standard format")
    
    def test_error_handling(self):
        """Test error handling with invalid input"""
        # Test with empty stacktrace
        result = self.agent.debug_code(
            stacktrace="",
            file_path="test.py"
        )
        
        # Should handle gracefully
        self.assertIsNotNone(result, "Should return result even with empty input")
    
    def test_code_generation_error_handling(self):
        """Test code generation error handling"""
        # Test with empty prompt
        result = self.agent.generate_code(
            prompt="",
            language="python"
        )
        
        # Should handle gracefully
        self.assertIsNotNone(result, "Should return result even with empty prompt")


if __name__ == '__main__':
    unittest.main()

