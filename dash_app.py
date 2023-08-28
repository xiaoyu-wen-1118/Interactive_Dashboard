import pandas as pd
import dash
import dash_bootstrap_components as dbc
import plotly.express as px
# from dash.dependencies import Input, Output, State
from dash import html, dcc, dash_table, ctx
from dash_extensions.enrich import Output, DashProxy, Input, State, MultiplexerTransform
import mysql_utils as mu
import mongodb_utils as mb
import neo4j_utils as nu
import requests


# All dataframe helpers

def get_df_prof(keyword_1, keyword_2):
    if keyword_1 is None:
        keyword_1 = keyword_2
    if keyword_2 is None:
        keyword_2 = keyword_1   
    
    df_prof = mu.get_topProfessor(keyword_1, keyword_2)
    # df_prof = df_prof.reset_index().drop(columns=["index"]).reset_index()
    df_prof.reset_index(inplace=True)
    df_prof["index"] = df_prof["index"] + 1
    
    return df_prof

# Create the components and layout
# app = dash.Dash(
#     __name__, 
#     external_stylesheets=[dbc.themes.BOOTSTRAP],
#     meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
# )
app = DashProxy(prevent_initial_callbacks=True, transforms=[MultiplexerTransform()], external_stylesheets=[dbc.themes.BOOTSTRAP])

app.title = "CS411 group project - Dashboard"

# Create navbar
PLOTLY_LOGO = "https://images.plot.ly/logo/new-branding/plotly-logomark.png"
search_bar = dbc.Row(
                    [
                        dbc.Col(dcc.Input(id="search_1", type="text", placeholder="Keyword 1", style={'marginRight':'15px', 'height':'35px', 'width':'150px'})),
                        dbc.Col(dcc.Input(id="search_2", type="text", placeholder="Keyword 2", style={'marginRight':'7px', 'height':'35px', 'width':'150px'})),
                        dbc.Col(dbc.Button("Search", id='btn_search', color="primary", className="ms-2", n_clicks=0),width="auto",),
                    ],
                    className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
                    align="center",
                    style={'marginRight':'15px'})

navbar = dbc.Navbar(id='navbar', 
                    children=[
                        html.A(
                            dbc.Row(
                                [
                                    dbc.Col(html.Img(src=PLOTLY_LOGO, height="30px")),
                                    dbc.Col(dbc.NavbarBrand("Discover graduate school and advisor", className="ms-2")),
                                ],
                                align="center",
                                className="g-0",
                                ),
                            style={"textDecoration": "none", 'marginLeft':'15px'},
                            ),
                        search_bar,
                        ], 
                    color = '#191970',
                    dark = True,)

options1 = ['Select year range','1 year', '3 years', '5 years', '10 years']
title_style = {'color':'#0047AB'}
# Create main body
body_app = dbc.Container([    
    html.Br(),
    #html.Div([dash_table.DataTable(id='dt1', columns =  [{"name": i, "id": i,} for i in (df_keyword.columns)])]),
    dbc.Row([
        dbc.Col([
             # Change to button later
             html.Div(html.H4('Top keywords in recent years'), style=title_style,),
             dcc.Dropdown(id="year", options = [{'label':i, 'value':i } for i in options1],
                          value = 'Select year range'),
             # html.Br(),
             dbc.Card(id = 'card_top_keywords',style={'height':'375px'}),
             ]),
        dbc.Col([
             html.Div(html.H4('Top10 professors on selected keywords'), style=title_style,),
             dbc.Card(id = 'card_top_prof',style={'height':'410px'}),
             ]),
        dbc.Col( 
            [
             html.Div(html.H4('Top10 universities on selected keywords'), style=title_style,),
             dbc.Card(id = 'card_top_school',style={'height':'410px'}),
             ])
        ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Div(html.H4('Professor info'), style=title_style,),
            dbc.Card(id = 'card_prof_info',style={'height': '400px'},)
            ], width=8),
        dbc.Col([
            html.Div(html.H4('Collaboration network'), style=title_style,),
            dbc.Card(id = 'card_prof_network',style={'height': '400px'})
            ], width=4)
        ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Div(html.H4('Favorite professors'), style=title_style,),
            dbc.Card(id = 'card_favorite_prof', style={'height': '300px'}),
            dbc.Button('Delete', id='btn_del'),
            ]),
        dbc.Col([
            html.Div(html.H4('Favorite universities'), style=title_style,),
            dbc.Card(id = 'card_favorite_school', style={'height': '300px'}),
            dbc.Button('Delete', id='btn_del2'),
            ])
        ]),
    html.Br(),           
    ],
    style = {'backgroundColor':'#f7f7f7', 'borderWidth':'5px'},
    fluid = True)

# Embeded all components into the layout
app.layout = html.Div(id = 'parent', children = [navbar,body_app])                                   

# Callback of card_top_keywords, most popular keywords in recent years
@app.callback([Output('card_top_keywords', 'children')],
              [Input('year', 'value')])

def update_fig_topKeywords(year):
    year_int = int(year.split(' ')[0])
    topKeywords_df = mb.get_topKeywordsByYear(year_int)
    
    # fig = px.bar(topKeywords_df, y="keyword_name", x="score_sum", height=350)
    fig = px.treemap(topKeywords_df, path=['keyword_name'], values='score_sum',height=350)
    fig.update_layout(uniformtext=dict(minsize=13, mode='show'))
    card_content = [dbc.CardBody(
            [dcc.Graph(figure = fig)]
        )]
    return card_content

# Callback of card_top_prof, top professors of selected keywords
@app.callback([Output('card_top_prof', 'children')],
              [Input('btn_search', 'n_clicks')],
              [State('search_1', 'value'),
               State('search_2', 'value')])

def update_fig_topProfessors(search, keyword_1, keyword_2):
    
    df_prof = get_df_prof(keyword_1, keyword_2)
    df_prof.drop(columns='id', inplace=True)
    
    top_professor_table = dash_table.DataTable(id="datatable_top_professors",
                                                editable=True,
                                                page_size=10,
                                                data=df_prof.to_dict('records'),
                                                row_selectable="multi",
                                                selected_rows=[],)
    card_content = [dbc.CardBody(
                        [top_professor_table,
                         dbc.Button('Add to favorite', id='btn_add',style={'marginRight':'10px','marginTop':'8px'}),
                         dbc.Button('Clear',id='btn_clear',style={'marginRight':'10px','marginTop':'8px'}),]
                    )]
    return card_content

# Callback of clear selected professor in datatable_top_professors
@app.callback([Output('datatable_top_professors', 'selected_rows')],
              [Input('btn_clear', 'n_clicks')])

def clear_selectedProf(n_clicks):
    return []

# Callback of card_prof_info
@app.callback([Output('card_prof_info', 'children')],
              [Input('datatable_top_professors', 'active_cell')],
              [State('search_1', 'value'),
               State('search_2', 'value')])

def update_fig_profInfo(active_cell, keyword_1, keyword_2):
    if active_cell: 
        df_prof = get_df_prof(keyword_1, keyword_2)
        
        row_idx = active_cell['row'] 
        prof_id = df_prof.iloc[row_idx]['id']
        prof_info_df = mu.get_selectProf(prof_id)
        
        # Prof_info
        prof_name = prof_info_df['Prof_name']
        email = prof_info_df['email']
        phone = prof_info_df['phone']
        affiliation = prof_info_df['Affiliation']
        photo_url = prof_info_df['photo_url']
        
        # Prof's top 5 publications
        top5pub_df = mu.prof_top10Publication(prof_id, keyword_1, keyword_2)
        top5pub_df.reset_index(inplace=True)
        top5pub_df['index'] = top5pub_df['index'] + 1 
        
        top_5pub_table = dash_table.DataTable(id="datatable_top_5publications",
                                                # editable=True,
                                                # page_size=6,
                                                fixed_rows={'headers':True},
                                                data=top5pub_df.to_dict('records'),
                                                style_cell={'minWidth': '100px'},
                                                style_table={'maxWidth':'1600px', 'height':'400px'})
                
        if requests.get(photo_url.astype('str')[0]).ok:
            print("Url is OK")

        card_content = [
                        dbc.Row([
                            dbc.Col(
                                html.Img(src=photo_url, style={'maxHeight':'390px', 'maxWidth':'300px', 'minWidth':'300px'}),
                                width=2,
                                align='top',
                                ),
                            dbc.Col(
                                dbc.CardBody([
                                    html.H1(prof_name, className="card-title"),
                                    html.H4(email, className="card-text"),
                                    html.H4(phone, className="card-text"),
                                    html.H4(affiliation, className="card-text")]),
                                width=2,
                                align='top',
                                ),
                            dbc.Col(dbc.CardBody(top_5pub_table),
                                    align='top',
                                    width=8),
                                    
                            ],
                            className='g-0')
                        ]

        return card_content
    else:   
        return
# Callback of card_prof_info
@app.callback([Output('card_prof_network', 'children')],
              [Input('datatable_top_professors', 'active_cell')],
              [State('search_1', 'value'),
               State('search_2', 'value')])

def update_fig_network(active_cell, keyword_1, keyword_2):
    print('graph start')
    if active_cell: 
        df_prof = get_df_prof(keyword_1, keyword_2)
        
        row_idx = active_cell['row'] 
        prof_name = df_prof.iloc[row_idx]['Professor']
        collab_df = nu.connectedProfessor(prof_name)
        
        pos, G = nu.getNetworkxPostion(collab_df)
        edge_trace = nu.createEdge(G, pos)
        node_trace = nu.createNode(G, pos)
        nu.addColor(G, node_trace)
        fig = nu.getFig(edge_trace, node_trace)
        # fig.layout.height = 300
        
        card_content = [dbc.Row(dbc.Col(dbc.CardBody(dcc.Graph(id='Graph',figure=fig, style={'height':370}))))
                                
                        ]
        print('graph')
        return card_content
    
# Callback of card_top_school of selected keywords
@app.callback([Output('card_top_school', 'children')],
              [Input('btn_search', 'n_clicks')],
              [State('search_1', 'value'),
               State('search_2', 'value')])

def update_fig_topUniversities(n_clicks, keyword_1, keyword_2):
    df_school = mb.get_topUniversity(keyword_1, keyword_2)
    df_school.reset_index(inplace=True)
    df_school["index"] = df_school["index"] + 1
    
    
    top_school_table = dash_table.DataTable(id="datatable_top_schools",
                                                editable=True,
                                                page_size=10,
                                                data=df_school.to_dict('records'),
                                                row_selectable="multi",
                                                selected_rows=[],)
    card_content = [dbc.CardBody(
                        [top_school_table,
                         dbc.Button('Add to favorite', id='btn_add2',style={'marginRight':'10px','marginTop':'8px'}),
                         dbc.Button('Clear',id='btn_clear2',style={'marginRight':'10px','marginTop':'8px'}),]
                    )]
    return card_content
    
# Callback of card_favorite_prof selected by user
@app.callback([Output('card_favorite_prof', 'children')],
              [Input('btn_add', 'n_clicks')],
              [State('datatable_top_professors', 'selected_rows'),
               State('search_1', 'value'),
               State('search_2', 'value')])

def update_fig_favoriteProf(add_clicks, selected_rows, keyword_1, keyword_2):
    if keyword_1 is None:
        keyword_1 = keyword_2
    if keyword_2 is None:
        keyword_2 = keyword_1 
    # button_clicked = ctx.triggered_id
    # if button_clicked == 'btn_add':
    #     print("button add is clicked")
    df_prof = get_df_prof(keyword_1, keyword_2)
    favorite_prof_df = pd.DataFrame(df_prof.iloc[selected_rows]['Professor'])
    n = len(selected_rows)
    k1_lst = [keyword_1] * n
    k2_lst = [keyword_2] * n
    favorite_prof_df['Keyword1'] = k1_lst
    favorite_prof_df['Keyword2'] = k2_lst
    
    mu.write_prof_tosql(favorite_prof_df)
    favProf_from_sql = mu.get_favorite_prof()
    
    favProf_table = dash_table.DataTable(id="datatable_favorite_professors",
                                            editable=True,
                                            page_size=10,
                                            data=favProf_from_sql.to_dict('records'),
                                            row_selectable="multi",
                                            selected_rows=[],)
    card_content = [dbc.CardBody(
                        [favProf_table,]
                    )]
    
    return card_content

# Callback of card_favorite_school selected by user
@app.callback([Output('card_favorite_school', 'children')],
              [Input('btn_add2', 'n_clicks')],
              [State('datatable_top_schools', 'selected_rows'),
               State('search_1', 'value'),
               State('search_2', 'value')])

def update_fig_favoriteSchool(add_clicks, selected_rows, keyword_1, keyword_2):
    if keyword_1 is None:
        keyword_1 = keyword_2
    if keyword_2 is None:
        keyword_2 = keyword_1 

    df_school = mb.get_topUniversity(keyword_1, keyword_2)
    favorite_school_df = pd.DataFrame(df_school.iloc[selected_rows]['University'])
    n = len(selected_rows)
    k1_lst = [keyword_1] * n
    k2_lst = [keyword_2] * n
    favorite_school_df['Keyword1'] = k1_lst
    favorite_school_df['Keyword2'] = k2_lst
    
    mu.write_school_tosql(favorite_school_df)
    favSchool_from_sql = mu.get_favorite_school()
    
    favSchool_table = dash_table.DataTable(id="datatable_favorite_schools",
                                            editable=True,
                                            page_size=10,
                                            data=favSchool_from_sql.to_dict('records'),
                                            row_selectable="multi",
                                            selected_rows=[],)
    card_content = [dbc.CardBody(
                        [favSchool_table,]
                    )]
    
    return card_content

# Callback of clear selected university in datatable_top_schools
@app.callback([Output('datatable_top_schools', 'selected_rows')],
              [Input('btn_clear2', 'n_clicks')])

def clear_selectedSchool(n_clicks):
    return []

#Call back of card_favorite_prof deleted by user
@app.callback([Output('card_favorite_prof', 'children')],
              [Input('btn_del', 'n_clicks')],
              [State('datatable_favorite_professors', 'selected_rows')])

def delete_fig_favoriteProf(n_clicks, selected_rows):
    print("Delete is called")
    
    favProf_from_sql = mu.get_favorite_prof()
    del_favProf_df = favProf_from_sql.iloc[selected_rows]
    
    mu.delete_prof_fromsql(del_favProf_df)
    favProf_updateFrom_sql = mu.get_favorite_prof()
    
    favProf_table = dash_table.DataTable(id="datatable_favorite_professors",
                                            editable=True,
                                            page_size=10,
                                            data=favProf_updateFrom_sql.to_dict('records'),
                                            row_selectable="multi",
                                            selected_rows=[],)
    card_content = [dbc.CardBody(
                        [favProf_table,]
                    )]
    
    return card_content

#Call back of card_favorite_school deleted by user
@app.callback([Output('card_favorite_school', 'children')],
              [Input('btn_del2', 'n_clicks')],
              [State('datatable_favorite_schools', 'selected_rows')])
def delete_fig_favoriteSchool(n_clicks, selected_rows):
    print("Delete is called")
    
    favSchool_from_sql = mu.get_favorite_school()
    del_favSchool_df = favSchool_from_sql.iloc[selected_rows]
    
    mu.delete_school_fromsql(del_favSchool_df)
    favSchool_updateFrom_sql = mu.get_favorite_school()
    
    favSchool_table = dash_table.DataTable(id="datatable_favorite_schools",
                                            editable=True,
                                            page_size=10,
                                            data=favSchool_updateFrom_sql.to_dict('records'),
                                            row_selectable="multi",
                                            selected_rows=[],)
    card_content = [dbc.CardBody(
                        [favSchool_table,]
                    )]
    
    return card_content

if __name__ == "__main__":
    app.run_server()