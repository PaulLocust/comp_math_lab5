import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from solve import solve
from math import sin, sqrt
import os


class InterpolationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Лабораторная: Интерполяция функций")
        self.root.geometry("800x600")

        self.x = None
        self.xs = []
        self.ys = []

        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        btn_file = tk.Button(frame, text="Загрузить из файла", command=self.load_from_file)
        btn_file.grid(row=0, column=0, padx=5)

        btn_input = tk.Button(frame, text="Ввод вручную", command=self.manual_input)
        btn_input.grid(row=0, column=1, padx=5)

        btn_example = tk.Button(frame, text="Использовать пример", command=self.use_example)
        btn_example.grid(row=0, column=2, padx=5)

        btn_function = tk.Button(frame, text="Сгенерировать по функции", command=self.generate_function)
        btn_function.grid(row=0, column=3, padx=5)

        self.solve_btn = tk.Button(self.root, text="Решить и Построить графики", command=self.process, state=tk.DISABLED)
        self.solve_btn.pack(pady=20)

        self.log_text = tk.Text(self.root, height=20, wrap=tk.WORD)
        self.log_text.pack(padx=10, fill=tk.BOTH, expand=True)

    def log(self, text):
        self.log_text.insert(tk.END, text + "\n")
        self.log_text.see(tk.END)

    def load_from_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
        if not filename:
            return

        try:
            with open(filename, 'r') as f:
                lines = f.readlines()

            self.x = float(lines[0].strip())
            self.xs = []
            self.ys = []

            for line in lines[1:]:
                if len(line.strip()) == 0:
                    continue
                parts = line.strip().split()
                if len(parts) == 2:
                    self.xs.append(float(parts[0]))
                    self.ys.append(float(parts[1]))

            if len(self.xs) == 0:
                raise ValueError("Нет данных в файле")

            self.log(f"Данные успешно загружены из файла: {os.path.basename(filename)}")
            self.solve_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении файла: {e}")

    def manual_input(self):
        try:
            self.x = float(simpledialog.askstring("Точка интерполяции", "Введите x:"))
            self.xs.clear()
            self.ys.clear()
            while True:
                point = simpledialog.askstring("Введите точку", "Введите x и y через пробел (или оставьте пустым для окончания):")
                if not point:
                    break
                parts = point.strip().split()
                if len(parts) == 2:
                    self.xs.append(float(parts[0]))
                    self.ys.append(float(parts[1]))
            if len(self.xs) < 2:
                raise ValueError("Недостаточно точек")
            self.log("Данные успешно введены вручную")
            self.solve_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при вводе данных: {e}")

    def use_example(self):
        self.x = 0.502
        self.xs = [0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
        self.ys = [1.5320, 2.5356, 3.5406, 4.5462, 5.5504, 6.5559, 7.5594]
        self.log("Загружен предустановленный пример")
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
                self.ys = list(map(f, self.xs))

                self.log("Данные успешно сгенерированы по функции")
                self.solve_btn.config(state=tk.NORMAL)
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при генерации функции: {e}")

        popup = tk.Toplevel(self.root)
        popup.title("Выбор функции")

        tk.Label(popup, text="Выберите функцию:").pack()
        func_var = tk.IntVar(value=1)
        functions = [
            "1. 2*x^2 - 5*x",
            "2. x^5",
            "3. sin(x)",
            "4. sqrt(x)"
        ]
        for i, func in enumerate(functions, start=1):
            tk.Radiobutton(popup, text=func, variable=func_var, value=i).pack(anchor='w')

        tk.Label(popup, text="Число узлов:").pack()
        entry_n = tk.Entry(popup)
        entry_n.insert(0, "5")
        entry_n.pack()

        tk.Label(popup, text="x0:").pack()
        entry_x0 = tk.Entry(popup)
        entry_x0.insert(0, "0.0")
        entry_x0.pack()

        tk.Label(popup, text="xn:").pack()
        entry_xn = tk.Entry(popup)
        entry_xn.insert(0, "1.0")
        entry_xn.pack()

        tk.Label(popup, text="Точка интерполяции x:").pack()
        entry_x = tk.Entry(popup)
        entry_x.insert(0, "0.5")
        entry_x.pack()

        tk.Button(popup, text="ОК", command=on_ok).pack(pady=10)

    def process(self):
        if not self.xs or not self.ys:
            messagebox.showerror("Ошибка", "Нет данных для обработки")
            return

        if len(set(self.xs)) != len(self.xs):
            messagebox.showerror("Ошибка", "Узлы интерполяции не должны совпадать")
            return

        if self.xs != sorted(self.xs):
            messagebox.showerror("Ошибка", "Узлы должны быть отсортированы по возрастанию")
            return

        self.log("Выполнение интерполяции...\n")
        solve(self.xs, self.ys, self.x, len(self.xs))


if __name__ == "__main__":
    root = tk.Tk()
    app = InterpolationApp(root)
    root.mainloop()
