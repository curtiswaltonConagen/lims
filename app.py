import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
import dash_table
from dash.dependencies import Input, Output, State
import pandas as pd
#import plotly.graph_objs as go
import plotly.express as px
import base64
import io

VALID_USERNAME_PASSWORD_PAIRS = [['hello', 'world']]
app = dash.Dash('auth')

auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

markdown_text = """

Select A Collection to view:

"""

markdown_spacer = """
.
.
"""
markdown_2 = """ Plate Map Info:"""
markdown_3 = """ Waiting to validate an experiment"""
collections = ['Plate Collection', 'Primer Plate Collection', 'Primer Collection', 'Miniprep Collection']
header = ['Experimenat Number', 'Description', 'Status']
plates_header = ['Plate ID', 'Plate Name', 'Plate description']


start_table_df = pd.DataFrame(columns=[''])
plates = pd.read_csv('plates.csv')
strains = pd.read_csv('strains.csv')
primer_plates = pd.read_csv('primer_plates.csv')
primers = pd.read_csv('primers.csv')
miniprep = pd.read_csv('miniprep.csv')
miniprep_plate_map = pd.read_csv('miniprep plate map.csv')
experiments = pd.read_csv('experiment list.csv')
app.layout = html.Div([
    html.H1('LIMS', style={"textAlign": "center"}),
    dcc.Tabs([
        dcc.Tab(label='Experiments', children=[
            dash_table.DataTable(
                id='experiments-table',
                data=experiments.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in experiments.columns],
                page_size=10,
                filter_action="native",
            ),
            html.H2(children=markdown_spacer),
            dcc.Markdown(children=markdown_spacer),
            dcc.Tabs([
                dcc.Tab(label='PCRs'),
                dcc.Tab(label='Transformations'),
                dcc.Tab(label='Plates Ready for screening'),
                dcc.Tab(label='Screening Results', children = [
                    dcc.Dropdown(id='plate-dropdown',
                                 options=[{'label': k, 'value': k} for k in ['Plate 1', 'PLT2', 'PLT3']],),

                    dcc.Graph(
                        id = 'plate-graph',

                    )

                ]



                        ),


            ])
            # dcc.Dropdown(
            #     id='yearly-dropdown',
            #     #options=[{'label': k, 'value': k} for k in transactions.Year.unique()],
            #     value='2020',
            #     style={"textAlign": "center"}
            # ),
            # dash_table.DataTable(
            #     id='my-datatable-categories-year',
            #     columns=[{'name': i, 'id': i} for i in ['Category', 'Amount']],
            # ),
            # dash_table.DataTable(
            #     id='my-datatable-categories-all-years',
            #     columns=[{'name': i, 'id': i} for i in header],
            # ),
            # dcc.Dropdown(
            #     id='category-dropdown',
            #     style={"textAlign": "center"},
            #     options=[{'label': k, 'value': k} for k in ['Groceries','Bank Fee']],
            # ),
            # dcc.Graph(
            #     id='yearly_graph'
            #
            # )
        ]),

        dcc.Tab(label='Inventory', children=[
            dcc.Markdown(children=markdown_text),
            dcc.Dropdown(
                id='collection-dropdown',
                options=[{'label': k, 'value': k} for k in collections],
                #value='January',
                style={"textAlign": "center"}
            ),

            dcc.Markdown(id='summary'),
            html.Div(id='display-selected-values'),
            #dcc.Graph(
            #    id='categorized_spending-pie'
            #),

            dash_table.DataTable(
                id='my-collections-table',
                data=start_table_df.to_dict('records'),
                columns=[{'id': c, 'name': c} for c in start_table_df.columns],
                #columns=[{'name': i, 'id': i} for i in plates.columns],
                #data=plates.to_dict('records'),
                editable=True,
                export_format='xlsx',
                export_headers='display',
                merge_duplicate_headers=True,
                row_selectable="single",
                selected_rows=[],
                page_size=10,
                style_cell={'textAlign':'left'},
                style_as_list_view=True,
                #filter_action='native',
            ),
            dcc.Markdown(children=markdown_2),
            dash_table.DataTable(
                id='my-platemap-table',
                #columns=[{'name': i, 'id': i} for i in plates.columns],
                #data=plates.to_dict('records'),
                editable=True,
                export_format='xlsx',
                export_headers='display',
                merge_duplicate_headers=True,
                style_cell={'textAlign':'left'},
                style_as_list_view=True,
                #row_deletable=True
            ),
            #html.Button('Add Plate', id='add_plate_button', n_clicks=0),

            #dash_table.DataTable(
            #    id='my-cat-datatable',
            #    columns=[{'name': i, 'id': i} for i in ['Category', 'Amount']],
            #),


        ]),
        dcc.Tab(label='Strain Collection', children=[

            dash_table.DataTable(
                id='strain-container',
                columns=[{'name': i, 'id': i} for i in strains.columns],
                data=strains.to_dict('records'),
                editable=True,
                page_size=10,
                filter_action="native",
                sort_action="native",
                sort_mode='multi',
            ),
            html.Button('Add Strain', id='add_strain_button', n_clicks=0),

        ]),
        dcc.Tab(label='Upload Nanohive Experiment', children=[
            dcc.Upload(
                id='datatable-upload',
                children=html.Div([
                    'Drag and Drop or ',
                    html.A('Select Files')
                ]),
                style={
                    'width': '100%', 'height': '60px', 'lineHeight': '60px',
                    'borderWidth': '1px', 'borderStyle': 'dashed',
                    'borderRadius': '5px', 'textAlign': 'center', 'margin': '10px'
                },
            ),
            dash_table.DataTable(id='datatable-upload-container'),
            html.Div(id='my-output'),

        ]),
    ])
])

# Screening Results
@app.callback(
    Output('plate-graph', component_property='figure'),
    Input(component_id='plate-dropdown', component_property='value'),
)
def create_graph(value):
    fig = px.bar(['A1','A2','A3','A4'], x=[1,2,3,4], y=[5,9,3,2],)
    return fig

# Upload to nanohive
def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    if 'csv' in filename:
        # Assume that the user uploaded a CSV file
        return pd.read_csv(
            io.StringIO(decoded.decode('utf-8')))
    elif 'xls' in filename:
        # Assume that the user uploaded an excel file
        return pd.read_excel(io.BytesIO(decoded))

@app.callback(
    Output('datatable-upload-container', 'data'),
    Output('datatable-upload-container', 'columns'),
    Output('my-output', component_property='children'),
    Input('datatable-upload', 'contents'),
    State('datatable-upload', 'filename'))

def update_output(contents, filename):
    if contents is None:
        return [{}], [],'Waiting on file'
    df = parse_contents(contents, filename)
    return df.to_dict('records'), [{"name": i, "id": i} for i in df.columns], "Validated"

# strain collection callback
@app.callback(
    Output(component_id='strain-container', component_property='data'),
    Input('add_strain_button', component_property='n_clicks'),
    State('strain-container', 'data'),
    State('strain-container', 'columns'))
def add_strain(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows


# collections table
@app.callback(

    Output(component_id='my-collections-table', component_property='data'),
    Output(component_id='my-collections-table', component_property='columns'),
    Output(component_id='my-platemap-table', component_property='data'),
    Output(component_id='my-platemap-table', component_property='columns'),
    Input('collection-dropdown', component_property='value'),
    Input('my-collections-table', component_property='derived_virtual_selected_rows'),
    State('my-collections-table', 'data'),
    State('my-collections-table', 'columns'))

def update_output(value, virtual, data, columns):

    table_2_data = start_table_df.to_dict('records')
    table_2_columns = [{'id': c, 'name': c} for c in start_table_df.columns]

    if value == None:
        table_1_data = start_table_df.to_dict('records')
        table_1_columns =[{'id': c, 'name': c} for c in start_table_df.columns]
        #able_2_data = start_table_df.to_dict('records')
        #table_2_columns = [{'id': c, 'name': c} for c in start_table_df.columns]

    elif value == 'Plate Collection':
        table_1_data = plates.to_dict('records')
        table_1_columns = [{"name": i, "id": i} for i in plates.columns]
        if virtual !=[]:
            table_2_data = plates.to_dict('records')
            table_2_columns = [{"name": i, "id": i} for i in plates.columns]


    elif value == 'Primer Plate Collection':
        table_1_data = primer_plates.to_dict('records')
        table_1_columns = [{"name": i, "id": i} for i in primer_plates.columns]
        if virtual !=[]:
            table_2_data = primer_plates.to_dict('records')
            table_2_columns = [{"name": i, "id": i} for i in primer_plates.columns]


    elif value == 'Primer Collection':
        table_1_data = primers.to_dict('records')
        table_1_columns = [{"name": i, "id": i} for i in primers.columns]
        #if virtual !=[]:
        #    table_2_data = primers.to_dict('records')
        #   table_2_columns = [{"name": i, "id": i} for i in primers.columns]

    elif value == 'Miniprep Collection':
        table_1_data = miniprep.to_dict('records')
        table_1_columns = [{"name": i, "id": i} for i in miniprep.columns]
        if virtual !=[]:
            table_2_data = miniprep_plate_map.to_dict('records')
            table_2_columns = [{"name": i, "id": i} for i in miniprep_plate_map.columns]

    return table_1_data, table_1_columns, table_2_data, table_2_columns




if __name__ == '__main__':
    app.run_server(debug=True)