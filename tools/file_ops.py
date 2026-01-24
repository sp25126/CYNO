from typing import Dict, Any, List, Optional
import os
from pathlib import Path
from tools.base import JobAgentTool

class FileWriteTool(JobAgentTool):
    def validate_input(self, **kwargs) -> bool:
        return "file_path" in kwargs and "content" in kwargs

    def execute(self, file_path: str, content: str, mode: str = "w") -> str:
        """Writes content to a file."""
        try:
            path = Path(file_path)
            # Basic security check - prevent escaping project root too easily if needed, 
            # but user asked for "folders he has access to", so we trust relative/absolute paths tailored to user context.
            
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, mode, encoding='utf-8') as f:
                f.write(content)
            
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"

class FileReadTool(JobAgentTool):
    def validate_input(self, **kwargs) -> bool:
        return "file_path" in kwargs

    def execute(self, file_path: str) -> str:
        """Reads content from a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"File not found: {file_path}"
                
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

class ListDirTool(JobAgentTool):
    def validate_input(self, **kwargs) -> bool:
        return True

    def execute(self, directory: str = ".") -> str:
        """Lists files and folders in a directory."""
        try:
            path = Path(directory)
            if not path.exists():
                return f"Directory not found: {directory}"
            
            items = []
            for item in path.iterdir():
                type_ = "DIR" if item.is_dir() else "FILE"
                items.append(f"[{type_}] {item.name}")
            
            return "\n".join(sorted(items))
        except Exception as e:
            return f"Error listing directory: {str(e)}"

class FileEditTool(JobAgentTool):
    def validate_input(self, **kwargs) -> bool:
        return "file_path" in kwargs and "old_text" in kwargs and "new_text" in kwargs

    def execute(self, file_path: str, old_text: str, new_text: str) -> str:
        """Replaces text in a file."""
        try:
            path = Path(file_path)
            if not path.exists():
                return f"File not found: {file_path}"
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if old_text not in content:
                return f"Text not found in file: '{old_text[:50]}...'"
            
            new_content = content.replace(old_text, new_text)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            return f"Successfully updated {file_path}"
        except Exception as e:
            return f"Error editing file: {str(e)}"

class CreateFolderTool(JobAgentTool):
    def validate_input(self, **kwargs) -> bool:
        return "folder_path" in kwargs

    def execute(self, folder_path: str) -> str:
        """Creates a new folder."""
        try:
            Path(folder_path).mkdir(parents=True, exist_ok=True)
            return f"Successfully created folder: {folder_path}"
        except Exception as e:
            return f"Error creating folder: {str(e)}"
