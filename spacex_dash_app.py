# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                            options=[
                                                {'label': 'All Sites', 'value': 'ALL'},
                                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
                                            ],
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0',
                                                        100: '100'},
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Count total success launches
        total_success = spacex_df[spacex_df['class'] == 1]['class'].count()
        # Calculate percentage of successful launches for each site
        success_percentage = spacex_df[spacex_df['class'] == 1].groupby('Launch Site')['class'].count() / total_success * 100
        # Create pie chart
        pie_chart_fig = px.pie(values=success_percentage.values, names=success_percentage.index, title='Total Success Launches by Site')
    else:
        selected_site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        pie_chart_data = selected_site_data['class'].value_counts().reset_index()
        pie_chart_data.columns = ['class', 'count']
        pie_chart_data['class'] = pie_chart_data['class'].astype(str)
        pie_chart_fig = px.pie(pie_chart_data, values='count', names='class', title=f'Total Success Launches for Site {selected_site}')
    return pie_chart_fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)

def update_scatter_chart(selected_site, selected_payload):
    if selected_site == 'ALL':
        filtered_data = spacex_df[(spacex_df['Payload Mass (kg)'] >= selected_payload[0]) & (spacex_df['Payload Mass (kg)'] <= selected_payload[1])]
        scatter_chart_fig = px.scatter(filtered_data, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Correlation between Payload and Success for all Sites')
    else:
        selected_site_data = spacex_df[spacex_df['Launch Site'] == selected_site]
        filtered_data = selected_site_data[(selected_site_data['Payload Mass (kg)'] >= selected_payload[0]) & (selected_site_data['Payload Mass (kg)'] <= selected_payload[1])]
        scatter_chart_fig = px.scatter(filtered_data, x='Payload Mass (kg)', y='class', color='Booster Version Category', title=f'Payload vs. Launch Success for {selected_site}')
    return scatter_chart_fig

# Run the app
if __name__ == '__main__':
    app.run_server()
