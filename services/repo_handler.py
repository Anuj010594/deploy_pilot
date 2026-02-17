import os
import shutil
import tempfile
import zipfile
import subprocess
from typing import Optional
from pathlib import Path
from urllib.parse import urlparse

class RepoHandler:
    """Handle GitHub repository cloning and ZIP extraction"""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size_mb = max_size_mb
        self.max_size_bytes = max_size_mb * 1024 * 1024
    
    def process_repository(self, github_url: Optional[str] = None, 
                          zip_file: Optional[bytes] = None) -> str:
        """
        Process repository from GitHub URL or ZIP file
        Returns: Path to extracted repository
        """
        if github_url:
            return self._clone_github_repo(github_url)
        elif zip_file:
            return self._extract_zip(zip_file)
        else:
            raise ValueError("Either github_url or zip_file must be provided")
    
    def _clone_github_repo(self, github_url: str) -> str:
        """Clone GitHub repository to temporary directory"""
        # Validate GitHub URL
        if not self._is_valid_github_url(github_url):
            raise ValueError("Invalid GitHub URL")
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="repo_scan_")
        
        try:
            # Clone repository
            result = subprocess.run([
                "git", "clone", "--depth", "1", github_url, temp_dir
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                raise RuntimeError(f"Failed to clone repository: {result.stderr}")
            
            # Check size
            if self._get_directory_size(temp_dir) > self.max_size_bytes:
                raise ValueError(f"Repository size exceeds {self.max_size_mb}MB limit")
            
            return temp_dir
            
        except Exception as e:
            self.cleanup_directory(temp_dir)
            raise e
    
    def _extract_zip(self, zip_data: bytes) -> str:
        """Extract ZIP file to temporary directory"""
        if len(zip_data) > self.max_size_bytes:
            raise ValueError(f"ZIP file size exceeds {self.max_size_mb}MB limit")
        
        temp_dir = tempfile.mkdtemp(prefix="repo_scan_")
        
        try:
            # Save ZIP to temporary file
            zip_path = os.path.join(temp_dir, "repo.zip")
            with open(zip_path, 'wb') as f:
                f.write(zip_data)
            
            # Extract ZIP
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Remove ZIP file
            os.remove(zip_path)
            
            # Find the extracted directory (usually has one root folder)
            extracted_items = os.listdir(temp_dir)
            if len(extracted_items) == 1 and os.path.isdir(os.path.join(temp_dir, extracted_items[0])):
                return os.path.join(temp_dir, extracted_items[0])
            
            return temp_dir
            
        except Exception as e:
            self.cleanup_directory(temp_dir)
            raise e
    
    def _is_valid_github_url(self, url: str) -> bool:
        """Validate GitHub URL format"""
        try:
            parsed = urlparse(url)
            return (parsed.netloc == "github.com" and 
                   len(parsed.path.strip('/').split('/')) >= 2)
        except:
            return False
    
    def _get_directory_size(self, directory: str) -> int:
        """Calculate total size of directory"""
        total = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    continue
        return total
    
    def cleanup_directory(self, directory: str) -> None:
        """Clean up temporary directory"""
        try:
            if os.path.exists(directory):
                shutil.rmtree(directory)
        except Exception:
            pass  # Best effort cleanup
