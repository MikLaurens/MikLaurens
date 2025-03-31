# ui.py
from PyQt5.QtWidgets import (QMainWindow, QApplication, QTabWidget, QWidget,
                             QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QLabel, QLineEdit, QDateEdit,
                             QComboBox, QSpinBox, QMessageBox, QFormLayout,
                             QHeaderView)
from PyQt5.QtCore import QDate
from database import Database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.setWindowTitle('Учет производства и продаж - ООО "Мясной дом"')
        self.setGeometry(100, 100, 800, 600)

        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()

        # Вкладка товаров
        self.products_tab = QWidget()
        self.init_products_tab()
        self.tabs.addTab(self.products_tab, "Товары")

        # Вкладка производства
        self.production_tab = QWidget()
        self.init_production_tab()
        self.tabs.addTab(self.production_tab, "Производство")

        # Вкладка продаж
        self.sales_tab = QWidget()
        self.init_sales_tab()
        self.tabs.addTab(self.sales_tab, "Продажи")

        # Вкладка отчетов
        self.reports_tab = QWidget()
        self.init_reports_tab()
        self.tabs.addTab(self.reports_tab, "Отчеты")

        self.setCentralWidget(self.tabs)

    def init_products_tab(self):
        layout = QVBoxLayout()

        # Форма добавления/редактирования товара
        form_layout = QHBoxLayout()

        self.product_name = QLineEdit()
        self.product_name.setPlaceholderText("Название товара")

        self.product_price = QLineEdit()
        self.product_price.setPlaceholderText("Цена")

        self.product_stock = QSpinBox()
        self.product_stock.setMinimum(0)
        self.product_stock.setValue(0)

        add_btn = QPushButton("Добавить товар")
        add_btn.clicked.connect(self.add_product)

        save_btn = QPushButton("Сохранить изменения")
        save_btn.clicked.connect(self.save_product_changes)

        delete_btn = QPushButton("Удалить выбранный")
        delete_btn.clicked.connect(self.delete_product)

        form_layout.addWidget(self.product_name)
        form_layout.addWidget(self.product_price)
        form_layout.addWidget(QLabel("Количество:"))
        form_layout.addWidget(self.product_stock)
        form_layout.addWidget(add_btn)
        form_layout.addWidget(save_btn)
        form_layout.addWidget(delete_btn)

        # Таблица товаров
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(4)
        self.products_table.setHorizontalHeaderLabels(["ID", "Название", "Цена", "Остаток"])
        self.products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.products_table.cellDoubleClicked.connect(self.load_product_for_edit)
        self.update_products_table()

        layout.addLayout(form_layout)
        layout.addWidget(self.products_table)

        self.products_tab.setLayout(layout)

    def load_product_for_edit(self, row, column):
        """Загружает данные товара в форму для редактирования"""
        product_id = int(self.products_table.item(row, 0).text())
        name = self.products_table.item(row, 1).text()
        price = self.products_table.item(row, 2).text()
        stock = int(self.products_table.item(row, 3).text())

        self.current_edit_id = product_id
        self.product_name.setText(name)
        self.product_price.setText(price)
        self.product_stock.setValue(stock)

    def save_product_changes(self):
        """Сохраняет изменения товара в базе данных"""
        if not hasattr(self, 'current_edit_id'):
            QMessageBox.warning(self, "Ошибка", "Выберите товар для редактирования (двойной клик по строке)")
            return

        name = self.product_name.text()
        price = self.product_price.text()
        stock = self.product_stock.value()

        if not name or not price:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть числом")
            return

        try:
            self.db.update_product(self.current_edit_id, name, price, stock)
            self.update_products_table()
            self.update_production_products()
            self.update_sale_products()

            # Очищаем форму после сохранения
            self.product_name.clear()
            self.product_price.clear()
            self.product_stock.setValue(0)
            delattr(self, 'current_edit_id')

            QMessageBox.information(self, "Успех", "Изменения сохранены")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить изменения: {str(e)}")

    def update_products_table(self):
        """Обновление таблицы товаров с форматированием цены"""
        products = self.db.get_products()
        self.products_table.setRowCount(len(products))

        for row, product in enumerate(products):
            for col, value in enumerate(product):
                # Для цены отображаем с 2 знаками после запятой
                if col == 2:  # Столбец с ценой
                    self.products_table.setItem(row, col, QTableWidgetItem(f"{float(value):.2f}"))
                else:
                    self.products_table.setItem(row, col, QTableWidgetItem(str(value)))

    def init_production_tab(self):
        layout = QVBoxLayout()

        # Форма добавления производства
        form_layout = QFormLayout()

        self.production_product = QComboBox()
        self.update_production_products()

        self.production_quantity = QSpinBox()
        self.production_quantity.setMinimum(1)
        self.production_quantity.setValue(1)

        self.production_date = QDateEdit()
        self.production_date.setDate(QDate.currentDate())
        self.production_date.setCalendarPopup(True)

        add_btn = QPushButton("Добавить производство")
        add_btn.clicked.connect(self.add_production)

        form_layout.addRow("Товар:", self.production_product)
        form_layout.addRow("Количество:", self.production_quantity)
        form_layout.addRow("Дата производства:", self.production_date)
        form_layout.addRow(add_btn)

        # Таблица производства
        self.production_table = QTableWidget()
        self.production_table.setColumnCount(4)
        self.production_table.setHorizontalHeaderLabels(["ID", "Товар", "Количество", "Дата"])
        self.production_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.update_production_table()

        layout.addLayout(form_layout)
        layout.addWidget(self.production_table)

        self.production_tab.setLayout(layout)

    def init_sales_tab(self):
        layout = QVBoxLayout()

        # Форма добавления продажи
        form_layout = QFormLayout()

        self.sale_product = QComboBox()
        self.update_sale_products()

        self.sale_quantity = QSpinBox()
        self.sale_quantity.setMinimum(1)
        self.sale_quantity.setValue(1)

        self.sale_date = QDateEdit()
        self.sale_date.setDate(QDate.currentDate())
        self.sale_date.setCalendarPopup(True)

        add_btn = QPushButton("Добавить продажу")
        add_btn.clicked.connect(self.add_sale)

        form_layout.addRow("Товар:", self.sale_product)
        form_layout.addRow("Количество:", self.sale_quantity)
        form_layout.addRow("Дата продажи:", self.sale_date)
        form_layout.addRow(add_btn)

        # Таблица продаж
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(5)
        self.sales_table.setHorizontalHeaderLabels(["ID", "Товар", "Количество", "Цена", "Дата"])
        self.sales_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.update_sales_table()

        layout.addLayout(form_layout)
        layout.addWidget(self.sales_table)

        self.sales_tab.setLayout(layout)

    def init_reports_tab(self):
        layout = QVBoxLayout()

        # Форма выбора периода для отчетов
        period_layout = QHBoxLayout()

        self.report_start_date = QDateEdit()
        self.report_start_date.setDate(QDate.currentDate().addMonths(-1))
        self.report_start_date.setCalendarPopup(True)

        self.report_end_date = QDateEdit()
        self.report_end_date.setDate(QDate.currentDate())
        self.report_end_date.setCalendarPopup(True)

        sales_report_btn = QPushButton("Отчет по продажам")
        sales_report_btn.clicked.connect(self.generate_sales_report)

        production_report_btn = QPushButton("Отчет по производству")
        production_report_btn.clicked.connect(self.generate_production_report)

        stock_report_btn = QPushButton("Отчет по остаткам")
        stock_report_btn.clicked.connect(self.generate_stock_report)

        period_layout.addWidget(QLabel("С:"))
        period_layout.addWidget(self.report_start_date)
        period_layout.addWidget(QLabel("По:"))
        period_layout.addWidget(self.report_end_date)
        period_layout.addWidget(sales_report_btn)
        period_layout.addWidget(production_report_btn)
        period_layout.addWidget(stock_report_btn)

        # Таблица отчетов
        self.report_table = QTableWidget()
        self.report_table.setColumnCount(5)
        self.report_table.setHorizontalHeaderLabels(["Тип", "Название", "Количество", "Сумма", "Дата"])
        self.report_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        layout.addLayout(period_layout)
        layout.addWidget(self.report_table)

        self.reports_tab.setLayout(layout)

    # Методы для работы с товарами
    def add_product(self):
        name = self.product_name.text()
        price = self.product_price.text()
        stock = self.product_stock.value()

        if not name or not price:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return

        try:
            price = float(price)
        except ValueError:
            QMessageBox.warning(self, "Ошибка", "Цена должна быть числом")
            return

        self.db.add_product(name, price, stock)
        self.update_products_table()
        self.update_production_products()
        self.update_sale_products()
        self.product_name.clear()
        self.product_price.clear()
        self.product_stock.setValue(0)

    def delete_product(self):
        selected = self.products_table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Ошибка", "Выберите товар для удаления")
            return

        product_id = int(self.products_table.item(selected, 0).text())

        reply = QMessageBox.question(self, 'Подтверждение',
                                     'Вы действительно хотите удалить этот товар?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.db.delete_product(product_id)
            self.update_products_table()
            self.update_production_products()
            self.update_sale_products()
            self.update_production_table()
            self.update_sales_table()

    def update_products_table(self):
        products = self.db.get_products()
        self.products_table.setRowCount(len(products))

        for row, product in enumerate(products):
            for col, value in enumerate(product):
                self.products_table.setItem(row, col, QTableWidgetItem(str(value)))

    def update_production_products(self):
        self.production_product.clear()
        products = self.db.get_products()
        for product in products:
            self.production_product.addItem(product[1], product[0])

    def update_sale_products(self):
        self.sale_product.clear()
        products = self.db.get_products()
        for product in products:
            self.sale_product.addItem(product[1], product[0])

    # Методы для работы с производством
    def add_production(self):
        product_id = self.production_product.currentData()
        quantity = self.production_quantity.value()
        date = self.production_date.date().toString("yyyy-MM-dd")

        if not product_id:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return

        try:
            self.db.add_production(product_id, quantity, date)
            self.update_production_table()
            self.update_products_table()
            QMessageBox.information(self, "Успех", "Производство добавлено")
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", str(e))

    def update_production_table(self):
        production_data = self.db.get_production()
        self.production_table.setRowCount(len(production_data))

        for row, data in enumerate(production_data):
            for col, value in enumerate(data):
                self.production_table.setItem(row, col, QTableWidgetItem(str(value)))

    # Методы для работы с продажами
    def add_sale(self):
        product_id = self.sale_product.currentData()
        quantity = self.sale_quantity.value()
        date = self.sale_date.date().toString("yyyy-MM-dd")

        if not product_id:
            QMessageBox.warning(self, "Ошибка", "Выберите товар")
            return

        try:
            self.db.add_sale(product_id, quantity, date)
            self.update_sales_table()
            self.update_products_table()
            QMessageBox.information(self, "Успех", "Продажа добавлена")
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Произошла ошибка: {str(e)}")

    def update_sales_table(self):
        sales_data = self.db.get_sales()
        self.sales_table.setRowCount(len(sales_data))

        for row, data in enumerate(sales_data):
            for col, value in enumerate(data):
                self.sales_table.setItem(row, col, QTableWidgetItem(str(value)))

    # Методы для работы с отчетами
    # ui.py (исправленные методы отчетов)
    def generate_sales_report(self):
        start_date = self.report_start_date.date().toString("yyyy-MM-dd")
        end_date = self.report_end_date.date().toString("yyyy-MM-dd")

        try:
            sales = self.db.get_sales_by_period(start_date, end_date)
            self.report_table.setRowCount(len(sales))
            self.report_table.setColumnCount(5)
            self.report_table.setHorizontalHeaderLabels(["ID", "Товар", "Количество", "Цена", "Дата"])

            for row, sale in enumerate(sales):
                for col in range(5):
                    self.report_table.setItem(row, col, QTableWidgetItem(str(sale[col])))

            # Добавляем итоговую строку
            total_quantity = sum(sale[2] for sale in sales)
            total_amount = sum(sale[2] * sale[3] for sale in sales)

            self.report_table.setRowCount(self.report_table.rowCount() + 1)
            self.report_table.setItem(self.report_table.rowCount() - 1, 1, QTableWidgetItem("ИТОГО:"))
            self.report_table.setItem(self.report_table.rowCount() - 1, 2, QTableWidgetItem(str(total_quantity)))
            self.report_table.setItem(self.report_table.rowCount() - 1, 3, QTableWidgetItem(str(total_amount)))

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при формировании отчета: {str(e)}")

    def generate_production_report(self):
        start_date = self.report_start_date.date().toString("yyyy-MM-dd")
        end_date = self.report_end_date.date().toString("yyyy-MM-dd")

        try:
            production = self.db.get_production_by_period(start_date, end_date)
            self.report_table.setRowCount(len(production))
            self.report_table.setColumnCount(4)
            self.report_table.setHorizontalHeaderLabels(["ID", "Товар", "Количество", "Дата"])

            for row, prod in enumerate(production):
                for col in range(4):
                    self.report_table.setItem(row, col, QTableWidgetItem(str(prod[col])))

            # Добавляем итоговую строку
            total_quantity = sum(prod[2] for prod in production)

            self.report_table.setRowCount(self.report_table.rowCount() + 1)
            self.report_table.setItem(self.report_table.rowCount() - 1, 1, QTableWidgetItem("ИТОГО:"))
            self.report_table.setItem(self.report_table.rowCount() - 1, 2, QTableWidgetItem(str(total_quantity)))

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при формировании отчета: {str(e)}")

    def generate_stock_report(self):
        try:
            stock = self.db.get_stock_report()
            self.report_table.setRowCount(len(stock))
            self.report_table.setColumnCount(5)
            self.report_table.setHorizontalHeaderLabels(["ID", "Товар", "Остаток", "Цена", "Сумма"])

            for row, item in enumerate(stock):
                for col in range(4):
                    self.report_table.setItem(row, col, QTableWidgetItem(str(item[col])))
                # Добавляем столбец с суммой (количество * цену)
                self.report_table.setItem(row, 4, QTableWidgetItem(str(item[2] * item[3])))

            # Добавляем итоговую строку
            total_stock = sum(item[2] for item in stock)
            total_amount = sum(item[2] * item[3] for item in stock)

            self.report_table.setRowCount(self.report_table.rowCount() + 1)
            self.report_table.setItem(self.report_table.rowCount() - 1, 1, QTableWidgetItem("ИТОГО:"))
            self.report_table.setItem(self.report_table.rowCount() - 1, 2, QTableWidgetItem(str(total_stock)))
            self.report_table.setItem(self.report_table.rowCount() - 1, 4, QTableWidgetItem(str(total_amount)))

        except Exception as e:
            QMessageBox.warning(self, "Ошибка", f"Ошибка при формировании отчета: {str(e)}")