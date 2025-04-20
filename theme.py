import tkinter as tk
from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class DrWebTheme:
    def __init__(self):
        self.style = ttk.Style()
        self.setup_theme()
        
    def setup_theme(self):
        # Основные цвета Dr.Web
        self.style.configure('DrWeb.TFrame', 
                           background='#f8f9fa',
                           relief='flat')
                           
        self.style.configure('DrWeb.TLabel',
                           background='#f8f9fa',
                           foreground='#2c3e50',
                           font=('Segoe UI', 10))
                           
        self.style.configure('DrWeb.TButton',
                           background='#3498db',
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'),
                           padding=10)
                           
        self.style.configure('DrWeb.TEntry',
                           fieldbackground='white',
                           foreground='#2c3e50',
                           font=('Segoe UI', 10),
                           padding=5)
                           
        self.style.configure('DrWeb.Horizontal.TProgressbar',
                           background='#3498db',
                           troughcolor='#e9ecef',
                           thickness=20)
                           
        self.style.configure('DrWeb.TText',
                           background='white',
                           foreground='#2c3e50',
                           font=('Consolas', 10),
                           padding=5)
                           
        self.style.configure('DrWeb.TScrollbar',
                           background='#e9ecef',
                           troughcolor='#f8f9fa',
                           arrowcolor='#2c3e50')
                           
        # Стиль для заголовков
        self.style.configure('DrWeb.Header.TLabel',
                           font=('Segoe UI', 24, 'bold'),
                           foreground='#2c3e50')
                           
        # Стиль для статистики
        self.style.configure('DrWeb.Stats.TLabel',
                           font=('Segoe UI', 12),
                           foreground='#2c3e50')
                           
        # Стиль для кнопок действий
        self.style.configure('DrWeb.Action.TButton',
                           background='#2ecc71',
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'))
                           
        # Стиль для кнопок предупреждений
        self.style.configure('DrWeb.Warning.TButton',
                           background='#e74c3c',
                           foreground='white',
                           font=('Segoe UI', 10, 'bold'))
                           
    def create_header(self, parent, text):
        label = ttk.Label(parent,
                         text=text,
                         style='DrWeb.Header.TLabel')
        return label
        
    def create_stats_label(self, parent, text):
        label = ttk.Label(parent,
                         text=text,
                         style='DrWeb.Stats.TLabel')
        return label
        
    def create_action_button(self, parent, text, command):
        button = ttk.Button(parent,
                          text=text,
                          command=command,
                          style='DrWeb.Action.TButton')
        return button
        
    def create_warning_button(self, parent, text, command):
        button = ttk.Button(parent,
                          text=text,
                          command=command,
                          style='DrWeb.Warning.TButton')
        return button
        
    def create_frame(self, parent):
        frame = ttk.Frame(parent, style='DrWeb.TFrame')
        return frame
        
    def create_label(self, parent, text):
        label = ttk.Label(parent,
                         text=text,
                         style='DrWeb.TLabel')
        return label
        
    def create_entry(self, parent):
        entry = ttk.Entry(parent, style='DrWeb.TEntry')
        return entry
        
    def create_progressbar(self, parent):
        progress = ttk.Progressbar(parent,
                                 style='DrWeb.Horizontal.TProgressbar',
                                 mode='determinate')
        return progress
        
    def create_text(self, parent):
        text = tk.Text(parent,
                      font=('Consolas', 10),
                      bg='white',
                      fg='#2c3e50',
                      padx=10,
                      pady=10)
        return text
        
    def create_scrollbar(self, parent):
        scrollbar = ttk.Scrollbar(parent, style='DrWeb.TScrollbar')
        return scrollbar
        
    def create_tooltip(self, widget, text):
        def show_tooltip(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() + 25
            y += widget.winfo_rooty() + 20
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{x}+{y}")
            label = ttk.Label(tooltip,
                            text=text,
                            justify='left',
                            background='#f8f9fa',
                            foreground='#2c3e50',
                            relief='solid',
                            borderwidth=1,
                            padding=5)
            label.pack()
            
        def hide_tooltip(event):
            tooltip = event.widget.winfo_children()[0]
            tooltip.destroy()
            
        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip) 