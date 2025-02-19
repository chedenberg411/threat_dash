import streamlit as st
import pandas as pd
import plotly.express as px
import json

# Load datasets
clearing = pd.read_csv('./clearinghouse.csv')
neiss = pd.read_csv('./neiss_filt.csv')
neiss['incident_year'] = pd.to_datetime(neiss['Treatment_Date']).dt.year

company_df = pd.read_csv('./company_products.csv')
product_mapping = company_df[['Product Type', 'Product_Name']].drop_duplicates()

trend_confidence_list=["Low","Moderate","High"]
trend_maturity_list=["Emerging","Established"]
trend_df=pd.read_csv("./threat_classifications.csv")

with open("./clearing_descriptions.json", 'r') as file:
    clearingdesc = json.load(file)

with open("./neiss_descriptions.json", 'r') as file:
    neissdesc = json.load(file)

neiss_trends = pd.read_csv('./neiss_product_trends.csv')
clearing_trends = pd.read_csv('./clearing_product_trends.csv')

increasing_products = trend_df[trend_df['overall_trend']>0]['Product_Name'].tolist() 
decreasing_products = trend_df[trend_df['overall_trend']<0]['Product_Name'].tolist() 

# Streamlit app layout
st.title("Product Liability Emerging Risks")
st.write("Select a product category to view trends in exposure")

# Sidebar filters
st.sidebar.header("Filters")
confidence = st.sidebar.selectbox("Trend Confidence", [None] + trend_confidence_list)
scale = st.sidebar.selectbox("Trend Scale", [None] + trend_maturity_list)

# Product selection
if scale is None and confidence is None:
    increase_product = st.sidebar.selectbox("Products with Increasing Risk", [None] + increasing_products)
    decrease_product = st.sidebar.selectbox("Products with Decreasing Risk", [None] + decreasing_products)
else:
    increase_filtered=trend_df[trend_df['overall_trend']>0]
    decrease_filtered=trend_df[trend_df['overall_trend']<0]
    if confidence:
        increase_filtered=increase_filtered[increase_filtered['Confidence']==confidence]
    if scale:
        increase_filtered=increase_filtered[increase_filtered['Threat Status']==scale]
    increase_product = st.sidebar.selectbox("Products with Increasing Risk", [None] + increase_filtered['Product_Name'].to_list())
    decrease_product = st.sidebar.selectbox("Products with Decreasing Risk", [None] + decrease_filtered['Product_Name'].to_list())

# Display product trends
if increase_product or decrease_product:
    product = increase_product if increase_product else decrease_product
    st.subheader(f"Threat Trends for: {product}")
    
    filtered_neiss_graph = neiss[neiss['Product_Name'] == product]
    filtered_clearing_graph = clearing[clearing['Product_Name'] == product]
    
    clearing_cases = filtered_clearing_graph.groupby('received_year').size().reset_index(name='cases')
    clearing_cases['Type'] = 'Consumer Complaints'
    neiss_cases = filtered_neiss_graph.groupby('incident_year').size().reset_index(name='cases')
    neiss_cases['Type'] = 'Injuries & Hospital Visits'
    
    figclear = px.line(clearing_cases, x='received_year', y='cases', color='Type', title='Cases Over Time')
    figneiss = px.line(neiss_cases, x='incident_year', y='cases', color='Type', title='Cases Over Time')
    
    st.plotly_chart(figclear)
    st.plotly_chart(figneiss)

    clearing_text = clearingdesc.get(product, "No data available").split("-")
    neiss_text = neissdesc.get(product, "No data available").split("-")
    
    st.subheader("Incident Descriptions")
    st.write("\n".join(clearing_text))
    st.write("\n".join(neiss_text))
