import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_plotly_network(data_dict, title, field_names):
    G = nx.Graph()
    colors = {
        'col1': '#e41a1c',  # Deep red for primary 
        'col2': '#377eb8',  # Blue for devices
        'col3': '#4daf4a',  # Green for IPs
        'col4': '#984ea3'   # Purple for custom
    }
    
    # Build graph
    df = pd.DataFrame({k: pd.Series(v) for k, v in data_dict.items()})
    
    # Add all nodes first
    for col in df.columns:
        for val in df[col].dropna():
            if val:
                G.add_node(str(val), color=colors[col], type=col)
    
    # Only connect other fields to field1 (Client IDs)
    for _, row in df.iterrows():
        client_id = str(row['col1'])
        if pd.isna(client_id) or not client_id.strip():
            continue
            
        # Connect client to all other fields in this row
        for col in ['col2', 'col3', 'col4']:
            if col in row and not pd.isna(row[col]) and row[col].strip():
                G.add_edge(client_id, str(row[col]))

    pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes())), iterations=50)
    
    # Edges
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.7, color='#333333'),
        hoverinfo='none',
        mode='lines',
        opacity=0.2
    )
    
    # Nodes by type with labels
    node_traces = []
    for col, color in colors.items():
        nodes = [n for n, attr in G.nodes(data=True) if attr.get('type') == col]
        if not nodes:
            continue
            
        x = [pos[node][0] for node in nodes]
        y = [pos[node][1] for node in nodes]
        degrees = [G.degree(node) for node in nodes]
        
        node_traces.append(go.Scatter(
            x=x, y=y,
            mode='markers+text',
            hovertext=[f"{node}<br>{field_names[col]}<br>Connections: {G.degree(node)}" 
                      for node in nodes],
            text=[str(node) for node in nodes],
            textposition="bottom center",
            textfont=dict(
                size=10,
                color='black'
            ),
            marker=dict(
                size=[30 + (deg * 5) for deg in degrees],
                color=color,
                line_width=2,
                line_color='white'
            ),
            name=field_names[col],
            hoverinfo='text'
        ))

    fig = go.Figure(
        data=[edge_trace] + node_traces,
        layout=go.Layout(
            showlegend=True,
            hovermode='closest',
            clickmode='event+select',
            margin=dict(b=20, l=20, r=20, t=60),
            plot_bgcolor='white',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            title=dict(
                text=title,
                x=0.5,
                y=0.95,
                xanchor='center',
                font=dict(size=20)
            ),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="right",
                x=0.99,
                bgcolor='rgba(255,255,255,0.8)',
                font=dict(color='black'),  # Black legend text
            )
        )
    )
    
    return fig

st.set_page_config(layout="wide")

# Title input up top
title = st.text_input("Report Title", "Fraud Ring Analysis")

# Field names and data input side by side
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

field_names = {}
data = {}

with col1:
    field_names['col1'] = st.text_input("Field 1 Name", "Client IDs")
    data['col1'] = st.text_area(f"Paste {field_names['col1']}", height=150).split('\n')

with col2:
    field_names['col2'] = st.text_input("Field 2 Name", "Device IDs")
    data['col2'] = st.text_area(f"Paste {field_names['col2']}", height=150).split('\n')

with col3:
    field_names['col3'] = st.text_input("Field 3 Name", "Passwords")
    data['col3'] = st.text_area(f"Paste {field_names['col3']}", height=150).split('\n')

with col4:
    field_names['col4'] = st.text_input("Field 4 Name", "Custom Field")
    data['col4'] = st.text_area(f"Paste {field_names['col4']}", height=150).split('\n')

if st.button("Analyze", type="primary"):
    # Clean data
    data = {k: [x.strip() for x in v if x.strip()] for k, v in data.items()}
    
    if any(data.values()):
        fig = create_plotly_network(data, title, field_names)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Paste some data first")
