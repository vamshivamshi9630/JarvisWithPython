"""
File & Folder Management Module

Operations:
- Create files/folders
- Delete files/folders
- Rename files
- Copy/Move files
- Search files
- List contents
- Open files/folders
"""

import os
import shutil
from pathlib import Path
from typing import Dict, Any, List
import subprocess


def create_file(filepath: str, content: str = "") -> Dict[str, Any]:
    """Create a new file"""
    try:
        path = Path(filepath)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        if content:
            with open(filepath, 'w') as f:
                f.write(content)
        else:
            path.touch()
        
        return {"filepath": filepath, "message": f"Created file: {filepath}"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not create file"}


def create_folder(folderpath: str) -> Dict[str, Any]:
    """Create a new folder"""
    try:
        Path(folderpath).mkdir(parents=True, exist_ok=True)
        return {"folderpath": folderpath, "message": f"Created folder: {folderpath}"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not create folder"}


def delete_file(filepath: str) -> Dict[str, Any]:
    """Delete a file safely"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return {"filepath": filepath, "message": f"Deleted file: {filepath}"}
        else:
            return {"error": "File not found", "message": f"File does not exist: {filepath}"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not delete file"}


def delete_folder(folderpath: str, recursive: bool = False) -> Dict[str, Any]:
    """Delete a folder"""
    try:
        if not os.path.exists(folderpath):
            return {"error": "Folder not found", "message": f"Folder does not exist"}
        
        if recursive:
            shutil.rmtree(folderpath)
        else:
            os.rmdir(folderpath)
        
        return {"folderpath": folderpath, "message": f"Deleted folder: {folderpath}"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not delete folder"}


def rename_file(old_path: str, new_path: str) -> Dict[str, Any]:
    """Rename a file"""
    try:
        if not os.path.exists(old_path):
            return {"error": "File not found"}
        
        os.rename(old_path, new_path)
        return {"old": old_path, "new": new_path, "message": f"Renamed to: {new_path}"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not rename"}


def copy_file(source: str, destination: str) -> Dict[str, Any]:
    """Copy a file"""
    try:
        if not os.path.exists(source):
            return {"error": "Source file not found"}
        
        shutil.copy2(source, destination)
        return {"source": source, "destination": destination, "message": f"Copied to: {destination}"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not copy file"}


def move_file(source: str, destination: str) -> Dict[str, Any]:
    """Move a file"""
    try:
        if not os.path.exists(source):
            return {"error": "Source file not found"}
        
        shutil.move(source, destination)
        return {"source": source, "destination": destination, "message": f"Moved to: {destination}"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not move file"}


def list_files(folderpath: str, extension: str = None) -> Dict[str, Any]:
    """List files in a folder"""
    try:
        if not os.path.exists(folderpath):
            return {"error": "Folder not found"}
        
        files = []
        for item in os.listdir(folderpath):
            if extension is None or item.endswith(extension):
                files.append(item)
        
        return {"folder": folderpath, "files": files, "count": len(files), "message": f"Found {len(files)} items"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not list files"}


def search_files(folder: str, pattern: str) -> Dict[str, Any]:
    """Search for files matching pattern"""
    try:
        matches = []
        for root, dirs, files in os.walk(folder):
            for file in files:
                if pattern.lower() in file.lower():
                    matches.append(os.path.join(root, file))
        
        return {"folder": folder, "pattern": pattern, "matches": matches, "count": len(matches), "message": f"Found {len(matches)} files"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not search"}


def get_file_info(filepath: str) -> Dict[str, Any]:
    """Get file information"""
    try:
        if not os.path.exists(filepath):
            return {"error": "File not found"}
        
        stat = os.stat(filepath)
        size_mb = stat.st_size / (1024*1024)
        
        return {
            "filepath": filepath,
            "size_bytes": stat.st_size,
            "size_mb": size_mb,
            "modified": stat.st_mtime,
            "message": f"File size: {size_mb:.2f} MB"
        }
    except Exception as e:
        return {"error": str(e), "message": f"Could not get file info"}


def get_disk_space(drive: str = "C:") -> Dict[str, Any]:
    """Get disk space information"""
    try:
        import shutil
        total, used, free = shutil.disk_usage(drive)
        
        total_gb = total / (1024**3)
        used_gb = used / (1024**3)
        free_gb = free / (1024**3)
        
        return {
            "drive": drive,
            "total_gb": total_gb,
            "used_gb": used_gb,
            "free_gb": free_gb,
            "message": f"Drive {drive}: {free_gb:.1f}GB free / {total_gb:.1f}GB total"
        }
    except Exception as e:
        return {"error": str(e), "message": f"Could not get disk space"}


def open_folder(folderpath: str) -> Dict[str, Any]:
    """Open folder in explorer"""
    try:
        if not os.path.exists(folderpath):
            return {"error": "Folder not found"}
        
        subprocess.Popen(f'explorer "{folderpath}"')
        return {"folderpath": folderpath, "message": f"Opened folder"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not open folder"}


def clear_temp_files() -> Dict[str, Any]:
    """Clear Windows temp files"""
    try:
        temp_folder = os.path.expandvars(r'%temp%')
        deleted_count = 0
        
        for item in os.listdir(temp_folder):
            try:
                item_path = os.path.join(temp_folder, item)
                if os.path.isfile(item_path):
                    os.remove(item_path)
                    deleted_count += 1
            except:
                pass
        
        return {"deleted": deleted_count, "message": f"Deleted {deleted_count} temp files"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not clear temp"}
