import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from typing import List, Dict
import pandas as pd
from datetime import datetime
import matplotlib.patches as patches
import numpy as np

# Utility Functions
def truncate_text(text: str, max_length: int, truncate_start: bool = True) -> str:
    """Truncate text and add ellipsis at start or end"""
    if len(text) <= max_length:
        return text
    if truncate_start:
        return '...' + text[-max_length:]
    return text[:max_length] + '...'

def process_text_input(text: str) -> List[str]:
    """Convert text input into list, handling various formats"""
    if not text:  # Handle None or empty string
        return []
    return [line.strip() for line in text.strip().split('\n') if line.strip()]

def calculate_metrics(G) -> Dict:
    """Calculate advanced network metrics"""
    metrics = {
        'total_nodes': G.number_of_nodes(),
        'total_connections': G.number_of_edges(),
        'avg_connections': np.mean([d for n, d in G.degree()]),
        'density': nx.density(G),
        'connected_components': nx.number_connected_components(G),
        'avg_clustering': nx.average_clustering(G),
        'most_central_nodes': sorted(
            nx.degree_centrality(G).items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
    }
    
    # Calculate community detection if possible
    try:
        communities = nx.community.greedy_modularity_communities(G)
        metrics['communities'] = len(communities)
    except:
        metrics['communities'] = 'N/A'
    
    return metrics

def create_connection_graph(data_dict):
    """Create a NetworkX graph from the input data"""
    G = nx.Graph()
    
    # Color mapping for different node types
    colors = {
        'col1': '#FF6B6B',  # Coral red
        'col2': '#4ECDC4',  # Turquoise
        'col3': '#45B7D1',  # Sky blue
        'col4': '#96CEB4'   # Sage green
    }
    
    # Get the maximum length of all columns
    max_length = max(len(values) for values in data_dict.values())
    
    # Create a pandas DataFrame with aligned rows
    df = pd.DataFrame({
        col: values + [None] * (max_length - len(values))
        for col, values in data_dict.items()
    })
    
    # Add nodes with their respective colors
    for col in df.columns:
        for value in df[col].dropna():
            if value:  # Only add if value exists
                G.add_node(str(value), color=colors[col], type=col)
    
    # Add edges by connecting values in the same row
    for idx in df.index:
        row_values = [str(val) for val in df.loc[idx] if pd.notna(val)]
        for i in range(len(row_values)):
            for j in range(i + 1, len(row_values)):
                G.add_edge(row_values[i], row_values[j])
    
    return G

def plot_graph(G, title_text, viz_settings):
    """Create and return an enhanced plot of the graph with tooltips"""
    plt.figure(figsize=(15, 10), facecolor=viz_settings['background_color'])
    
    ax = plt.gca()
    ax.set_facecolor(viz_settings['background_color'])
    
    # Get node colors with custom alpha
    colors = [f"{G.nodes[node]['color']}{viz_settings['node_alpha']:02x}" 
             for node in G.nodes()]
    
    # Calculate node sizes based on connections
    degrees = dict(G.degree())
    max_degree = max(degrees.values()) if degrees else 1
    min_degree = min(degrees.values()) if degrees else 1
    
    node_sizes = []
    for node in G.nodes():
        if max_degree == min_degree:
            size = (viz_settings['min_node_size'] + viz_settings['max_node_size']) / 2
        else:
            size = viz_settings['min_node_size'] + \
                   (viz_settings['max_node_size'] - viz_settings['min_node_size']) * \
                   (degrees[node] - min_degree) / (max_degree - min_degree)
        node_sizes.append(size)
    
    # Use specified layout
    if viz_settings['layout'] == 'spring':
        pos = nx.spring_layout(G, k=viz_settings['spacing'])
    elif viz_settings['layout'] == 'circular':
        pos = nx.circular_layout(G)
    else:
        pos = nx.kamada_kawai_layout(G)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos,
                          edge_color=viz_settings['edge_color'],
                          alpha=viz_settings['edge_alpha'],
                          width=viz_settings['edge_width'])
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos,
                          node_color=colors,
                          node_size=node_sizes,
                          alpha=1,
                          edgecolors=viz_settings['node_edge_color'],
                          linewidths=viz_settings['node_edge_width'])
    
    # Create labels with annotations for full text
    for node in G.nodes():
        x, y = pos[node]
        full_text = node
        truncated = truncate_text(node, 
                                viz_settings['max_label_length'],
                                not viz_settings['truncate_start'])
        
        # Draw truncated label
        plt.text(x, y, truncated,
                fontsize=viz_settings['font_size'],
                fontweight='bold',
                horizontalalignment='center',
                verticalalignment='center')
        
        # Add small indicator if text is truncated
        if full_text != truncated:
            plt.text(x, y - 0.02,
                    f"({G.degree(node)} connections)",
                    fontsize=viz_settings['font_size'] - 2,
                    alpha=0.7,
                    horizontalalignment='center',
                    verticalalignment='top')
    
    plt.title(title_text, 
             pad=20,
             fontsize=14,
             fontweight='bold',
             fontfamily='sans-serif')
    
    # Add legend for node sizes
    if viz_settings['show_legend']:
        legend_elements = [
            plt.scatter([], [], s=viz_settings['min_node_size'], 
                       label=f'Min Connections ({min_degree})'),
            plt.scatter([], [], s=viz_settings['max_node_size'], 
                       label=f'Max Connections ({max_degree})')
        ]
        plt.legend(handles=legend_elements, loc='upper left', 
                  bbox_to_anchor=(1.1, 1))
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    plt.text(0.98, 0.02, f"Generated: {current_time}",
             fontsize=8,
             transform=plt.gca().transAxes,
             ha='right',
             alpha=0.7)
    
    plt.grid(True, linestyle='--', alpha=0.1)
    plt.tight_layout(pad=2.0)
    
    return plt

# Set up the Streamlit page
st.set_page_config(page_title="Connection Visualizer", layout="wide")

# Custom CSS for better styling
st.markdown("""
    <style>
    .stTextInput > label {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .stTextArea > label {
        font-size: 1.2rem;
        font-weight: bold;
        color: #2c3e50;
    }
    .stButton > button {
        width: 100%;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🔍 Connection Pattern Visualizer")
st.markdown("---")

# Enhanced visualization settings
with st.expander("Visualization Settings", expanded=False):
    st.markdown("### Basic Settings")
    col_settings1, col_settings2, col_settings3 = st.columns(3)
    
    with col_settings1:
        max_label_length = st.slider(
            "Maximum Label Length",
            min_value=5,
            max_value=50,
            value=20,
            help="Truncate node labels to this length"
        )
        truncate_start = st.checkbox(
            "Truncate Start of Label",
            value=False,
            help="If checked, truncates the start of the label instead of the end"
        )
    
    with col_settings2:
        min_node_size = st.slider(
            "Minimum Node Size",
            min_value=1000,
            max_value=3000,
            value=2000,
            help="Size of nodes with fewest connections"
        )
        max_node_size = st.slider(
            "Maximum Node Size",
            min_value=2000,
            max_value=5000,
            value=4000,
            help="Size of nodes with most connections"
        )
    
    with col_settings3:
        layout_type = st.selectbox(
            "Layout Algorithm",
            ['spring', 'circular', 'kamada_kawai'],
            help="Choose how nodes are arranged"
        )
        show_legend = st.checkbox("Show Size Legend", value=True)
    
    st.markdown("### Advanced Settings")
    col_adv1, col_adv2, col_adv3 = st.columns(3)
    
    with col_adv1:
        node_alpha = st.slider("Node Transparency", 0, 255, 200)
        edge_alpha = st.slider("Edge Transparency", 0.0, 1.0, 0.2)
        bg_color = st.color_picker("Background Color", "#f0f2f6")
    
    with col_adv2:
        edge_color = st.color_picker("Edge Color", "#2c3e50")
        edge_width = st.slider("Edge Width", 0.5, 3.0, 1.5)
        node_spacing = st.slider("Node Spacing", 0.5, 2.0, 1.5)
    
    with col_adv3:
        font_size = st.slider("Font Size", 6, 16, 9)
        node_edge_color = st.color_picker("Node Border Color", "#FFFFFF")
        node_edge_width = st.slider("Node Border Width", 0.0, 3.0, 2.0)

# Store all visualization settings
viz_settings = {
    'max_label_length': max_label_length,
    'truncate_start': truncate_start,
    'min_node_size': min_node_size,
    'max_node_size': max_node_size,
    'layout': layout_type,
    'show_legend': show_legend,
    'node_alpha': node_alpha,
    'edge_alpha': edge_alpha,
    'background_color': bg_color,
    'edge_color': edge_color,
    'edge_width': edge_width,
    'spacing': node_spacing,
    'font_size': font_size,
    'node_edge_color': node_edge_color,
    'node_edge_width': node_edge_width
}

# Create columns for the text inputs
col1, col2 = st.columns(2)
col3, col4 = st.columns(2)

with col1:
    column1_name = st.text_input("Column 1 Name", "Client IDs")
    column1_data = st.text_area(f"Paste {column1_name} (one per line)", height=150)

with col2:
    column2_name = st.text_input("Column 2 Name", "Cookie Hashes")
    column2_data = st.text_area(f"Paste {column2_name} (one per line)", height=150)

with col3:
    column3_name = st.text_input("Column 3 Name", "Password Hashes")
    column3_data = st.text_area(f"Paste {column3_name} (one per line)", height=150)

with col4:
    column4_name = st.text_input("Column 4 Name", "Custom Field")
    column4_data = st.text_area(f"Paste {column4_name} (one per line)", height=150)

title_text = st.text_input("Visualization Title", 
                          "Connection Analysis of Fraud Patterns",
                          help="Enter a brief title or description for your visualization")

# Generate visualization button
if st.button("Generate Visualization", type="primary"):
    data = {
        'col1': process_text_input(column1_data),
        'col2': process_text_input(column2_data),
        'col3': process_text_input(column3_data),
        'col4': process_text_input(column4_data)
    }
    
    if any(data.values()):
        G = create_connection_graph(data)
        plt = plot_graph(G, title_text, viz_settings)
        st.pyplot(plt)
        
        # Enhanced Analysis Section
        st.markdown("### 📊 Detailed Analysis")
        
        # Calculate metrics
        metrics = calculate_metrics(G)
        
        # Display metrics in columns
        metric_col1, metric_col2 = st.columns(2)
        
        with metric_col1:
            st.markdown("#### Network Statistics")
            st.write(f"Total Nodes: {metrics['total_nodes']}")
            st.write(f"Total Connections: {metrics['total_connections']}")
            st.write(f"Average Connections: {metrics['avg_connections']:.2f}")
            st.write(f"Network Density: {metrics['density']:.3f}")
            st.write(f"Connected Components: {metrics['connected_components']}")
            st.write(f"Average Clustering: {metrics['avg_clustering']:.3f}")
            st.write(f"Communities Detected: {metrics['communities']}")
        
        with metric_col2:
            st.markdown("#### Most Connected Nodes")
            central_nodes_df = pd.DataFrame(
                metrics['most_central_nodes'],
                columns=['Node', 'Centrality Score']
            )
            st.dataframe(central_nodes_df)
        
        # Detailed connection analysis
        st.markdown("#### Connection Details")
        connected_nodes = []
        for node in G.nodes():
            degree = G.degree(node)
            if degree > 1:
                connected_nodes.append({
                    'Value': node,
                    'Connections': degree,
                    'Type': G.nodes[node]['type'],
                    'Centrality Score': nx.degree_centrality(G)[node]
                })
        
        if connected_nodes:
            analysis_df = pd.DataFrame(connected_nodes)
            analysis_df = analysis_df.sort_values('Connections', ascending=False)
            st.dataframe(analysis_df, use_container_width=True)
        else:
            st.info("No shared connections found in the data.")
    else:
        st.warning("Please enter some data in at least two columns to generate a visualization.")

# Add sample data button and display
with st.expander("Show Sample Data"):
    st.markdown("### Sample Data for Testing")
    sample_data = {
        "Client IDs": """1234
2234
3334
4444
5555""",
        
        "Cookie Hashes": """ab77777
cd29343
ab77777
ab77777
ef88888""",
        
        "Password Hashes": """hh11111
jj93991
jj93991
jj93991
kk22222""",
        
        "IP Addresses": """192.168.1.1
192.168.1.2
192.168.1.1
192.168.1.3
192.168.1.2"""
    }
    
    # Create two columns for sample data
    col1, col2 = st.columns(2)
    
    # Display first two samples in first column
    with col1:
        for name in list(sample_data.keys())[:2]:
            st.text_area(
                f"Sample {name}",
                value=sample_data[name],
                height=150,
                help=f"Click to copy sample {name.lower()}"
            )
    
    # Display last two samples in second column
    with col2:
        for name in list(sample_data.keys())[2:]:
            st.text_area(
                f"Sample {name}",
                value=sample_data[name],
                height=150,
                help=f"Click to copy sample {name.lower()}"
            )
    
    st.markdown("""
    #### How to use sample data:
    1. Click on any text area above
    2. Press Ctrl+A (Cmd+A on Mac) to select all
    3. Press Ctrl+C (Cmd+C on Mac) to copy
    4. Paste into the corresponding input field above
    
    This sample data shows common patterns:
    - Shared cookie hashes (ab77777)
    - Shared password hashes (jj93991)
    - Shared IP addresses (192.168.1.1, 192.168.1.2)
    """)