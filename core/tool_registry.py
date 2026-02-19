"""
Tool Registry - Central repository of all system capabilities
This is the critical foundation for LLM-based planning
The LLM reads this to understand what tools are available and how to use them
"""

from typing import Dict, List, Any, Optional, Tuple
from enum import Enum


class ParameterType(Enum):
    """Parameter types supported by tools"""
    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    ARRAY = "array"
    ENUM = "enum"


class ToolParameter:
    """Represents a parameter of a tool"""
    
    def __init__(self, 
                 name: str, 
                 param_type: ParameterType,
                 description: str,
                 required: bool = True,
                 default: Any = None,
                 enum_values: Optional[List[str]] = None):
        self.name = name
        self.param_type = param_type
        self.description = description
        self.required = required
        self.default = default
        self.enum_values = enum_values
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for LLM"""
        param_dict = {
            "name": self.name,
            "type": self.param_type.value,
            "description": self.description,
            "required": self.required,
        }
        if self.default is not None:
            param_dict["default"] = self.default
        if self.enum_values:
            param_dict["enum"] = self.enum_values
        return param_dict


class Tool:
    """Represents a system tool/capability"""
    
    def __init__(self,
                 name: str,
                 description: str,
                 category: str,
                 parameters: Optional[List[ToolParameter]] = None,
                 examples: Optional[List[str]] = None):
        self.name = name
        self.description = description
        self.category = category  # app_control, file_management, system_control, web_control, etc.
        self.parameters = parameters or []
        self.examples = examples or []
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for LLM (OpenAI function calling format)"""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": {
                        p.name: {
                            "type": p.param_type.value,
                            "description": p.description,
                            **({"enum": p.enum_values} if p.enum_values else {}),
                        }
                        for p in self.parameters
                    },
                    "required": [p.name for p in self.parameters if p.required]
                }
            }
        }
    
    def to_prompt_text(self) -> str:
        """Convert to text format for LLM prompt"""
        text = f"Tool: {self.name}\n"
        text += f"Description: {self.description}\n"
        
        if self.parameters:
            text += "Parameters:\n"
            for param in self.parameters:
                text += f"  - {param.name} ({param.param_type.value}): {param.description}\n"
        
        if self.examples:
            text += "Examples:\n"
            for example in self.examples:
                text += f"  - {example}\n"
        
        return text


class ToolRegistry:
    """Central registry of all system tools"""
    
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Initialize all available system tools"""
        
        # ==============================================================
        # APPLICATION CONTROL TOOLS
        # ==============================================================
        self.register_tool(Tool(
            name="open_application",
            description="Open an application on the computer",
            category="app_control",
            parameters=[
                ToolParameter("app_name", ParameterType.STRING, "Name of the application (chrome, firefox, notepad, vscode, etc.)", required=True),
                ToolParameter("wait_time", ParameterType.INTEGER, "Time to wait for app to load in seconds", required=False, default=2),
            ],
            examples=[
                "open_application(app_name='chrome')",
                "open_application(app_name='notepad', wait_time=1)",
                "open_application(app_name='vscode')",
            ]
        ))
        
        self.register_tool(Tool(
            name="close_application",
            description="Close a running application",
            category="app_control",
            parameters=[
                ToolParameter("app_name", ParameterType.STRING, "Name of the application to close", required=True),
            ],
            examples=[
                "close_application(app_name='chrome')",
            ]
        ))
        
        # ==============================================================
        # WEB NAVIGATION & SEARCH TOOLS
        # ==============================================================
        self.register_tool(Tool(
            name="navigate_to_website",
            description="Navigate to a website in the currently open browser",
            category="web_control",
            parameters=[
                ToolParameter("website", ParameterType.STRING, "Website name or URL (youtube.com, google.com, etc.)", required=True),
            ],
            examples=[
                "navigate_to_website(website='youtube.com')",
                "navigate_to_website(website='google.com')",
            ]
        ))
        
        self.register_tool(Tool(
            name="search",
            description="Search for something on the currently open website or search engine",
            category="web_control",
            parameters=[
                ToolParameter("query", ParameterType.STRING, "Search query/term", required=True),
                ToolParameter("location", ParameterType.STRING, "Where to search (youtube, google, current_site, etc.)", required=False, default="current_site"),
            ],
            examples=[
                "search(query='python tutorial')",
                "search(query='relaxing music', location='youtube')",
            ]
        ))
        
        # ==============================================================
        # KEYBOARD & TEXT INPUT TOOLS
        # ==============================================================
        self.register_tool(Tool(
            name="type_text",
            description="Type text in the currently focused application",
            category="input_control",
            parameters=[
                ToolParameter("text", ParameterType.STRING, "Text to type", required=True),
            ],
            examples=[
                "type_text(text='hello world')",
                "type_text(text='my search query')",
            ]
        ))
        
        self.register_tool(Tool(
            name="press_key",
            description="Press a keyboard key or key combination",
            category="input_control",
            parameters=[
                ToolParameter("key", ParameterType.STRING, "Key to press (enter, space, ctrl+l, alt+tab, ctrl+c, etc.)", required=True),
            ],
            examples=[
                "press_key(key='enter')",
                "press_key(key='space')",
                "press_key(key='ctrl+l')",
            ]
        ))
        
        self.register_tool(Tool(
            name="press_keys_sequence",
            description="Press multiple keys in sequence",
            category="input_control",
            parameters=[
                ToolParameter("keys", ParameterType.ARRAY, "List of keys to press", required=True),
            ],
            examples=[
                "press_keys_sequence(keys=['ctrl+a', 'delete'])",
                "press_keys_sequence(keys=['home', 'shift+end'])",
            ]
        ))
        
        # ==============================================================
        # MEDIA CONTROL TOOLS
        # ==============================================================
        self.register_tool(Tool(
            name="play_media",
            description="Play media (music, video) in currently focused application",
            category="media_control",
            parameters=[
                ToolParameter("media_type", ParameterType.STRING, "Type of media (audio, video, music)", required=False, default="audio"),
            ],
            examples=[
                "play_media()",
                "play_media(media_type='music')",
            ]
        ))
        
        self.register_tool(Tool(
            name="pause_media",
            description="Pause media playback",
            category="media_control",
            parameters=[],
            examples=["pause_media()"]
        ))
        
        self.register_tool(Tool(
            name="stop_media",
            description="Stop media playback",
            category="media_control",
            parameters=[],
            examples=["stop_media()"]
        ))
        
        self.register_tool(Tool(
            name="next_track",
            description="Skip to next track/video",
            category="media_control",
            parameters=[],
            examples=["next_track()"]
        ))
        
        self.register_tool(Tool(
            name="previous_track",
            description="Go to previous track/video",
            category="media_control",
            parameters=[],
            examples=["previous_track()"]
        ))
        
        # ==============================================================
        # FILE MANAGEMENT TOOLS
        # ==============================================================
        self.register_tool(Tool(
            name="open_file",
            description="Open a file with default or specified application",
            category="file_management",
            parameters=[
                ToolParameter("file_path", ParameterType.STRING, "Path to the file", required=True),
                ToolParameter("app_name", ParameterType.STRING, "Application to open with (optional)", required=False),
            ],
            examples=[
                "open_file(file_path='C:/Users/Documents/file.txt')",
                "open_file(file_path='jarvis.py', app_name='vscode')",
            ]
        ))
        
        self.register_tool(Tool(
            name="create_file",
            description="Create a new file with content",
            category="file_management",
            parameters=[
                ToolParameter("file_path", ParameterType.STRING, "Path for the new file", required=True),
                ToolParameter("content", ParameterType.STRING, "Content to write", required=False, default=""),
            ],
            examples=[
                "create_file(file_path='notes.txt', content='My notes')",
            ]
        ))
        
        # ==============================================================
        # SYSTEM CONTROL TOOLS
        # ==============================================================
        self.register_tool(Tool(
            name="set_volume",
            description="Set system volume level",
            category="system_control",
            parameters=[
                ToolParameter("level", ParameterType.INTEGER, "Volume level (0-100)", required=True),
            ],
            examples=[
                "set_volume(level=50)",
                "set_volume(level=100)",
            ]
        ))
        
        self.register_tool(Tool(
            name="adjust_volume",
            description="Increase or decrease volume",
            category="system_control",
            parameters=[
                ToolParameter("direction", ParameterType.ENUM, "up or down", required=True, enum_values=["up", "down"]),
                ToolParameter("amount", ParameterType.INTEGER, "Amount to adjust (1-20)", required=False, default=5),
            ],
            examples=[
                "adjust_volume(direction='up', amount=10)",
                "adjust_volume(direction='down')",
            ]
        ))
        
        self.register_tool(Tool(
            name="set_brightness",
            description="Set screen brightness",
            category="system_control",
            parameters=[
                ToolParameter("level", ParameterType.INTEGER, "Brightness level (0-100)", required=True),
            ],
            examples=[
                "set_brightness(level=75)",
            ]
        ))
        
        self.register_tool(Tool(
            name="lock_screen",
            description="Lock the computer screen",
            category="system_control",
            parameters=[],
            examples=["lock_screen()"]
        ))
        
        self.register_tool(Tool(
            name="shutdown",
            description="Shutdown the computer",
            category="system_control",
            parameters=[
                ToolParameter("delay_seconds", ParameterType.INTEGER, "Delay before shutdown in seconds", required=False, default=0),
            ],
            examples=[
                "shutdown()",
                "shutdown(delay_seconds=60)",
            ]
        ))
        
        self.register_tool(Tool(
            name="restart",
            description="Restart the computer",
            category="system_control",
            parameters=[
                ToolParameter("delay_seconds", ParameterType.INTEGER, "Delay before restart in seconds", required=False, default=0),
            ],
            examples=[
                "restart()",
            ]
        ))
        
        self.register_tool(Tool(
            name="enable_wifi",
            description="Enable WiFi",
            category="system_control",
            parameters=[],
            examples=["enable_wifi()"]
        ))
        
        self.register_tool(Tool(
            name="disable_wifi",
            description="Disable WiFi",
            category="system_control",
            parameters=[],
            examples=["disable_wifi()"]
        ))
        
        self.register_tool(Tool(
            name="enable_bluetooth",
            description="Enable Bluetooth",
            category="system_control",
            parameters=[],
            examples=["enable_bluetooth()"]
        ))
        
        self.register_tool(Tool(
            name="disable_bluetooth",
            description="Disable Bluetooth",
            category="system_control",
            parameters=[],
            examples=["disable_bluetooth()"]
        ))
        
        # ==============================================================
        # INFORMATION TOOLS
        # ==============================================================
        self.register_tool(Tool(
            name="get_system_status",
            description="Get current system status (volume, brightness, wifi, etc.)",
            category="information",
            parameters=[],
            examples=["get_system_status()"]
        ))
        
        self.register_tool(Tool(
            name="get_time",
            description="Get current time",
            category="information",
            parameters=[],
            examples=["get_time()"]
        ))
        
        self.register_tool(Tool(
            name="get_weather",
            description="Get current weather (requires internet)",
            category="information",
            parameters=[
                ToolParameter("location", ParameterType.STRING, "City or location", required=False),
            ],
            examples=[
                "get_weather()",
                "get_weather(location='New York')",
            ]
        ))
    
    def register_tool(self, tool: Tool):
        """Register a tool in the registry"""
        self.tools[tool.name] = tool
    
    def get_tool(self, tool_name: str) -> Optional[Tool]:
        """Get a tool by name"""
        return self.tools.get(tool_name)
    
    def get_all_tools(self) -> List[Tool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def get_tools_by_category(self, category: str) -> List[Tool]:
        """Get all tools in a category"""
        return [t for t in self.tools.values() if t.category == category]
    
    def get_categories(self) -> List[str]:
        """Get all tool categories"""
        return sorted(set(t.category for t in self.tools.values()))
    
    def get_for_openai_function_calling(self) -> List[Dict]:
        """Get tools in OpenAI function calling format"""
        return [tool.to_dict() for tool in self.tools.values()]
    
    def get_for_prompt(self) -> str:
        """Get tools in text format for prompt"""
        text = "Available Tools:\n"
        text += "=" * 60 + "\n\n"
        
        for category in self.get_categories():
            text += f"\n### {category.upper().replace('_', ' ')}\n"
            text += "-" * 60 + "\n"
            for tool in self.get_tools_by_category(category):
                text += tool.to_prompt_text() + "\n"
        
        return text
    
    def validate_tool_call(self, tool_name: str, parameters: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate that a tool call has valid parameters
        Returns: (is_valid, error_message)
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return False, f"Tool '{tool_name}' not found"
        
        # Check required parameters
        required_params = {p.name for p in tool.parameters if p.required}
        provided_params = set(parameters.keys())
        
        missing = required_params - provided_params
        if missing:
            return False, f"Missing required parameters: {', '.join(missing)}"
        
        # Check parameter types (basic validation)
        for param_name, param_value in parameters.items():
            param_def = next((p for p in tool.parameters if p.name == param_name), None)
            if param_def and param_def.enum_values:
                if param_value not in param_def.enum_values:
                    return False, f"Parameter '{param_name}' must be one of: {param_def.enum_values}"
        
        return True, ""


# Global tool registry instance
tool_registry = ToolRegistry()


def get_tool_registry() -> ToolRegistry:
    """Get the global tool registry"""
    return tool_registry
