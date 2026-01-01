import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="ODE Solution Glueing Factory", layout="wide")

st.title("🧩 The ODE Solution Gluing Factory")
st.markdown(r"""
**The Goal:** Construct a valid solution to the IVP on the interval $[-2, 2]$.
$$xy' = 2y - 6x^4\sqrt{y}, \quad y(0)=0$$
""")

# --- Session State to store the "glued" pieces ---
if 'pieces' not in st.session_state:
    st.session_state.pieces = []

# --- Sidebar: The Toolbox ---
st.sidebar.header("🛠️ Solution Toolbox")

solution_type = st.sidebar.radio(
    "Select a solution form:",
    ("1. Zero Solution (y=0)", 
     "2. Right Branch (defined for x > x0)", 
     "3. Left Branch (defined for x < x0)")
)

# Dynamic inputs based on choice
if "Zero" in solution_type:
    col1, col2 = st.sidebar.columns(2)
    a = col1.number_input("Start (a)", value=-1.0, step=0.1)
    b = col2.number_input("End (b)", value=1.0, step=0.1)
    if st.sidebar.button("Add Piece"):
        st.session_state.pieces.append({
            "type": "zero", "range": [a, b], "color": "black", "label": f"y=0 on [{a}, {b}]"
        })

elif "Right" in solution_type:
    x0 = st.sidebar.number_input("x0 (Gluing Point)", value=1.0, step=0.1)
    limit = st.sidebar.number_input("End x (visual limit)", value=2.0, step=0.1)
    if st.sidebar.button("Add Piece"):
        st.session_state.pieces.append({
            "type": "right", "x0": x0, "range": [x0, limit], "color": "blue", 
            "label": f"Right Branch, x0={x0}"
        })

elif "Left" in solution_type:
    x0 = st.sidebar.number_input("x0 (Gluing Point)", value=-1.0, step=0.1)
    limit = st.sidebar.number_input("Start x (visual limit)", value=-2.0, step=0.1)
    if st.sidebar.button("Add Piece"):
        st.session_state.pieces.append({
            "type": "left", "x0": x0, "range": [limit, x0], "color": "red", 
            "label": f"Left Branch, x0={x0}"
        })

# Button to clear graph
if st.sidebar.button("Clear All"):
    st.session_state.pieces = []

# --- Plotting Logic ---
fig, ax = plt.subplots(figsize=(10, 6))

# Set fixed plotting window
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-0.5, 5)
ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
ax.axvline(0, color='gray', linestyle='--', linewidth=0.8)
ax.set_xlabel("x")
ax.set_ylabel("y")
ax.grid(True, alpha=0.3)

# Plot valid pieces
for piece in st.session_state.pieces:
    if piece["type"] == "zero":
        x = np.linspace(piece["range"][0], piece["range"][1], 100)
        y = np.zeros_like(x)
        ax.plot(x, y, color=piece["color"], linewidth=3, label=piece["label"])
        
    elif piece["type"] == "right":
        # y = x^2(x^3 - x0^3)^2
        x = np.linspace(piece["range"][0], piece["range"][1], 100)
        # Ensure we don't plot where not defined (though range handles this)
        x_valid = x[x >= piece["x0"]] 
        if len(x_valid) > 0:
            y = (x_valid**2) * ((x_valid**3 - piece["x0"]**3)**2)
            ax.plot(x_valid, y, color=piece["color"], linewidth=2, label=piece["label"])

    elif piece["type"] == "left":
        # y = x^2(x^3 - x0^3)^2
        x = np.linspace(piece["range"][0], piece["range"][1], 100)
        x_valid = x[x <= piece["x0"]]
        if len(x_valid) > 0:
            y = (x_valid**2) * ((x_valid**3 - piece["x0"]**3)**2)
            ax.plot(x_valid, y, color=piece["color"], linewidth=2, label=piece["label"])

# Legend handling to avoid duplicates
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys())

st.pyplot(fig)

# --- Analysis Text ---
st.markdown("### 🧐 Analysis")
if len(st.session_state.pieces) > 0:
    st.write("Current pieces added:")
    for p in st.session_state.pieces:
        st.write(f"- {p['label']}")
else:
    st.write("Add pieces from the sidebar to build your solution.")
