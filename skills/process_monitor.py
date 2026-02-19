"""
Process Monitoring Module

Monitor and manage running processes:
- List all processes
- Get process CPU/RAM usage
- Kill processes
- Find process by name
- Monitor heavy processes
"""

import psutil
from typing import Dict, Any, List


def get_running_processes() -> Dict[str, Any]:
    """Get list of all running processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'],
                    'memory': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {"count": len(processes), "processes": processes, "message": f"Found {len(processes)} running processes"}
    except Exception as e:
        return {"error": str(e), "message": "Could not get processes"}


def find_process(process_name: str) -> Dict[str, Any]:
    """Find a specific process by name"""
    try:
        process_name_lower = process_name.lower()
        found = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if process_name_lower in proc.info['name'].lower():
                    found.append({
                        'pid': proc.info['pid'],
                        'name': proc.info['name'],
                        'cpu': proc.info['cpu_percent'],
                        'memory': proc.info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if found:
            return {"name": process_name, "count": len(found), "processes": found, "message": f"Found {len(found)} process(es): {process_name}"}
        else:
            return {"name": process_name, "count": 0, "message": f"No processes found: {process_name}"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not find process"}


def is_running(process_name: str) -> Dict[str, Any]:
    """Check if a process is running"""
    try:
        for proc in psutil.process_iter(['name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    return {"running": True, "message": f"{process_name} is running"}
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {"running": False, "message": f"{process_name} is not running"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not check process status"}


def kill_process(process_name: str, force: bool = False) -> Dict[str, Any]:
    """Terminate a process"""
    try:
        killed = []
        process_name_lower = process_name.lower()
        
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name_lower in proc.info['name'].lower():
                    if force:
                        proc.kill()
                    else:
                        proc.terminate()
                    killed.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        if killed:
            action = "Force killed" if force else "Terminated"
            return {"killed": killed, "count": len(killed), "message": f"{action} {len(killed)} process(es)"}
        else:
            return {"message": f"No processes found to kill: {process_name}"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not kill process"}


def get_heavy_processes(limit: int = 5) -> Dict[str, Any]:
    """Get processes using most resources"""
    try:
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'name': proc.info['name'],
                    'cpu': proc.info['cpu_percent'] or 0,
                    'memory': proc.info['memory_percent'] or 0,
                    'resource_usage': (proc.info['cpu_percent'] or 0) + (proc.info['memory_percent'] or 0)
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by resource usage
        processes.sort(key=lambda x: x['resource_usage'], reverse=True)
        heavy = processes[:limit]
        
        return {"heavy_processes": heavy, "limit": limit, "message": f"Top {limit} resource-heavy processes"}
    except Exception as e:
        return {"error": str(e), "message": "Could not get heavy processes"}


def get_process_details(process_name: str) -> Dict[str, Any]:
    """Get detailed information about a process"""
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    p = psutil.Process(proc.info['pid'])
                    return {
                        'name': p.name(),
                        'pid': p.pid,
                        'status': p.status(),
                        'cpu_percent': p.cpu_percent(),
                        'memory_info': p.memory_info(),
                        'message': f"Process: {p.name()} | PID: {p.pid} | CPU: {p.cpu_percent()}%"
                    }
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return {"message": f"Process not found: {process_name}"}
    except Exception as e:
        return {"error": str(e), "message": "Could not get process details"}
