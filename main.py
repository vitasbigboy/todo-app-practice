import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk

# --- МОДУЛЬ РАБОТЫ С БАЗОЙ ДАННЫХ (Соединение и запросы) ---
def init_db():
    """Создание таблицы задач, если её нет"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'активна'
        )
    ''')
    conn.commit()
    conn.close()

def add_task_to_db(title, description):
    """Добавление новой задачи в БД"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (title, description) VALUES (?, ?)',
                   (title, description))
    conn.commit()
    conn.close()

def get_all_tasks_from_db():
    """Получение всех задач из БД"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, status FROM tasks')
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def update_task_status_in_db(task_id, new_status):
    """Обновление статуса задачи"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE tasks SET status = ? WHERE id = ?',
                   (new_status, task_id))
    conn.commit()
    conn.close()

def delete_task_from_db(task_id):
    """Удаление задачи из БД"""
    conn = sqlite3.connect('tasks.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()

# --- МОДУЛЬ ПОЛЬЗОВАТЕЛЬСКОГО ИНТЕРФЕЙСА ---
class TodoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер задач")
        self.root.geometry("600x400")

        # Поля ввода (сбор данных от пользователя)
        tk.Label(root, text="Название задачи:").pack(pady=5)
        self.title_entry = tk.Entry(root, width=50)
        self.title_entry.pack()

        tk.Label(root, text="Описание:").pack(pady=5)
        self.desc_entry = tk.Entry(root, width=50)
        self.desc_entry.pack()

        # Кнопка добавления (обработка данных)
        tk.Button(root, text="Добавить задачу", command=self.add_task).pack(pady=10)

        # Таблица для отображения задач (заполнение UI данными из БД)
        self.tree = ttk.Treeview(root, columns=('ID', 'Title', 'Description', 'Status'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Title', text='Название')
        self.tree.heading('Description', text='Описание')
        self.tree.heading('Status', text='Статус')
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

        # Кнопки действий
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Обновить список", command=self.load_tasks).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Завершить задачу", command=self.complete_task).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Удалить задачу", command=self.delete_task).pack(side=tk.LEFT, padx=5)

        # Загрузка задач при старте
        self.load_tasks()

    def add_task(self):
        """Обработка нажатия кнопки 'Добавить' (сбор данных и запрос в БД)"""
        title = self.title_entry.get()
        desc = self.desc_entry.get()
        if title:
            add_task_to_db(title, desc)
            self.title_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            self.load_tasks()
        else:
            messagebox.showwarning("Ошибка", "Название задачи не может быть пустым")

    def load_tasks(self):
        """Заполнение таблицы данными из БД"""
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        # Загрузка данных из БД
        tasks = get_all_tasks_from_db()
        for task in tasks:
            self.tree.insert('', tk.END, values=task)

    def complete_task(self):
        """Изменение статуса задачи на 'завершена'"""
        selected = self.tree.selection()
        if selected:
            task_id = self.tree.item(selected[0])['values'][0]
            update_task_status_in_db(task_id, 'завершена')
            self.load_tasks()
        else:
            messagebox.showwarning("Ошибка", "Выберите задачу")

    def delete_task(self):
        """Удаление задачи"""
        selected = self.tree.selection()
        if selected:
            task_id = self.tree.item(selected[0])['values'][0]
            delete_task_from_db(task_id)
            self.load_tasks()
        else:
            messagebox.showwarning("Ошибка", "Выберите задачу")

# --- ЗАПУСК ПРИЛОЖЕНИЯ ---
if __name__ == "__main__":
    init_db()  # Создаем БД и таблицу при запуске
    root = tk.Tk()
    app = TodoApp(root)
    root.mainloop()
