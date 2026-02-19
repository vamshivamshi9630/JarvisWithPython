"""
System Information & Hardware Status Module

Provides real-time information about:
- CPU usage and temperature
- RAM usage
- Disk usage
- Battery status
- OS information
- Network information
"""

import psutil
import platform
import socket
from typing import Dict, Any


def get_cpu_info() -> Dict[str, Any]:
    """Get CPU usage percentage and count"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        return {
            "cpu_usage": cpu_percent,
            "cpu_count": cpu_count,
            "message": f"CPU usage: {cpu_percent}% ({cpu_count} cores)"
        }
    except Exception as e:
        return {"error": str(e), "message": f"Could not read CPU info"}


def get_cpu_temperature() -> Dict[str, Any]:
    """Get CPU temperature (Windows only)"""
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            core_temps = []
            for name, entries in temps.items():
                for entry in entries:
                    core_temps.append(entry.current)
            if core_temps:
                avg_temp = sum(core_temps) / len(core_temps)
                return {
                    "temperature": avg_temp,
                    "message": f"CPU temperature: {avg_temp:.1f}°C"
                }
        return {"message": "Temperature sensor not available"}
    except Exception as e:
        return {"error": str(e), "message": "Could not read temperature"}


def get_ram_info() -> Dict[str, Any]:
    """Get RAM usage information"""
    try:
        ram = psutil.virtual_memory()
        used_gb = ram.used / (1024**3)
        total_gb = ram.total / (1024**3)
        percent = ram.percent
        return {
            "ram_used_gb": used_gb,
            "ram_total_gb": total_gb,
            "ram_percent": percent,
            "message": f"RAM: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent}%)"
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not read RAM info"}


def get_disk_info(drive: str = "C:") -> Dict[str, Any]:
    """Get disk usage information"""
    try:
        disk = psutil.disk_usage(drive)
        used_gb = disk.used / (1024**3)
        total_gb = disk.total / (1024**3)
        free_gb = disk.free / (1024**3)
        percent = disk.percent
        return {
            "disk_used_gb": used_gb,
            "disk_total_gb": total_gb,
            "disk_free_gb": free_gb,
            "disk_percent": percent,
            "message": f"Disk {drive}: {used_gb:.1f}GB / {total_gb:.1f}GB ({percent}%) | Free: {free_gb:.1f}GB"
        }
    except Exception as e:
        return {"error": str(e), "message": f"Could not read disk info for {drive}"}


def get_battery_info() -> Dict[str, Any]:
    """Get battery percentage and status"""
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            is_charging = battery.power_plugged
            time_left = battery.secsleft if not is_charging else None
            
            status = "Charging" if is_charging else "Discharging"
            time_str = ""
            if time_left and time_left != psutil.POWER_TIME_UNLIMITED:
                hours = time_left // 3600
                mins = (time_left % 3600) // 60
                time_str = f" | {hours}h {mins}m left"
            
            return {
                "battery_percent": percent,
                "is_charging": is_charging,
                "status": status,
                "message": f"Battery: {percent}% | {status}{time_str}"
            }
        return {"message": "No battery detected (desktop PC?)"}
    except Exception as e:
        return {"error": str(e), "message": "Could not read battery info"}


def get_os_info() -> Dict[str, Any]:
    """Get OS information"""
    try:
        os_name = platform.system()
        os_version = platform.version()
        processor = platform.processor()
        hostname = socket.gethostname()
        username = psutil.Process().username()
        
        return {
            "os": os_name,
            "version": os_version,
            "processor": processor,
            "hostname": hostname,
            "username": username,
            "message": f"OS: {os_name} | PC: {hostname} | User: {username}"
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not read OS info"}


def get_boot_time() -> Dict[str, Any]:
    """Get system boot time"""
    try:
        boot_time = psutil.boot_time()
        from datetime import datetime
        boot_datetime = datetime.fromtimestamp(boot_time)
        return {
            "boot_time": boot_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "message": f"Last boot: {boot_datetime.strftime('%Y-%m-%d %H:%M:%S')}"
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not read boot time"}


def get_network_info() -> Dict[str, Any]:
    """Get network information"""
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        
        return {
            "hostname": hostname,
            "ip_address": ip_address,
            "message": f"IP: {ip_address} | PC: {hostname}"
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not read network info"}


def get_system_status() -> Dict[str, Any]:
    """Get complete system status summary"""
    cpu = get_cpu_info()
    ram = get_ram_info()
    disk = get_disk_info()
    battery = get_battery_info()
    
    return {
        "cpu": cpu,
        "ram": ram,
        "disk": disk,
        "battery": battery,
        "message": f"{cpu['message']} | {ram['message']} | {disk['message']}"
    }
