import os
import json
import glob
from typing import List, Dict, Tuple, Optional, Set
from pathlib import Path

from models.response_models import (
    DetectionResult, LanguageType, BuildTool, MultiDetectionResult, ConfidenceLevel
)
from services.rules import DetectionRules

class ProjectDetector:
    """Core detection engine for project platforms"""
    
    def __init__(self, min_confidence: float = 0.45):
        """
        Initialize detector with minimum confidence threshold.
        
        Args:
            min_confidence: Minimum confidence score to consider valid (default: 0.45)
        """
        self.rules = DetectionRules()
        self.min_confidence = max(0.0, min(1.0, min_confidence))
    
    def scan_project(self, project_path: str, max_depth: int = 3) -> MultiDetectionResult:
        """
        Main entry point for project scanning.
        
        Args:
            project_path: Root path of the project to scan
            max_depth: Maximum directory depth to scan (default: 3)
            
        Returns:
            MultiDetectionResult with all detections and primary detection
        """
        detected_files = self._scan_directory(project_path, max_depth)
        detections = self._analyze_files(detected_files, project_path)
        
        # Filter by minimum confidence threshold
        valid_detections = [d for d in detections if d.confidence_score >= self.min_confidence]
        
        if not valid_detections:
            # If no valid detections, include all but mark as unreliable
            if detections:
                valid_detections = detections
            else:
                valid_detections = [self._create_unknown_result()]
        
        # Sort by confidence score
        valid_detections.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return MultiDetectionResult(
            detections=valid_detections,
            primary=valid_detections[0],
            min_confidence_threshold=self.min_confidence
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
    
    def _read_file_content(self, file_path: str, max_bytes: int = 50000) -> str:
        """
        Safely read file content for pattern matching.
        
        Args:
            file_path: Path to the file
            max_bytes: Maximum bytes to read (default 50KB)
            
        Returns:
            File content as string, or empty string on error
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read(max_bytes)
        except Exception:
            return ""
    
    def _check_content_patterns(
        self,
        platform: str,
        project_path: str,
        files: List[str]
    ) -> int:
        """
        Check file contents for platform-specific patterns.
        
        Args:
            platform: Platform to check
            project_path: Root path of project
            files: List of found files
            
        Returns:
            Number of content pattern matches
        """
        platform_data = self.rules.PLATFORM_FILES.get(platform, {})
        content_patterns = platform_data.get("content_patterns", {})
        
        if not content_patterns:
            return 0
        
        matches = 0
        checked_files = set()
        
        for file_pattern, patterns in content_patterns.items():
            # Find files matching the pattern
            for file_rel_path in files:
                file_name = os.path.basename(file_rel_path)
                
                # Avoid checking the same file multiple times
                if file_rel_path in checked_files:
                    continue
                
                # Check if file matches the pattern (support wildcards)
                pattern_match = False
                if file_pattern.startswith("*"):
                    pattern_match = file_name.endswith(file_pattern[1:])
                else:
                    pattern_match = (file_pattern == file_name)
                
                if pattern_match:
                    checked_files.add(file_rel_path)
                    file_path = os.path.join(project_path, file_rel_path)
                    
                    if not os.path.isfile(file_path):
                        continue
                    
                    content = self._read_file_content(file_path)
                    
                    # Check for patterns in content
                    for pattern in patterns:
                        if pattern.lower() in content.lower():
                            matches += 1
                            break  # Count once per file
        
        return matches
    
    def _check_structure_indicators(
        self,
        platform: str,
        project_path: str
    ) -> int:
        """
        Check for platform-specific directory structures.
        
        Args:
            platform: Platform to check
            project_path: Root path of project
            
        Returns:
            Number of structure indicators found
        """
        platform_data = self.rules.PLATFORM_FILES.get(platform, {})
        structure_indicators = platform_data.get("structure_indicators", [])
        
        if not structure_indicators:
            return 0
        
        found = 0
        for indicator in structure_indicators:
            indicator_path = os.path.join(project_path, indicator)
            if os.path.exists(indicator_path):
                found += 1
        
        return found
    
    def _check_config_files(
        self,
        platform: str,
        files: List[str]
    ) -> int:
        """
        Check for platform-specific configuration files.
        
        Args:
            platform: Platform to check
            files: List of found files
            
        Returns:
            Number of config files found
        """
        platform_data = self.rules.PLATFORM_FILES.get(platform, {})
        config_files = platform_data.get("config_files", [])
        
        if not config_files:
            return 0
        
        found = 0
        for config_file in config_files:
            if any(config_file in f for f in files):
                found += 1
        
        return found
    
    def _detect_platform(self, platform: str, files: List[str], project_path: str) -> DetectionResult:
        """Detect specific platform from file list with enhanced scoring"""
        platform_data = self.rules.PLATFORM_FILES[platform]
        score = 0.0
        detected_files = []
        framework = None
        build_tool = None
        
        # Check primary files
        primary_found = 0
        for pattern in platform_data["primary"]:
            matches = self._find_pattern_matches(pattern, files)
            if matches:
                primary_found += 1
                detected_files.extend(matches)
                
                # Determine build tool from primary files
                if platform == "java":
                    if "pom.xml" in matches:
                        build_tool = BuildTool.MAVEN
                    elif any("gradle" in m for m in matches):
                        build_tool = BuildTool.GRADLE
                elif platform == "nodejs":
                    build_tool = self._detect_nodejs_build_tool(files, project_path)
                elif platform == "dotnet":
                    build_tool = BuildTool.DOTNET
                elif platform == "go":
                    build_tool = BuildTool.GO
                elif platform == "python":
                    build_tool = BuildTool.PIP
                elif platform == "rust":
                    build_tool = BuildTool.CARGO
                elif platform == "php":
                    build_tool = BuildTool.COMPOSER
                elif platform == "ruby":
                    build_tool = BuildTool.BUNDLE
        
        # Award points for primary files (cap at weight value)
        if primary_found > 0:
            score += self.rules.SCORE_WEIGHTS["primary_file"]
        
        # Check secondary files
        secondary_found = 0
        for pattern in platform_data["secondary"]:
            matches = self._find_pattern_matches(pattern, files)
            if matches:
                secondary_found += 1
                detected_files.extend(matches)
        
        # Award points for secondary files (scaled by number found, capped)
        if secondary_found > 0:
            secondary_score = min(
                secondary_found * (self.rules.SCORE_WEIGHTS["secondary_file"] / 2),
                self.rules.SCORE_WEIGHTS["secondary_file"]
            )
            score += secondary_score
        
        # Check structure indicators (NEW)
        structure_found = self._check_structure_indicators(platform, project_path)
        if structure_found > 0:
            structure_score = min(
                structure_found * (self.rules.SCORE_WEIGHTS["structure_indicator"] / 2),
                self.rules.SCORE_WEIGHTS["structure_indicator"]
            )
            score += structure_score
        
        # Check config files (NEW)
        config_found = self._check_config_files(platform, files)
        if config_found > 0:
            config_score = min(
                config_found * (self.rules.SCORE_WEIGHTS["config_file"] / 2),
                self.rules.SCORE_WEIGHTS["config_file"]
            )
            score += config_score
        
        # Detect framework (enhanced)
        framework = self._detect_framework(platform, files, project_path)
        if framework:
            score += self.rules.SCORE_WEIGHTS["framework_match"]
        
        # Check content patterns (NEW)
        content_matches = self._check_content_patterns(platform, project_path, files)
        if content_matches > 0:
            content_score = min(
                content_matches * (self.rules.SCORE_WEIGHTS["content_match"] / 2),
                self.rules.SCORE_WEIGHTS["content_match"]
            )
            score += content_score
        
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
                elif platform == "dotnet":
                    # Check .csproj file content for .NET
                    if self._check_dotnet_project_file(files, project_path, indicator):
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
    
    def _check_dotnet_project_file(self, files: List[str], project_path: str, indicator: str) -> bool:
        """Check if an indicator exists in .csproj or .sln files"""
        # First check if it's a filename (like Startup.cs)
        if any(indicator in f for f in files):
            return True
        
        # Then check content of .csproj files
        csproj_files = [f for f in files if f.endswith('.csproj')]
        
        for csproj_file in csproj_files:
            csproj_path = os.path.join(project_path, csproj_file)
            try:
                with open(csproj_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    if indicator in content:
                        return True
            except:
                continue
        
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
            "go": (LanguageType.GO, True),
            "rust": (LanguageType.RUST, True),
            "php": (LanguageType.PHP, False),
            "ruby": (LanguageType.RUBY, False)
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
            # If not found by build_tool value, check if there's a single default command
            if not build_command and len(build_commands) == 1:
                build_command = list(build_commands.values())[0]
        
        return build_command, None
    
    def _create_unknown_result(self) -> DetectionResult:
        """Create result for unknown/undetected projects"""
        return DetectionResult(
            primary_language=LanguageType.UNKNOWN,
            confidence_score=0.0,
            detected_files=[]
        )
