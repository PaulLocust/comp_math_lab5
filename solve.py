from functools import reduce
from math import factorial
import numpy as np
import matplotlib.pyplot as plt


def lagrange_polynomial(xs, ys, n):
    return lambda x: sum([
        ys[i] * reduce(
            lambda a, b: a * b,
            [(x - xs[j]) / (xs[i] - xs[j]) for j in range(n) if i != j]
        )
        for i in range(n)
    ])


def divided_differences(x, y):
    n = len(y)
    coef = np.copy(y).astype(float)
    for j in range(1, n):
        for i in range(n-1, j-1, -1):
            coef[i] = (coef[i] - coef[i-1]) / (x[i] - x[i-j])
    return coef


def newton_divided_difference_polynomial(xs, ys, n):
    coef = divided_differences(xs, ys)
    return lambda x: ys[0] + sum([
        coef[k] * reduce(lambda a, b: a * b, [x - xs[j] for j in range(k)]) for k in range(1, n)
    ])


def finite_differences(y):
    n = len(y)
    delta_y = np.zeros((n, n))
    delta_y[:, 0] = y
    for j in range(1, n):
        for i in range(n - j):
            delta_y[i, j] = delta_y[i + 1, j - 1] - delta_y[i, j - 1]
    return delta_y


def print_finite_differences_table(delta_y):
    n = delta_y.shape[0]
    table = "Таблица конечных разностей:\n"
    for i in range(n):
        row = [f"{delta_y[i, j]:.4f}" if i + j < n else "" for j in range(n)]
        table += "\t".join(row) + "\n"
    return table


def newton_finite_difference_polynomial(xs, ys, n):
    h = xs[1] - xs[0]
    delta_y = finite_differences(ys)
    return lambda x: ys[0] + sum([
        reduce(lambda a, b: a * b, [(x - xs[0]) / h - j for j in range(k)]) * delta_y[0, k] / factorial(k)
        for k in range(1, n)
    ])


def gauss_polynomial(xs, ys, n):
    n = len(xs) - 1
    alpha_ind = n // 2
    fin_difs = []
    fin_difs.append(ys[:])

    for k in range(1, n + 1):
        last = fin_difs[-1][:]
        fin_difs.append(
            [last[i + 1] - last[i] for i in range(n - k + 1)])

    h = xs[1] - xs[0]
    dts1 = [0, -1, 1, -2, 2, -3, 3, -4, 4]

    f1 = lambda x: ys[alpha_ind] + sum([
        reduce(lambda a, b: a * b,
               [(x - xs[alpha_ind]) / h + dts1[j] for j in range(k)])
        * fin_difs[k][len(fin_difs[k]) // 2] / factorial(k)
        for k in range(1, n + 1)])

    f2 = lambda x: ys[alpha_ind] + sum([
        reduce(lambda a, b: a * b,
               [(x - xs[alpha_ind]) / h - dts1[j] for j in range(k)])
        * fin_difs[k][len(fin_difs[k]) // 2 - (1 - len(fin_difs[k]) % 2)] / factorial(k)
        for k in range(1, n + 1)])

    return lambda x: f1(x) if x > xs[alpha_ind] else f2(x)


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
        if method in [gauss_polynomial] and even_n:
            continue

        P = method(xs, ys, n)
        y_val = P(x)
        results += f"{name}:\nP({x}) = {y_val:.6f}\n" + "-" * 60 + "\n"

        if return_plots:
            fig = create_plot(xs, ys, x, P, name)
            figures.append(fig)
        else:
            draw_plot(xs, ys, x, P, name)

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