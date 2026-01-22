import os
import subprocess
import platform


EDITOR_ALIASES = {
    "notepad++": "notepad++",
    "notepad plus plus": "notepad++",
    "notepad": "notepad",
    "vscode": "code",
    "vs code": "code",
    "code": "code",
    "sublime": "subl",
    "atom": "atom",
    "vim": "vim",
    "nano": "nano",
}


def open_file(file_name: str, editor: str | None = None):
    file_name = file_name.strip()
    
    # Try multiple path variations
    possible_paths = [
        file_name,  # As given
        os.path.abspath(file_name),  # Absolute path
        os.path.join(os.getcwd(), file_name),  # In current directory
    ]
    
    # Also try in parent directories (useful for jarvis.py from ai/ folder)
    if not os.path.exists(file_name):
        base = os.getcwd()
        for _ in range(3):  # Try up to 3 parent directories
            test_path = os.path.join(base, file_name)
            if os.path.exists(test_path):
                possible_paths.insert(0, test_path)
                break
            base = os.path.dirname(base)
    
    # Find the first existing path
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = os.path.abspath(path)
            break

    if not file_path:
        return f"❌ File not found: {file_name} (searched in current directory and parent directories)"

    try:
        if platform.system() == "Windows":

            # open with specific editor
            if editor:
                editor = editor.lower().strip()
                editor_cmd = EDITOR_ALIASES.get(editor, editor)

                try:
                    subprocess.Popen(
                        f'start "" "{editor_cmd}" "{file_path}"',
                        shell=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return f"📄 Opened {file_name} in {editor}"
                except Exception as e:
                    # Fallback to default if editor fails
                    pass

            # default Windows file open
            subprocess.Popen(
                f'start "" "{file_path}"',
                shell=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return f"📄 Opened {file_name}"

        # Linux / Mac
        if editor:
            editor = editor.lower().strip()
            editor_cmd = EDITOR_ALIASES.get(editor, editor)
            subprocess.Popen([editor_cmd, file_path])
            return f"📄 Opened {file_name} in {editor}"
        
        subprocess.Popen(["xdg-open", file_path])
        return f"📄 Opened {file_name}"

    except Exception as e:
        return f"❌ Error opening file: {str(e)}"
