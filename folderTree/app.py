import streamlit as st
import os
from streamlit_tree_independent_components import tree_independent_components

def folder_to_tree(path, node_id="0"):
    """Recursively convert a folder to tree structure for the component."""
    node = {
        "id": node_id,
        "name": os.path.basename(path) or path,
        "icon": "",
        "disable": False,
        "children": []
    }
    try:
        entries = sorted(os.listdir(path))
    except Exception:
        return node
    for idx, entry in enumerate(entries):
        entry_path = os.path.join(path, entry)
        child_id = f"{node_id}-{idx}"
        if os.path.isdir(entry_path):
            node["children"].append(folder_to_tree(entry_path, child_id))
        else:
            node["children"].append({
                "id": child_id,
                "name": entry,
                "icon": "",
                "disable": False
            })
    return node

st.title("Interactive Folder Tree Viewer")
folder_path = st.text_input("Enter folder path (server-side):")
if folder_path and os.path.isdir(folder_path):
    tree_data = folder_to_tree(folder_path)
    result = tree_independent_components(tree_data)
    st.write("Selected nodes:", result.get("setSelected", []))
elif folder_path:
    st.error("Please enter a valid directory path.")
