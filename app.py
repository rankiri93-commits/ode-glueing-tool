import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="מפעל הדבקת פתרונות", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    /* Global RTL for Hebrew */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    
    /* Force Sidebar Width */
    section[data-testid="stSidebar"] {
        width: 450px !important;
    }
    
    /* Align text right */
    h1, h2, h3, p, .stMarkdown, .stRadio, .stNumberInput, .stSelectbox {
        text-align: right;
    }
    
    /* Ensure Latex is LTR */
    .stLatex {
        direction: ltr;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.title("🧩 מפעל הדבקת פתרונות")
st.markdown("**המטרה:** לבנות פתרון חוקי לבעיית ההתחלה:")

# Main Equation
st.latex(r"xy' = 2y - 6x^4\sqrt{y}, \quad y(0)=0")


# --- Session State ---
if 'pieces' not in st.session_state:
    st.session_state.pieces = []

# --- Sidebar: The Toolbox ---
st.sidebar.header("🛠️ ארגז כלים")

# FIX 1: Simplified Radio Labels (Hebrew Only) to prevent scrambling
# We map the Hebrew label back to the internal key ('zero', 'pos', 'neg')
radio_options = [
    "פתרון האפס",
    "ענף חיובי",
    "ענף שלילי"
]

selected_label = st.sidebar.radio(
    "בחר את צורת הפתרון:",
    radio_options
)

# Logic to handle selection
if selected_label == "פתרון האפס":
    # Show the formula clearly BELOW the radio button
    st.sidebar.latex(r"y = 0")
    
    col1, col2 = st.sidebar.columns(2)
    b = col1.number_input("סוף (b)", value=2.0, step=0.1)
    a = col2.number_input("התחלה (a)", value=-2.0, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        st.session_state.pieces.append({
            "type": "zero", 
            "range": [a, b], 
            "color": "black", 
            "label": r"y=0",
            "desc": f"y=0 בטווח [{a}, {b}]"
        })

elif selected_label == "ענף חיובי":
    st.sidebar.latex(r"y = x^2(x^3 - x_0^3)^2")
    
    # User chooses x0
    x0 = st.sidebar.number_input("נקודת הדבקה (x₀ > 0)", value=1.5, min_value=0.1, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        label = fr"y = x^2(x^3 - {x0}^3)^2"
        desc = f"ענף חיובי, x₀={x0}"
        st.session_state.pieces.append({
            "type": "pos", 
            "x0": x0, 
            "range": [0, x0], 
            "color": "blue", 
            "label": label,
            "desc": desc
        })

elif selected_label == "ענף שלילי":
    st.sidebar.latex(r"y = x^2(x^3 - x_0^3)^2")
    
    # User chooses x0
    x0 = st.sidebar.number_input("נקודת הדבקה (x₀ < 0)", value=-1.5, max_value=-0.1, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        label = fr"y = x^2(x^3 - ({x0})^3)^2"
        desc = f"ענף שלילי, x₀={x0}"
        st.session_state.pieces.append({
            "type": "neg", 
            "x0": x0, 
            "range": [x0, 0], 
            "color": "red", 
            "label": label,
            "desc": desc
        })

if st.sidebar.button("נקה הכל (התחל מחדש)"):
    st.session_state.pieces = []


# --- Plotting Logic ---

col_graph, col_empty = st.columns([0.75, 0.25])

with col_graph:
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    # Set fixed plotting window
    ax.set_xlim(-2.5, 2.5)
    ax.set_ylim(-0.5, 6) 
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.axvline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.3)
    ax.set_title("Visualization of Selected Solutions")

    # Plot valid pieces
    for piece in st.session_state.pieces:
        # Wrap label in $...$ for Matplotlib LaTeX rendering
        plot_label = f"${piece['label']}$"
        
        if piece["type"] == "zero":
            x = np.linspace(piece["range"][0], piece["range"][1], 100)
            y = np.zeros_like(x)
            ax.plot(x, y, color=piece["color"], linewidth=3, label=plot_label)
            
        elif piece["type"] == "pos":
            x = np.linspace(0, piece["x0"], 100)
            y = (x**2) * ((x**3 - piece["x0"]**3)**2)
            ax.plot(x, y, color=piece["color"], linewidth=2, label=plot_label)

        elif piece["type"] == "neg":
            x = np.linspace(piece["x0"], 0, 100)
            y = (x**2) * ((x**3 - piece["x0"]**3)**2)
            ax.plot(x, y, color=piece["color"], linewidth=2, label=plot_label)

    # Unique Legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    if by_label:
        ax.legend(by_label.values(), by_label.keys(), loc='upper center')
    
    st.pyplot(fig)


# --- Analysis Text ---
st.markdown("### 🧐 ניתוח הפתרון שנבנה")

if len(st.session_state.pieces) > 0:
    st.write("המקטעים שנבחרו כרגע:")
    for i, p in enumerate(st.session_state.pieces):
        desc = p.get('desc', "מקטע")
        label = p.get('label', "")
        
        # FIX 2: Use Columns to physically separate Hebrew text (Right) from Math (Left)
        # This prevents them from mixing and reversing.
        c_math, c_text = st.columns([0.5, 0.5])
        
        with c_text:
            # Hebrew text on the right
            st.markdown(f"**{i+1}. {desc}:**")
            
        with c_math:
            # Math formula on the left (aligned right to meet the text)
            st.latex(label)
else:
    st.write("אנא הוסף מקטעים מארגז הכלים בצד כדי לבנות את הפתרון.")
