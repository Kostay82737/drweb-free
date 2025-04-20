import os
import json
import hashlib
import datetime
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import zipfile
import tempfile
import shutil
from updater import Updater
from theme import DrWebTheme
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class DrWebFree:
    def __init__(self):
        self.updater = Updater()
        self.load_signatures()
        
        # Статистика сканирования
        self.scan_stats = {
            'total_files': 0,
            'infected_files': 0,
            'cleaned_files': 0,
            'scan_time': 0
        }
        
    def load_signatures(self):
        """Загрузка базы сигнатур из файла"""
        try:
            with open("signatures.json", 'r') as f:
                data = json.load(f)
                self.virus_signatures = data['signatures']
                self.heuristic_rules = data['heuristic_rules']
        except Exception as e:
            print(f"Ошибка загрузки сигнатур: {e}")
            self.virus_signatures = {}
            self.heuristic_rules = {
                'suspicious_strings': [],
                'suspicious_extensions': [],
                'packers': {}
            }
            
    def check_for_updates(self):
        """Проверка обновлений"""
        self.updater.run_update()
        
    def calculate_file_hash(self, file_path):
        """Вычисление MD5 хеша файла"""
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5()
                while chunk := f.read(8192):
                    file_hash.update(chunk)
            return file_hash.hexdigest()
        except Exception as e:
            print(f"Ошибка при вычислении хеша файла {file_path}: {e}")
            return None
            
    def check_suspicious_strings(self, file_path):
        """Проверка на подозрительные строки"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read().lower()
                for string in self.heuristic_rules['suspicious_strings']:
                    if string.encode() in content:
                        return True
        except:
            pass
        return False
        
    def check_file_entropy(self, file_path):
        """Проверка энтропии файла"""
        try:
            with open(file_path, 'rb') as f:
                data = f.read()
                if not data:
                    return False
                    
                counts = {}
                for byte in data:
                    counts[byte] = counts.get(byte, 0) + 1
                    
                entropy = 0
                for count in counts.values():
                    p = count / len(data)
                    entropy -= p * (p.bit_length() - 1)
                    
                return entropy > 7
        except:
            return False
            
    def check_packed_files(self, file_path):
        """Проверка на упакованные файлы"""
        try:
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header in self.heuristic_rules['packers']
        except:
            return False
            
    def scan_file(self, file_path):
        """Сканирование файла"""
        results = {
            'file_path': file_path,
            'is_infected': False,
            'threats': [],
            'can_clean': False
        }
        
        try:
            # Проверка расширения
            if Path(file_path).suffix.lower() in self.heuristic_rules['suspicious_extensions']:
                results['threats'].append('Подозрительное расширение')
                results['is_infected'] = True
                
            # Проверка хеша
            file_hash = self.calculate_file_hash(file_path)
            if file_hash in self.virus_signatures:
                threat = self.virus_signatures[file_hash]
                results['threats'].append(f'Обнаружен {threat["name"]} ({threat["type"]})')
                results['is_infected'] = True
                results['can_clean'] = True
                
            # Эвристический анализ
            if self.check_suspicious_strings(file_path):
                results['threats'].append('Подозрительные строки в файле')
                results['is_infected'] = True
                
            if self.check_file_entropy(file_path):
                results['threats'].append('Высокая энтропия (возможно упакован/зашифрован)')
                results['is_infected'] = True
                
            if self.check_packed_files(file_path):
                results['threats'].append('Обнаружен упакованный файл')
                results['is_infected'] = True
                
        except Exception as e:
            results['threats'].append(f'Ошибка сканирования: {e}')
            results['is_infected'] = True
            
        return results
        
    def clean_file(self, file_path):
        """Очистка зараженного файла"""
        try:
            # Создаем резервную копию
            backup_path = f"{file_path}.bak"
            shutil.copy2(file_path, backup_path)
            
            # Здесь можно добавить логику очистки в зависимости от типа вируса
            
            return True
        except Exception as e:
            print(f"Ошибка при очистке файла: {e}")
            return False
            
    def scan_directory(self, directory_path, progress_callback=None):
        """Сканирование директории"""
        scan_results = []
        self.scan_stats = {
            'total_files': 0,
            'infected_files': 0,
            'cleaned_files': 0,
            'scan_time': datetime.datetime.now()
        }
        
        try:
            for root, _, files in os.walk(directory_path):
                for file in files:
                    self.scan_stats['total_files'] += 1
                    file_path = os.path.join(root, file)
                    
                    result = self.scan_file(file_path)
                    scan_results.append(result)
                    
                    if result['is_infected']:
                        self.scan_stats['infected_files'] += 1
                        if result['can_clean'] and self.clean_file(file_path):
                            self.scan_stats['cleaned_files'] += 1
                            
                    if progress_callback:
                        progress = (self.scan_stats['total_files'] / 
                                  sum(1 for _, _, files in os.walk(directory_path) for _ in files) * 100)
                        progress_callback(progress)
                        
        except Exception as e:
            print(f"Ошибка при сканировании: {e}")
            
        self.scan_stats['scan_time'] = datetime.datetime.now() - self.scan_stats['scan_time']
        return scan_results
        
    def generate_report(self, scan_results):
        """Генерация отчета"""
        report = []
        report.append("=== ОТЧЕТ DR.WEB FREE ===")
        report.append(f"Время сканирования: {self.scan_stats['scan_time']}")
        report.append(f"Всего проверено файлов: {self.scan_stats['total_files']}")
        report.append(f"Найдено зараженных файлов: {self.scan_stats['infected_files']}")
        report.append(f"Очищено файлов: {self.scan_stats['cleaned_files']}")
        report.append("\nЗараженные файлы:")
        
        for result in scan_results:
            if result['is_infected']:
                report.append(f"\nФайл: {result['file_path']}")
                for threat in result['threats']:
                    report.append(f"- {threat}")
                if result['can_clean']:
                    report.append("- Файл был очищен")
                    
        return "\n".join(report)

class AntivirusGUI:
    def __init__(self):
        self.root = ttk.Window(themename="cosmo")
        self.root.title("Dr.Web Free")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        self.theme = DrWebTheme()
        self.antivirus = DrWebFree()
        self.scan_thread = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Основной фрейм
        main_frame = self.theme.create_frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        header_frame = self.theme.create_frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = self.theme.create_header(header_frame, "Dr.Web Free")
        title_label.pack(side=tk.LEFT)
        
        # Меню
        menubar = tk.Menu(self.root, bg='#f8f9fa', fg='#2c3e50')
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0, bg='#f8f9fa', fg='#2c3e50')
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Выбрать директорию", command=self.select_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0, bg='#f8f9fa', fg='#2c3e50')
        menubar.add_cascade(label="Инструменты", menu=tools_menu)
        tools_menu.add_command(label="Проверить обновления", command=self.check_updates)
        
        # Панель управления
        control_frame = self.theme.create_frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Поле пути
        self.path_var = tk.StringVar()
        path_entry = self.theme.create_entry(control_frame)
        path_entry.config(textvariable=self.path_var, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        # Кнопка сканирования
        scan_button = self.theme.create_action_button(control_frame, "Начать сканирование", self.start_scan)
        scan_button.pack(side=tk.RIGHT)
        
        # Статистика
        stats_frame = self.theme.create_frame(main_frame)
        stats_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.total_files_var = tk.StringVar(value="Всего файлов: 0")
        self.infected_files_var = tk.StringVar(value="Зараженных: 0")
        self.cleaned_files_var = tk.StringVar(value="Очищено: 0")
        
        total_label = self.theme.create_stats_label(stats_frame, textvariable=self.total_files_var)
        infected_label = self.theme.create_stats_label(stats_frame, textvariable=self.infected_files_var)
        cleaned_label = self.theme.create_stats_label(stats_frame, textvariable=self.cleaned_files_var)
        
        total_label.pack(side=tk.LEFT, padx=10)
        infected_label.pack(side=tk.LEFT, padx=10)
        cleaned_label.pack(side=tk.LEFT, padx=10)
        
        # Прогресс-бар
        self.progress = self.theme.create_progressbar(main_frame)
        self.progress.pack(fill=tk.X, pady=(0, 20))
        
        # Отчет
        report_frame = self.theme.create_frame(main_frame)
        report_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок отчета
        report_header = self.theme.create_stats_label(report_frame, "Результаты сканирования")
        report_header.pack(anchor=tk.W, pady=(0, 10))
        
        # Текстовое поле для отчета
        self.report_text = self.theme.create_text(report_frame)
        self.report_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Полоса прокрутки
        scrollbar = self.theme.create_scrollbar(report_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.report_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.report_text.yview)
        
        # Добавляем подсказки
        self.theme.create_tooltip(scan_button, "Начать сканирование выбранной директории")
        self.theme.create_tooltip(path_entry, "Выберите директорию для сканирования")
        
    def select_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.path_var.set(directory)
            
    def check_updates(self):
        self.antivirus.check_for_updates()
        
    def update_progress(self, value):
        self.progress['value'] = value
        self.root.update_idletasks()
        
    def update_stats(self, total, infected, cleaned):
        self.total_files_var.set(f"Всего файлов: {total}")
        self.infected_files_var.set(f"Зараженных: {infected}")
        self.cleaned_files_var.set(f"Очищено: {cleaned}")
        
    def scan_completed(self, scan_results):
        report = self.antivirus.generate_report(scan_results)
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, report)
        
        # Обновляем статистику
        self.update_stats(
            self.antivirus.scan_stats['total_files'],
            self.antivirus.scan_stats['infected_files'],
            self.antivirus.scan_stats['cleaned_files']
        )
        
        messagebox.showinfo("Сканирование завершено", 
                          f"Найдено {self.antivirus.scan_stats['infected_files']} зараженных файлов")
        
    def start_scan(self):
        directory = self.path_var.get()
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("Ошибка", "Выберите корректную директорию")
            return
            
        def scan_thread():
            scan_results = self.antivirus.scan_directory(directory, self.update_progress)
            self.root.after(0, lambda: self.scan_completed(scan_results))
            
        self.scan_thread = threading.Thread(target=scan_thread)
        self.scan_thread.daemon = True
        self.scan_thread.start()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = AntivirusGUI()
    app.run() 