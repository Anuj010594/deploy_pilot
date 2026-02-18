"""
Platform Validation Service

Validates required build files for all supported platforms:
- Java (Maven, Gradle)
- Node.js (npm, yarn, pnpm)
- Python (pip, poetry)
- .NET (dotnet)
- Go (go modules)
"""

import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path

from models.request_models import DetectionResult, LanguageType
from models.response_models import (
    MissingFile, 
    Severity, 
    ValidationStatus,
    VersionOption
)


class ValidationService:
    """Service for validating project build files"""
    
    def __init__(self):
        """Initialize validation service with platform-specific rules"""
        self.validation_rules = self._initialize_validation_rules()
        self.version_options = self._initialize_version_options()
    
    def _initialize_validation_rules(self) -> Dict:
        """Define validation rules for each platform"""
        return {
            LanguageType.JAVA: {
                "required_files": [
                    {
                        "files": ["pom.xml", "build.gradle", "build.gradle.kts"],
                        "any_of": True,
                        "description": "Java build configuration file (Maven or Gradle)",
                        "severity": Severity.CRITICAL,
                        "can_generate": True,
                        "file_type": "build_config"
                    }
                ],
                "optional_files": [
                    {
                        "files": ["src/main/java"],
                        "description": "Java source directory",
                        "severity": Severity.WARNING,
                        "can_generate": False,
                        "file_type": "source_directory"
                    }
                ]
            },
            LanguageType.NODEJS: {
                "required_files": [
                    {
                        "files": ["package.json"],
                        "any_of": False,
                        "description": "Node.js package configuration",
                        "severity": Severity.CRITICAL,
                        "can_generate": True,
                        "file_type": "package_config"
                    }
                ],
                "optional_files": [
                    {
                        "files": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
                        "description": "Package lock file",
                        "severity": Severity.INFO,
                        "can_generate": False,
                        "file_type": "lock_file"
                    }
                ]
            },
            LanguageType.PYTHON: {
                "required_files": [
                    {
                        "files": ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"],
                        "any_of": True,
                        "description": "Python dependencies file",
                        "severity": Severity.CRITICAL,
                        "can_generate": True,
                        "file_type": "dependency_config"
                    }
                ],
                "optional_files": [
                    {
                        "files": ["setup.cfg", "setup.py"],
                        "description": "Python package configuration",
                        "severity": Severity.INFO,
                        "can_generate": False,
                        "file_type": "package_config"
                    }
                ]
            },
            LanguageType.DOTNET: {
                "required_files": [
                    {
                        "files": ["*.csproj", "*.fsproj", "*.vbproj"],
                        "any_of": True,
                        "description": ".NET project file",
                        "severity": Severity.CRITICAL,
                        "can_generate": True,
                        "file_type": "project_file",
                        "is_pattern": True
                    }
                ],
                "optional_files": [
                    {
                        "files": ["*.sln"],
                        "description": ".NET solution file",
                        "severity": Severity.INFO,
                        "can_generate": False,
                        "file_type": "solution_file",
                        "is_pattern": True
                    }
                ]
            },
            LanguageType.GO: {
                "required_files": [
                    {
                        "files": ["go.mod"],
                        "any_of": False,
                        "description": "Go module file",
                        "severity": Severity.CRITICAL,
                        "can_generate": True,
                        "file_type": "module_config"
                    }
                ],
                "optional_files": [
                    {
                        "files": ["go.sum"],
                        "description": "Go dependency checksums",
                        "severity": Severity.INFO,
                        "can_generate": False,
                        "file_type": "checksum_file"
                    }
                ]
            },
            LanguageType.RUST: {
                "required_files": [
                    {
                        "files": ["Cargo.toml"],
                        "any_of": False,
                        "description": "Rust package manifest file",
                        "severity": Severity.CRITICAL,
                        "can_generate": True,
                        "file_type": "package_config"
                    }
                ],
                "optional_files": [
                    {
                        "files": ["Cargo.lock"],
                        "description": "Rust dependency lock file",
                        "severity": Severity.INFO,
                        "can_generate": False,
                        "file_type": "lock_file"
                    }
                ]
            },
            LanguageType.RUBY: {
                "required_files": [
                    {
                        "files": ["Gemfile"],
                        "any_of": False,
                        "description": "Ruby dependencies file",
                        "severity": Severity.CRITICAL,
                        "can_generate": True,
                        "file_type": "dependency_config"
                    }
                ],
                "optional_files": [
                    {
                        "files": ["Gemfile.lock"],
                        "description": "Ruby dependency lock file",
                        "severity": Severity.INFO,
                        "can_generate": False,
                        "file_type": "lock_file"
                    }
                ]
            },
            LanguageType.PHP: {
                "required_files": [
                    {
                        "files": ["composer.json"],
                        "any_of": False,
                        "description": "PHP package configuration",
                        "severity": Severity.CRITICAL,
                        "can_generate": True,
                        "file_type": "package_config"
                    }
                ],
                "optional_files": [
                    {
                        "files": ["composer.lock"],
                        "description": "PHP dependency lock file",
                        "severity": Severity.INFO,
                        "can_generate": False,
                        "file_type": "lock_file"
                    }
                ]
            }
        }
    
    def _initialize_version_options(self) -> Dict:
        """Define available version options for each platform"""
        return {
            LanguageType.JAVA: {
                "java_version": [
                    VersionOption(version="21", recommended=True, description="Java 21 LTS (Latest)"),
                    VersionOption(version="17", recommended=True, description="Java 17 LTS"),
                    VersionOption(version="11", recommended=False, description="Java 11 LTS"),
                    VersionOption(version="8", recommended=False, description="Java 8 LTS (Legacy)")
                ],
                "packaging_type": [
                    VersionOption(version="jar", recommended=True, description="JAR - Standard Java Archive"),
                    VersionOption(version="war", recommended=False, description="WAR - Web Application Archive")
                ]
            },
            LanguageType.NODEJS: {
                "node_version": [
                    VersionOption(version="20", recommended=True, description="Node.js 20 LTS (Latest)"),
                    VersionOption(version="18", recommended=True, description="Node.js 18 LTS"),
                    VersionOption(version="16", recommended=False, description="Node.js 16 LTS"),
                    VersionOption(version="14", recommended=False, description="Node.js 14 LTS (Legacy)")
                ]
            },
            LanguageType.PYTHON: {
                "python_version": [
                    VersionOption(version="3.12", recommended=True, description="Python 3.12 (Latest)"),
                    VersionOption(version="3.11", recommended=True, description="Python 3.11"),
                    VersionOption(version="3.10", recommended=False, description="Python 3.10"),
                    VersionOption(version="3.9", recommended=False, description="Python 3.9"),
                    VersionOption(version="3.8", recommended=False, description="Python 3.8 (Legacy)")
                ]
            },
            LanguageType.DOTNET: {
                "dotnet_version": [
                    VersionOption(version="net8.0", recommended=True, description=".NET 8.0 (Latest LTS)"),
                    VersionOption(version="net7.0", recommended=False, description=".NET 7.0"),
                    VersionOption(version="net6.0", recommended=True, description=".NET 6.0 LTS")
                ],
                "project_type": [
                    VersionOption(version="WebAPI", recommended=True, description="ASP.NET Core Web API"),
                    VersionOption(version="Web", recommended=False, description="ASP.NET Core Web App"),
                    VersionOption(version="Console", recommended=False, description="Console Application")
                ]
            },
            LanguageType.GO: {
                "go_version": [
                    VersionOption(version="1.22", recommended=True, description="Go 1.22 (Latest)"),
                    VersionOption(version="1.21", recommended=True, description="Go 1.21"),
                    VersionOption(version="1.20", recommended=False, description="Go 1.20")
                ]
            },
            LanguageType.RUST: {
                "rust_version": [
                    VersionOption(version="1.76", recommended=True, description="Rust 1.76 (Latest Stable)"),
                    VersionOption(version="1.75", recommended=True, description="Rust 1.75"),
                    VersionOption(version="1.74", recommended=False, description="Rust 1.74")
                ]
            },
            LanguageType.RUBY: {
                "ruby_version": [
                    VersionOption(version="3.3", recommended=True, description="Ruby 3.3 (Latest)"),
                    VersionOption(version="3.2", recommended=True, description="Ruby 3.2"),
                    VersionOption(version="3.1", recommended=False, description="Ruby 3.1"),
                    VersionOption(version="2.7", recommended=False, description="Ruby 2.7 (Legacy)")
                ]
            },
            LanguageType.PHP: {
                "php_version": [
                    VersionOption(version="8.3", recommended=True, description="PHP 8.3 (Latest)"),
                    VersionOption(version="8.2", recommended=True, description="PHP 8.2"),
                    VersionOption(version="8.1", recommended=False, description="PHP 8.1"),
                    VersionOption(version="7.4", recommended=False, description="PHP 7.4 (Legacy)")
                ]
            }
        }
    
    def validate_project(
        self, 
        detection_result: DetectionResult, 
        project_path: str
    ) -> Tuple[ValidationStatus, List[MissingFile], Dict[str, List[VersionOption]]]:
        """
        Validate a project based on detection results
        
        Args:
            detection_result: Detection result from Detection Service
            project_path: Path to project directory (read-only)
        
        Returns:
            Tuple of (status, missing_files, version_options)
        """
        # Map string to enum if needed
        language = self._normalize_language(detection_result.primary_language)
        
        if language not in self.validation_rules:
            return (
                ValidationStatus.ERROR,
                [MissingFile(
                    file_name="N/A",
                    file_type="unknown",
                    severity=Severity.CRITICAL,
                    description=f"Unsupported platform: {detection_result.primary_language}",
                    can_generate=False
                )],
                {}
            )
        
        rules = self.validation_rules[language]
        missing_files = []
        
        # Validate required files
        for rule in rules.get("required_files", []):
            if not self._check_files_exist(project_path, rule):
                missing_files.extend(self._create_missing_file_entries(rule))
        
        # Check optional files (warnings only)
        for rule in rules.get("optional_files", []):
            if not self._check_files_exist(project_path, rule):
                missing_files.extend(self._create_missing_file_entries(rule))
        
        # Perform platform-specific validation
        additional_missing = self._platform_specific_validation(
            language, 
            detection_result, 
            project_path
        )
        missing_files.extend(additional_missing)
        
        # Determine status
        critical_missing = [f for f in missing_files if f.severity == Severity.CRITICAL]
        
        if critical_missing:
            status = ValidationStatus.MISSING_FILES
        elif missing_files:
            status = ValidationStatus.INCOMPLETE
        else:
            status = ValidationStatus.READY
        
        # Get version options for this platform
        version_options = self.version_options.get(language, {})
        
        return status, missing_files, version_options
    
    def _normalize_language(self, language: str) -> Optional[LanguageType]:
        """Normalize language string to LanguageType enum"""
        language_map = {
            "java": LanguageType.JAVA,
            "node.js": LanguageType.NODEJS,
            "nodejs": LanguageType.NODEJS,
            "python": LanguageType.PYTHON,
            ".net": LanguageType.DOTNET,
            "dotnet": LanguageType.DOTNET,
            "go": LanguageType.GO,
            "rust": LanguageType.RUST,
            "ruby": LanguageType.RUBY,
            "php": LanguageType.PHP
        }
        return language_map.get(language.lower())
    
    def _check_files_exist(self, project_path: str, rule: Dict) -> bool:
        """
        Check if files exist according to rule
        
        Args:
            project_path: Base project path
            rule: Validation rule with 'files' and optional 'any_of'
        
        Returns:
            True if validation passes, False otherwise
        """
        files = rule["files"]
        any_of = rule.get("any_of", False)
        is_pattern = rule.get("is_pattern", False)
        
        if is_pattern:
            # Handle glob patterns (e.g., *.csproj)
            return self._check_pattern_files(project_path, files)
        
        if any_of:
            # At least one file must exist
            return any(self._file_exists(project_path, f) for f in files)
        else:
            # All files must exist
            return all(self._file_exists(project_path, f) for f in files)
    
    def _file_exists(self, project_path: str, file_name: str) -> bool:
        """Check if a file exists (safely)"""
        try:
            # Prevent path traversal
            safe_path = Path(project_path) / file_name
            # Ensure the resolved path is within project_path
            if not str(safe_path.resolve()).startswith(str(Path(project_path).resolve())):
                return False
            return safe_path.exists()
        except Exception:
            return False
    
    def _check_pattern_files(self, project_path: str, patterns: List[str]) -> bool:
        """Check if files matching patterns exist"""
        try:
            base_path = Path(project_path)
            for pattern in patterns:
                matches = list(base_path.glob(pattern))
                if matches:
                    return True
            return False
        except Exception:
            return False
    
    def _create_missing_file_entries(self, rule: Dict) -> List[MissingFile]:
        """Create MissingFile entries from a rule"""
        files = rule["files"]
        any_of = rule.get("any_of", False)
        
        if any_of:
            # If any_of, create one entry for the group
            file_names = " OR ".join(files)
            return [MissingFile(
                file_name=file_names,
                file_type=rule["file_type"],
                severity=rule["severity"],
                description=rule["description"],
                can_generate=rule["can_generate"]
            )]
        else:
            # Create individual entries
            return [MissingFile(
                file_name=f,
                file_type=rule["file_type"],
                severity=rule["severity"],
                description=rule["description"],
                can_generate=rule["can_generate"]
            ) for f in files]
    
    def _platform_specific_validation(
        self,
        language: LanguageType,
        detection_result: DetectionResult,
        project_path: str
    ) -> List[MissingFile]:
        """Perform additional platform-specific validation"""
        missing = []
        
        if language == LanguageType.NODEJS:
            # Check if frontend framework detected but no build script
            missing.extend(self._validate_nodejs_build_script(detection_result, project_path))
        
        elif language == LanguageType.PYTHON:
            # Check for __init__.py in package structures
            missing.extend(self._validate_python_package_structure(project_path))
        
        elif language == LanguageType.JAVA:
            # Check for src directory structure
            missing.extend(self._validate_java_structure(project_path))
        
        return missing
    
    def _validate_nodejs_build_script(
        self, 
        detection_result: DetectionResult, 
        project_path: str
    ) -> List[MissingFile]:
        """Validate Node.js build scripts for frontend frameworks"""
        missing = []
        
        # Check if it's a frontend framework
        frontend_frameworks = ["React", "Vue", "Angular", "Svelte", "Next.js"]
        if detection_result.framework in frontend_frameworks:
            # Check if package.json has build script
            package_json_path = Path(project_path) / "package.json"
            if package_json_path.exists():
                try:
                    import json
                    with open(package_json_path, 'r') as f:
                        data = json.load(f)
                        scripts = data.get("scripts", {})
                        if "build" not in scripts:
                            missing.append(MissingFile(
                                file_name="build script in package.json",
                                file_type="build_script",
                                severity=Severity.WARNING,
                                description="Frontend framework detected but no build script found",
                                can_generate=True
                            ))
                except Exception:
                    pass
        
        return missing
    
    def _validate_python_package_structure(self, project_path: str) -> List[MissingFile]:
        """Validate Python package structure"""
        # This is a soft validation - not critical
        return []
    
    def _validate_java_structure(self, project_path: str) -> List[MissingFile]:
        """Validate Java source structure"""
        # This is a soft validation - not critical
        return []
    
    def get_available_actions(self, status: ValidationStatus) -> List[str]:
        """
        Determine available actions based on validation status
        
        Args:
            status: Validation status
        
        Returns:
            List of available action names
        """
        if status == ValidationStatus.READY:
            return ["build", "dockerize", "deploy"]
        elif status == ValidationStatus.INCOMPLETE:
            return ["generate_files", "dockerize"]
        elif status == ValidationStatus.MISSING_FILES:
            return ["generate_files", "manual_fix"]
        else:
            return []
