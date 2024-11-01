import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from typing import List
import pandas as pd
from datetime import datetime
import matplotlib.patches as patches

def truncate_text(text: str, max_length: int) -> str:
    """Truncate text and add ellipsis if needed"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + '...'

def process_text_input(text: str) -> List[str]:
    """Convert text input into list, handling various formats"""
    if not text.strip():
        return []
    return [line.strip() for line in text.strip().split('\n') if line.strip()]

def create_connection_graph(data_dict):
    """Create a NetworkX graph from the input data"""
    G = nx.Graph()
    
    # Enhanced color scheme
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

def plot_graph(G, title_text, max_label_length, min_node_size, max_node_size):
    """Create and return an enhanced plot of the graph"""
    plt.figure(figsize=(15, 10), facecolor='#f0f2f6')
    
    ax = plt.gca()
    ax.set_facecolor('#f8f9fa')
    
    # Get node colors
    colors = [G.nodes[node]['color'] for node in G.nodes()]
    
    # Calculate node sizes based on number of connections
    degrees = dict(G.degree())
    max_degree = max(degrees.values()) if degrees else 1
    min_degree = min(degrees.values()) if degrees else 1
    
    # Scale node sizes between min and max size based on connections
    node_sizes = []
    for node in G.nodes():
        if max_degree == min_degree:
            size = (min_node_size + max_node_size) / 2
        else:
            size = min_node_size + (max_node_size - min_node_size) * \
                   (degrees[node] - min_degree) / (max_degree - min_degree)
        node_sizes.append(size)
    
    pos = nx.spring_layout(G, k=1.5, iterations=50)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos,
                          edge_color='#2c3e50',
                          alpha=0.2,
                          width=1.5)
    
    # Draw nodes with varying sizes
    nx.draw_networkx_nodes(G, pos,
                          node_color=colors,
                          node_size=node_sizes,
                          alpha=0.7,
                          edgecolors='white',
                          linewidths=2)
    
    # Draw labels with truncation
    labels = {node: truncate_text(node, max_label_length) for node in G.nodes()}
    nx.draw_networkx_labels(G, pos,
                           labels=labels,
                           font_size=9,
                           font_weight='bold',
                           font_family='sans-serif')
    
    plt.title(title_text, 
             pad=20,
             fontsize=14,
             fontweight='bold',
             fontfamily='sans-serif')
    
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

# Custom CSS
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

# Add visualization settings in an expander
with st.expander("Visualization Settings", expanded=False):
    st.markdown("### Display Settings")
    col_settings1, col_settings2 = st.columns(2)
    
    with col_settings1:
        max_label_length = st.slider(
            "Maximum Label Length",
            min_value=5,
            max_value=50,
            value=20,
            help="Truncate node labels to this length"
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

if st.button("Generate Visualization", type="primary"):
    data = {
        'col1': process_text_input(column1_data),
        'col2': process_text_input(column2_data),
        'col3': process_text_input(column3_data),
        'col4': process_text_input(column4_data)
    }
    
    if any(data.values()):
        G = create_connection_graph(data)
        plt = plot_graph(G, title_text, max_label_length, min_node_size, max_node_size)
        st.pyplot(plt)
        
        st.markdown("### 📊 Connection Analysis")
        
        connected_nodes = []
        for node in G.nodes():
            degree = G.degree(node)
            if degree > 1:
                connected_nodes.append({
                    'Value': node,
                    'Connections': degree,
                    'Type': G.nodes[node]['type']
                })
        
        if connected_nodes:
            analysis_df = pd.DataFrame(connected_nodes)
            analysis_df = analysis_df.sort_values('Connections', ascending=False)
            st.dataframe(analysis_df, use_container_width=True)
        else:
            st.info("No shared connections found in the data.")
        
    else:
        st.warning("Please enter some data in at least two columns to generate a visualization.")

with st.expander("Show Sample Data"):
    st.markdown("### Sample Data for Testing")
    sample_data = {
        "Client IDs": "1234\n2234\n3334\n4444",
        "Cookie Hashes": "ab77777\ncd29343\nab77777\nab77777",
        "Password Hashes": "hh11111\njj93991\njj93991\njj93991"
    }
    for name, data in sample_data.items():
        st.text_area(f"Sample {name}", value=data, height=100)