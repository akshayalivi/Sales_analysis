from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
import base64

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    # Get selected month and uploaded CSV file
    selected_month = request.form['month']
    csv_file = request.files['csv_file']
    
    # Read CSV file
    csv_data = csv_file.read().decode('utf-8')
    sales_data = pd.read_csv(StringIO(csv_data))
    
    # Convert the "Price Each" and "Quantity Ordered" columns to numeric
    sales_data["Price Each"] = pd.to_numeric(sales_data["Price Each"], errors="coerce")
    sales_data["Quantity Ordered"] = pd.to_numeric(sales_data["Quantity Ordered"], errors="coerce")

    # Drop rows with NaN values
    sales_data.dropna(inplace=True)

    # Calculate total sales for each product
    product_sales = sales_data.groupby("Product")["Price Each"].sum().sort_values(ascending=False)

    # Calculate total quantity sold for each product
    product_quantity = sales_data.groupby("Product")["Quantity Ordered"].sum().sort_values(ascending=False)

    # Calculate average price for each product
    product_avg_price = product_sales / product_quantity

    # Calculate the most sold product
    most_sold_product = product_quantity.idxmax()
    most_sold_quantity = product_quantity.max()

    # Calculate the product with the highest revenue
    highest_revenue_product = product_sales.idxmax()
    highest_revenue = product_sales.max()

    # Calculate the product with the highest average price
    highest_avg_price_product = product_avg_price.idxmax()
    highest_avg_price = product_avg_price.max()

    # Top 10 Sold Products
    top_10_products = product_quantity.head(10)

    # Plot top 10 products
    plt.figure(figsize=(10, 6))
    top_10_products.plot(kind='bar', color='skyblue')
    plt.title('Top 10 Sold Products')
    plt.xlabel('Product')
    plt.ylabel('Quantity Sold')
    plt.xticks(rotation=45)
    plt.tight_layout()
    top_10_products_image = BytesIO()
    plt.savefig(top_10_products_image, format='png')
    top_10_products_image.seek(0)
    top_10_products_image_base64 = base64.b64encode(top_10_products_image.read()).decode('utf-8')
    plt.close()

    # Plot total sales for each product
    plt.figure(figsize=(10, 6))
    product_sales.plot(kind='bar', color='salmon')
    plt.title('Total Sales for Each Product')
    plt.xlabel('Product')
    plt.ylabel('Total Sales')
    plt.xticks(rotation=45)
    plt.tight_layout()
    product_sales_image = BytesIO()
    plt.savefig(product_sales_image, format='png')
    product_sales_image.seek(0)
    product_sales_image_base64 = base64.b64encode(product_sales_image.read()).decode('utf-8')
    plt.close()

    # Prepare analysis results
    analysis_results = {
        'product_sales': product_sales,
        'top_10_products': top_10_products,
        'most_sold_product': most_sold_product,
        'most_sold_quantity': most_sold_quantity,
        'highest_revenue_product': highest_revenue_product,
        'highest_revenue': highest_revenue,
        'highest_avg_price_product': highest_avg_price_product,
        'highest_avg_price': highest_avg_price,
        'top_10_products_image': top_10_products_image_base64,
        'product_sales_image': product_sales_image_base64
    }

    return render_template('results.html', selected_month=selected_month, analysis_results=analysis_results)

if __name__ == '__main__':
    app.run(debug=True)
