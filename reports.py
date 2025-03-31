# reports.py
from datetime import datetime
from database import Database  # Импорт класса Database для работы с базой данных


class Reports:
    """Класс для генерации различных отчетов предприятия"""

    def __init__(self):
        """Инициализация объекта Reports с подключением к базе данных"""
        self.db = Database()  # Создаем экземпляр Database для работы с БД

    def sales_report(self, start_date, end_date):
        """
        Генерация отчета по продажам за указанный период

        Args:
            start_date (str): Начальная дата периода в формате 'YYYY-MM-DD'
            end_date (str): Конечная дата периода в формате 'YYYY-MM-DD'

        Returns:
            list: Список кортежей с данными о продажах:
                  (название товара, общее количество, общая сумма, цена за единицу)
        """
        cursor = self.db.conn.cursor()
        # SQL-запрос для получения данных о продажах:
        # - Группировка по товарам
        # - Суммирование количества и выручки
        # - Фильтрация по дате продажи
        cursor.execute('''
        SELECT p.name, SUM(s.quantity), SUM(s.quantity * p.price), p.price
        FROM sales s
        JOIN products p ON s.product_id = p.id
        WHERE s.sale_date BETWEEN ? AND ?
        GROUP BY p.name
        ''', (start_date, end_date))

        report = cursor.fetchall()  # Получаем все строки результата запроса
        return report

    def stock_report(self):
        """
        Генерация отчета по остаткам на складе

        Returns:
            dict: Словарь с двумя ключами:
                  - 'products': остатки готовой продукции
                  - 'materials': остатки сырья
        """
        cursor = self.db.conn.cursor()

        # Получаем остатки готовой продукции
        cursor.execute('SELECT name, stock FROM products')
        products = cursor.fetchall()

        # Получаем остатки сырья
        cursor.execute('SELECT name, quantity FROM raw_materials')
        materials = cursor.fetchall()

        return {
            'products': products,  # Список кортежей (название, количество)
            'materials': materials  # Список кортежей (название, количество)
        }

    def production_report(self, start_date, end_date):
        """
        Генерация отчета по производству за указанный период

        Args:
            start_date (str): Начальная дата периода в формате 'YYYY-MM-DD'
            end_date (str): Конечная дата периода в формате 'YYYY-MM-DD'

        Returns:
            list: Список кортежей с данными о производстве:
                  (название товара, общее количество, дата производства)
        """
        cursor = self.db.conn.cursor()
        # SQL-запрос для получения данных о производстве:
        # - Группировка по товарам и датам производства
        # - Суммирование количества произведенной продукции
        # - Фильтрация по дате производства
        cursor.execute('''
        SELECT p.name, SUM(pr.quantity), pr.production_date
        FROM production pr
        JOIN products p ON pr.product_id = p.id
        WHERE pr.production_date BETWEEN ? AND ?
        GROUP BY p.name, pr.production_date
        ''', (start_date, end_date))

        report = cursor.fetchall()  # Получаем все строки результата запроса
        return report