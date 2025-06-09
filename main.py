import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from math import sin, sqrt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os
import locale

from solve import solve


class InterpolationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная: Интерполяция функций")
        self.root.geometry("1000x800")

        # Устанавливаем локаль для корректного преобразования чисел
        locale.setlocale(locale.LC_ALL, '')

        self.x = None
        self.xs = []
        self.ys = []
        self.figures = []
        self.current_figure_index = 0

        self.create_widgets()

    def parse_number(self, num_str):
        """Преобразует строку в число, поддерживая и точку, и запятую"""
        if not num_str:
            raise ValueError("Пустое значение")

        try:
            # Сначала пробуем преобразовать как есть
            return float(num_str)
        except ValueError:
            try:
                # Заменяем запятую на точку и пробуем снова
                return float(num_str.replace(',', '.'))
            except ValueError:
                raise ValueError(f"Некорректное число: '{num_str}'")

    def create_widgets(self):
        """Создает все виджеты интерфейса"""
        # Основной фрейм для кнопок управления
        control_frame = tk.Frame(self.root, padx=10, pady=10)
        control_frame.pack(fill=tk.X)

        # Кнопки загрузки данных
        buttons = [
            ("Загрузить из файла", self.load_from_file),
            ("Ввод вручную", self.show_manual_input_window),
            ("Использовать пример", self.use_example),
            ("Сгенерировать по функции", self.generate_function)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = tk.Button(control_frame, text=text, command=command)
            btn.grid(row=0, column=i, padx=5, sticky="ew")

        # Кнопка решения
        self.solve_btn = tk.Button(
            self.root,
            text="Решить и Построить графики",
            command=self.process,
            state=tk.DISABLED
        )
        self.solve_btn.pack(pady=(0, 15))

        # Лог действий
        self.log_text = tk.Text(
            self.root,
            height=12,
            wrap=tk.WORD,
            font=('Arial', 10),
            padx=10,
            pady=10
        )
        self.log_text.pack(fill=tk.BOTH, padx=10, expand=False)

        # Навигация по графикам
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(pady=5, fill=tk.X)

        self.prev_btn = tk.Button(
            self.nav_frame,
            text="← Предыдущий",
            command=self.show_prev_figure,
            state=tk.DISABLED
        )
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(
            self.nav_frame,
            text="Следующий →",
            command=self.show_next_figure,
            state=tk.DISABLED
        )
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.figure_label = tk.Label(
            self.nav_frame,
            text="График 1 из 1",
            font=('Arial', 10)
        )
        self.figure_label.pack(side=tk.LEFT, padx=10)

        # Область для графиков
        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))

    def log(self, text):
        """Добавляет сообщение в лог"""
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def load_from_file(self):
        """Загружает данные из файла"""
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filename:
            return
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()

            self.x = self.parse_number(lines[0].strip())
            self.xs, self.ys = [], []
            for line in lines[1:]:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) == 2:
                        self.xs.append(self.parse_number(parts[0]))
                        self.ys.append(self.parse_number(parts[1]))

            if not self.xs:
                raise ValueError("Нет данных")

            self.log(f"Данные успешно загружены из файла: {os.path.basename(filename)}")
            self.solve_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {e}")

    def show_manual_input_window(self):
        """Показывает окно для ручного ввода данных"""
        self.manual_window = tk.Toplevel(self.root)
        self.manual_window.title("Ручной ввод данных")
        self.manual_window.geometry("600x500")
        self.manual_window.grab_set()

        # Основной фрейм
        main_frame = tk.Frame(self.manual_window, padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Поле для точки интерполяции
        tk.Label(main_frame, text="Точка интерполяции (x):", font=('Arial', 11)).pack(anchor='w')
        self.x_entry = tk.Entry(main_frame, font=('Arial', 11))
        self.x_entry.pack(fill=tk.X, pady=(0, 15))

        # Таблица с узлами
        tk.Label(main_frame, text="Узлы интерполяции (x и y):", font=('Arial', 11)).pack(anchor='w')

        # Фрейм для таблицы
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(5, 10))

        # Создаем Treeview
        self.tree = ttk.Treeview(
            table_frame,
            columns=("x", "y"),
            show="headings",
            height=8,
            selectmode="browse"
        )

        # Настраиваем колонки
        self.tree.heading("x", text="X", anchor=tk.CENTER)
        self.tree.heading("y", text="Y", anchor=tk.CENTER)
        self.tree.column("x", width=150, anchor=tk.CENTER)
        self.tree.column("y", width=150, anchor=tk.CENTER)

        # Полоса прокрутки
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Размещаем элементы
        self.tree.pack(side="left", fill=tk.BOTH, expand=True)
        scrollbar.pack(side="right", fill="y")

        # Добавляем 5 строк по умолчанию
        for _ in range(5):
            self.tree.insert("", tk.END, values=("", ""))

        # Кнопки управления
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=(10, 0))

        buttons = [
            ("Добавить строку", self.add_row),
            ("Удалить строку", self.delete_row),
            ("Сохранить", self.save_manual_input),
            ("Отмена", self.manual_window.destroy)
        ]

        for text, command in buttons:
            btn = tk.Button(btn_frame, text=text, command=command)
            btn.pack(side="left", padx=5)

        # Настраиваем редактирование ячеек
        self.tree.bind("<Double-1>", self.on_cell_edit)

    def on_cell_edit(self, event):
        """Редактирование ячеек при двойном клике"""
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        column = self.tree.identify_column(event.x)
        item = self.tree.identify_row(event.y)
        col_index = int(column[1]) - 1

        # Получаем текущее значение
        current_value = self.tree.item(item, "values")[col_index]

        # Создаем поле для редактирования
        entry = tk.Entry(self.manual_window, font=('Arial', 11))
        entry.insert(0, current_value)
        entry.select_range(0, tk.END)
        entry.focus()

        def save_edit(event=None):
            """Сохраняет изменения"""
            new_value = entry.get()
            values = list(self.tree.item(item, "values"))
            values[col_index] = new_value
            self.tree.item(item, values=values)
            entry.destroy()

        entry.bind("<Return>", save_edit)
        entry.bind("<FocusOut>", lambda e: save_edit())

        # Позиционируем поле над ячейкой
        x, y, width, height = self.tree.bbox(item, column)
        entry.place(x=x, y=y, width=width, height=height)

    def add_row(self):
        """Добавляет новую строку в таблицу"""
        self.tree.insert("", tk.END, values=("", ""))

    def delete_row(self):
        """Удаляет выбранную строку из таблицы"""
        selected_item = self.tree.selection()
        if selected_item:
            self.tree.delete(selected_item)

    def save_manual_input(self):
        """Сохраняет введенные данные"""
        try:
            # Проверяем точку интерполяции
            if not self.x_entry.get():
                raise ValueError("Не введена точка интерполяции x")

            self.x = self.parse_number(self.x_entry.get())

            # Получаем все точки из таблицы
            self.xs = []
            self.ys = []

            for child in self.tree.get_children():
                values = self.tree.item(child)["values"]
                if len(values) == 2:
                    x_val, y_val = values[0], values[1]
                    if x_val and y_val:  # Пропускаем пустые строки
                        self.xs.append(self.parse_number(x_val))
                        self.ys.append(self.parse_number(y_val))

            # Проверяем минимальное количество точек
            if len(self.xs) < 2:
                raise ValueError("Необходимо ввести как минимум 2 точки")

            # Проверяем уникальность x
            if len(set(self.xs)) != len(self.xs):
                raise ValueError("Значения x не должны повторяться")

            # Проверяем сортировку
            if self.xs != sorted(self.xs):
                raise ValueError("Значения x должны быть отсортированы по возрастанию")

            self.log("Данные успешно введены вручную")
            self.solve_btn.config(state=tk.NORMAL)
            self.manual_window.destroy()

        except ValueError as e:
            messagebox.showerror("Ошибка ввода", str(e), parent=self.manual_window)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении данных: {e}", parent=self.manual_window)

    def use_example(self):
        """Загружает пример данных"""
        self.x = 0.502
        self.xs = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
        self.ys = [1.5320, 2.5356, 3.5406, 4.5462, 5.5504, 6.5559, 7.5594]
        self.log("Загружен пример")
        self.solve_btn.config(state=tk.NORMAL)

    def generate_function(self):
        """Генерирует данные по выбранной функции"""

        def on_ok():
            try:
                func_index = func_var.get()
                n = int(entry_n.get())
                x0 = self.parse_number(entry_x0.get())
                xn = self.parse_number(entry_xn.get())
                self.x = self.parse_number(entry_x.get())

                if func_index == 1:
                    f = lambda x: 2 * x ** 2 - 5 * x
                elif func_index == 2:
                    f = lambda x: x ** 5
                elif func_index == 3:
                    f = lambda x: sin(x)
                elif func_index == 4:
                    f = lambda x: sqrt(x)
                else:
                    raise ValueError("Неверный выбор функции")

                h = (xn - x0) / (n - 1)
                self.xs = [x0 + h * i for i in range(n)]
                self.ys = [f(x) for x in self.xs]

                self.log("Сгенерированы данные по функции")
                self.solve_btn.config(state=tk.NORMAL)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка генерации: {e}")

        popup = tk.Toplevel(self.root)
        popup.title("Выбор функции")

        tk.Label(popup, text="Выберите функцию:").pack()
        func_var = tk.IntVar(value=1)
        funcs = ["1. 2x² - 5x", "2. x⁵", "3. sin(x)", "4. sqrt(x)"]
        for i, func in enumerate(funcs, 1):
            tk.Radiobutton(popup, text=func, variable=func_var, value=i).pack(anchor='w')

        for label_text, entry_default in [("Число узлов:", "5"), ("x0:", "0.0"), ("xn:", "1.0"),
                                          ("x (точка интерполяции):", "0.5")]:
            tk.Label(popup, text=label_text).pack()
            entry = tk.Entry(popup)
            entry.insert(0, entry_default)
            entry.pack()
            if label_text == "Число узлов:":
                entry_n = entry
            elif label_text == "x0:":
                entry_x0 = entry
            elif label_text == "xn:":
                entry_xn = entry
            elif label_text.startswith("x "):
                entry_x = entry

        tk.Button(popup, text="ОК", command=on_ok).pack(pady=10)

    def clear_plot_frame(self):
        """Очищает фрейм с графиком"""
        for widget in self.plot_frame.winfo_children():
            widget.destroy()

    def show_current_figure(self):
        """Отображает текущий график"""
        self.clear_plot_frame()

        if not self.figures:
            return

        canvas = FigureCanvasTkAgg(self.figures[self.current_figure_index], master=self.plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, pady=10)

        # Обновляем информацию о текущем графике
        self.figure_label.config(text=f"График {self.current_figure_index + 1} из {len(self.figures)}")

        # Обновляем состояние кнопок навигации
        self.prev_btn.config(state=tk.NORMAL if self.current_figure_index > 0 else tk.DISABLED)
        self.next_btn.config(state=tk.NORMAL if self.current_figure_index < len(self.figures) - 1 else tk.DISABLED)

    def show_prev_figure(self):
        """Показывает предыдущий график"""
        if self.current_figure_index > 0:
            self.current_figure_index -= 1
            self.show_current_figure()

    def show_next_figure(self):
        """Показывает следующий график"""
        if self.current_figure_index < len(self.figures) - 1:
            self.current_figure_index += 1
            self.show_current_figure()

    def process(self):
        """Обрабатывает данные и строит графики"""
        if not self.xs or not self.ys:
            messagebox.showerror("Ошибка", "Нет данных для обработки")
            return
        if len(set(self.xs)) != len(self.xs):
            messagebox.showerror("Ошибка", "Узлы не должны совпадать")
            return
        if self.xs != sorted(self.xs):
            messagebox.showerror("Ошибка", "Узлы должны быть отсортированы")

        self.log_text.delete("1.0", tk.END)
        self.clear_plot_frame()
        self.figures = []
        self.current_figure_index = 0

        self.log("Выполнение интерполяции...\n")

        try:
            result_text, figures = solve(self.xs, self.ys, self.x, len(self.xs), return_plots=True)
            self.log(result_text)

            self.figures = figures
            if self.figures:
                self.show_current_figure()
                if len(self.figures) > 1:
                    self.prev_btn.config(state=tk.NORMAL)
                    self.next_btn.config(state=tk.NORMAL)
                else:
                    self.prev_btn.config(state=tk.DISABLED)
                    self.next_btn.config(state=tk.DISABLED)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка решения: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = InterpolationApp(root)
    root.mainloop()