"""
Suggestion Engine

Generates intelligent suggestions for corrective actions based on
validation results and missing files.
"""

from typing import List, Dict, Optional
from models.request_models import DetectionResult, LanguageType
from models.response_models import MissingFile, Suggestion, Severity


class SuggestionEngine:
    """Engine for generating corrective action suggestions"""
    
    def __init__(self):
        """Initialize suggestion engine with platform-specific suggestion templates"""
        self.suggestion_templates = self._initialize_suggestion_templates()
    
    def _initialize_suggestion_templates(self) -> Dict:
        """Define suggestion templates for each platform and file type"""
        return {
            LanguageType.JAVA: {
                "build_config": [
                    {
                        "action": "Generate Maven pom.xml",
                        "description": "Create a minimal Maven configuration file with standard Java project structure",
                        "automated": True,
                        "priority": 1
                    },
                    {
                        "action": "Generate Gradle build.gradle",
                        "description": "Create a Gradle build configuration file (modern alternative to Maven)",
                        "automated": True,
                        "priority": 2
                    },
                    {
                        "action": "Upload existing build file",
                        "description": "Upload your existing pom.xml or build.gradle file",
                        "automated": False,
                        "priority": 3
                    }
                ],
                "source_directory": [
                    {
                        "action": "Create standard Maven directory structure",
                        "description": "Create src/main/java and src/test/java directories",
                        "automated": True,
                        "priority": 1
                    }
                ]
            },
            LanguageType.NODEJS: {
                "package_config": [
                    {
                        "action": "Generate package.json",
                        "description": "Create a package.json file with detected dependencies and build scripts",
                        "automated": True,
                        "priority": 1
                    },
                    {
                        "action": "Initialize with npm init",
                        "description": "Manually initialize package.json using npm init command",
                        "automated": False,
                        "priority": 2
                    }
                ],
                "build_script": [
                    {
                        "action": "Add build script to package.json",
                        "description": "Add framework-specific build script to package.json",
                        "automated": True,
                        "priority": 1
                    }
                ]
            },
            LanguageType.PYTHON: {
                "dependency_config": [
                    {
                        "action": "Generate requirements.txt",
                        "description": "Create a requirements.txt file for pip-based dependency management",
                        "automated": True,
                        "priority": 1
                    },
                    {
                        "action": "Generate pyproject.toml",
                        "description": "Create a modern pyproject.toml file for Poetry or pip (PEP 518)",
                        "automated": True,
                        "priority": 2
                    },
                    {
                        "action": "Generate setup.py",
                        "description": "Create a setup.py file for traditional Python package distribution",
                        "automated": True,
                        "priority": 3
                    }
                ],
                "package_config": [
                    {
                        "action": "Generate setup.cfg",
                        "description": "Create setup configuration for package metadata",
                        "automated": True,
                        "priority": 2
                    }
                ]
            },
            LanguageType.DOTNET: {
                "project_file": [
                    {
                        "action": "Generate .csproj file",
                        "description": "Create a C# project file with selected framework version and project type",
                        "automated": True,
                        "priority": 1
                    },
                    {
                        "action": "Initialize with dotnet new",
                        "description": "Manually create project using dotnet CLI",
                        "automated": False,
                        "priority": 2
                    }
                ],
                "solution_file": [
                    {
                        "action": "Generate .sln file",
                        "description": "Create a solution file to organize multiple projects",
                        "automated": True,
                        "priority": 2
                    }
                ]
            },
            LanguageType.GO: {
                "module_config": [
                    {
                        "action": "Generate go.mod",
                        "description": "Create a Go module file with specified module name and Go version",
                        "automated": True,
                        "priority": 1
                    },
                    {
                        "action": "Initialize with go mod init",
                        "description": "Manually initialize Go module using go mod init command",
                        "automated": False,
                        "priority": 2
                    }
                ]
            },
            LanguageType.RUST: {
                "package_config": [
                    {
                        "action": "Generate Cargo.toml",
                        "description": "Create a Rust package manifest file with dependencies",
                        "automated": True,
                        "priority": 1
                    },
                    {
                        "action": "Initialize with cargo init",
                        "description": "Manually initialize Rust project using cargo init command",
                        "automated": False,
                        "priority": 2
                    }
                ]
            },
            LanguageType.RUBY: {
                "dependency_config": [
                    {
                        "action": "Generate Gemfile",
                        "description": "Create a Ruby dependencies file with gem specifications",
                        "automated": True,
                        "priority": 1
                    },
                    {
                        "action": "Initialize with bundle init",
                        "description": "Manually initialize Gemfile using bundle init command",
                        "automated": False,
                        "priority": 2
                    }
                ]
            },
            LanguageType.PHP: {
                "package_config": [
                    {
                        "action": "Generate composer.json",
                        "description": "Create a PHP package configuration file with dependencies",
                        "automated": True,
                        "priority": 1
                    },
                    {
                        "action": "Initialize with composer init",
                        "description": "Manually initialize composer.json using composer init command",
                        "automated": False,
                        "priority": 2
                    }
                ]
            }
        }
    
    def generate_suggestions(
        self,
        missing_files: List[MissingFile],
        detection_result: DetectionResult
    ) -> List[Suggestion]:
        """
        Generate suggestions based on missing files
        
        Args:
            missing_files: List of missing files from validation
            detection_result: Original detection result
        
        Returns:
            List of suggestions ordered by priority
        """
        suggestions = []
        language = self._normalize_language(detection_result.primary_language)
        
        if not language or language not in self.suggestion_templates:
            # Generic suggestions for unsupported platforms
            return self._generate_generic_suggestions(missing_files)
        
        templates = self.suggestion_templates[language]
        
        # Generate suggestions for each missing file
        for missing_file in missing_files:
            if missing_file.severity == Severity.CRITICAL:
                # Critical files get higher priority suggestions
                file_suggestions = self._get_suggestions_for_file_type(
                    templates,
                    missing_file.file_type,
                    missing_file.file_name
                )
                suggestions.extend(file_suggestions)
        
        # Add general suggestions
        suggestions.extend(self._generate_general_suggestions(language, detection_result))
        
        # Sort by priority
        suggestions.sort(key=lambda s: s.priority)
        
        # Remove duplicates
        unique_suggestions = self._deduplicate_suggestions(suggestions)
        
        return unique_suggestions
    
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
    
    def _get_suggestions_for_file_type(
        self,
        templates: Dict,
        file_type: str,
        file_name: str
    ) -> List[Suggestion]:
        """Get suggestions for a specific file type"""
        suggestions = []
        
        if file_type in templates:
            for template in templates[file_type]:
                suggestions.append(Suggestion(
                    action=template["action"],
                    description=template["description"],
                    automated=template["automated"],
                    file_type=file_type,
                    priority=template["priority"]
                ))
        
        return suggestions
    
    def _generate_general_suggestions(
        self,
        language: LanguageType,
        detection_result: DetectionResult
    ) -> List[Suggestion]:
        """Generate general platform-specific suggestions"""
        suggestions = []
        
        # Version configuration suggestion
        suggestions.append(Suggestion(
            action=f"Configure {language.value} version",
            description=f"Select the appropriate {language.value} runtime version for your project",
            automated=True,
            priority=2
        ))
        
        # Dependency management suggestion
        if language == LanguageType.NODEJS and detection_result.framework:
            suggestions.append(Suggestion(
                action=f"Configure {detection_result.framework} dependencies",
                description=f"Set up dependencies specific to {detection_result.framework}",
                automated=True,
                priority=2
            ))
        
        return suggestions
    
    def _generate_generic_suggestions(self, missing_files: List[MissingFile]) -> List[Suggestion]:
        """Generate generic suggestions for unsupported platforms"""
        suggestions = []
        
        for missing_file in missing_files:
            if missing_file.can_generate:
                suggestions.append(Suggestion(
                    action=f"Generate {missing_file.file_name}",
                    description=f"Auto-generate {missing_file.file_name}",
                    automated=True,
                    file_type=missing_file.file_type,
                    priority=1
                ))
            else:
                suggestions.append(Suggestion(
                    action=f"Manually create {missing_file.file_name}",
                    description=f"Create {missing_file.file_name} manually or upload existing file",
                    automated=False,
                    file_type=missing_file.file_type,
                    priority=2
                ))
        
        return suggestions
    
    def _deduplicate_suggestions(self, suggestions: List[Suggestion]) -> List[Suggestion]:
        """Remove duplicate suggestions based on action"""
        seen = set()
        unique = []
        
        for suggestion in suggestions:
            if suggestion.action not in seen:
                seen.add(suggestion.action)
                unique.append(suggestion)
        
        return unique
    
    def generate_dockerfile_suggestions(
        self,
        platform: LanguageType,
        dockerfile_exists: bool
    ) -> List[Suggestion]:
        """
        Generate Dockerfile-specific suggestions
        
        Args:
            platform: Target platform
            dockerfile_exists: Whether Dockerfile already exists
        
        Returns:
            List of Dockerfile-related suggestions
        """
        suggestions = []
        
        if dockerfile_exists:
            suggestions.append(Suggestion(
                action="Use existing Dockerfile",
                description="Use the Dockerfile found in your project",
                automated=True,
                file_type="dockerfile",
                priority=1
            ))
            suggestions.append(Suggestion(
                action="Regenerate Dockerfile",
                description="Replace existing Dockerfile with an optimized version",
                automated=True,
                file_type="dockerfile",
                priority=2
            ))
        else:
            suggestions.append(Suggestion(
                action=f"Generate {platform.value} Dockerfile",
                description=f"Auto-generate an optimized Dockerfile for {platform.value}",
                automated=True,
                file_type="dockerfile",
                priority=1
            ))
            suggestions.append(Suggestion(
                action="Upload custom Dockerfile",
                description="Upload your own Dockerfile",
                automated=False,
                file_type="dockerfile",
                priority=2
            ))
        
        # Add multi-stage build suggestion for supported platforms
        if platform in [LanguageType.JAVA, LanguageType.NODEJS, LanguageType.GO, LanguageType.RUST, LanguageType.RUBY, LanguageType.PHP]:
            suggestions.append(Suggestion(
                action="Generate multi-stage Dockerfile",
                description="Create an optimized multi-stage Dockerfile for smaller image size",
                automated=True,
                file_type="dockerfile",
                priority=2
            ))
        
        return suggestions
    
    def generate_version_suggestions(
        self,
        platform: LanguageType,
        current_version: Optional[str] = None
    ) -> List[Suggestion]:
        """
        Generate version-related suggestions
        
        Args:
            platform: Target platform
            current_version: Currently detected version if any
        
        Returns:
            List of version-related suggestions
        """
        suggestions = []
        
        version_names = {
            LanguageType.JAVA: "Java",
            LanguageType.NODEJS: "Node.js",
            LanguageType.PYTHON: "Python",
            LanguageType.DOTNET: ".NET",
            LanguageType.GO: "Go",
            LanguageType.RUST: "Rust",
            LanguageType.RUBY: "Ruby",
            LanguageType.PHP: "PHP"
        }
        
        version_name = version_names.get(platform, str(platform))
        
        if current_version:
            suggestions.append(Suggestion(
                action=f"Keep detected version ({current_version})",
                description=f"Use the detected {version_name} version {current_version}",
                automated=True,
                priority=1
            ))
        
        suggestions.append(Suggestion(
            action=f"Select {version_name} version",
            description=f"Choose a specific {version_name} version from available options",
            automated=True,
            priority=1 if not current_version else 2
        ))
        
        suggestions.append(Suggestion(
            action=f"Use latest LTS version",
            description=f"Automatically use the latest Long-Term Support version of {version_name}",
            automated=True,
            priority=2
        ))
        
        return suggestions
