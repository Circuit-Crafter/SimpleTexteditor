#!/usr/bin/env python3
# Version: 1.2
# Last Updated: 2026-06-14
"""Very simple text editor with Tkinter and Dark Mode."""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sys
import os
import subprocess

class SimpleTextEditor:
    def __init__(self, root):
        self.root = root
        

        self.dark_mode = True
        
        # Dark Mode Colors
        self.root_bg_dark = "#1e1e1e"
        self.text_bg_dark = "#212121"
        self.text_fg_dark = "#e0e0e0"
        self.menu_bg_dark = "#242424"
        self.menu_fg_dark = "#e0e0e0"
        # Light Mode Colors
        self.root_bg_light = "#e0e0e0"
        self.text_bg_light = "#ffffff"
        self.text_fg_light = "#1e1e1e"
        self.menu_bg_light = "#f0f0f0"
        self.menu_fg_light = "#1e1e1e"

        # Colors
        self.root_bg_color =  self.root_bg_dark
        self.text_bg_color = self.text_bg_dark
        self.text_fg_color = self.text_fg_dark
        self.menu_bg_color = self.menu_bg_dark
        self.menu_fg_color = self.menu_fg_dark

        # Icon
        icon_path = self._get_icon_path()
        try:
            icon_image = Image.open(icon_path)
            icon_image = icon_image.resize((32, 32), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(icon_image)
            self.root.iconphoto(True, photo)
            self.photo = photo
        except Exception:
            pass
        
        self.root.title("Simple Text Editor")
        self.root.geometry("900x700")
        self.root.config(bg=self.root_bg_color)
        
        self.filename = None
        
        self.text = tk.Text(
            self.root,
            undo=True,
            autoseparators=True,
            maxundo=-1,
            wrap="word",
            bg=self.text_bg_color,
            fg=self.text_fg_color,
            insertbackground=self.text_fg_color
        )
        self.text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Status Bar
        self.status = tk.StringVar()
        self.status.set("New Document")
        status_bar = tk.Label(self.root, textvariable=self.status, anchor=tk.W,
                             bg=self.menu_bg_color, fg=self.menu_fg_color)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=2, pady=2)
        
        self.menu_bar = tk.Menu(self.root, bg=self.menu_bg_color, fg=self.menu_fg_color)
        self._create_file_menu()
        self._create_view_menu()
        self._bind_shortcuts()
        self.root.config(menu=self.menu_bar)
        
        # Ask save when closed
        self.root.protocol("WM_DELETE_WINDOW", self.exit_editor)

    def _get_icon_path(self):
        """Returns the correct icon path."""
        if hasattr(sys, "_MEIPASS"):
            return os.path.join(sys._MEIPASS, "icon.png")
        else:
            return "icon.png"
    
    def _create_file_menu(self):
        

        file_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.menu_bg_color , fg=self.menu_fg_color)#color change
        file_menu.add_command(label="New", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Open...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Save", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", accelerator="Ctrl+Q", command=self.exit_editor)
        self.file_menu = file_menu
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        
    def _toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        if not self.dark_mode:
            self.root_bg_color =  self.root_bg_light
            self.text_bg_color = self.text_bg_light
            self.text_fg_color = self.text_fg_light
            self.menu_bg_color = self.menu_bg_light
            self.menu_fg_color = self.menu_fg_light
        else:
            self.root_bg_color =  self.root_bg_dark
            self.text_bg_color = self.text_bg_dark
            self.text_fg_color = self.text_fg_dark
            self.menu_bg_color = self.menu_bg_dark
            self.menu_fg_color = self.menu_fg_dark
        # Root
        self.root.config(bg=self.root_bg_color)

        # Text
        self.text.config(
            bg=self.text_bg_color,
            fg=self.text_fg_color,
            insertbackground=self.text_fg_color
        )

        # Statusbar
        for widget in self.root.pack_slaves():
            if isinstance(widget, tk.Label):
                widget.config(bg=self.menu_bg_color, fg=self.menu_fg_color)

        #Menu
        self.menu_bar.config(bg=self.menu_bg_color, fg=self.menu_fg_color)
        self.file_menu.config(bg=self.menu_bg_color, fg=self.menu_fg_color)
        self.view_menu.config(bg=self.menu_bg_color, fg=self.menu_fg_color)
        if self.dark_mode:
            self.view_menu.entryconfig(0, label="Light Mode")
        else:
            self.view_menu.entryconfig(0, label="Dark Mode")

        



    def _create_view_menu(self):

        self.view_menu = tk.Menu(self.menu_bar, tearoff=0, bg=self.menu_bg_color, fg=self.menu_fg_color)
        self.view_menu.add_command(label="Light Mode", command=self._toggle_dark_mode)

        self.menu_bar.add_cascade(label="View", menu=self.view_menu)

    def _bind_shortcuts(self):
        self.root.bind("<Control-n>", lambda event: self.new_file())
        self.root.bind("<Control-o>", lambda event: self.open_file())
        self.root.bind("<Control-s>", lambda event: self.save_file())
        self.root.bind("<Control-q>", lambda event: self.exit_editor())
        self.root.bind('<Control-a>', self.select_all)
        self.root.bind('<Control-BackSpace>', self.delete_previous_word)
        # Bind clipboard shortcuts to the Text widget to override
        # the widget default handlers and avoid duplicate actions.
        self.text.bind("<Control-c>", self.copy_text)
        self.text.bind("<Control-x>", self.cut_text)
        self.text.bind("<Control-v>", self.paste_text)
        self.text.bind("<Control-y>", self.redo)
        self.text.bind("<Key>", self._on_key)
        self.root.bind("<Control-w>",sys.exit)

    def _on_key(self, event=None):
        if event.keysym in ("space", "Return", "BackSpace", "Delete"):
            self.text.edit_separator()
        if self.filename:
            self._set_status(f"Modified: {self.filename}")
    def undo(self, event=None):
        try:
            self.text.edit_undo()
        except:
            pass
        return "break"

    def redo(self, event=None):
        try:
            self.text.edit_redo()
        except:
            pass
        return "break"
    def select_all(self, event=None):
        self.text.tag_add('sel', '1.0', 'end')
        self.text.mark_set('insert', '1.0')
        self.text.see('insert')
        return 'break'
    
    def delete_previous_word(self, event=None):
        try:
            cursor_pos = self.text.index(tk.INSERT)
            prev_word_start = self.text.search(r'\m\w+', cursor_pos, backwards=True, regexp=True)

            if not prev_word_start:
                prev_word_start = "1.0"

            self.text.delete(prev_word_start, cursor_pos)

        except Exception:
            pass

        return "break"

    import subprocess

    def copy_text(self, event=None):
        try:
            selection = self.text.get("sel.first", "sel.last")
            if selection:
                subprocess.run(
                    ["wl-copy"],
                    input=selection,
                    text=True,
                    check=False
                )
        except tk.TclError:
            pass
        return "break"

    def cut_text(self, event=None):
        try:
            selection = self.text.get("sel.first", "sel.last")
            if selection:
                subprocess.run(
                    ["wl-copy"],
                    input=selection,
                    text=True,
                    check=False
                )
                self.text.delete("sel.first", "sel.last")
        except tk.TclError:
            pass
        return "break"

    def paste_text(self, event=None):
        """Inserts text from the clipboard."""
        try:
            clipboard_content = self.root.clipboard_get()
            self.text.insert(tk.INSERT, clipboard_content)
        except tk.TclError:
            pass
        return "break"


    def _set_status(self, text):
        self.status.set(text)

    def new_file(self):
        if self._ask_save_if_modified():
            self.text.delete("1.0", tk.END)
            self.text.edit_modified(False)
            self.filename = None
            self._set_status("New Document")

    def open_file(self):
        if not self._ask_save_if_modified():
            return
        path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text.delete("1.0", tk.END)
                self.text.insert(tk.END, content)
                self.text.edit_modified(False)
                self.filename = path
                self._set_status(f"Opened: {self.filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open: {e}")

    def save_file(self):
        if self.filename is None:
            return self.save_file_as()
        try:
            with open(self.filename, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END))
            self.text.edit_modified(False)
            self._set_status(f"Saved: {self.filename}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Couldn't save: {e}")
            return False

    def save_file_as(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not path:
            return False
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.text.get("1.0", tk.END))
            self.text.edit_modified(False)
            self.filename = path
            self._set_status(f"Saved: {self.filename}")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Could not save: {e}")
            return False

    def _ask_save_if_modified(self):
        if self.text.edit_modified():
            answer = messagebox.askyesnocancel("Save", "Save changes?")
            if answer is None:
                return False
            if answer:
                return self.save_file()
        return True

    def exit_editor(self):
        if self._ask_save_if_modified():
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleTextEditor(root)
    if len(sys.argv) > 1:
        path = sys.argv[1]
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                app.text.insert("1.0", content)
                app.text.edit_modified(False)
                app.filename = path
                app._set_status(f"Opened: {path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not open: {e}")
    root.mainloop()
