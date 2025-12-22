import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import sys
import logging
from PIL import Image, ImageTk  # Requires Pillow, need to check if available or use simple labels

# --- Pfad-Hack für direkten Aufruf ---
if __name__ == "__main__" or __package__ is None:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    interfaces_dir = os.path.dirname(current_dir)
    smartdesk_dir = os.path.dirname(interfaces_dir)
    src_dir = os.path.dirname(smartdesk_dir)
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)

# --- Logger Setup ---
try:
    from smartdesk.shared.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

# --- Abgerundete Ecken (nur Windows) ---
try:
    import win32gui
    import ctypes
except ImportError:
    win32gui = None
    ctypes = None
    logger.info("'pywin32' nicht gefunden.")

# --- Projekt-Imports ---
try:
    from smartdesk.core.services import desktop_service
    from smartdesk.core.services import wallpaper_service
    from smartdesk.shared.localization import get_text
    from smartdesk.core.storage.file_operations import save_desktops, load_desktops as load_desktops_from_storage
except ImportError as e:
    logger.error(f"FATALER FEHLER: {e}")
    # Mocking for testing if imports fail
    def get_text(key, **kwargs):
        return key.split('.')[-1]
    desktop_service = None
    wallpaper_service = None

class DesktopManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(get_text("gui.manage_dialog.title"))
        
        # Fenster initial verstecken für die Animation
        self.root.withdraw()

        self.window_width = 600
        self.window_height = 450

        # Bildschirmabmessungen sicher ermitteln
        try:
            self.root.update_idletasks()
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            if screen_width <= 0 or screen_height <= 0:
                screen_width = 1920
                screen_height = 1080
        except Exception:
            screen_width = 1920
            screen_height = 1080

        self.screen_width = screen_width
        self.screen_height = screen_height

        # Position für unten rechts berechnen
        padding_x = 20
        padding_y = 60

        self.target_x = max(0, screen_width - self.window_width - padding_x)
        self.y_pos = max(0, screen_height - self.window_height - padding_y)

        # Animation Setup
        self.start_x = screen_width
        self.current_x = self.start_x
        self.is_animating = True
        self.is_closing = False
        self._animation_id = None

        self.root.geometry(f"{self.window_width}x{self.window_height}+{self.current_x}+{self.y_pos}")
        self.root.resizable(False, False)
        self.root.overrideredirect(True)

        # --- Farben ---
        self.bg_dark = "#2b2b2b"
        self.bg_list = "#333333"
        self.bg_input = "#3c3c3c"
        self.fg_primary = "#ffffff"
        self.fg_secondary = "#aaaaaa"
        self.accent = "#14a085"
        self.accent_hover = "#0d7377"
        self.accent_red = "#d9534f"
        self.accent_red_hover = "#c9302c"
        self.button_bg = "#3c3c3c"
        self.button_hover = "#4a4a4a"

        self.root.configure(bg=self.bg_dark)

        # --- UI Aufbau ---
        self.setup_ui()

        # Fenster anzeigen und Animation starten
        self.root.deiconify()
        self.root.update_idletasks()
        self._animation_id = self.root.after(50, self.animate_slide_in_from_right)
        self.root.after(100, self.apply_rounded_corners)
        self.root.after(200, self._request_focus)

        # Daten laden
        self.load_desktops()

    def setup_ui(self):
        # Hauptcontainer
        main_frame = tk.Frame(self.root, bg=self.bg_dark)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Titel
        title_frame = tk.Frame(main_frame, bg=self.bg_dark)
        title_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            title_frame, 
            text=get_text("gui.manage_dialog.header"), 
            font=('Segoe UI', 14, 'bold'),
            bg=self.bg_dark, 
            fg=self.fg_primary
        ).pack(side=tk.LEFT)

        # Content Area (Split View)
        content_frame = tk.Frame(main_frame, bg=self.bg_dark)
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Linke Seite: Liste
        left_frame = tk.Frame(content_frame, bg=self.bg_dark, width=200)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        left_frame.pack_propagate(False)

        tk.Label(
            left_frame,
            text=get_text("gui.manage_dialog.list_label"),
            font=('Segoe UI', 9, 'bold'),
            bg=self.bg_dark,
            fg=self.fg_secondary,
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 5))

        self.desktop_listbox = tk.Listbox(
            left_frame,
            bg=self.bg_list,
            fg=self.fg_primary,
            selectbackground=self.accent,
            selectforeground=self.fg_primary,
            relief=tk.FLAT,
            bd=0,
            font=('Segoe UI', 10),
            activestyle='none'
        )
        self.desktop_listbox.pack(fill=tk.BOTH, expand=True)
        self.desktop_listbox.bind('<<ListboxSelect>>', self.on_desktop_select)

        # Rechte Seite: Details
        self.right_frame = tk.Frame(content_frame, bg=self.bg_dark)
        self.right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Details Container (initial versteckt oder leer)
        self.details_container = tk.Frame(self.right_frame, bg=self.bg_dark)
        self.details_container.pack(fill=tk.BOTH, expand=True)

        # Name
        tk.Label(
            self.details_container,
            text=get_text("gui.manage_dialog.details_name"),
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_secondary,
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 3))

        self.name_entry = tk.Entry(
            self.details_container,
            font=('Segoe UI', 10),
            bg=self.bg_input,
            fg=self.fg_primary,
            insertbackground=self.fg_primary,
            relief=tk.FLAT,
            bd=0
        )
        self.name_entry.pack(fill=tk.X, ipady=6, pady=(0, 15))

        # Pfad (Read-only Info)
        tk.Label(
            self.details_container,
            text=get_text("gui.manage_dialog.details_path"),
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_secondary,
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 3))

        self.path_label = tk.Label(
            self.details_container,
            text="-",
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_secondary,
            anchor='w',
            wraplength=350,
            justify=tk.LEFT
        )
        self.path_label.pack(fill=tk.X, pady=(0, 15))

        # Wallpaper
        tk.Label(
            self.details_container,
            text=get_text("gui.manage_dialog.details_wallpaper"),
            font=('Segoe UI', 9),
            bg=self.bg_dark,
            fg=self.fg_secondary,
            anchor='w'
        ).pack(fill=tk.X, pady=(0, 3))

        wallpaper_frame = tk.Frame(self.details_container, bg=self.bg_dark)
        wallpaper_frame.pack(fill=tk.X, pady=(0, 15))

        self.wallpaper_path_label = tk.Label(
            wallpaper_frame,
            text=get_text("gui.manage_dialog.wallpaper_none"),
            font=('Segoe UI', 9, 'italic'),
            bg=self.bg_dark,
            fg=self.fg_secondary,
            anchor='w',
            wraplength=250
        )
        self.wallpaper_path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(
            wallpaper_frame,
            text=get_text("gui.manage_dialog.button_change"),
            font=('Segoe UI', 9),
            bg=self.button_bg,
            fg=self.fg_primary,
            activebackground=self.button_hover,
            activeforeground=self.fg_primary,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self.change_wallpaper
        ).pack(side=tk.RIGHT, padx=(10, 0))

        # Buttons unten
        button_frame = tk.Frame(self.root, bg=self.bg_dark)
        button_frame.pack(fill=tk.X, padx=20, pady=20)

        # Delete Button (Links)
        self.delete_btn = tk.Button(
            button_frame,
            text=get_text("gui.common.button_delete"),
            font=('Segoe UI', 9),
            bg=self.accent_red,
            fg="#ffffff",
            activebackground=self.accent_red_hover,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.delete_desktop
        )
        self.delete_btn.pack(side=tk.LEFT)

        # Save & Close Buttons (Rechts)
        tk.Button(
            button_frame,
            text=get_text("gui.common.button_close"),
            font=('Segoe UI', 9),
            bg=self.button_bg,
            fg=self.fg_primary,
            activebackground=self.button_hover,
            activeforeground=self.fg_primary,
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.close_window
        ).pack(side=tk.RIGHT)

        self.save_btn = tk.Button(
            button_frame,
            text=get_text("gui.common.button_save"),
            font=('Segoe UI', 9),
            bg=self.accent,
            fg="#ffffff",
            activebackground=self.accent_hover,
            activeforeground="#ffffff",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=5,
            cursor="hand2",
            command=self.save_changes
        )
        self.save_btn.pack(side=tk.RIGHT, padx=(0, 10))

    def load_desktops(self):
        self.desktop_listbox.delete(0, tk.END)
        self.desktops = desktop_service.get_all_desktops()
        for d in self.desktops:
            name = d.name
            if d.is_active:
                name += get_text("gui.common.status_active")
            if d.protected:
                name += get_text("gui.common.status_protected")
            self.desktop_listbox.insert(tk.END, name)
        
        # Reset UI
        self.current_desktop = None
        self.name_entry.delete(0, tk.END)
        self.path_label.config(text="-")
        self.wallpaper_path_label.config(text=get_text("gui.manage_dialog.wallpaper_none"))
        self.save_btn.config(state=tk.DISABLED, bg=self.button_bg)
        self.delete_btn.config(state=tk.DISABLED, bg=self.button_bg)

    def on_desktop_select(self, event):
        selection = self.desktop_listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        self.current_desktop = self.desktops[index]
        
        # Fill UI
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, self.current_desktop.name)
        self.path_label.config(text=self.current_desktop.path)
        
        wp = self.current_desktop.wallpaper_path
        if wp and os.path.exists(wp):
            self.wallpaper_path_label.config(text=os.path.basename(wp))
        else:
            self.wallpaper_path_label.config(text=get_text("gui.manage_dialog.wallpaper_none"))

        # Enable Buttons
        self.save_btn.config(state=tk.NORMAL, bg=self.accent)
        
        if self.current_desktop.protected or self.current_desktop.is_active:
            self.delete_btn.config(state=tk.DISABLED, bg=self.button_bg)
        else:
            self.delete_btn.config(state=tk.NORMAL, bg=self.accent_red)

        if self.current_desktop.protected:
             self.name_entry.config(state=tk.DISABLED)
        else:
             self.name_entry.config(state=tk.NORMAL)

    def change_wallpaper(self):
        if not self.current_desktop:
            return
            
        file_path = filedialog.askopenfilename(
            title=get_text("gui.main.wallpaper.browse_title"),
            filetypes=[(get_text("gui.main.wallpaper.file_types"), "*.jpg *.jpeg *.png *.bmp")]
        )
        
        if file_path:
            # Direkt zuweisen via Service
            success = desktop_service.assign_wallpaper(self.current_desktop.name, file_path)
            if success:
                # Reload data to get new path
                self.load_desktops()
                # Reselect current
                for i, d in enumerate(self.desktops):
                    if d.name == self.current_desktop.name:
                        self.desktop_listbox.selection_set(i)
                        self.on_desktop_select(None)
                        break
                messagebox.showinfo(get_text("gui.common.success_title"), get_text("gui.manage_dialog.success_wallpaper"))
            else:
                messagebox.showerror(get_text("gui.common.error_title"), get_text("gui.manage_dialog.error_wallpaper"))

    def save_changes(self):
        if not self.current_desktop:
            return
            
        new_name = self.name_entry.get().strip()
        if not new_name:
            messagebox.showerror(get_text("gui.common.error_title"), get_text("gui.manage_dialog.error_empty_name"))
            return
            
        if new_name == self.current_desktop.name:
            return # Nichts zu tun
            
        success = desktop_service.update_desktop(
            self.current_desktop.name,
            new_name,
            self.current_desktop.path # Pfad bleibt gleich
        )
        
        if success:
            messagebox.showinfo(get_text("gui.common.success_title"), get_text("gui.manage_dialog.success_save"))
            self.load_desktops()
        else:
            messagebox.showerror(get_text("gui.common.error_title"), get_text("gui.manage_dialog.error_save"))

    def delete_desktop(self):
        if not self.current_desktop:
            return
            
        if messagebox.askyesno(get_text("gui.common.confirm_title"), get_text("gui.manage_dialog.msgbox_delete_confirm_text", name=self.current_desktop.name)):
            # Wir nutzen hier eine angepasste Logik, da desktop_service.delete_desktop input() verwendet
            try:
                # 1. Check Active
                if self.current_desktop.is_active:
                    messagebox.showerror(get_text("gui.common.error_title"), get_text("gui.manage_dialog.error_delete_active"))
                    return

                # 2. Check Protected
                if self.current_desktop.protected:
                    messagebox.showerror(get_text("gui.common.error_title"), get_text("gui.manage_dialog.error_delete_protected"))
                    return

                # 3. Delete Wallpaper
                if self.current_desktop.wallpaper_path and os.path.exists(self.current_desktop.wallpaper_path):
                    try:
                        os.remove(self.current_desktop.wallpaper_path)
                    except Exception as e:
                        logger.warning(f"Konnte Wallpaper nicht löschen: {e}")

                # 4. Remove from list and save
                # Wir müssen die Liste neu laden um sicherzugehen
                desktops = load_desktops_from_storage()
                target = next((d for d in desktops if d.name == self.current_desktop.name), None)
                if target:
                    desktops.remove(target)
                    save_desktops(desktops)
                    messagebox.showinfo(get_text("gui.common.success_title"), get_text("desktop_handler.success.delete", name=target.name))
                    self.load_desktops()
                else:
                    messagebox.showerror(get_text("gui.common.error_title"), get_text("gui.manage_dialog.error_not_found"))

            except Exception as e:
                logger.error(f"Fehler beim Löschen: {e}")
                messagebox.showerror(get_text("gui.common.error_title"), get_text("gui.main.generic_errors.delete", e=e))

    # --- Animation & Window Management (Copy-Paste from gui_create.py) ---
    def _request_focus(self):
        try:
            self.root.lift()
            self.root.focus_force()
            if win32gui:
                try:
                    frame_hwnd = self.root.winfo_id()
                    hwnd = win32gui.GetParent(frame_hwnd) or frame_hwnd
                    win32gui.SetForegroundWindow(hwnd)
                except Exception:
                    pass
        except Exception:
            pass

    def apply_rounded_corners(self):
        if not win32gui: return
        try:
            self.root.update_idletasks()
            frame_hwnd = self.root.winfo_id()
            hwnd = win32gui.GetParent(frame_hwnd) or frame_hwnd
            if self._try_dwm_rounded_corners(hwnd): return
            self._apply_region_rounded_corners(hwnd)
        except Exception: pass

    def _try_dwm_rounded_corners(self, hwnd):
        if not ctypes: return False
        try:
            DWMWA_WINDOW_CORNER_PREFERENCE = 33
            DWMWCP_ROUND = 2
            dwmapi = ctypes.windll.dwmapi
            preference = ctypes.c_int(DWMWCP_ROUND)
            result = dwmapi.DwmSetWindowAttribute(hwnd, DWMWA_WINDOW_CORNER_PREFERENCE, ctypes.byref(preference), ctypes.sizeof(preference))
            return result == 0
        except Exception: return False

    def _apply_region_rounded_corners(self, hwnd):
        try:
            rect = win32gui.GetWindowRect(hwnd)
            width = rect[2] - rect[0]
            height = rect[3] - rect[1]
            radius = 20
            hrgn = win32gui.CreateRoundRectRgn(0, 0, width + 1, height + 1, radius, radius)
            win32gui.SetWindowRgn(hwnd, hrgn, True)
        except Exception: pass

    def close_window(self):
        if self.is_closing: return
        self.is_closing = True
        self.is_animating = False
        if self._animation_id:
            try: self.root.after_cancel(self._animation_id)
            except Exception: pass
            self._animation_id = None
        self.animate_slide_out_to_right()

    def animate_slide_out_to_right(self):
        if not self.is_closing: return
        try:
            if not self.root.winfo_exists():
                self._final_cleanup()
                return
        except tk.TclError:
            self._final_cleanup()
            return
        
        delay_ms = 10
        ease_factor = 0.20
        if self.current_x >= self.screen_width:
            self._final_cleanup()
        else:
            distance_to_go = self.screen_width - self.current_x
            step = max(3, int(distance_to_go * ease_factor))
            self.current_x += step
            self._set_geometry(self.current_x)
            self.root.after(delay_ms, self.animate_slide_out_to_right)

    def _final_cleanup(self):
        try:
            self.root.quit()
            self.root.destroy()
        except Exception: pass

    def animate_slide_in_from_right(self):
        if not self.is_animating or self.is_closing: return
        try:
            if not self.root.winfo_exists(): return
        except tk.TclError: return
        
        delay_ms = 10
        ease_factor = 0.20
        distance_to_go = self.current_x - self.target_x
        
        if distance_to_go <= 1:
            self.current_x = self.target_x
            self.is_animating = False
            self._set_geometry(self.target_x)
            self._animation_id = None
        else:
            step = max(1, int(distance_to_go * ease_factor))
            self.current_x -= step
            self._set_geometry(self.current_x)
            self._animation_id = self.root.after(delay_ms, self.animate_slide_in_from_right)

    def _set_geometry(self, x_pos):
        try:
            x = max(0, int(x_pos))
            y = max(0, int(self.y_pos))
            self.root.geometry(f"{self.window_width}x{self.window_height}+{x}+{y}")
        except Exception: pass

def show_manage_desktops_window():
    try:
        root = tk.Tk()
        DesktopManagerGUI(root)
        root.mainloop()
    except Exception as e:
        logger.error(f"Fehler beim Starten: {e}")

if __name__ == "__main__":
    show_manage_desktops_window()
