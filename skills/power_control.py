"""
Power Control Module

Controls:
- Volume (increase, decrease, mute, unmute)
- Brightness (increase, decrease, get current)
- WiFi (on/off)
- Bluetooth (on/off)
- Airplane mode
"""

import subprocess
import os
from typing import Dict, Any

# Try importing optional libraries
try:
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    from ctypes import cast, POINTER
    HAS_PYCAW = True
except ImportError:
    HAS_PYCAW = False

try:
    from screen_brightness_control import set_brightness, get_brightness
    HAS_BRIGHTNESS = True
except ImportError:
    HAS_BRIGHTNESS = False

try:
    import pywifi
    from pywifi import const
    HAS_PYWIFI = True
except ImportError:
    HAS_PYWIFI = False


def set_volume(level: int) -> Dict[str, Any]:
    """Set volume to specific level (0-100)"""
    if not HAS_PYCAW:
        return {"error": "pycaw not installed", "message": "Volume control not available"}
    
    try:
        level = max(0, min(100, level))  # Clamp 0-100
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        volume.SetMasterVolumeLevelScalar(level / 100.0)
        
        return {
            "level": level,
            "message": f"Volume set to {level}%"
        }
    except Exception as e:
        return {"error": str(e), "message": f"Could not set volume: {e}"}


def increase_volume(step: int = 5) -> Dict[str, Any]:
    """Increase volume by step"""
    if not HAS_PYCAW:
        return {"error": "pycaw not installed", "message": "Volume control not available"}
    
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        current = volume.GetMasterVolumeLevelScalar() * 100
        new_level = int(current) + step
        volume.SetMasterVolumeLevelScalar(min(100, new_level) / 100.0)
        
        return {
            "level": min(100, new_level),
            "message": f"Volume increased to {min(100, new_level)}%"
        }
    except Exception as e:
        return {"error": str(e), "message": f"Could not increase volume"}


def decrease_volume(step: int = 5) -> Dict[str, Any]:
    """Decrease volume by step"""
    if not HAS_PYCAW:
        return {"error": "pycaw not installed", "message": "Volume control not available"}
    
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        current = volume.GetMasterVolumeLevelScalar() * 100
        new_level = max(0, int(current) - step)
        volume.SetMasterVolumeLevelScalar(new_level / 100.0)
        
        return {
            "level": new_level,
            "message": f"Volume decreased to {new_level}%"
        }
    except Exception as e:
        return {"error": str(e), "message": f"Could not decrease volume"}


def mute_volume() -> Dict[str, Any]:
    """Mute system volume"""
    try:
        os.system("nircmd.exe mutesysvolume 1")
        return {"message": "Muted volume"}
    except Exception as e:
        return set_volume(0)


def unmute_volume() -> Dict[str, Any]:
    """Unmute system volume"""
    try:
        os.system("nircmd.exe mutesysvolume 0")
        return {"message": "Unmuted volume"}
    except Exception as e:
        return set_volume(50)


def set_brightness(level: int) -> Dict[str, Any]:
    """Set brightness to specific level (0-100)"""
    if not HAS_BRIGHTNESS:
        return {"error": "brightness control not available", "message": "Brightness control not available"}
    
    try:
        level = max(0, min(100, level))
        set_brightness(level)
        return {"level": level, "message": f"Brightness set to {level}%"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not set brightness"}


def get_brightness_level() -> Dict[str, Any]:
    """Get current brightness level"""
    if not HAS_BRIGHTNESS:
        return {"error": "brightness control not available"}
    
    try:
        level = get_brightness()[0]
        return {"level": level, "message": f"Brightness: {level}%"}
    except Exception as e:
        return {"error": str(e), "message": "Could not read brightness"}


def increase_brightness(step: int = 10) -> Dict[str, Any]:
    """Increase brightness by step"""
    if not HAS_BRIGHTNESS:
        return {"error": "brightness control not available"}
    
    try:
        current = get_brightness()[0]
        new_level = min(100, current + step)
        set_brightness(new_level)
        return {"level": new_level, "message": f"Brightness increased to {new_level}%"}
    except Exception as e:
        return {"error": str(e), "message": "Could not increase brightness"}


def decrease_brightness(step: int = 10) -> Dict[str, Any]:
    """Decrease brightness by step"""
    if not HAS_BRIGHTNESS:
        return {"error": "brightness control not available"}
    
    try:
        current = get_brightness()[0]
        new_level = max(0, current - step)
        set_brightness(new_level)
        return {"level": new_level, "message": f"Brightness decreased to {new_level}%"}
    except Exception as e:
        return {"error": str(e), "message": "Could not decrease brightness"}


def toggle_wifi() -> Dict[str, Any]:
    """Toggle WiFi on/off"""
    try:
        # Windows command to toggle WiFi
        subprocess.run("netsh interface set interface name=\"WiFi\" admin=disable", shell=True)
        return {"message": "WiFi toggle initiated"}
    except Exception as e:
        return {"error": str(e), "message": "Could not toggle WiFi"}


def toggle_airplane_mode() -> Dict[str, Any]:
    """Toggle airplane mode"""
    try:
        # PowerShell command for airplane mode
        subprocess.run(
            'powershell -Command "& {Add-Type -Assembly System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait(\"%{F4}\")}"',
            shell=True
        )
        return {"message": "Airplane mode toggle initiated"}
    except Exception as e:
        return {"error": str(e), "message": "Could not toggle airplane mode"}


def get_power_info() -> Dict[str, Any]:
    """Get power status"""
    try:
        battery_status = os.popen("wmic battery get status").read()
        return {"status": battery_status, "message": f"Power status: {battery_status}"}
    except Exception as e:
        return {"error": str(e), "message": "Could not read power info"}
