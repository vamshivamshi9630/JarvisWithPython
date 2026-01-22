from skills.system_cmds import run_system
from skills.app_opener import open_app
from skills.file_opener import open_file
from skills.chat import get_greeting_response, get_small_talk_response, is_greeting, is_small_talk
from skills.system_controls import handle_system_control, connect_bluetooth_device, connect_wifi_network, get_bluetooth_devices, get_wifi_networks
from ai.knowledge import answer

def execute(intent: dict):
    if not intent or "intent" not in intent:
        return "❌ Invalid command."

    kind = intent["intent"]

    try:
        if kind == "chat":
            query = intent.get("query", "")
            if is_greeting(query.lower().strip()):
                return get_greeting_response(query)
            elif is_small_talk(query.lower()):
                return get_small_talk_response(query)
            return "😊 How can I help you?"

        if kind == "system":
            return run_system(intent)

        if kind == "system_control":
            control = intent.get("control", "")
            action = intent.get("action", "")
            
            # Handle device/network connection commands
            if control == "connect_bluetooth":
                return connect_bluetooth_device(intent.get("device", ""))
            elif control == "connect_wifi":
                return connect_wifi_network(intent.get("network", ""), intent.get("password", ""))
            elif control == "list_bluetooth":
                return get_bluetooth_devices()
            elif control == "list_wifi":
                return get_wifi_networks()
            else:
                # Regular system control (on/off, up/down)
                return handle_system_control(control, action)

        if kind == "open_app":
            return open_app(intent["target"])

        if kind == "open_file":
            return open_file(
                intent["file"],
                intent.get("app")
            )

        if kind == "knowledge":
            return answer(intent["query"])

    except Exception as e:
        return f"❌ Error: {str(e)[:100]}"

    return "❌ I don't understand that command."
