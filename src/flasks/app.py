from flask import Flask, render_template, url_for, request
import pandas as pd
import sys

app = Flask(__name__)

df = pd.read_csv('../../data/amazon.csv')

df['actual_price'] = df['actual_price'].str.replace('₹', '')
df['actual_price'] = df['actual_price'].str.replace(',', '')
df['actual_price'] = df['actual_price'].str.replace('.', '')
df['actual_price'] = df['actual_price'].astype('int')

df['rating'] = pd.to_numeric(df['rating'], errors = 'coerce')
df['rating_count'] = df['rating_count'].str.replace(',', '')
df['rating_count'] = df['rating_count'].fillna(0)
df['rating_count'] = df['rating_count'].astype('int')

def get_product_category():
    categories = df['category'].map(lambda x: x.split('|'))
    df['categories'] = categories

    category = []
    def process_list(lst):
        for item in lst:
            category.append(item)

    df['categories'].apply(process_list)
    category = set(category)
    return category

#Top 10 produk keseluruhan berdasarkan rating dan rating_count

def top_products_by_rating():
    products = df.groupby(['product_id']).agg({
                                                'rating_count': 'sum',
                                                'rating': 'mean'
                                                }).sort_values(by=['rating_count', 'rating'], ascending=[False, False]).reset_index() 
    
    top_products = df.merge(products, how='inner', on='product_id')
    top_products.drop(columns=['rating_count_y', 'rating_y'])
    return top_products[:5].sort_values(by=['rating_count_x', 'rating_x'], ascending=[False, False])

# Recommendation products by keyword, category, or price 
def search_product(keyword=None, category=None, min_price=None, max_price=None):
    if keyword:
        result = df[df['product_name'].str.contains(keyword, case=False)]
    
    if category:
        result = df[df['category'].str.contains(category, case=False)]

    if min_price:
        result = df[df['actual_price'] >= min_price]
    
    if max_price:
        result = df[df['actual_price'] <= max_price]

    products = result.groupby(['product_id']).agg({
                                    'rating_count': 'sum',
                                    'rating': 'mean'
                                }).reset_index()
    
    top_products = df.merge(products, how='inner', on='product_id')
    top_products = top_products.drop(columns=['rating_count_y', 'rating_y'])
    return top_products.sort_values(by=['rating_count_x', 'rating_x'], ascending=[False, False])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method== 'POST':
        keyword = request.form['keyword']
        return render_template('products.html', search_product=search_product(keyword=keyword), get_product_category=get_product_category())
    return render_template('index.html', top_products=top_products_by_rating(), get_product_category=get_product_category())

@app.route('/products/<string:category>')
def search(category):
    return render_template('products.html', category=category, search_product=search_product(category=category), get_product_category=get_product_category())

if __name__ == '__main__':
    app.run(debug=True)