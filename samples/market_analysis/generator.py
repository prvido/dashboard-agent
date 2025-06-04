import csv
import random
from datetime import datetime, timedelta

# Load products
def load_ids_from_csv(filename, id_column):
    ids = []
    with open(f'samples/market_analysis/{filename}', mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            ids.append(row[id_column])
    return ids

# Generate random date
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

def generate_sales_csv(
        products_file, customers_file, sales_file,
        num_sales=200
    ):
    products = load_ids_from_csv(products_file, 'product_id')
    customers = load_ids_from_csv(customers_file, 'customer_id')
    start = datetime(2025, 1, 1)
    end = datetime(2025, 5, 31)

    with open(sales_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['sale_id', 'sale_date', 'product_id', 'customer_id', 'unit_price', 'quantity', 'amount'])

        for i in range(1, num_sales + 1):
            sale_id = f"SAL{i:05d}"
            sale_date = random_date(start, end).strftime('%Y-%m-%d')
            product_id = random.choice(products)
            customer_id = random.choice(customers)
            unit_price = round(random.uniform(10, 100), 2)
            quantity = random.randint(1, 10)
            amount = round(unit_price * quantity, 2)

            writer.writerow([sale_id, sale_date, product_id, customer_id, unit_price, quantity, amount])

    print(f"{sales_file} generated successfully with {num_sales} records.")

generate_sales_csv('products.csv', 'customers.csv', 'sales.csv', num_sales=500)
