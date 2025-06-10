from math import factorial
import numpy as np
import matplotlib.pyplot as plt


def lagrange_polynomial(xs, ys, n, x):
    """
    Интерполяция по методу Лагранжа.

    Входные параметры:
    xs : массив координат узлов интерполяции
    ys : массив значений функции в узлах
    n  : количество узлов
    x  : точка, в которой вычисляем значение интерполированного многочлена

    Возвращает:
    значение интерполированного многочлена в точке x
    """
    total = 0
    for i in range(n):
        product = 1
        for j in range(n):
            if i != j:
                product *= (x - xs[j]) / (xs[i] - xs[j])
        total += ys[i] * product
    return total


def divided_differences(xs, ys):
    """
    Вычисление коэффициентов для интерполяционного многочлена Ньютона по разделённым разностям.

    Входные параметры:
    xs : массив координат узлов интерполяции
    ys : массив значений функции в узлах

    Возвращает:
    coef : список коэффициентов разделённых разностей
    """
    n = len(ys)
    coef = ys.copy()
    for j in range(1, n):
        for i in range(n - 1, j - 1, -1):
            coef[i] = (coef[i] - coef[i - 1]) / (xs[i] - xs[i - j])
    return coef


def newton_divided_difference_polynomial(xs, ys, n, x):
    """
    Интерполяция многочленом Ньютона с использованием разделённых разностей.

    Входные параметры:
    xs : массив координат узлов интерполяции
    ys : массив значений функции в узлах
    n  : количество узлов
    x  : точка, в которой вычисляем значение интерполированного многочлена

    Возвращает:
    значение интерполированного многочлена в точке x
    """
    coef = divided_differences(xs, ys)
    total = ys[0]
    for k in range(1, n):
        product = 1
        for j in range(k):
            product *= x - xs[j]
        total += coef[k] * product
    return total


def finite_differences(ys):
    """
    Построение таблицы конечных разностей для метода конечных разностей.

    Входные параметры:
    ys : массив значений функции в узлах интерполяции

    Возвращает:
    delta_y : двумерный список (матрица) конечных разностей размером n x n
    """
    n = len(ys)
    # Инициализация пустой матрицы нулями
    delta_y = []
    for _ in range(n):
        row = []
        for _ in range(n):
            row.append(0)
        delta_y.append(row)

    for i in range(n):
        delta_y[i][0] = ys[i]
    for j in range(1, n):
        for i in range(n - j):
            delta_y[i][j] = delta_y[i + 1][j - 1] - delta_y[i][j - 1]
    return delta_y


def newton_finite_difference_polynomial(xs, ys, n, x):
    """
    Интерполяция многочленом Ньютона с использованием конечных разностей.

    Входные параметры:
    xs : массив координат узлов интерполяции (равномерно расположенных)
    ys : массив значений функции в узлах
    n  : количество узлов
    x  : точка, в которой вычисляем значение интерполированного многочлена

    Возвращает:
    значение интерполированного многочлена в точке x
    """

    h = xs[1] - xs[0]  # шаг
    delta_y = finite_differences(ys)
    total = ys[0]
    for k in range(1, n):
        product = 1
        for j in range(k):
            product *= (x - xs[0]) / h - j
        total += delta_y[0][k] * product / factorial(k)
    return total


def gauss_polynomial(xs, ys, n, x):
    """
    Интерполяция многочленом Гаусса с использованием центральных конечных разностей.

    Входные параметры:
    xs : массив координат узлов интерполяции (равномерно расположенных)
    ys : массив значений функции в узлах
    n  : количество узлов
    x  : точка, в которой вычисляем значение интерполированного многочлена

    Возвращает:
    значение интерполированного многочлена в точке x
    """

    m = len(xs)
    alpha_ind = (m - 1) // 2  # центральный узел

    # Построение таблицы конечных разностей
    fin_difs = []
    fin_difs.append(ys[:])
    for k in range(1, m):
        prev = fin_difs[-1]
        current = []
        for i in range(len(prev) - 1):
            current.append(prev[i + 1] - prev[i])
        fin_difs.append(current)

    h = xs[1] - xs[0]
    t = (x - xs[alpha_ind]) / h
    total = ys[alpha_ind]

    dts = [0, 1, -1, 2, -2, 3, -3, 4, -4]  # порядок множителей для произведения
    for k in range(1, n):
        product = 1
        for j in range(k):
            product *= t + dts[j]
        mid_index = len(fin_difs[k]) // 2
        if len(fin_difs[k]) % 2 == 0:
            index = mid_index - 1
        else:
            index = mid_index
        total += fin_difs[k][index] * product / factorial(k)

    return total


def print_finite_differences_table(delta_y):
    n = len(delta_y)
    table = "Таблица конечных разностей:\n"
    for i in range(n):
        row = []
        for j in range(n - i):
            row.append(f"{delta_y[i][j]:.4f}")
        table += "\t".join(row) + "\n"
    return table


def draw_plot(xs, ys, x_point, interpolation_func, method_name):
    x_vals = np.linspace(xs[0] - 0.1, xs[-1] + 0.1, 1000)
    y_vals = [interpolation_func(x) for x in x_vals]

    plt.figure(figsize=(8, 5))
    plt.plot(x_vals, y_vals, label=f"{method_name}", color="green")
    plt.scatter(xs, ys, color="blue", label="Узлы интерполяции")
    plt.scatter([x_point], [interpolation_func(x_point)], color="red", label=f"P({x_point:.3f})")
    plt.title(f"Интерполяция методом: {method_name}")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()


def solve(xs, ys, x, n, return_plots=False):
    results = ""
    delta_y = finite_differences(ys)
    results += print_finite_differences_table(delta_y) + "\n"
    results += "-" * 60 + "\n"

    methods = [
        ("Многочлен Лагранжа", lagrange_polynomial),
        ("Многочлен Ньютона (раздел. разности)", newton_divided_difference_polynomial),
        ("Многочлен Ньютона (конеч. разности)", newton_finite_difference_polynomial),
        ("Многочлен Гаусса", gauss_polynomial)
    ]

    h = xs[1] - xs[0]
    finite_diff_valid = all(abs(xs[i] - xs[i - 1] - h) < 1e-5 for i in range(1, n))
    even_n = n % 2 == 0

    figures = []

    for name, method in methods:
        if method == newton_finite_difference_polynomial and not finite_diff_valid:
            continue
        if method == newton_divided_difference_polynomial and finite_diff_valid:
            continue
        if method == gauss_polynomial and even_n:
            continue

        y_val = method(xs, ys, n, x)
        results += f"{name}:\nP({x}) = {y_val:.6f}\n" + "-" * 60 + "\n"

        if return_plots:
            fig = create_plot(xs, ys, x, lambda z: method(xs, ys, n, z), name)
            figures.append(fig)
        else:
            draw_plot(xs, ys, x, lambda z: method(xs, ys, n, z), name)

    return (results, figures) if return_plots else results


def create_plot(xs, ys, x_point, interpolation_func, method_name):
    x_vals = np.linspace(xs[0] - 0.1, xs[-1] + 0.1, 1000)
    y_vals = [interpolation_func(x) for x in x_vals]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(x_vals, y_vals, label=f"{method_name}", color="green")
    ax.scatter(xs, ys, color="blue", label="Узлы интерполяции")
    ax.scatter([x_point], [interpolation_func(x_point)], color="red", label=f"P({x_point:.3f})")
    ax.set_title(f"Интерполяция методом: {method_name}")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True)
    ax.legend()
    fig.tight_layout()
    return fig
