import os
import json
import requests
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from theme import DrWebTheme
import zipfile
import tempfile
import shutil
from pathlib import Path
import sys
import subprocess

class Updater:
    def __init__(self):
        self.theme = DrWebTheme()
        self.repo_owner = "your_username"  # Замените на ваше имя пользователя GitHub
        self.repo_name = "drweb-free"     # Замените на имя вашего репозитория
        self.current_version = "1.0.0"
        self.update_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}/releases/latest"
        self.signatures_url = f"https://raw.githubusercontent.com/{self.repo_owner}/{self.repo_name}/main/signatures.json"
        
    def check_for_updates(self):
        try:
            response = requests.get(self.update_url)
            if response.status_code == 200:
                latest_release = response.json()
                latest_version = latest_release['tag_name']
                
                if self.compare_versions(latest_version, self.current_version) > 0:
                    self.show_update_dialog(latest_release)
                else:
                    messagebox.showinfo("Обновления", "У вас установлена последняя версия")
            else:
                messagebox.showerror("Ошибка", "Не удалось проверить обновления")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось проверить обновления: {str(e)}")
            
    def compare_versions(self, v1, v2):
        """Сравнение версий"""
        v1_parts = [int(x) for x in v1.split('.')]
        v2_parts = [int(x) for x in v2.split('.')]
        return (v1_parts > v2_parts) - (v1_parts < v2_parts)
        
    def show_update_dialog(self, release_info):
        dialog = tk.Toplevel()
        dialog.title("Доступно обновление")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        
        # Основной фрейм
        main_frame = self.theme.create_frame(dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        header_label = self.theme.create_header(main_frame, 
            f"Доступно обновление до версии {release_info['tag_name']}")
        header_label.pack(pady=(0, 20))
        
        # Описание изменений
        changelog_frame = self.theme.create_frame(main_frame)
        changelog_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        changelog_label = self.theme.create_label(changelog_frame, "Изменения:")
        changelog_label.pack(anchor=tk.W)
        
        changelog_text = self.theme.create_text(changelog_frame)
        changelog_text.pack(fill=tk.BOTH, expand=True)
        changelog_text.insert(tk.END, release_info['body'])
        changelog_text.config(state=tk.DISABLED)
        
        # Кнопки
        button_frame = self.theme.create_frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        update_button = self.theme.create_action_button(button_frame, "Обновить", 
            lambda: self.start_update(dialog, release_info['assets'][0]['browser_download_url']))
        update_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = self.theme.create_warning_button(button_frame, "Отмена",
            dialog.destroy)
        cancel_button.pack(side=tk.RIGHT, padx=5)
        
    def start_update(self, dialog, download_url):
        dialog.destroy()
        self.show_progress_dialog(download_url)
        
    def show_progress_dialog(self, download_url):
        progress_dialog = tk.Toplevel()
        progress_dialog.title("Обновление")
        progress_dialog.geometry("400x150")
        progress_dialog.resizable(False, False)
        
        # Основной фрейм
        main_frame = self.theme.create_frame(progress_dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Заголовок
        header_label = self.theme.create_header(main_frame, "Обновление")
        header_label.pack(pady=(0, 20))
        
        # Прогресс-бар
        progress = self.theme.create_progressbar(main_frame)
        progress.pack(fill=tk.X, pady=(0, 10))
        
        # Статус
        status_label = self.theme.create_label(main_frame, "Загрузка обновлений...")
        status_label.pack()
        
        # Запускаем обновление в отдельном потоке
        update_thread = threading.Thread(target=self.download_update, 
            args=(download_url, progress, status_label, progress_dialog))
        update_thread.daemon = True
        update_thread.start()
        
    def download_update(self, download_url, progress, status_label, dialog):
        try:
            # Создаем временную директорию
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "update.zip")
            
            # Загружаем обновление
            response = requests.get(download_url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            block_size = 1024
            downloaded = 0
            
            with open(zip_path, 'wb') as f:
                for data in response.iter_content(block_size):
                    downloaded += len(data)
                    f.write(data)
                    progress['value'] = (downloaded / total_size) * 100
                    status_label.config(text=f"Загрузка обновлений... {int(progress['value'])}%")
                    dialog.update()
            
            # Устанавливаем обновление
            self.install_update(zip_path)
            
            # Обновляем сигнатуры
            self.update_signatures()
            
            messagebox.showinfo("Обновление", "Обновление успешно установлено")
            dialog.destroy()
            
            # Перезапускаем приложение
            self.restart_application()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось установить обновление: {str(e)}")
            dialog.destroy()
            
    def install_update(self, zip_path):
        """Установка обновления"""
        try:
            # Распаковываем архив
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(".")
                
            # Удаляем временные файлы
            os.remove(zip_path)
            os.rmdir(os.path.dirname(zip_path))
            
            return True
        except Exception as e:
            print(f"Ошибка при установке обновления: {e}")
            return False
            
    def update_signatures(self):
        """Обновление базы сигнатур"""
        try:
            response = requests.get(self.signatures_url)
            if response.status_code == 200:
                signatures = response.json()
                with open("signatures.json", 'w') as f:
                    json.dump(signatures, f)
                return True
            return False
        except Exception as e:
            print(f"Ошибка при обновлении сигнатур: {e}")
            return False
            
    def restart_application(self):
        """Перезапуск приложения"""
        python = sys.executable
        os.execl(python, python, *sys.argv)
            
    def run_update(self):
        self.check_for_updates() 