import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from solve import solve
from math import sin, sqrt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os


class InterpolationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная: Интерполяция функций")
        self.root.geometry("1000x800")

        self.x = None
        self.xs = []
        self.ys = []
        self.figures = []
        self.current_figure_index = 0

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Button(frame, text="Загрузить из файла", command=self.load_from_file).grid(row=0, column=0, padx=5)
        tk.Button(frame, text="Ввод вручную", command=self.show_manual_input_window).grid(row=0, column=1, padx=5)
        tk.Button(frame, text="Использовать пример", command=self.use_example).grid(row=0, column=2, padx=5)
        tk.Button(frame, text="Сгенерировать по функции", command=self.generate_function).grid(row=0, column=3, padx=5)

        self.solve_btn = tk.Button(self.root, text="Решить и Построить графики", command=self.process,
                                   state=tk.DISABLED)
        self.solve_btn.pack(pady=20)

        self.log_text = tk.Text(self.root, height=15, wrap=tk.WORD)
        self.log_text.pack(padx=10, fill=tk.BOTH, expand=False)

        # Фрейм для навигации по графикам
        self.nav_frame = tk.Frame(self.root)
        self.nav_frame.pack(pady=5)

        self.prev_btn = tk.Button(self.nav_frame, text="← Предыдущий", command=self.show_prev_figure, state=tk.DISABLED)
        self.prev_btn.pack(side=tk.LEFT, padx=5)

        self.next_btn = tk.Button(self.nav_frame, text="Следующий →", command=self.show_next_figure, state=tk.DISABLED)
        self.next_btn.pack(side=tk.LEFT, padx=5)

        self.figure_label = tk.Label(self.nav_frame, text="График 1 из 1")
        self.figure_label.pack(side=tk.LEFT, padx=10)

        self.plot_frame = tk.Frame(self.root)
        self.plot_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def load_from_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if not filename:
            return
        try:
            with open(filename, 'r') as f:
                lines = f.readlines()

            self.x = float(lines[0].strip())
            self.xs, self.ys = [], []
            for line in lines[1:]:
                if line.strip():
                    parts = line.strip().split()
                    if len(parts) == 2:
                        self.xs.append(float(parts[0]))
                        self.ys.append(float(parts[1]))

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
        self.manual_window.grab_set()  # Делает окно модальным

        # Основной фрейм для содержимого
        main_frame = tk.Frame(self.manual_window)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Поле для ввода x
        tk.Label(main_frame, text="Точка интерполяции (x):").pack(anchor='w', pady=(0, 5))
        self.x_entry = tk.Entry(main_frame)
        self.x_entry.pack(fill=tk.X, pady=(0, 10))

        # Таблица для ввода точек
        tk.Label(main_frame, text="Введите узлы интерполяции (x и y):").pack(anchor='w')

        # Фрейм для таблицы с прокруткой
        table_frame = tk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Создаем Treeview для таблицы
        self.tree = ttk.Treeview(table_frame, columns=("x", "y"), show="headings", height=8)
        self.tree.heading("x", text="x")
        self.tree.heading("y", text="y")
        self.tree.column("x", width=150)
        self.tree.column("y", width=150)

        # Добавляем прокрутку
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Кнопки управления
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Добавить строку", command=self.add_row).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Удалить строку", command=self.delete_row).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Сохранить", command=self.save_manual_input).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Отмена", command=self.manual_window.destroy).pack(side="left", padx=5)

        # Добавляем 5 пустых строк по умолчанию
        for _ in range(5):
            self.tree.insert("", "end", values=("", ""))

        # Разрешаем редактирование ячеек
        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
        """Обработчик двойного клика для редактирования ячеек"""
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            column = self.tree.identify_column(event.x)
            item = self.tree.identify_row(event.y)

            # Получаем текущее значение
            col_index = int(column[1]) - 1
            current_value = self.tree.item(item, "values")[col_index]

            # Создаем поле для редактирования
            entry = tk.Entry(self.manual_window)
            entry.insert(0, current_value)
            entry.select_range(0, tk.END)
            entry.focus()

            def save_edit(event):
                """Сохраняет изменения в ячейке"""
                new_value = entry.get()
                values = list(self.tree.item(item, "values"))
                values[col_index] = new_value
                self.tree.item(item, values=values)
                entry.destroy()

            entry.bind("<Return>", save_edit)
            entry.bind("<FocusOut>", lambda e: entry.destroy())

            # Размещаем поле редактирования поверх ячейки
            x, y, width, height = self.tree.bbox(item, column)
            entry.place(x=x, y=y, width=width, height=height)

    def add_row(self):
        """Добавляет новую строку в таблицу"""
        self.tree.insert("", "end", values=("", ""))

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

            self.x = float(self.x_entry.get())

            # Получаем все точки из таблицы
            self.xs = []
            self.ys = []

            for child in self.tree.get_children():
                values = self.tree.item(child)["values"]
                if len(values) == 2:
                    x_val, y_val = values[0], values[1]
                    if x_val and y_val:  # Пропускаем пустые строки
                        try:
                            self.xs.append(float(x_val))
                            self.ys.append(float(y_val))
                        except ValueError:
                            raise ValueError(f"Некорректные данные в строке: x={x_val}, y={y_val}")

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
        self.x = 0.502
        self.xs = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
        self.ys = [1.5320, 2.5356, 3.5406, 4.5462, 5.5504, 6.5559, 7.5594]
        self.log("Загружен пример")
        self.solve_btn.config(state=tk.NORMAL)

    def generate_function(self):
        def on_ok():
            try:
                func_index = func_var.get()
                n = int(entry_n.get())
                x0 = float(entry_x0.get())
                xn = float(entry_xn.get())
                self.x = float(entry_x.get())

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
        if not self.xs or not self.ys:
            messagebox.showerror("Ошибка", "Нет данных для обработки")
            return
        if len(set(self.xs)) != len(self.xs):
            messagebox.showerror("Ошибка", "Узлы не должны совпадать")
            return
        if self.xs != sorted(self.xs):
            messagebox.showerror("Ошибка", "Узлы должны быть отсортированы")
            return

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
                # Активируем кнопки навигации если есть несколько графиков
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