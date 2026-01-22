import os
import subprocess

def run_system(intent):
    action = intent["action"]

    if action == "cls":
        os.system("cls")
        return "🧹 Screen cleared"

    if action == "pwd":
        return os.getcwd()

    if action == "ls":
        return subprocess.call("dir", shell=True)

    if action == "cd":
        try:
            path = intent["path"]
            
            # If it's a relative path like "ai", look for it in current directory
            if not os.path.isabs(path) and not os.path.exists(path):
                # Try relative to current directory
                test_path = os.path.join(os.getcwd(), path)
                if os.path.exists(test_path):
                    path = test_path
            
            os.chdir(path)
            return f"📂 Current directory: {os.getcwd()}"
        except Exception as e:
            return f"❌ Error changing directory: {str(e)}"
