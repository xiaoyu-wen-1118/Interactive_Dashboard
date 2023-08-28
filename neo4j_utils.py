import plotly.graph_objs as go
from neo4j import GraphDatabase
import pandas as pd
import networkx as nx


driver = GraphDatabase.driver(uri = "bolt://localhost:7687" , auth = ("neo4j","uiuccs411"))
session = session = driver.session(database ='academicworld')


def connectedProfessor( faculty ):
    
    query = f"match(f:FACULTY{{name: \"{faculty}\" }})-->(p:PUBLICATION)<--(f1:FACULTY) WHERE f<>f1 RETURN f.name, f1.name LIMIT 50"
    
    result = session.run(query).data()
    df= pd.DataFrame(result)
    return df

#get a networkx graph
#assign each of the node in the graph a x and y coordinate
def getNetworkxPostion(df):
    frm = df.columns[0]
    to = df.columns[1]
   
    G = nx.from_pandas_edgelist(df, source= frm , target= to )
    nx.draw_spring(G, with_labels = True)
    pos = nx.spring_layout(G)
    return pos, G

#create Edge
def createEdge(G, pos):
    edge_trace = go.Scatter(
        x=[],
        y=[],
        line=dict(width=0.5,color='#888'),
        hoverinfo='none',
        mode='lines')
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])
    return edge_trace

#create Node
def createNode(G, pos):
    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=10,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),  
            line=dict(width=2)))
    
    for node in G.nodes():
        x, y = pos[node]
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
    return node_trace

#add color to node points
def addColor(G, node_trace):
    for node, adjacencies in enumerate(G.adjacency()):
        node_trace['marker']['color']+=tuple([len(adjacencies[1])])
        node_info = 'Name: ' + str(adjacencies[0])
        node_trace['text']+=tuple([node_info])    

def addCollaboration(G):
    names = ""
    for node, adjacencies in enumerate(G.adjacency()):
        names += str(adjacencies[0] + ', ')
    return names

def getFig(edge_trace, node_trace):   
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    # title='Collaboration network',
                    titlefont=dict(size=16),
                    showlegend=False,
                    hovermode='closest',
                    # margin=dict(b=20,l=5,r=5,t=40),
                    margin=dict(b=5,l=5,r=5,t=5),
                    annotations=[ dict(
                        showarrow=False,
                        xref="paper", yref="paper",
                        x=0.005, y=-0.002 ) ],
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))
    return fig








 


 
