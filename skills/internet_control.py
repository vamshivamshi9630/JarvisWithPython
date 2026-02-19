"""
Internet & Network Control Module

Network operations:
- Check internet connection
- Get current IP
- Get connected WiFi name
- Internet speed test
- Ping websites
"""

import socket
import subprocess
from typing import Dict, Any

try:
    import speedtest
    HAS_SPEEDTEST = True
except ImportError:
    HAS_SPEEDTEST = False

try:
    import pywifi
    HAS_PYWIFI = True
except ImportError:
    HAS_PYWIFI = False


def check_internet() -> Dict[str, Any]:
    """Check if internet is available"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return {"connected": True, "message": "Internet is connected"}
    except socket.error:
        return {"connected": False, "message": "No internet connection"}


def get_ip_address() -> Dict[str, Any]:
    """Get current public IP address"""
    try:
        # Method 1: Using socket
        try:
            hostname = socket.gethostname()
            local_ip = socket.gethostbyname(hostname)
            return {"ip": local_ip, "message": f"Local IP: {local_ip}"}
        except:
            # Method 2: Using external service (requires internet)
            import requests
            response = requests.get('https://api.ipify.org?format=json', timeout=2)
            public_ip = response.json()['ip']
            return {"ip": public_ip, "message": f"Public IP: {public_ip}"}
    except Exception as e:
        return {"error": str(e), "message": "Could not get IP address"}


def get_dns_info() -> Dict[str, Any]:
    """Get DNS information"""
    try:
        hostname = socket.gethostname()
        return {"hostname": hostname, "message": f"Hostname: {hostname}"}
    except Exception as e:
        return {"error": str(e), "message": "Could not get DNS info"}


def ping_website(website: str) -> Dict[str, Any]:
    """Ping a website"""
    try:
        # Remove http/https if present
        website = website.replace("https://", "").replace("http://", "").split("/")[0]
        
        result = subprocess.run(
            f'ping -n 1 {website}',
            shell=True,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return {"website": website, "status": "Online", "message": f"{website} is online"}
        else:
            return {"website": website, "status": "Offline", "message": f"{website} is offline"}
    except Exception as e:
        return {"error": str(e), "message": f"Could not ping {website}"}


def internet_speed_test() -> Dict[str, Any]:
    """Run internet speed test"""
    if not HAS_SPEEDTEST:
        return {"error": "speedtest-cli not installed", "message": "Speed test not available"}
    
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        
        download = st.download() / 1_000_000  # Convert to Mbps
        upload = st.upload() / 1_000_000
        
        return {
            "download_mbps": download,
            "upload_mbps": upload,
            "message": f"Speed: {download:.2f} Mbps down / {upload:.2f} Mbps up"
        }
    except Exception as e:
        return {"error": str(e), "message": "Speed test failed"}


def get_wifi_name() -> Dict[str, Any]:
    """Get connected WiFi network name"""
    try:
        result = subprocess.run(
            'netsh wlan show interfaces',
            shell=True,
            capture_output=True,
            text=True
        )
        
        for line in result.stdout.split('\n'):
            if 'SSID' in line and ':' in line:
                ssid = line.split(':')[-1].strip()
                if ssid:
                    return {"ssid": ssid, "message": f"Connected to: {ssid}"}
        
        return {"message": "Could not find WiFi network"}
    except Exception as e:
        return {"error": str(e), "message": "Could not get WiFi name"}


def get_network_interfaces() -> Dict[str, Any]:
    """Get all network interfaces"""
    try:
        result = subprocess.run(
            'ipconfig',
            shell=True,
            capture_output=True,
            text=True
        )
        return {"info": result.stdout, "message": "Network configuration retrieved"}
    except Exception as e:
        return {"error": str(e), "message": "Could not get network info"}


def get_connected_devices() -> Dict[str, Any]:
    """Get list of connected devices on network"""
    try:
        result = subprocess.run(
            'arp -a',
            shell=True,
            capture_output=True,
            text=True
        )
        devices = []
        for line in result.stdout.split('\n'):
            if line.strip():
                devices.append(line.strip())
        
        return {"devices": devices, "count": len(devices), "message": f"Found {len(devices)} devices"}
    except Exception as e:
        return {"error": str(e), "message": "Could not get connected devices"}
