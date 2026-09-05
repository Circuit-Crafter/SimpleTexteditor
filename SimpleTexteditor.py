#!/usr/bin/env python3
# Version: 1.4-0
# Last Updated: 2026-09-04
"""Very simple text editor with Tkinter and Dark Mode."""

import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import sys
import os
import subprocess
import shutil
import tkinter.font as tkfont

class SimpleTextEditor:
    def __init__(self, root):
        self.root = root
        self._setup_view_values()

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
        self.root.geometry("900x550")
        self.root.config(bg=self.root_bg_color)
        
        self.filename = None
        
        self.editor_frame = tk.Frame(
            self.root,
            bg=self.root_bg_color
        )

        self.editor_frame.pack(
            fill=tk.BOTH,
            expand=True,
            padx=5,
            pady=5
        )
        self.scrollbar = tk.Scrollbar(
            self.editor_frame,
            orient=tk.VERTICAL,
            bg=self.scrollbar_bg_color,
            troughcolor=self.scrollbar_trough_color,
            activebackground=self.scrollbar_active_color,
            width=12,
            relief=tk.FLAT
        )
        self.h_scrollbar = tk.Scrollbar(
        self.editor_frame,
        orient=tk.HORIZONTAL,
        bg=self.scrollbar_bg_color,
        troughcolor=self.scrollbar_trough_color,
        activebackground=self.scrollbar_active_color,
        width=12,
        relief=tk.FLAT
    )




        self.text = tk.Text(
            self.editor_frame,
            undo=True,
            autoseparators=True,
            maxundo=-1,
            wrap="none",
            height=1,
            font=self.editor_font,
            bg=self.text_bg_color,
            fg=self.text_fg_color,
            insertbackground=self.text_fg_color
        )
        #Configure search highlight tag
        self.text.tag_configure("search_match",background="#ffff00",foreground="#000000")
        

        # Link scrollbar and text
        self.scrollbar.config(command=self.text.yview)
        self.h_scrollbar.config(command=self.text.xview)

        self.text.config(
            yscrollcommand=self.scrollbar.set,
            xscrollcommand=self.h_scrollbar.set
        )


        self.scrollbar.pack(
            side=tk.RIGHT,
            fill=tk.Y
        )
        self.h_scrollbar.pack(
            side=tk.BOTTOM,
            fill=tk.X
        )

        self.text.pack(
            side=tk.LEFT,
            fill=tk.BOTH,
            expand=True
        )
        
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
            self.scrollbar_bg_color = self.scrollbar_bg_light
            self.scrollbar_trough_color = self.scrollbar_trough_light
            self.scrollbar_active_color = self.scrollbar_active_light
        else:
            self.root_bg_color =  self.root_bg_dark
            self.text_bg_color = self.text_bg_dark
            self.text_fg_color = self.text_fg_dark
            self.menu_bg_color = self.menu_bg_dark
            self.menu_fg_color = self.menu_fg_dark
            self.scrollbar_bg_color = self.scrollbar_bg_dark
            self.scrollbar_trough_color = self.scrollbar_trough_dark
            self.scrollbar_active_color = self.scrollbar_active_dark
        # Root
        self.root.config(bg=self.root_bg_color)

        # Text
        self.text.config(
            bg=self.text_bg_color,
            fg=self.text_fg_color,
            insertbackground=self.text_fg_color
        )
        
        # Scrollbar
        self.scrollbar.config(
            bg=self.scrollbar_bg_color,
            troughcolor=self.scrollbar_trough_color,
            activebackground=self.scrollbar_active_color
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

        


    def _setup_view_values(self):
        self.dark_mode = True
        
        # Dark Mode Colors
        self.root_bg_dark = "#1e1e1e"
        self.text_bg_dark = "#212121"
        self.text_fg_dark = "#f1f1f1"
        self.menu_bg_dark = "#242424"
        self.menu_fg_dark = "#e0e0e0"
        # Light Mode Colors
        self.root_bg_light = "#e0e0e0"
        self.text_bg_light = "#ffffff"
        self.text_fg_light = "#1e1e1e"
        self.menu_bg_light = "#f0f0f0"
        self.menu_fg_light = "#1e1e1e"
        
        # Scrollbar Colors (Dark Mode)
        self.scrollbar_bg_dark = "#2a2a2a"
        self.scrollbar_trough_dark = "#1e1e1e"
        self.scrollbar_active_dark = "#444444"
        
        # Scrollbar Colors (Light Mode)
        self.scrollbar_bg_light = "#d0d0d0"
        self.scrollbar_trough_light = "#f5f5f5"
        self.scrollbar_active_light = "#b0b0b0"

        # Colors
        self.root_bg_color =  self.root_bg_dark
        self.text_bg_color = self.text_bg_dark
        self.text_fg_color = self.text_fg_dark
        self.menu_bg_color = self.menu_bg_dark
        self.menu_fg_color = self.menu_fg_dark
        self.scrollbar_bg_color = self.scrollbar_bg_dark
        self.scrollbar_trough_color = self.scrollbar_trough_dark
        self.scrollbar_active_color = self.scrollbar_active_dark
        
        #Font
        self.font_family = "TkFixedFont"
        self.font_size = 12
        self.min_font_size = 8
        self.max_font_size = 48
        self.editor_font = tkfont.Font(
            family=self.font_family,
            size=self.font_size
        )
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
        
        
        #Zoom keys
        self.text.bind("<Control-MouseWheel>", self.zoom_mousewheel)
        # for Linux mouse wheel
        self.text.bind("<Control-Button-4>", self.zoom_in)
        self.text.bind("<Control-Button-5>", self.zoom_out)
        # for Keyboard zoom
        self.text.bind("<Control-KeyPress>", self.zoom_keyboard)
        self.root.bind("<Control-f>", self.open_search)


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


    def copy_text(self, event=None):
        try:
            selection = self.text.get("sel.first", "sel.last")

            if not selection:
                return "break"

            if shutil.which("wl-copy"):
                subprocess.run(
                    ["wl-copy"],
                    input=selection,
                    text=True,
                    check=False
                )

            elif shutil.which("xclip"):
                subprocess.run(
                    ["xclip", "-selection", "clipboard"],
                    input=selection,
                    text=True,
                    check=False
                )

            else:
                self.root.clipboard_clear()
                self.root.clipboard_append(selection)
                self.root.update()

        except tk.TclError:
            pass

        return "break"

    def cut_text(self, event=None):
        try:
            self.copy_text()

            if self.text.tag_ranges("sel"):
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


    #Zoom related funktions
    def _update_zoom_status(self):
        zoom_percent = round((self.font_size / 12) * 100)

        if self.filename:
            self._set_status(
                f"{self.filename} — Zoom: {zoom_percent}%"
            )
        else:
            self._set_status(
                f"New Document — Zoom: {zoom_percent}%"
            )
    def zoom_in(self, event=None):
        if self.font_size < self.max_font_size:
            self.font_size += 1
            self.editor_font.configure(size=self.font_size)
            self._update_zoom_status()

        return "break"
    def zoom_out(self, event=None):
        if self.font_size > self.min_font_size:
            self.font_size -= 1
            self.editor_font.configure(size=self.font_size)
            self._update_zoom_status()

        return "break"
    def reset_zoom(self, event=None):
        self.font_size = 12
        self.editor_font.configure(size=self.font_size)
        self._update_zoom_status()

        return "break"
    def _update_zoom_status(self):
        zoom_percent = round((self.font_size / 12) * 100)

        if self.filename:
            self._set_status(
                f"{self.filename} — Zoom: {zoom_percent}%"
            )
        else:
            self._set_status(
                f"New Document — Zoom: {zoom_percent}%"
            )
    def zoom_mousewheel(self, event):
        if event.delta > 0:
            self.zoom_in()
        elif event.delta < 0:
            self.zoom_out()

        return "break"
    def zoom_keyboard(self, event):
        """
        Handles Ctrl + / Ctrl - / Ctrl 0 independently
        of the keyboard layout.
        """

        # Ctrl + 0 -> reset
        if event.keysym == "0":
            return self.reset_zoom()

        # Ctrl + minus
        if event.keysym in (
            "minus",
            "underscore",
            "KP_Subtract"
        ):
            return self.zoom_out()

        # Ctrl + plus
        if event.keysym in (
            "plus",
            "equal",
            "KP_Add"
        ):
            return self.zoom_in()

        return None







    #Search window system
    def open_search(self, event=None):
        #Check for existing search window
        if hasattr(self, "search_window") and self.search_window.winfo_exists():
            self.search_window.focus_force()
            self.search_entry.focus_set()
            return "break"
        #Create search window
        self.search_window = tk.Toplevel(self.root)
        self.search_window.title("Search")
        self.search_window.geometry("430x120")
        self.search_window.resizable(False, False)

        self.search_window.config(bg=self.menu_bg_color)

        tk.Label(
            self.search_window,
            text="Search:",
            bg=self.menu_bg_color,
            fg=self.menu_fg_color
        ).pack(padx=10, pady=(10, 2), anchor="w")

        self.search_entry = tk.Entry(
            self.search_window,
            bg=self.text_bg_color,
            fg=self.text_fg_color,
            insertbackground=self.text_fg_color
        )
        self.search_entry.pack(
            padx=10,
            pady=(0, 10),
            fill=tk.X
        )
        #Options
        options_frame = tk.Frame(
        self.search_window,
        bg=self.menu_bg_color)
    
        options_frame.pack(fill=tk.X, padx=10)

        self.case_sensitive = tk.BooleanVar(value=False)

        #toggle for case sensitvity
        tk.Checkbutton(
            options_frame,
            text="Case sensitive",
            variable=self.case_sensitive,
            command=self.search_text,
            bg=self.menu_bg_color,
            fg=self.menu_fg_color,
            selectcolor=self.text_bg_color,
            activebackground=self.menu_bg_color,
            activeforeground=self.menu_fg_color
        ).pack(side=tk.LEFT)
        #Previous result 
        tk.Button(
            options_frame,
            text="Previous",
            command=self.search_previous,
            width=10
        ).pack(side=tk.RIGHT, padx=(5, 0))
        #Next result
        tk.Button(
            options_frame,
            text="Next",
            command=self.search_next,
            width=10
        ).pack(side=tk.RIGHT)

        self.search_entry.bind("<KeyRelease>", self.search_text)
        self.search_entry.bind("<Return>", self.search_next)
        self.search_window.bind("<Escape>", self.close_search)

        self.search_window.protocol(
            "WM_DELETE_WINDOW",
            self.close_search
        )

        self.search_entry.focus_set()

        return "break"

    def search_text(self, event=None):
        search_term = self.search_entry.get()

        # Remove old tags
        self.text.tag_remove("search_match", "1.0", tk.END)

        if not search_term:
            return

        start = "1.0"

        while True:
            position = self.text.search(
                search_term,
                start,
                stopindex=tk.END,
                nocase=not self.case_sensitive.get()
            )

            if not position:
                break

            end = f"{position}+{len(search_term)}c"

            self.text.tag_add(
                "search_match",
                position,
                end
            )

            start = end


    def search_next(self, event=None):
        search_term = self.search_entry.get()

        if not search_term:
            return "break"

        start = self.text.index(tk.INSERT)

        position = self.text.search(
            search_term,
            start,
            stopindex=tk.END,
            nocase=not self.case_sensitive.get()
        )

        # Return to start when bottom is reached
        if not position:
            position = self.text.search(
                search_term,
                "1.0",
                stopindex=tk.END,
                nocase=not self.case_sensitive.get()
            )

        if position:
            end = f"{position}+{len(search_term)}c"

            self.text.mark_set("insert", end)
            self.text.see(position)

            self.text.tag_remove("sel", "1.0", tk.END)
            self.text.tag_add("sel", position, end)

        return "break"
    def search_previous(self, event=None):
        search_term = self.search_entry.get()

        if not search_term:
            return "break"

        start = self.text.index(tk.INSERT)

        position = self.text.search(
            search_term,
            start,
            stopindex="1.0",
            backwards=True,
            nocase=not self.case_sensitive.get()
        )

        # When start is reached return to end
        if not position:
            position = self.text.search(
                search_term,
                tk.END,
                stopindex="1.0",
                backwards=True,
                nocase=not self.case_sensitive.get()
            )

        if position:
            end = f"{position}+{len(search_term)}c"

            self.text.mark_set("insert", position)
            self.text.see(position)

            self.text.tag_remove("sel", "1.0", tk.END)
            self.text.tag_add("sel", position, end)

        return "break"



    def close_search(self, event=None):
        self.text.tag_remove("search_match", "1.0", tk.END)

        if hasattr(self, "search_window") and self.search_window.winfo_exists():
            self.search_window.destroy()

        self.text.focus_set()

        return "break"
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
