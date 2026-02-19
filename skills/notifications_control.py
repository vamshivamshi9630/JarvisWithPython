"""
Notifications & Alerts Module

Display notifications to user:
- Windows notifications
- Toast notifications
- Alert dialogs
- Reminder alerts
"""

from typing import Dict, Any

try:
    from win10toast import ToastNotifier
    HAS_TOAST = True
except ImportError:
    HAS_TOAST = False

try:
    from plyer import notification
    HAS_PLYER = True
except ImportError:
    HAS_PLYER = False

try:
    import tkinter as tk
    from tkinter import messagebox
    HAS_TKINTER = True
except ImportError:
    HAS_TKINTER = False


def show_notification(title: str, message: str, duration: int = 5) -> Dict[str, Any]:
    """Show Windows 10 toast notification"""
    if HAS_TOAST:
        try:
            notifier = ToastNotifier()
            notifier.show_toast(title, message, duration=duration, threaded=True)
            return {"title": title, "message": message, "message": f"Notification: {title}"}
        except Exception as e:
            pass
    
    # Fallback to plyer if win10toast fails
    if HAS_PLYER:
        try:
            notification.notify(
                title=title,
                message=message,
                timeout=duration
            )
            return {"title": title, "message": message, "message": f"Notification: {title}"}
        except Exception as e:
            pass
    
    return {"error": "Notification system not available", "message": "Could not show notification"}


def show_alert(title: str, message: str) -> Dict[str, Any]:
    """Show alert dialog"""
    if HAS_TKINTER:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showinfo(title, message)
            root.destroy()
            return {"title": title, "message": message, "message": f"Alert: {title}"}
        except Exception as e:
            pass
    
    # Fallback to notification
    return show_notification(title, message)


def show_warning(title: str, message: str) -> Dict[str, Any]:
    """Show warning dialog"""
    if HAS_TKINTER:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showwarning(title, message)
            root.destroy()
            return {"title": title, "message": message, "message": f"Warning: {title}"}
        except Exception as e:
            pass
    
    return show_notification(title, message)


def show_error(title: str, message: str) -> Dict[str, Any]:
    """Show error dialog"""
    if HAS_TKINTER:
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(title, message)
            root.destroy()
            return {"title": title, "message": message, "message": f"Error: {title}"}
        except Exception as e:
            pass
    
    return show_notification(title, message)


def show_question(title: str, message: str) -> Dict[str, Any]:
    """Show yes/no question dialog"""
    if HAS_TKINTER:
        try:
            root = tk.Tk()
            root.withdraw()
            result = messagebox.askyesno(title, message)
            root.destroy()
            return {
                "title": title,
                "message": message,
                "result": "Yes" if result else "No",
                "message": f"Question: {title} -> {'Yes' if result else 'No'}"
            }
        except Exception as e:
            pass
    
    return {"message": "Question dialog not available"}


def show_reminder(title: str, message: str, delay_seconds: int = 0) -> Dict[str, Any]:
    """Show reminder notification"""
    try:
        import threading
        import time
        
        def delay_notify():
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            show_notification(title, message)
        
        thread = threading.Thread(target=delay_notify, daemon=True)
        thread.start()
        
        return {
            "title": title,
            "message": message,
            "delay": delay_seconds,
            "message": f"Reminder set: {title} in {delay_seconds}s"
        }
    except Exception as e:
        return {"error": str(e), "message": "Could not set reminder"}
