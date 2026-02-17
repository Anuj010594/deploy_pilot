import os
import json
import glob
from typing import List, Dict, Tuple, Optional
from pathlib import Path

from ..models.response_models import (
    DetectionResult, LanguageType, BuildTool, MultiDetectionResult
)
from .rules import DetectionRules

class ProjectDetector:
    """Core detection engine for project platforms"""
    
    def __init__(self):
        self.rules = DetectionRules()
    
    def scan_project(self, project_path: str, max_depth: int = 3) -> MultiDetectionResult:
        """Main entry point for project scanning"""
        detected_files = self._scan_directory(project_path, max_depth)
        detections = self._analyze_files(detected_files, project_path)
        
        if not detections:
            detections = [self._create_unknown_result()]
        
        # Sort by confidence score
        detections.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return MultiDetectionResult(
            detections=detections,
            primary=detections[0]
        )
    
    def _scan_directory(self, path: str, max_depth: int) -> List[str]:
        """Recursively scan directory for relevant files"""
        detected_files = []
        
        for root, dirs, files in os.walk(path):
            # Calculate current depth
            depth = root[len(path):].count(os.sep)
            if depth >= max_depth:
                dirs.clear()
                continue
            
            # Filter ignored directories
            dirs[:] = [d for d in dirs if d not in self.rules.IGNORED_DIRS]
            
            # Add relevant files
            for file in files:
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, path)
                detected_files.append(relative_path)
        
        return detected_files
    
    def _analyze_files(self, files: List[str], project_path: str) -> List[DetectionResult]:
        """Analyze detected files to determine platforms"""
        results = []
        
        # Check each platform
        for platform, platform_data in self.rules.PLATFORM_FILES.items():
            detection = self._detect_platform(platform, files, project_path)
            if detection.confidence_score > 0:
                results.append(detection)
        
        return results
    
    def _detect_platform(self, platform: str, files: List[str], project_path: str) -> DetectionResult:
        """Detect specific platform from file list"""
        platform_data = self.rules.PLATFORM_FILES[platform]
        score = 0.0
        detected_files = []
        framework = None
        build_tool = None
        
        # Check primary files
        for pattern in platform_data["primary"]:
            matches = self._find_pattern_matches(pattern, files)
            if matches:
                score += self.rules.SCORE_WEIGHTS["primary_file"]
                detected_files.extend(matches)
                
                # Determine build tool from primary files
                if platform == "java":
                    if "pom.xml" in matches:
                        build_tool = BuildTool.MAVEN
                    elif any("gradle" in m for m in matches):
                        build_tool = BuildTool.GRADLE
                elif platform == "nodejs":
                    build_tool = self._detect_nodejs_build_tool(files, project_path)
        
        # Check secondary files
        for pattern in platform_data["secondary"]:
            matches = self._find_pattern_matches(pattern, files)
            if matches:
                score += self.rules.SCORE_WEIGHTS["secondary_file"]
                detected_files.extend(matches)
        
        # Detect framework
        framework = self._detect_framework(platform, files, project_path)
        if framework:
            score += self.rules.SCORE_WEIGHTS["framework_file"]
        
        # Determine language and build requirements
        language, build_required = self._get_language_info(platform)
        
        # Get build/install commands
        build_command, install_command = self._get_commands(platform, build_tool)
        
        return DetectionResult(
            primary_language=language,
            framework=framework,
            build_tool=build_tool,
            build_required=build_required,
            build_command=build_command,
            install_command=install_command,
            confidence_score=min(score, 1.0),
            detected_files=list(set(detected_files))
        )
    
    def _find_pattern_matches(self, pattern: str, files: List[str]) -> List[str]:
        """Find files matching a pattern"""
        matches = []
        
        if pattern.startswith("*"):
            # Glob pattern
            matches = [f for f in files if f.endswith(pattern[1:])]
        elif "/" in pattern:
            # Directory pattern
            matches = [f for f in files if pattern in f]
        else:
            # Exact filename
            matches = [f for f in files if os.path.basename(f) == pattern]
        
        return matches
    
    def _detect_framework(self, platform: str, files: List[str], project_path: str) -> Optional[str]:
        """Detect framework for a given platform"""
        framework_indicators = self.rules.PLATFORM_FILES[platform]["framework_indicators"]
        
        for framework_name, indicators in framework_indicators.items():
            for indicator in indicators:
                if platform == "nodejs":
                    # Check package.json content for Node.js
                    if self._check_package_json_dependency(project_path, indicator):
                        return framework_name
                elif any(indicator in f for f in files):
                    return framework_name
        
        return None
    
    def _check_package_json_dependency(self, project_path: str, dependency: str) -> bool:
        """Check if a dependency exists in package.json"""
        package_json_path = os.path.join(project_path, "package.json")
        
        if not os.path.exists(package_json_path):
            return False
        
        try:
            with open(package_json_path, 'r') as f:
                package_data = json.load(f)
                
            deps = {}
            deps.update(package_data.get("dependencies", {}))
            deps.update(package_data.get("devDependencies", {}))
            
            return dependency in deps
        except:
            return False
    
    def _detect_nodejs_build_tool(self, files: List[str], project_path: str) -> Optional[BuildTool]:
        """Detect Node.js build tool based on lock files"""
        if any("pnpm-lock.yaml" in f for f in files):
            return BuildTool.PNPM
        elif any("yarn.lock" in f for f in files):
            return BuildTool.YARN
        elif any("package-lock.json" in f for f in files):
            return BuildTool.NPM
        return BuildTool.NPM  # Default
    
    def _get_language_info(self, platform: str) -> Tuple[LanguageType, bool]:
        """Get language type and build requirement"""
        mapping = {
            "java": (LanguageType.JAVA, True),
            "nodejs": (LanguageType.NODEJS, True),
            "python": (LanguageType.PYTHON, False),
            "dotnet": (LanguageType.DOTNET, True),
            "go": (LanguageType.GO, True)
        }
        return mapping.get(platform, (LanguageType.UNKNOWN, False))
    
    def _get_commands(self, platform: str, build_tool: Optional[BuildTool]) -> Tuple[Optional[str], Optional[str]]:
        """Get build and install commands"""
        build_commands = self.rules.BUILD_COMMANDS.get(platform, {})
        
        if platform == "python":
            return None, "pip install -r requirements.txt"
        
        build_command = None
        if build_tool:
            build_command = build_commands.get(build_tool.value)
        
        return build_command, None
    
    def _create_unknown_result(self) -> DetectionResult:
        """Create result for unknown/undetected projects"""
        return DetectionResult(
            primary_language=LanguageType.UNKNOWN,
            confidence_score=0.0,
            detected_files=[]
        )
