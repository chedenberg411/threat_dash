import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd
import json
# Load datasets
clearing = pd.read_csv('./clearinghouse.csv')
neiss = pd.read_csv('./neiss.csv')
neiss['incident_year'] = pd.to_datetime(neiss['Treatment_Date']).dt.year


trend_df=pd.read_csv("./threat_classifications.csv")
company_df = pd.read_csv('./company_products.csv')
company_groups = company_df.groupby('Mapped Company')

trend_confidence_list=["Low","Moderate","High"]
trend_maturity_list=["Emerging","Established"]

product_mapping=company_df[['Product Type','Product_Name']].drop_duplicates()

product_file = pd.read_csv("~/LASM/IncidentReports.csv", on_bad_lines='warn', encoding='cp1252', skiprows=[0])
product_file = product_file.merge(product_mapping,on='Product Type')

with open("./clearing_descriptions.json", 'r') as file:
    clearingdesc = json.load(file)

with open("./neiss_descriptions.json", 'r') as file:
    neissdesc = json.load(file)


# Load product trend data
neiss_trends = pd.read_csv('./neiss_product_trends.csv')
clearing_trends = pd.read_csv('./clearing_product_trends.csv')
# neiss_trends=neiss_trends.merge(clearing_trends,on='Product_Name',how='inner')


# Identify increasing and decreasing products
increasing_products = neiss_trends[neiss_trends['Trend Megnitude'].str.contains("Increase", na=False)]['Product_Name'].tolist() + \
                        clearing_trends[clearing_trends['Trend Megnitude'].str.contains("Increase", na=False)]['Product_Name'].tolist()
decreasing_products = neiss_trends[neiss_trends['Trend Megnitude'].str.contains("Decrease", na=False)]['Product_Name'].tolist() + \
                        clearing_trends[clearing_trends['Trend Megnitude'].str.contains("Decrease", na=False)]['Product_Name'].tolist()


# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=["https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css"])

server = app.server

app.layout = html.Div([
    html.Div("Product Liability Emerging Risks", className="text-center text-white text-5xl font-extrabold py-12 shadow-md bg-gradient-to-r from-blue-800 to-indigo-800"),
    html.Div("Select a product category to view trends in exposure  ", className="text-center text-xl font-bold mb-4 p-6"),

    html.Div(className="grid grid-cols-5 gap-3",children=[
    html.Div(children=[
    html.Div(className="flex fixed left-0 top-25 flex-col p-4 bg-white shadow-md w-64", children=[
        html.Div([
        html.H2("Filter for threat confidence and maturity", className=" text-small mb-4 mt-4"),

        dcc.Dropdown(id='filter-trend-confidence', options=[{'label': cat, 'value': cat} for cat in trend_confidence_list], placeholder="Trend Confidence"),
        dcc.Dropdown(id='filter-trend-scale', options=[{'label': comp, 'value': comp} for comp in trend_maturity_list], placeholder="Trend Scale"),
        html.H2("Filter Products with Increasing Risk Levels", className=" text-small mb-4 mt-4"),
        html.Div(className="container mx-auto pb-2", children=[
            html.Div(className="gap-6", children=[
                dcc.Dropdown(
                    id='increase-product-dropdown',
                    multi=False,
                    options=[{'label': product, 'value': product} for product in increasing_products],
                    placeholder="Select products with increasing trends",
                    className="w-full border border-gray-300 rounded-md",
                    optionHeight=120
                )
            ])
        ])
        ]),
        html.Div([
        html.H2("Filter Products with Decreasing Risk Levels", className=" text-small mt-4 mb-4"),
        html.Div(className="container mx-auto pb-2", children=[
            dcc.Dropdown(
                id='decrease-product-dropdown',
                multi=False,
                options=[{'label': product, 'value': product} for product in decreasing_products],
                placeholder="Select products with increasing trends",
                className="w-full border border-gray-300 rounded-md",
                optionHeight=120
            )
        ])
        ])


    ])]),

    html.Div(className="col-span-4",children=[
    html.Div(className="container mx-auto p-2", children=[
                # Wrap the two sections in a grid with two columns
        html.Div(id='summary-title', className="flex justify-left"),
        html.Div(className="grid gap-6 mt-2 flex justify-center", children=[
            
            html.Div(id='summary-section', className="flex justify-center")

        ])
        ]),
    html.Div(className="container grid grid-cols-2 mx-auto p-6", children=[
                # Wrap the two sections in a grid with two columns
        dcc.Graph(id='clearing-graph', className="mt-6 bg-white p-6 rounded-lg shadow-lg"),
        html.Div(id='incident-summary-section', className="bg-gray-100  mt-6 p-6 rounded-lg ")
    ]),
    html.Div(className="container grid grid-cols-2 mx-auto p-6", children=[
                # Wrap the two sections in a grid with two columns
        dcc.Graph(id='neiss-graph', className="mt-6 bg-white p-6 rounded-lg shadow-lg"),
        html.Div(id='hospital-summary-section', className="bg-gray-100 mt-6  p-6 rounded-lg ")
    ])
    ])])

], className="bg-gray-100 min-h-screen")


@app.callback(

    [
     Output('increase-product-dropdown', 'options'),
     Output('decrease-product-dropdown', 'options')],
    [Input('filter-trend-confidence', 'value'),
     Input('filter-trend-scale', 'value')
     ]
)
def update_products(trend_conf,trend_scale):
    increasing_products=trend_df[trend_df['overall_trend']>0]
    decreaing_products=trend_df[trend_df['overall_trend']<0]
    print(trend_conf)
    if trend_conf is None and trend_scale is None:
        incoptions = [{'label': p, 'value': p} for p in increasing_products['Product_Name'].to_list()]
        decoptions = [{'label': p, 'value': p} for p in decreaing_products['Product_Name'].to_list()]
        print("defaults")
        return incoptions,decoptions
    
    if trend_conf is not None:
        increasing_products=increasing_products[increasing_products['Confidence']==trend_conf]
    if trend_scale is not None:
        increasing_products=increasing_products[increasing_products['Threat Status']==trend_scale]
    decreaing_products=decreaing_products[decreaing_products['Confidence']==trend_conf]
    decreaing_products=decreaing_products[decreaing_products['Threat Status']==trend_scale]

    incoptions = [{'label': p, 'value': p} for p in increasing_products['Product_Name'].to_list()]
    decoptions = [{'label': p, 'value': p} for p in decreaing_products['Product_Name'].to_list()]
    print(incoptions)
    return incoptions,decoptions

@app.callback(
    [Output('summary-section', 'children'),
     Output('summary-title', 'children'),
     Output('neiss-graph', 'figure'),
     Output('clearing-graph', 'figure'),
    Output('incident-summary-section', 'children'),
    Output('hospital-summary-section', 'children')
     ],
    [
     Input('increase-product-dropdown', 'value'),
     Input('decrease-product-dropdown', 'value')]
)
def update_summary_and_graph( selected_increase_products, selected_decrease_products):
    if not (selected_increase_products or selected_decrease_products):
        return html.Div("Select a product to view emerging trends.", className="text-gray-700"),"", px.line(title="Select a company"),px.line(title="Select a company"),"",""
    

    print(selected_increase_products)
 
    if selected_decrease_products:
        product=selected_decrease_products
    elif selected_increase_products:
        product=selected_increase_products
    else:
        product=None
                   
    
    summary_title=html.Div([
        html.H2(f"Thread Trends for: {product}", className=" text-large text-semibold mb-4")])
    


    filtered_neiss_graph=neiss[neiss['Product_Name']==product]
    filtered_clearing_graph=clearing[clearing['Product_Name']==product] 
    filtered_product_file = product_file[product_file['Product_Name']==product]

    clearing_cases = filtered_clearing_graph.groupby('received_year').size().reset_index(name='cases')
    clearing_cases['cases']=clearing_cases['cases']/clearing_cases['cases'].sum()
    neiss_cases = filtered_neiss_graph.groupby('incident_year').size().reset_index(name='cases')
    neiss_cases['cases']=neiss_cases['cases']/neiss_cases['cases'].sum()
    clearing_cases['Type'] = 'Consumer Complaints'
    neiss_cases['Type'] = 'Injuries & Hospital Visits'

    clearing_growth=(clearing_cases[clearing_cases['received_year']==2023]['cases']/clearing_cases[clearing_cases['received_year']!=2023].mean()['cases'])-1
    neiss_growth=(neiss_cases[neiss_cases['incident_year']==2023]['cases']/neiss_cases[neiss_cases['incident_year']!=2023].mean()['cases'])-1
    # consumer_growth=filtered_product_file[filtered_product_file['Year']==2023]['cases']/filtered_product_file[filtered_product_file['Year']!=2023].mean()['cases']
    print(clearing_growth.values[0])
    summary_content = html.Div(html.Div(className="grid grid-cols-4 gap-6 flex justify-center",
            children=[
                html.Div(className="bg-red-500 text-white p-6 rounded-lg shadow-md text-center", children=[
                    html.H1(f"{clearing_growth.values[0]*100:.0f}%", className="text-5xl font-bold"),
                    html.P("Growth in Incidents", className="text-sm")
                ]), 
                html.Div(className="bg-red-500 text-white p-6 rounded-lg shadow-md text-center", children=[
                    html.H1(f"{neiss_growth.values[0]*100:.0f}%", className="text-5xl font-bold"),
                    html.P("Growth   in Hospitalizations", className="text-sm")
                ]),
                html.Div(className="bg-green-500 text-white p-6 rounded-lg shadow-md text-center", children=[
                    html.H1("10", className="text-5xl font-bold"),
                    html.P("Change in Customer Complaints", className="text-sm")
                ]),
                html.Div(className="bg-yellow-500 text-white p-6 rounded-lg shadow-md text-center", children=[
                    html.H1("98%", className="text-5xl font-bold"),
                    html.P("Faster growth than average", className="text-sm")
                ])
    ]))

    clearing_cases.rename(columns={'received_year': 'Year'}, inplace=True)
    neiss_cases.rename(columns={'incident_year': 'Year'}, inplace=True)
    
    # Create line chart with corrected column names
    figclear = px.line(clearing_cases, x='Year', y='cases', color='Type', title='Cases Over Time')
    figneiss = px.line(neiss_cases  , x='Year', y='cases', color='Type', title='Cases Over Time')
    
    risk_index = (((neiss_cases[neiss_cases['Year']==2023]['cases']+clearing_cases[clearing_cases['Year']==2023]['cases'])/(neiss_cases[neiss_cases['Year']!=2023]['cases'].mean()+clearing_cases[clearing_cases['Year']!=2023]['cases'].mean()))-1)*100
    print(risk_index.values[0])

    if product in clearingdesc.keys():            
        clearing_text=clearingdesc[product].split("-")
    else:
        clearing_text=""

    if product in neissdesc.keys():            
        neiss_text=neissdesc[product].split("-")
    else:
        neiss_text=""
    

    clearing_case_descriptions = html.Div(className="bg-blue-500 text-white p-6 rounded-lg shadow-md text-center", children=[
        html.Ul([html.Li(description) for description in clearing_text], className="list-none"),

    ])

    neiss_case_descriptions = html.Div(className="bg-blue-500 text-white p-6 rounded-lg shadow-md text-center", children=[
        html.Ul([html.Li(description) for description in neiss_text], className="list-none"),

    ])

    return summary_content,summary_title, figneiss,figclear,clearing_case_descriptions,neiss_case_descriptions

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
