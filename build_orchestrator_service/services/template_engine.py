"""
Template Engine Service

Renders Jinja2 templates for build files and Dockerfiles
with version-aware configuration.
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, Template, TemplateNotFound

from models.request_models import LanguageType, FileType, VersionConfig


class TemplateEngine:
    """Service for rendering templates using Jinja2"""
    
    def __init__(self):
        """Initialize template engine with Jinja2 environment"""
        # Get the templates directory
        templates_dir = Path(__file__).parent.parent / "templates"
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(templates_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True
        )
        
        # Template mappings
        self.template_map = self._initialize_template_map()
    
    def _initialize_template_map(self) -> Dict:
        """Map file types to template paths"""
        return {
            LanguageType.JAVA: {
                FileType.POM_XML: "java/pom.xml.j2",
                FileType.BUILD_GRADLE: "java/build.gradle.j2",
                FileType.DOCKERFILE: "java/Dockerfile.j2"
            },
            LanguageType.NODEJS: {
                FileType.PACKAGE_JSON: "nodejs/package.json.j2",
                FileType.DOCKERFILE: "nodejs/Dockerfile.j2"
            },
            LanguageType.PYTHON: {
                FileType.REQUIREMENTS_TXT: "python/requirements.txt.j2",
                FileType.PYPROJECT_TOML: "python/pyproject.toml.j2",
                FileType.DOCKERFILE: "python/Dockerfile.j2"
            },
            LanguageType.DOTNET: {
                FileType.CSPROJ: "dotnet/project.csproj.j2",
                FileType.DOCKERFILE: "dotnet/Dockerfile.j2"
            },
            LanguageType.GO: {
                FileType.GO_MOD: "go/go.mod.j2",
                FileType.DOCKERFILE: "go/Dockerfile.j2"
            },
            LanguageType.RUST: {
                FileType.CARGO_TOML: "rust/Cargo.toml.j2",
                FileType.DOCKERFILE: "rust/Dockerfile.j2"
            },
            LanguageType.RUBY: {
                FileType.GEMFILE: "ruby/Gemfile.j2",
                FileType.DOCKERFILE: "ruby/Dockerfile.j2"
            },
            LanguageType.PHP: {
                FileType.COMPOSER_JSON: "php/composer.json.j2",
                FileType.DOCKERFILE: "php/Dockerfile.j2"
            }
        }
    
    def render_template(
        self,
        platform: LanguageType,
        file_type: FileType,
        config: VersionConfig,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Render a template with provided configuration
        
        Args:
            platform: Target platform
            file_type: Type of file to generate
            config: Version and configuration settings
            context: Additional context for template rendering
        
        Returns:
            Rendered template content
        
        Raises:
            ValueError: If template not found or platform not supported
        """
        # Get template path
        if platform not in self.template_map:
            raise ValueError(f"Unsupported platform: {platform}")
        
        if file_type not in self.template_map[platform]:
            raise ValueError(f"Template not found for {file_type} on {platform}")
        
        template_path = self.template_map[platform][file_type]
        
        # Prepare rendering context
        render_context = self._prepare_context(platform, file_type, config, context)
        
        # Load and render template
        try:
            template = self.env.get_template(template_path)
            return template.render(**render_context)
        except TemplateNotFound:
            raise ValueError(f"Template file not found: {template_path}")
        except Exception as e:
            raise ValueError(f"Error rendering template: {str(e)}")
    
    def _prepare_context(
        self,
        platform: LanguageType,
        file_type: FileType,
        config: VersionConfig,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Prepare context for template rendering
        
        Args:
            platform: Target platform
            file_type: Type of file to generate
            config: Version configuration
            context: Additional context
        
        Returns:
            Complete context dictionary for rendering
        """
        # Start with base context
        render_context = context.copy() if context else {}
        
        # Add platform-specific context
        if platform == LanguageType.JAVA:
            render_context.update(self._prepare_java_context(config, context))
        elif platform == LanguageType.NODEJS:
            render_context.update(self._prepare_nodejs_context(config, context))
        elif platform == LanguageType.PYTHON:
            render_context.update(self._prepare_python_context(config, context))
        elif platform == LanguageType.DOTNET:
            render_context.update(self._prepare_dotnet_context(config, context))
        elif platform == LanguageType.GO:
            render_context.update(self._prepare_go_context(config, context))
        elif platform == LanguageType.RUST:
            render_context.update(self._prepare_rust_context(config, context))
        elif platform == LanguageType.RUBY:
            render_context.update(self._prepare_ruby_context(config, context))
        elif platform == LanguageType.PHP:
            render_context.update(self._prepare_php_context(config, context))
        
        # Add common context
        render_context.update({
            "env_vars": config.env_vars or {},
            "port": config.expose_port
        })
        
        return render_context
    
    def _prepare_java_context(self, config: VersionConfig, context: Optional[Dict]) -> Dict:
        """Prepare Java-specific context"""
        java_context = {
            "java_version": config.java_version or config.runtime_version or "17",
            "packaging_type": config.packaging_type.value if config.packaging_type else "jar",
            "group_id": config.group_id or "com.example",
            "artifact_id": config.artifact_id or "myapp",
            "version": "1.0.0",
        }
        
        # Add build tool info from context
        if context:
            java_context["build_tool"] = context.get("build_tool", "maven")
            java_context["main_class"] = context.get("main_class", "com.example.Main")
            java_context["dependencies"] = context.get("dependencies", [])
        
        return java_context
    
    def _prepare_nodejs_context(self, config: VersionConfig, context: Optional[Dict]) -> Dict:
        """Prepare Node.js-specific context"""
        nodejs_context = {
            "node_version": config.node_version or config.runtime_version or "18",
            "package_name": config.package_name or "my-app",
            "version": "1.0.0",
        }
        
        # Add framework-specific info from context
        if context:
            nodejs_context["framework"] = context.get("framework")
            nodejs_context["package_manager"] = context.get("package_manager", "npm")
            nodejs_context["main_file"] = context.get("main_file", "index.js")
            nodejs_context["dependencies"] = context.get("dependencies", {})
            nodejs_context["dev_dependencies"] = context.get("dev_dependencies", {})
            nodejs_context["needs_build"] = context.get("needs_build", False)
            nodejs_context["has_yarn_lock"] = context.get("has_yarn_lock", False)
            nodejs_context["has_pnpm_lock"] = context.get("has_pnpm_lock", False)
            
            # Add framework-specific commands
            framework = context.get("framework", "")
            if framework == "Next.js":
                nodejs_context["dev_command"] = "next dev"
                nodejs_context["build_command"] = "next build"
                nodejs_context["start_command"] = "next start"
            elif framework == "React":
                nodejs_context["dev_command"] = "vite dev"
                nodejs_context["build_command"] = "vite build"
                nodejs_context["start_command"] = "vite preview"
            elif framework == "Vue":
                nodejs_context["dev_command"] = "vite dev"
                nodejs_context["build_command"] = "vite build"
                nodejs_context["start_command"] = "vite preview"
        
        return nodejs_context
    
    def _prepare_python_context(self, config: VersionConfig, context: Optional[Dict]) -> Dict:
        """Prepare Python-specific context"""
        python_context = {
            "python_version": config.python_version or config.runtime_version or "3.11",
            "project_name": config.project_name or "my-python-app",
            "version": "0.1.0",
        }
        
        # Add dependencies from config or context
        if config.dependencies:
            python_context["dependencies"] = config.dependencies
        elif context and "dependencies" in context:
            python_context["dependencies"] = context["dependencies"]
        
        # Add framework-specific info
        if context:
            python_context["framework"] = context.get("framework")
            python_context["main_file"] = context.get("main_file", "main.py")
            python_context["main_module"] = context.get("main_module", "main:app")
            python_context["has_pyproject"] = context.get("has_pyproject", False)
            python_context["has_requirements"] = context.get("has_requirements", False)
            python_context["has_pipfile"] = context.get("has_pipfile", False)
        
        return python_context
    
    def _prepare_dotnet_context(self, config: VersionConfig, context: Optional[Dict]) -> Dict:
        """Prepare .NET-specific context"""
        dotnet_context = {
            "dotnet_version": config.dotnet_version or config.runtime_version or "net8.0",
            "dotnet_sdk_version": self._get_sdk_version(config.dotnet_version or "net8.0"),
            "project_type": config.project_type.value if config.project_type else "WebAPI",
            "namespace": "MyApp",
        }
        
        # Add dependencies from context
        if context:
            dotnet_context["dependencies"] = context.get("dependencies", [])
            dotnet_context["assembly_name"] = context.get("assembly_name", "MyApp.dll")
        
        return dotnet_context
    
    def _prepare_go_context(self, config: VersionConfig, context: Optional[Dict]) -> Dict:
        """Prepare Go-specific context"""
        go_context = {
            "go_version": config.go_version or config.runtime_version or "1.22",
            "module_name": config.module_name or "example.com/myapp",
        }
        
        # Add dependencies from config or context
        if config.dependencies:
            # Convert simple list to module format
            go_context["dependencies"] = [
                {"module": dep, "version": "latest"} 
                for dep in config.dependencies
            ]
        elif context and "dependencies" in context:
            go_context["dependencies"] = context["dependencies"]
        
        if context:
            go_context["has_go_sum"] = context.get("has_go_sum", False)
            go_context["main_package"] = context.get("main_package", ".")
        
        return go_context
    
    def _get_sdk_version(self, dotnet_version: str) -> str:
        """Map .NET target framework to SDK version"""
        version_map = {
            "net8.0": "8.0",
            "net7.0": "7.0",
            "net6.0": "6.0"
        }
        return version_map.get(dotnet_version, "8.0")
    
    def _prepare_rust_context(self, config: VersionConfig, context: Optional[Dict]) -> Dict:
        """Prepare Rust-specific context"""
        rust_context = {
            "rust_version": config.rust_version or config.runtime_version or "1.76",
            "package_name": config.package_name_rust or "my-rust-app",
            "version": "0.1.0",
            "edition": "2021"
        }
        
        if context:
            rust_context["framework"] = context.get("framework")
            rust_context["dependencies"] = context.get("dependencies", {})
            rust_context["dev_dependencies"] = context.get("dev_dependencies", {})
            rust_context["has_cargo_lock"] = context.get("has_cargo_lock", False)
            rust_context["binary_name"] = context.get("binary_name", "app")
        
        return rust_context
    
    def _prepare_ruby_context(self, config: VersionConfig, context: Optional[Dict]) -> Dict:
        """Prepare Ruby-specific context"""
        ruby_context = {
            "ruby_version": config.ruby_version or config.runtime_version or "3.3",
            "version": "1.0.0"
        }
        
        if context:
            ruby_context["framework"] = context.get("framework")
            ruby_context["dependencies"] = context.get("dependencies", {})
            ruby_context["test_framework"] = context.get("test_framework", "rspec")
            ruby_context["main_file"] = context.get("main_file", "app.rb")
        
        return ruby_context
    
    def _prepare_php_context(self, config: VersionConfig, context: Optional[Dict]) -> Dict:
        """Prepare PHP-specific context"""
        php_context = {
            "php_version": config.php_version or config.runtime_version or "8.2",
            "package_name": "vendor/my-php-app",
            "version": "1.0.0"
        }
        
        if context:
            php_context["framework"] = context.get("framework")
            php_context["dependencies"] = context.get("dependencies", {})
            php_context["dev_dependencies"] = context.get("dev_dependencies", {})
            php_context["namespace"] = context.get("namespace", "App")
        
        return php_context
    
    def get_recommended_file_name(
        self,
        platform: LanguageType,
        file_type: FileType,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Get recommended file name for a template
        
        Args:
            platform: Target platform
            file_type: Type of file
            context: Additional context
        
        Returns:
            Recommended file name
        """
        # Standard file names
        file_name_map = {
            FileType.POM_XML: "pom.xml",
            FileType.BUILD_GRADLE: "build.gradle",
            FileType.PACKAGE_JSON: "package.json",
            FileType.REQUIREMENTS_TXT: "requirements.txt",
            FileType.PYPROJECT_TOML: "pyproject.toml",
            FileType.GO_MOD: "go.mod",
            FileType.CARGO_TOML: "Cargo.toml",
            FileType.GEMFILE: "Gemfile",
            FileType.COMPOSER_JSON: "composer.json",
            FileType.DOCKERFILE: "Dockerfile"
        }
        
        # .NET csproj needs custom naming
        if file_type == FileType.CSPROJ:
            if context and "project_name" in context:
                return f"{context['project_name']}.csproj"
            return "MyApp.csproj"
        
        return file_name_map.get(file_type, str(file_type))
