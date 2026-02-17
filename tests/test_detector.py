import unittest
import tempfile
import os
import json
from pathlib import Path

from services.detector import ProjectDetector
from models.response_models import LanguageType, ConfidenceLevel

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
    
    def test_confidence_levels(self):
        """Test confidence level classification"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a complete Spring Boot project for high confidence
            os.makedirs(os.path.join(temp_dir, "src/main/java/com/example"), exist_ok=True)
            os.makedirs(os.path.join(temp_dir, "src/main/resources"), exist_ok=True)
            os.makedirs(os.path.join(temp_dir, "src/test/java"), exist_ok=True)
            
            # pom.xml with Spring Boot content
            with open(os.path.join(temp_dir, "pom.xml"), "w") as f:
                f.write("""<?xml version="1.0"?>
<project>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-web</artifactId>
</project>""")
            
            # application.properties
            with open(os.path.join(temp_dir, "src/main/resources/application.properties"), "w") as f:
                f.write("server.port=8080\n")
            
            # Main Java file with annotations
            with open(os.path.join(temp_dir, "src/main/java/com/example/App.java"), "w") as f:
                f.write("@SpringBootApplication\npublic class App {}")
            
            result = self.detector.scan_project(temp_dir)
            
            self.assertEqual(result.primary.primary_language, LanguageType.JAVA)
            self.assertGreaterEqual(result.primary.confidence_score, 0.65)
            self.assertIn(result.primary.confidence_level, [ConfidenceLevel.HIGH, ConfidenceLevel.VERY_HIGH])
    
    def test_min_confidence_threshold(self):
        """Test minimum confidence threshold filtering"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create minimal project
            with open(os.path.join(temp_dir, "package.json"), "w") as f:
                json.dump({"name": "test"}, f)
            
            # Test with high threshold
            detector_strict = ProjectDetector(min_confidence=0.80)
            result_strict = detector_strict.scan_project(temp_dir)
            
            # Should still return something (might be unknown if threshold not met)
            self.assertIsNotNone(result_strict.primary)
            
            # Test with low threshold
            detector_lenient = ProjectDetector(min_confidence=0.30)
            result_lenient = detector_lenient.scan_project(temp_dir)
            
            self.assertEqual(result_lenient.primary.primary_language, LanguageType.NODEJS)

if __name__ == "__main__":
    unittest.main()
