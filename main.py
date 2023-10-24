import sys
import csv
import numpy as np
from sympy import symbols, sympify
from sympy.utilities.lambdify import lambdify
import math
import random
import matplotlib.pyplot as plt
from PyQt6.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox, QVBoxLayout, QTableWidget, QTableWidgetItem
from Unlinear_Integral import Ui_Form
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class IntegralsSolver(QWidget):
    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)
        self.initializeUI()
        np.set_printoptions(precision=3)
        # self.show()
        self.setGeometry(100, 100, 860, 600)
        self.func_text = '-2*x'
        self.result = 0
        self.analit_value = 0
        self.points_x = []
        self.points_y = []

    def initializeUI(self):

        # Знайти віджет QGraphicsView за ім'ям ("graphicsView")
        self.ui.graphicsView = self.findChild(QWidget, "graphicsView")

        # Створити віджет графіка Matplotlib
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)

        # Отримати поточні вісі для побудови графіка
        self.ax = self.figure.add_subplot(111)

        layout = QVBoxLayout(self.ui.graphicsView)
        layout.addWidget(self.canvas)
        # self.ui.horizontalLayout_8.addWidget(self.canvas)

        #validation
        self.ui.func_entry.setPlaceholderText("Введіть формулу в нотації Python")
        regex1 = QRegularExpression("-?[0-9]+\.?[0-9]*")
        self.ui.a_entry.setValidator(QRegularExpressionValidator(regex1))
        self.ui.b_entry.setValidator(QRegularExpressionValidator(regex1))
        regex2 = QRegularExpression("[0-9]+")
        self.ui.n1_entry.setValidator(QRegularExpressionValidator(regex2))
        self.ui.n2_entry.setValidator(QRegularExpressionValidator(regex2))
        self.ui.n3_entry.setValidator(QRegularExpressionValidator(regex2))

        # Add signal/slot connections for buttons
        self.ui.plot_button.clicked.connect(self.run_plot)
        self.ui.rect_button.clicked.connect(self.rectangle_integral)
        self.ui.trap_button.clicked.connect(self.trapeziod_integral)
        self.ui.monte_button.clicked.connect(self.monte_carlo_integral)
        # clear table
        self.ui.button_clear.clicked.connect(self.clear_table)
        # save to file
        self.ui.save_button.clicked.connect(self.save_table_file)

    def f(self, x):
        pass

    def run_plot(self):
        func_text = self.ui.func_entry.text()
        if func_text == '':
            func_text = self.func_text
        f = self.convert_to_func(func_text)
        self.plot(f)

    def rectangle_integral(self):
        func_text = self.ui.func_entry.text()
        if func_text == '':
            func_text = self.func_text
        f = self.convert_to_func(func_text)
        method = 'прямокутників'
        iterations_num = int(self.ui.n1_entry.text())
        self.run_method(f, self.rectangle_integral_calc, method, self.ui.table_rect, iterations_num)

    def trapeziod_integral(self):
        func_text = self.ui.func_entry.text()
        if func_text == '':
            func_text = self.func_text
        f = self.convert_to_func(func_text)
        method = 'трапецій'
        iterations_num = int(self.ui.n2_entry.text())
        self.run_method(f, self.trapeziod_integral_calc, method, self.ui.table_trap, iterations_num)

    def monte_carlo_integral(self):
        func_text = self.ui.func_entry.text()
        if func_text == '':
            func_text = self.func_text
        f = self.convert_to_func(func_text)
        method = 'Монте-Карло'
        iterations_num = int(self.ui.n3_entry.text())
        self.run_method(f, self.monte_carlo_integral_calc, method, self.ui.table_monte, iterations_num)

    def convert_to_func(self, func_text):
        try:
            # variables in math expressions
            x = symbols('x')
            y = symbols('y')
            z = symbols('z')
            # convert text to SymPy object
            expression = sympify(func_text)
            # function from expression, use numpy to optimize work
            # with NumPy objects if variables or result are arrays
            return lambdify(x, expression, 'numpy')
        except Exception as e:
            self.ui.result_label.setText(f'Помилка у перетворені тексту в функцію: {str(e)}')

    def run_method(self, f, method_function, method, table, iterations_num):
        a = float(self.ui.a_entry.text())
        b = float(self.ui.b_entry.text())
        if math.isnan(f(a)) or math.isnan(f(b)):
            self.ui.result_label.setText(f'Некоректне введення відрізку')
            return
        # self.result = 0

        try:
            # iterations_num = int(self.ui.n1_entry.text())
            method_function(f, a, b, iterations_num)
            print(f'result:{self.result}')
            self.ui.result_label.setText(f"Результат (Метод {method}): {self.result: .6f}")
            self.update_table(table, iterations_num)
            self.plot_result(f, method)
        except ValueError:
            self.ui.result_label.setText("Помилка при обчисленні інтегралу")

    # Метод прямокутників
    def rectangle_integral_calc(self, f, a, b, n):
        try:
            dx = (b - a)/n
            y_sum = 0
            half_dx = dx/2
            # summ of function values f(a + (2n-1)dx/2),  a + (2n-1)dx/2 - middle of each interval
            for i in range(1, n+1):
                y_sum += f(a + (2*i-1)*half_dx)
            self.result = y_sum*dx
        except ZeroDivisionError as e:
            self.ui.result_label.setText(f'Помилка: {e}')


    # Метод трапецій
    def trapeziod_integral_calc(self,f, a, b, n):
        try:
            dx = (b - a)/n
            y_sum = (f(a) + f(b))/2
            x = a
            # summ of function values f(a + ndx)
            for i in range(1, n):
                x += dx
                y_sum += f(x)
            self.result = y_sum*dx
        except ZeroDivisionError as e:
            self.ui.result_label.setText(f'Помилка: {e}')

    def monte_carlo_integral_calc(self, f, a, b, n):
        inner_points = 0
        step = 10000
        self.points_x = []
        self.points_y = []
        try:
            # find min and max y
            dx = (b - a)/step
            x = a
            y_max = f(a)
            y_min = f(b)
            for i in range(0, step):
                x += dx
                y = f(x)
                if y_max < y:
                    y_max = y
                if y_min > y:
                    y_min = y

            line =  y_max if  y_min >= 0 else y_min
            for i in range(0, n):
                x = random.random()*(b-a) + a
                y = random.random()*line
                if abs(y) <= abs(f(x)):
                    inner_points += 1
                self.points_x.append(x)
                self.points_y.append(y)

            self.result = (inner_points/n)*(b-a)*line
        except ZeroDivisionError as e:
            self.ui.result_label.setText(f'Помилка: {e}')

    def update_table(self, table, param):
        row_position = table.rowCount()
        table.insertRow(row_position)
        self.analit_value = self.ui.analit_entry.text()
        table.setItem(row_position, 0, QTableWidgetItem(str(param)))
        table.setItem(row_position, 1, QTableWidgetItem(f"{self.analit_value}"))
        table.setItem(row_position, 2, QTableWidgetItem(f"{str(round(self.result, 6))}"))

    def plot(self, func):
            a = float(self.ui.a_entry.text())
            b = float(self.ui.b_entry.text())
            x = np.linspace(a, b, 500)
            y = []
            try:
                y = [func(xi) for xi in x]
            except ZeroDivisionError as e:
                self.ui.result_label.setText(f'Помилка: {e}')

            # графік у вікні matplotlib
            plt.figure()
            plt.plot(x, y, label=self.ui.func_entry.text())
            plt.xlabel('x')
            plt.ylabel('y')
            plt.title(f'Графік функції')
            plt.legend()
            plt.grid(True)
            plt.show()

    def plot_result(self, func, method):
        a = float(self.ui.a_entry.text())
        b = float(self.ui.b_entry.text())
        x = np.linspace(a, b, 500)
        y = []
        interval_line_y = np.array([])
        try:
            y = [func(xi) for xi in x]
            # segment boundaries
            if min(y) >= 0:
                interval_line_y = np.linspace(0, max(y), 2)
            elif max(y) <= 0:
                interval_line_y = np.linspace(min(y), 0, 2)
            else:
                interval_line_y = np.linspace(min(y), max(y), 2)
        except ZeroDivisionError as e:
            self.ui.result_label.setText(f'Помилка: {e}')

        # графік canvas у вікні інтерфейсу

        self.ax.clear()
        self.ax.plot(x, y, label=self.ui.func_entry.text())
        self.ax.plot([a]*len(interval_line_y), interval_line_y, color='red')
        self.ax.plot([b]*len(interval_line_y), interval_line_y, color='red')
        self.ax.axhline(0, color='black')
        self.ax.axvline(0, color='black')
        self.ax.set_xlabel('x')
        self.ax.set_ylabel('y')
        self.ax.grid(True)
        self.ax.set_title(f'Інтегрування методом {method}')
        self.ax.legend()
        if method == 'Монте-Карло':
            self.ax.scatter(self.points_x, self.points_y, color='green', marker='.')
        self.canvas.draw()

    def clear_table(self):
        current_tab_widget = self.ui.tabWidget.currentWidget()
        table_widget = current_tab_widget.findChild(QTableWidget)
        table_widget.setRowCount(0)

    def save_table_file(self):
        # Поточний індекс вкладки
        current_tab_index = self.ui.tabWidget.currentIndex()

        # Отримати поточну вкладку за індексом
        current_tab = self.ui.tabWidget.widget(current_tab_index)

        # Отримати об'ект QTableWidget на поточній вкладці
        table_widget = current_tab.findChild(QTableWidget)

        # Отримуємо дані таблиці
        data = []
        for row in range(table_widget.rowCount()):
             # додати назву методу
            row_data = [self.ui.tabWidget.tabText(current_tab_index)]
            for column in range(table_widget.columnCount()):
                item = table_widget.item(row, column)
                if item is not None:
                    row_data.append(item.text())
                else:
                    row_data.append('')
            data.append(row_data)

        # Відкрити діалогове вікно для вибору файлу та отримати шлях
        file_name, _ = QFileDialog.getSaveFileName(self, "Збереження в файл", "equation_resolutions.csv", "CSV Files (*.csv);;All Files (*)")

        if file_name:
            try:
                with open(file_name, 'a', newline='', encoding="utf-16") as csv_file:
                    csv_writer = csv.writer(csv_file)
                    for row_data in data:
                        csv_writer.writerow(row_data)
                QMessageBox.information(self, "Успех", "Таблица успешно сохранена в файл.")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Помилка при збереженні файла: {str(e)}")
def main():
    app = QApplication(sys.argv)
    window = IntegralsSolver()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
