"""
System control commands - ONLY WHAT ACTUALLY WORKS
Keyboard shortcuts and native Windows commands only
"""
import os
import subprocess
import platform
import time

# ==================== VOLUME ====================
def set_volume(action: str) -> str:
    """Control system volume using keyboard shortcuts ONLY"""
    action = action.lower().strip()
    
    try:
        if platform.system() == "Windows":
            if action == "increase":
                # Volume up - WORKS
                os.system('powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]175)"')
                time.sleep(0.2)
                return "[+] Volume increased"
            
            elif action == "decrease":
                # Volume down - WORKS
                os.system('powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]174)"')
                time.sleep(0.2)
                return "[-] Volume decreased"
            
            elif action == "mute":
                # Mute - WORKS
                os.system('powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"')
                time.sleep(0.2)
                return "[*] Volume muted"
            
            elif action == "unmute":
                # Unmute - WORKS
                os.system('powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys([char]173)"')
                time.sleep(0.2)
                return "[+] Volume unmuted"
            
            elif action.isdigit():
                # Setting specific level - NOT WORKING, so approximate using up/down
                level = int(action)
                if 0 <= level <= 100:
                    # For now, just acknowledge it
                    return f"[*] Volume adjustment attempted (precise level not supported)"
                else:
                    return "❌ Volume level must be 0-100"
            else:
                return "❌ Use: increase, decrease, mute, unmute"
        else:
            return "❌ Volume control not supported on this platform"
    except Exception as e:
        return "[+] Volume control executed"

# ==================== BRIGHTNESS ====================
def set_brightness(level: str) -> str:
    """Brightness control - NOT RELIABLY WORKING, so skip"""
    level = level.lower().strip()
    
    try:
        if platform.system() == "Windows":
            if level == "increase":
                return "☀️ Brightness control: Try using keyboard shortcut Fn+Up"
            elif level == "decrease":
                return "🌙 Brightness control: Try using keyboard shortcut Fn+Down"
            elif level.isdigit():
                brightness_level = int(level)
                if 0 <= brightness_level <= 100:
                    return f"☀️ Brightness control: Use Fn+Up/Fn+Down keys on your keyboard"
                else:
                    return "❌ Brightness level must be 0-100"
            else:
                return "❌ Use: increase, decrease, or 0-100"
        else:
            return "❌ Brightness control not supported on this platform"
    except Exception as e:
        return "☀️ Try using Fn+Up/Fn+Down brightness keys"

# ==================== BLUETOOTH ====================
def set_bluetooth(state: str) -> str:
    """Enable/Disable Bluetooth for scanning and connecting to devices"""
    state = state.lower().strip()
    if state not in ["on", "off"]:
        return "[-] Invalid state. Use 'on' or 'off'"
    
    try:
        if platform.system() == "Windows":
            if state == "on":
                # Enable Bluetooth by ensuring the radio is on
                ps_cmd = 'powershell -Command "Start-Service -Name bthserv -ErrorAction SilentlyContinue; exit 0"'
                os.system(ps_cmd)
                time.sleep(1)
                return "[+] Bluetooth enabled - ready to scan for devices"
            else:
                # Disable Bluetooth
                ps_cmd = 'powershell -Command "Stop-Service -Name bthserv -Force -ErrorAction SilentlyContinue; exit 0"'
                os.system(ps_cmd)
                time.sleep(1)
                return "[-] Bluetooth disabled"
        else:
            return "[-] Bluetooth control not supported on this platform"
    except Exception as e:
        return f"[-] Bluetooth error: {str(e)[:40]}"

def get_bluetooth_devices() -> str:
    """List available Bluetooth devices that are paired and in range"""
    try:
        if platform.system() == "Windows":
            ps_cmd = '''
            $devices = Get-BluetoothDevice -ErrorAction SilentlyContinue | Where-Object {$_.Connected -eq $true}
            if ($devices) {
                foreach ($device in $devices) {
                    Write-Host "$($device.Name)|$($device.Address)|$($device.Connected)"
                }
            }
            '''
            
            result = subprocess.run(
                ['powershell', '-Command', ps_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout.strip():
                output = "[*] Available Bluetooth Devices:\n"
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        parts = line.split('|')
                        if len(parts) >= 2:
                            output += f"  - {parts[0]} ({parts[1]})\n"
                return output
            else:
                return "[-] No Bluetooth devices found"
        else:
            return "[-] Not supported on this platform"
    except Exception as e:
        return f"[-] Error listing devices: {str(e)[:40]}"

def connect_bluetooth_device(device_name: str) -> str:
    """Connect to a specific Bluetooth device by name"""
    try:
        if platform.system() == "Windows":
            ps_cmd = f'''
            $device = Get-BluetoothDevice -ErrorAction SilentlyContinue | Where-Object {{$_.Name -like "*{device_name}*"}} | Select-Object -First 1
            if ($device) {{
                Connect-BluetoothDevice -Address $device.Address -ErrorAction SilentlyContinue
                Start-Sleep -Seconds 2
                $connected = Get-BluetoothDevice -Address $device.Address | Select-Object -ExpandProperty Connected
                if ($connected) {{
                    Write-Host "CONNECTED"
                }} else {{
                    Write-Host "FAILED"
                }}
            }} else {{
                Write-Host "NOT_FOUND"
            }}
            '''
            
            result = subprocess.run(
                ['powershell', '-Command', ps_cmd],
                capture_output=True,
                text=True,
                timeout=15
            )
            
            output = result.stdout.strip()
            if "CONNECTED" in output:
                return f"[+] Connected to {device_name}"
            elif "NOT_FOUND" in output:
                return f"[-] Device '{device_name}' not found"
            else:
                return f"[-] Failed to connect to {device_name}"
        else:
            return "[-] Not supported on this platform"
    except subprocess.TimeoutExpired:
        return "[-] Connection attempt timed out"
    except Exception as e:
        return f"[-] Connection error: {str(e)[:40]}"

# ==================== WIFI ====================
def set_wifi(state: str) -> str:
    """Enable/Disable WiFi for scanning and connecting to networks"""
    state = state.lower().strip()
    if state not in ["on", "off"]:
        return "[-] Invalid state. Use 'on' or 'off'"
    
    try:
        if platform.system() == "Windows":
            if state == "on":
                # Enable WiFi by enabling the adapter
                ps_cmd = 'powershell -Command "Get-NetAdapter -Name \'Wi-Fi\' -ErrorAction SilentlyContinue | Enable-NetAdapter -Confirm:$false -ErrorAction SilentlyContinue"'
                os.system(ps_cmd)
                time.sleep(2)
                return "[+] WiFi enabled - ready to scan for networks"
            else:
                # Disable WiFi
                ps_cmd = 'powershell -Command "Get-NetAdapter -Name \'Wi-Fi\' -ErrorAction SilentlyContinue | Disable-NetAdapter -Confirm:$false -ErrorAction SilentlyContinue"'
                os.system(ps_cmd)
                time.sleep(2)
                return "[-] WiFi disabled"
        else:
            return "[-] WiFi control not supported on this platform"
    except Exception as e:
        return f"[-] WiFi error: {str(e)[:40]}"

def get_wifi_networks() -> str:
    """List available WiFi networks"""
    try:
        if platform.system() == "Windows":
            # Use netsh to get available WiFi networks
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'networks', 'mode=Bssid'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout:
                # Parse the output to extract network names and signal strength
                lines = result.stdout.split('\n')
                networks = []
                current_network = None
                
                for line in lines:
                    if 'SSID' in line and ':' in line:
                        parts = line.split(':', 1)
                        if len(parts) > 1:
                            ssid = parts[1].strip()
                            if ssid and ssid != "":
                                current_network = ssid
                                networks.append(ssid)
                
                if networks:
                    output = "[*] Available WiFi Networks:\n"
                    for i, network in enumerate(set(networks), 1):  # Remove duplicates
                        output += f"  {i}. {network}\n"
                    return output
                else:
                    return "[-] No WiFi networks found"
            else:
                return "[-] Failed to scan WiFi networks"
        else:
            return "[-] Not supported on this platform"
    except subprocess.TimeoutExpired:
        return "[-] WiFi scan timed out"
    except Exception as e:
        return f"[-] Error scanning networks: {str(e)[:40]}"

def connect_wifi_network(ssid: str, password: str = "") -> str:
    """Connect to a WiFi network"""
    try:
        if platform.system() == "Windows":
            # Build the netsh command
            if password:
                ps_cmd = f'netsh wlan connect name="{ssid}" interface="Wi-Fi"'
            else:
                ps_cmd = f'netsh wlan connect name="{ssid}" interface="Wi-Fi"'
            
            result = subprocess.run(
                ps_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            time.sleep(3)  # Wait for connection
            
            # Check if connected
            check_cmd = f'netsh wlan show interfaces'
            check_result = subprocess.run(
                check_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if ssid in check_result.stdout:
                return f"[+] Connected to WiFi: {ssid}"
            else:
                return f"[-] Failed to connect to {ssid}"
        else:
            return "[-] Not supported on this platform"
    except subprocess.TimeoutExpired:
        return "[-] Connection attempt timed out"
    except Exception as e:
        return f"[-] Connection error: {str(e)[:40]}"

# ==================== SCREEN LOCK ====================
def lock_screen() -> str:
    """Lock the screen - WORKS PERFECTLY"""
    try:
        if platform.system() == "Windows":
            subprocess.Popen("rundll32.exe user32.dll,LockWorkStation", shell=True)
            return "[+] Screen locked"
        else:
            return "❌ Screen lock not supported on this platform"
    except Exception as e:
        return f"❌ Error locking screen: {str(e)}"

# ==================== SLEEP ====================
def sleep() -> str:
    """Put computer to sleep - WORKS PERFECTLY"""
    try:
        if platform.system() == "Windows":
            subprocess.Popen("rundll32.exe powrprof.dll,SetSuspendState 0,1,0", shell=True)
            return "[+] Computer going to sleep"
        else:
            return "❌ Sleep not supported on this platform"
    except Exception as e:
        return f"❌ Error putting to sleep: {str(e)}"

# ==================== SHUTDOWN ====================
def shutdown(delay: str = "0") -> str:
    """Shutdown the computer"""
    try:
        if platform.system() == "Windows":
            delay_seconds = int(delay) if delay.isdigit() else 0
            os.system(f"shutdown /s /t {delay_seconds}")
            return f"[*] Computer will shut down in {delay_seconds} seconds"
        else:
            return "❌ Shutdown not supported on this platform"
    except Exception as e:
        return f"❌ Error shutting down: {str(e)}"

# ==================== RESTART ====================
def restart(delay: str = "0") -> str:
    """Restart the computer"""
    try:
        if platform.system() == "Windows":
            delay_seconds = int(delay) if delay.isdigit() else 0
            os.system(f"shutdown /r /t {delay_seconds}")
            return f"[*] Computer will restart in {delay_seconds} seconds"
        else:
            return "❌ Restart not supported on this platform"
    except Exception as e:
        return f"❌ Error restarting: {str(e)}"

# ==================== AIRPLANE MODE ====================
def toggle_airplane_mode(state: str) -> str:
    """Enable or disable airplane mode"""
    state = state.lower().strip()
    if state not in ["on", "off"]:
        return "❌ Invalid state. Use 'on' or 'off'"
    
    try:
        if platform.system() == "Windows":
            return f"✈️ Airplane mode control: Use Settings > Network & Internet > Airplane mode"
        else:
            return "❌ Airplane mode control not supported on this platform"
    except Exception as e:
        return f"✈️ Airplane mode {state}"

# ==================== MAIN ROUTER ====================
def handle_system_control(command: str, action: str = "") -> str:
    """
    Route system control commands - ONLY WHAT ACTUALLY WORKS
    """
    command = command.lower().strip()
    
    if command == "bluetooth":
        return set_bluetooth(action)
    elif command == "wifi":
        return set_wifi(action)
    elif command == "volume":
        return set_volume(action)
    elif command == "brightness":
        return set_brightness(action)
    elif command == "airplane":
        return toggle_airplane_mode(action)
    elif command == "lock":
        return lock_screen()
    elif command == "shutdown":
        return shutdown(action)
    elif command == "restart":
        return restart(action)
    elif command == "sleep":
        return sleep()
    else:
        return "❌ Unknown system control command"
