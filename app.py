import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from typing import List
import pandas as pd

def process_text_input(text: str) -> List[str]:
    """Convert text input into list, handling various formats"""
    if not text.strip():
        return []
    return [line.strip() for line in text.strip().split('\n') if line.strip()]

def create_connection_graph(data_dict):
    """Create a NetworkX graph from the input data"""
    G = nx.Graph()
    
    # Color mapping for different node types
    colors = {
        'col1': '#ff9999',  # Light red
        'col2': '#99ff99',  # Light green
        'col3': '#9999ff',  # Light blue
        'col4': '#ffff99'   # Light yellow
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

def plot_graph(G):
    """Create and return a plot of the graph"""
    plt.figure(figsize=(15, 10))
    
    # Get node colors
    colors = [G.nodes[node]['color'] for node in G.nodes()]
    
    # Use spring layout for node positioning
    pos = nx.spring_layout(G, k=1, iterations=50)
    
    # Draw the graph
    nx.draw(G, pos,
            node_color=colors,
            with_labels=True,
            node_size=2000,
            font_size=8,
            font_weight='bold',
            edge_color='gray',
            width=1,
            alpha=0.7)
    
    return plt

# Set up the Streamlit page
st.set_page_config(page_title="Connection Visualizer", layout="wide")
st.title("Connection Pattern Visualizer")

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

# Add a button to generate the visualization
if st.button("Generate Visualization"):
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
        plt = plot_graph(G)
        st.pyplot(plt)
        
        # Display connection analysis
        st.subheader("Connection Analysis")
        
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
            st.dataframe(analysis_df)
        else:
            st.write("No shared connections found.")
        
    else:
        st.warning("Please enter some data in at least two columns to generate a visualization.")

# Add sample data button
if st.button("Load Sample Data"):
    sample_data = {
        "Client IDs": "1234\n2234\n3334\n4444",
        "Cookie Hashes": "ab77777\ncd29343\nab77777\nab77777",
        "Password Hashes": "hh11111\njj93991\njj93991\njj93991"
    }
    st.text("Sample data (copy to respective fields):")
    for name, data in sample_data.items():
        st.text_area(name, value=data, height=100)