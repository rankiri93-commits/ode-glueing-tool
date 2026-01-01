import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="מפעל הדבקת פתרונות", layout="wide")

# --- Custom CSS ---
st.markdown("""
<style>
    /* 1. Global RTL for the whole app (Hebrew) */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    
    /* 2. Force Sidebar Width */
    section[data-testid="stSidebar"] {
        width: 450px !important;
    }
    
    /* 3. General Text Alignment */
    h1, h2, h3, p, .stMarkdown, .stRadio, .stNumberInput, .stSelectbox {
        text-align: right;
    }
    
    /* 4. THE FIX: Force all Math (KaTeX) to stay LTR and isolated */
    .katex, .katex-display {
        direction: ltr !important;
        unicode-bidi: isolate !important;
    }
    
    /* 5. Analysis Section: Align list bullets correctly */
    ul {
        direction: rtl;
        list-style-position: inside;
        text-align: right;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.title("🧩 מפעל הדבקת פתרונות")

st.markdown("""
בממשק זה ניתן לבחור תנאי התחלה, ולהשתמש בצורות הפתרונות הכלליים על מנת לחפש פתרון למשוואה המקיים את תנאי ההתחלה.
שימו לב לכך שהפתרונות צריכים להיות גזירים ובפרט רציפים בכל תחום הגדרתם.
מומלץ להזיז את תנאי ההתחלה ולבדוק כיצד צורות הפתרונות האפשריים משתנות.
""")

# --- Session State ---
if 'pieces' not in st.session_state:
    st.session_state.pieces = []

# --- Sidebar: The Toolbox ---
st.sidebar.header("🛠️ ארגז כלים")

radio_options = [
    "תנאי התחלה (נקודה)",
    "פתרון האפס",
    "ענף חיובי",
    "ענף שלילי"
]

selected_label = st.sidebar.radio(
    "בחר את צורת הפתרון:",
    radio_options
)

# Logic to handle selection

# OPTION 1: INITIAL CONDITION (POINT)
if selected_label == "תנאי התחלה (נקודה)":
    st.sidebar.info("הוסף נקודה (x₀, y₀) לגרף:")
    
    col_pt1, col_pt2 = st.sidebar.columns(2)
    x_pt = col_pt1.number_input("x₀", value=0.0, step=0.1)
    y_pt = col_pt2.number_input("y₀", value=0.0, step=0.1)
    
    if st.sidebar.button("הוסף נקודה"):
        st.session_state.pieces.append({
            "type": "point",
            "x": x_pt,
            "y": y_pt,
            "color": "green",
            "label": f"({x_pt}, {y_pt})",
            "desc": f"תנאי התחלה בנקודה ({x_pt}, {y_pt})"
        })

# OPTION 2: ZERO SOLUTION
elif selected_label == "פתרון האפס":
    st.sidebar.info("נוסחה:")
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

# OPTION 3: POSITIVE BRANCH (Updated Logic x > x0)
elif selected_label == "ענף חיובי":
    st.sidebar.info("נוסחה:", r"0<x<x_0")
    st.sidebar.latex(r"y = x^2(x^3 - x_0^3)^2")
    
    x0 = st.sidebar.number_input("נקודת הדבקה (x₀ > 0)", value=1.0, min_value=0.1, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        label = fr"y = x^2(x^3 - {x0}^3)^2"
        desc = f"ענף חיובי, x₀={x0}"
        st.session_state.pieces.append({
            "type": "pos", 
            "x0": x0, 
            "range": [x0, 2.5], # Plots from x0 to the right edge
            "color": "blue", 
            "label": label,
            "desc": desc
        })

# OPTION 4: NEGATIVE BRANCH (Updated Logic x < x0)
elif selected_label == "ענף שלילי":
    st.sidebar.info("נוסחה:")
    st.sidebar.latex(r"y = x^2(x^3 - x_0^3)^2 \quad (x < x_0)")
    
    x0 = st.sidebar.number_input("נקודת הדבקה (x₀ < 0)", value=-1.0, max_value=-0.1, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        label = fr"y = x^2(x^3 - ({x0})^3)^2"
        desc = f"ענף שלילי, x₀={x0}"
        st.session_state.pieces.append({
            "type": "neg", 
            "x0": x0, 
            "range": [-2.5, x0], # Plots from left edge to x0
            "color": "red", 
            "label": label,
            "desc": desc
        })

if st.sidebar.button("נקה הכל (התחל מחדש)"):
    st.session_state.pieces = []


# --- Plotting Logic ---

col_graph, col_empty = st.columns([0.75, 0.25])

with col_graph:
    # 1. ODE Equation - Cleanly Centered
    c1, c_eqn, c2 = st.columns([0.1, 0.8, 0.1])
    with c_eqn:
        st.latex(r"xy' = 2y - 6x^4\sqrt{y}, \quad y(0)=0")

    # 2. The Plot
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

    # Dynamic limits: We define a "view window" but allow Y to grow if needed
    ax.set_xlim(-2.5, 2.5)
    # Remove hardcoded set_ylim to allow auto-scaling for "Take Off" solutions
    # ax.set_ylim(-0.5, 6) <--- REMOVED to fix visibility issues
    
    ax.axhline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.axvline(0, color='gray', linestyle='--', linewidth=0.8)
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.grid(True, alpha=0.3)

    # Plot valid pieces
    for piece in st.session_state.pieces:
        
        # Handle POINTS
        if piece["type"] == "point":
            ax.scatter([piece["x"]], [piece["y"]], color=piece["color"], s=100, zorder=10, label="Initial Condition")
            continue

        # Handle CURVES
        plot_label = f"${piece['label']}$"
        
        if piece["type"] == "zero":
            x = np.linspace(piece["range"][0], piece["range"][1], 200)
            y = np.zeros_like(x)
            ax.plot(x, y, color=piece["color"], linewidth=3, label=plot_label)
            
        elif piece["type"] == "pos":
            # Plot from x0 to a reasonable max (e.g., 2.5)
            x = np.linspace(piece["x0"], 2.5, 200)
            y = (x**2) * ((x**3 - piece["x0"]**3)**2)
            ax.plot(x, y, color=piece["color"], linewidth=2, label=plot_label)

        elif piece["type"] == "neg":
            # Plot from reasonable min (e.g., -2.5) to x0
            x = np.linspace(-2.5, piece["x0"], 200)
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
        
        if p['type'] == 'point':
            st.markdown(f"**{i+1}. {desc}**")
        else:
            # Column layout for equations
            col_text, col_math = st.columns([0.6, 0.4])
            with col_text:
                st.markdown(f"**{i+1}. {desc} :**")
            with col_math:
                st.latex(label)
else:
    st.write("אנא הוסף מקטעים מארגז הכלים בצד כדי לבנות את הפתרון.")
