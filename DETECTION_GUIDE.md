# Enhanced Detection System Guide

## Overview

The detection system has been significantly enhanced to provide more accurate and reliable project platform detection through:

1. **Improved Scoring Weights** - Better balanced for accurate detection
2. **Content-Based Analysis** - Reads file contents for deeper insights
3. **Structure Detection** - Recognizes project directory patterns
4. **Configuration File Detection** - Identifies platform-specific configs
5. **Confidence Thresholds** - Automated reliability classification
6. **Extended Language Support** - Added Rust, PHP, and Ruby

---

## Confidence Scoring System

### Scoring Weights (Totals 100%)

| Component | Weight | Purpose |
|-----------|--------|---------|
| **Primary File** | 35% | Core project files (e.g., `pom.xml`, `package.json`) |
| **Secondary File** | 10% | Supporting files (e.g., lock files, wrappers) |
| **Structure Indicator** | 15% | Directory structure (e.g., `src/main/java`) |
| **Config File** | 10% | Configuration files (e.g., `tsconfig.json`) |
| **Framework Match** | 20% | Framework detection (e.g., React, Spring Boot) |
| **Content Match** | 10% | File content analysis (e.g., imports, annotations) |

### Confidence Levels

| Level | Score Range | Description | Recommended Action |
|-------|-------------|-------------|-------------------|
| **UNRELIABLE** | < 0.45 | Very low confidence | Manual review required |
| **MODERATE** | 0.45 - 0.64 | Moderate confidence | Proceed with caution |
| **HIGH** | 0.65 - 0.79 | High confidence | Safe for automation |
| **VERY_HIGH** | ≥ 0.80 | Very high confidence | Fully automated |

---

## Recommended Confidence Threshold

### For Your Use Case (Build Automation & Docker)

**Recommended: 0.65 (High Confidence)**

**Rationale:**
- **0.45 (Minimum)**: Too permissive - may trigger builds on ambiguous projects
- **0.65 (Recommended)**: Balanced - ensures proper detection before automated actions
- **0.80 (Very High)**: Conservative - might miss valid projects with incomplete structure

### When to Adjust

- **Use 0.45-0.55**: When exploring/scanning diverse repositories
- **Use 0.65-0.75**: For automated build/Docker operations (RECOMMENDED)
- **Use 0.80+**: For critical production deployments only

---

## Score Examples

### Spring Boot Project

```
Components Found:
✓ pom.xml (Primary: +0.35)
✓ mvnw (Secondary: +0.05)
✓ src/main/java, src/main/resources (Structure: +0.10)
✓ application.properties (Config: +0.05)
✓ Spring Boot framework detected (Framework: +0.20)
✓ @SpringBootApplication in code (Content: +0.05)
───────────────────────────────────
Total Score: 0.80 (VERY_HIGH)
```

### React Application

```
Components Found:
✓ package.json (Primary: +0.35)
✓ package-lock.json, tsconfig.json (Secondary: +0.10)
✓ src, public (Structure: +0.10)
✓ tsconfig.json, webpack.config.js (Config: +0.10)
✓ React framework detected (Framework: +0.20)
✓ "react" in package.json (Content: +0.05)
───────────────────────────────────
Total Score: 0.90 (VERY_HIGH)
```

### FastAPI Application

```
Components Found:
✓ requirements.txt, pyproject.toml (Primary: +0.35)
✓ main.py (Secondary: +0.05)
✓ src, tests (Structure: +0.10)
✓ setup.cfg (Config: +0.05)
✓ FastAPI not detected (Framework: +0.00)
✓ "fastapi" in requirements.txt (Content: +0.05)
───────────────────────────────────
Total Score: 0.60 (MODERATE)
```

### Minimal Node.js

```
Components Found:
✓ package.json (Primary: +0.35)
✗ No secondary files
✗ No structure indicators
✗ No config files
✗ No framework detected
✗ No content matches
───────────────────────────────────
Total Score: 0.35 (UNRELIABLE)
```

---

## New Detection Features

### 1. Content-Based Analysis

The system now reads file contents to detect:

**Java Projects:**
- Spring Boot annotations (`@SpringBootApplication`)
- Maven/Gradle dependencies in build files
- Framework imports

**Node.js Projects:**
- Dependencies in `package.json`
- Import statements in `.jsx`/`.tsx` files
- Framework-specific patterns

**Python Projects:**
- Framework imports (`from fastapi import`, `from django`)
- Dependencies in `requirements.txt`/`pyproject.toml`

### 2. Structure Recognition

Detects standard project layouts:

- **Java**: `src/main/java`, `src/test/java`, `src/main/resources`
- **Node.js**: `src`, `public`, `dist`, `build`
- **Python**: `src`, `tests`, `docs`
- **.NET**: `Controllers`, `Models`, `Views`, `wwwroot`
- **Go**: `cmd`, `pkg`, `internal`, `api`

### 3. Configuration Files

Recognizes platform-specific configs:

- **Java**: `application.properties`, `application.yml`
- **Node.js**: `tsconfig.json`, `webpack.config.js`, `vite.config.js`
- **Python**: `setup.cfg`, `pyproject.toml`, `tox.ini`
- **.NET**: `appsettings.json`, `launchSettings.json`

---

## Extended Language Support

### Newly Added Languages

**Rust**
- Primary: `Cargo.toml`
- Frameworks: Actix, Rocket, Axum, Warp
- Build: `cargo build --release`

**PHP**
- Primary: `composer.json`
- Frameworks: Laravel, Symfony, WordPress, CodeIgniter
- Build: `composer install`

**Ruby**
- Primary: `Gemfile`
- Frameworks: Ruby on Rails, Sinatra, Jekyll
- Build: `bundle install`

---

## API Usage

### Basic Scan

```bash
curl -X POST "http://localhost:8000/api/scan" \
  -F "github_url=https://github.com/user/repo"
```

### With Custom Threshold

```bash
curl -X POST "http://localhost:8000/api/scan" \
  -F "github_url=https://github.com/user/repo" \
  -F "min_confidence=0.65"
```

### Response Example

```json
{
  "detections": [
    {
      "primary_language": "Java",
      "framework": "Spring Boot",
      "build_tool": "Maven",
      "build_required": true,
      "build_command": "mvn clean package",
      "confidence_score": 0.85,
      "confidence_level": "very_high",
      "detected_files": ["pom.xml", "mvnw", "src/main/java"]
    }
  ],
  "primary": { /* same as above */ },
  "min_confidence_threshold": 0.65
}
```

---

## Integration Recommendations

### For Automated Build Pipeline

```python
from services.detector import ProjectDetector

# Initialize with high confidence threshold
detector = ProjectDetector(min_confidence=0.65)
result = detector.scan_project("/path/to/repo")

if result.primary.confidence_level in ["high", "very_high"]:
    # Safe to automate
    if result.primary.build_required:
        os.system(result.primary.build_command)
else:
    # Request manual review
    print(f"Low confidence ({result.primary.confidence_score})")
    print("Manual review recommended")
```

### For Docker Image Creation

```python
def should_dockerize(detection_result):
    """Determine if project should be automatically Dockerized"""
    
    # Require high confidence
    if detection_result.confidence_score < 0.65:
        return False, "Confidence too low"
    
    # Check if build is well-defined
    if detection_result.build_required and not detection_result.build_command:
        return False, "Build command unclear"
    
    # All checks passed
    return True, "Safe to dockerize"

# Usage
detector = ProjectDetector(min_confidence=0.65)
result = detector.scan_project("/repo")

can_dockerize, reason = should_dockerize(result.primary)
if can_dockerize:
    create_dockerfile(result.primary)
else:
    print(f"Cannot auto-dockerize: {reason}")
```

---

## Best Practices

### 1. Choose Appropriate Thresholds

- **Exploration/Discovery**: 0.35-0.50
- **Standard Operations**: 0.65-0.75 ✅ **RECOMMENDED**
- **Production Critical**: 0.80+

### 2. Always Check Confidence Level

```python
if result.primary.confidence_level == "unreliable":
    # Require manual intervention
    request_manual_review(result)
elif result.primary.confidence_level in ["high", "very_high"]:
    # Proceed with automation
    automate_build(result)
else:
    # Show warning but allow proceed
    show_warning(result)
    proceed_with_confirmation(result)
```

### 3. Handle Multiple Detections

```python
# Check for polyglot projects
if len(result.detections) > 1:
    print(f"Multi-language project detected:")
    for detection in result.detections:
        print(f"  - {detection.primary_language}: {detection.confidence_score:.2f}")
```

### 4. Validate Before Automation

```python
def safe_to_automate(detection):
    return (
        detection.confidence_score >= 0.65 and
        detection.build_command is not None and
        detection.build_tool is not None
    )
```

---

## Testing

Run the test suite to verify detection accuracy:

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python -m pytest tests/test_detector.py -v

# Run specific test
python -m pytest tests/test_detector.py::TestProjectDetector::test_confidence_levels -v
```

---

## Summary

The enhanced detection system provides:

✅ **More Accurate Detection** - Multi-factor scoring  
✅ **Reliability Classification** - Automated confidence levels  
✅ **Deep Analysis** - Content and structure inspection  
✅ **Extended Support** - 8 major languages/platforms  
✅ **Safe Automation** - Threshold-based filtering  

**Recommended Minimum Confidence: 0.65** for production build automation and Docker image creation.
