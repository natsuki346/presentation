# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go

# Read the spacex data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Get the unique launch sites from the data
launch_sites = spacex_df['Launch Site'].unique()

# Prepare options for the dropdown menu
launch_site_options = [{'label': site, 'value': site} for site in launch_sites]

# Add a "All Sites" option
launch_site_options = [{'label': 'All Sites', 'value': 'ALL'}] + launch_site_options

# Create a Dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # Task 1: Add the Launch Site Dropdown
    html.Div([
        dcc.Dropdown(
            id='site-dropdown',
            options=launch_site_options,  # Dropdown options
            value='ALL',  # Default value
            placeholder="Select a Launch Site",
            searchable=True  # Make it searchable
        ),
    ], style={'font-size': 20}),
    html.Br(),

    # Task 3: Add RangeSlider for payload selection
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i}kg' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload],  # Use the min and max payload values from the data
    ),
    
    # Task 2: Add a pie chart for launch success
    html.Div(dcc.Graph(id='success-pie-chart')),
    
    # Task 4: Add a scatter chart for payload vs success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        site_data = spacex_df
    else:
        site_data = spacex_df[spacex_df['Launch Site'] == selected_site]

    success_count = site_data['class'].value_counts()
    fig = go.Figure(data=[go.Pie(labels=['Failure', 'Success'],
                                 values=[success_count.get(0, 0), success_count.get(1, 0)])])

    fig.update_layout(title=f'Success Rate for {selected_site}' if selected_site != 'ALL' else 'Total Success Rate')
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, selected_payload_range):
    min_payload, max_payload = selected_payload_range

    if selected_site == 'ALL':
        filtered_df = spacex_df[
            (spacex_df['Payload Mass (kg)'] >= min_payload) & 
            (spacex_df['Payload Mass (kg)'] <= max_payload)
        ]
    else:
        filtered_df = spacex_df[
            (spacex_df['Launch Site'] == selected_site) & 
            (spacex_df['Payload Mass (kg)'] >= min_payload) & 
            (spacex_df['Payload Mass (kg)'] <= max_payload)
        ]
    
    fig = px.scatter(
        filtered_df, 
        x='Payload Mass (kg)', 
        y='class', 
        color='Booster Version Category', 
        title=f'Scatter Plot for {selected_site} (Payload: {min_payload} - {max_payload} kg)',
        labels={'Payload Mass (kg)': 'Payload Mass (kg)', 'class': 'Launch Outcome'}
    )

    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)