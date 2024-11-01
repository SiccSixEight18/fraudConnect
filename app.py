import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from typing import List
import pandas as pd
from datetime import datetime
import matplotlib.patches as patches

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

def plot_graph(G, title_text):
    """Create and return an enhanced plot of the graph"""
    # Create figure with specific size and background color
    plt.figure(figsize=(15, 10), facecolor='#f0f2f6')
    
    # Create main axis with a slight gray background
    ax = plt.gca()
    ax.set_facecolor('#f8f9fa')
    
    # Get node colors
    colors = [G.nodes[node]['color'] for node in G.nodes()]
    
    # Use spring layout with optimized parameters
    pos = nx.spring_layout(G, k=1.5, iterations=50)
    
    # Draw edges with alpha for better visibility
    nx.draw_networkx_edges(G, pos,
                          edge_color='#2c3e50',
                          alpha=0.2,
                          width=1.5)
    
    # Draw nodes with enhanced styling
    nx.draw_networkx_nodes(G, pos,
                          node_color=colors,
                          node_size=2500,
                          alpha=0.7,
                          edgecolors='white',
                          linewidths=2)
    
    # Draw labels with improved styling
    nx.draw_networkx_labels(G, pos,
                           font_size=9,
                           font_weight='bold',
                           font_family='sans-serif')
    
    # Add title with enhanced styling
    plt.title(title_text, 
             pad=20,
             fontsize=14,
             fontweight='bold',
             fontfamily='sans-serif')
    
    # Add date stamp in bottom right corner
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    plt.text(0.98, 0.02, f"Generated: {current_time}",
             fontsize=8,
             transform=plt.gca().transAxes,
             ha='right',
             alpha=0.7)
    
    # Add a subtle grid
    plt.grid(True, linestyle='--', alpha=0.1)
    
    # Add padding around the plot
    plt.tight_layout(pad=2.0)
    
    return plt

# Set up the Streamlit page with improved styling
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

# Main title with styling
st.title("🔍 Connection Pattern Visualizer")
st.markdown("---")

# Description
st.markdown("""
    Enter data in the columns below to visualize connections. Data points in the same row will be connected in the visualization.
    Each column is color-coded in the final graph for easy identification.
""")

# Create columns for the text inputs with improved layout
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

# Title input for the visualization
title_text = st.text_input("Visualization Title", 
                          "Connection Analysis of Fraud Patterns",
                          help="Enter a brief title or description for your visualization")

# Add a button to generate the visualization
if st.button("Generate Visualization", type="primary"):
    # Process all inputs
    data = {
        'col1': process_text_input(column1_data),
        'col2': process_text_input(column2_data),
        'col3': process_text_input(column3_data),
        'col4': process_text_input(column4_data)
    }
    
    # Check if we have any data to process
    if any(data.values()):
        # Create and display the graph
        G = create_connection_graph(data)
        plt = plot_graph(G, title_text)
        st.pyplot(plt)
        
        # Display connection analysis with improved styling
        st.markdown("### 📊 Connection Analysis")
        
        # Find nodes with multiple connections
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
            st.dataframe(analysis_df, use_container_width=True)
        else:
            st.info("No shared connections found in the data.")
        
    else:
        st.warning("Please enter some data in at least two columns to generate a visualization.")

# Add sample data button with improved styling
with st.expander("Show Sample Data"):
    st.markdown("### Sample Data for Testing")
    sample_data = {
        "Client IDs": "1234\n2234\n3334\n4444",
        "Cookie Hashes": "ab77777\ncd29343\nab77777\nab77777",
        "Password Hashes": "hh11111\njj93991\njj93991\njj93991"
    }
    for name, data in sample_data.items():
        st.text_area(f"Sample {name}", value=data, height=100)