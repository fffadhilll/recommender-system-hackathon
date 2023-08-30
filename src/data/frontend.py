import streamlit as st
import pandas as pd
from streamlit_card import card

#Dataset

df = pd.read_csv('../data/amazon.csv')

df['actual_price'] = df['actual_price'].str.replace('₹', '')
df['actual_price'] = df['actual_price'].str.replace(',', '')
df['actual_price'] = df['actual_price'].str.replace('.', '')
df['actual_price'] = df['actual_price'].astype('int')

df['rating'] = pd.to_numeric(df['rating'], errors = 'coerce')
df['rating_count'] = df['rating_count'].str.replace(',', '')
df['rating_count'] = df['rating_count'].fillna(0)
df['rating_count'] = df['rating_count'].astype('int')

#Top 10 produk keseluruhan berdasarkan rating dan rating_count

def top_products_by_rating():
    products = df.groupby(['product_id']).agg({
                                                'rating_count': 'sum',
                                                'rating': 'mean'
                                                }).sort_values(by=['rating_count', 'rating'], ascending=[False, False]).reset_index() 
    
    top_products = df.merge(products, how='inner', on='product_id')
    top_products.drop(columns=['rating_count_y', 'rating_y'])
    return top_products[:10].sort_values(by=['rating_count_x', 'rating_x'], ascending=[False, False])

# Recommendation products by keyword, category, or price 
def search_product(keyword, category=None, min_price=None, max_price=None):
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

#Dataset



st.title('Rekomendasi Produk')

keyword = st.text_input(label='', placeholder='Tulis produkmu disini!')

container = st.container()
if keyword:
    result = search_product(keyword)
    cols = st.columns(5)
    for i in cols:
        cols[i].write('a')
    # for index, row in result.iterrows():
        # n_rows = len(result) // int(5)
        # rows = [st.container() for _ in range(n_rows)]
        # cols_per_row = [r.columns(5) for r in rows]
        # cols = [column for row in cols_per_row for column in row]
        # cols[index].image(row['img_link'])
        # cols[index].write(row['product_name']) 
        # with cols[index]: 
        #     st.write(row['product_name'])
            # card(
            #     title='',
            #     text=[row['product_name'], f'Price: {row["actual_price"]}'],
            #     image=row['img_link'],
            # )
    