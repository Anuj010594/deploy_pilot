import unittest
import tempfile
import os
import json
from pathlib import Path

from app.services.detector import ProjectDetector
from app.models.response_models import LanguageType

class TestProjectDetector(unittest.TestCase):
    
    def setUp(self):
        self.detector = ProjectDetector()
    
    def test_java_maven_detection(self):
        """Test Java Maven project detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create Maven project structure
            os.makedirs(os.path.join(temp_dir, "src", "main", "java"))
            
            # Create pom.xml
            with open(os.path.join(temp_dir, "pom.xml"), "w") as f:
                f.write("<project></project>")
            
            result = self.detector.scan_project(temp_dir)
            
            self.assertEqual(result.primary.primary_language, LanguageType.JAVA)
            self.assertEqual(result.primary.build_tool.value, "Maven")
            self.assertTrue(result.primary.build_required)
            self.assertGreater(result.primary.confidence_score, 0.5)
    
    def test_nodejs_detection(self):
        """Test Node.js project detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create package.json
            package_data = {
                "name": "test-app",
                "dependencies": {
                    "react": "^18.0.0"
                }
            }
            
            with open(os.path.join(temp_dir, "package.json"), "w") as f:
                json.dump(package_data, f)
            
            # Create package-lock.json
            with open(os.path.join(temp_dir, "package-lock.json"), "w") as f:
                f.write("{}")
            
            result = self.detector.scan_project(temp_dir)
            
            self.assertEqual(result.primary.primary_language, LanguageType.NODEJS)
            self.assertEqual(result.primary.build_tool.value, "npm")
            self.assertEqual(result.primary.framework, "React")
    
    def test_python_detection(self):
        """Test Python project detection"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create requirements.txt
            with open(os.path.join(temp_dir, "requirements.txt"), "w") as f:
                f.write("flask==2.0.0\n")
            
            # Create app.py
            with open(os.path.join(temp_dir, "app.py"), "w") as f:
                f.write("from flask import Flask\n")
            
            result = self.detector.scan_project(temp_dir)
            
            self.assertEqual(result.primary.primary_language, LanguageType.PYTHON)
            self.assertFalse(result.primary.build_required)
            self.assertEqual(result.primary.framework, "Flask")
    
    def test_unknown_project(self):
        """Test unknown project type"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some random files
            with open(os.path.join(temp_dir, "random.txt"), "w") as f:
                f.write("random content")
            
            result = self.detector.scan_project(temp_dir)
            
            self.assertEqual(result.primary.primary_language, LanguageType.UNKNOWN)
            self.assertEqual(result.primary.confidence_score, 0.0)

if __name__ == "__main__":
    unittest.main()
