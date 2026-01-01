import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page Config ---
st.set_page_config(page_title="מפעל הדבקת פתרונות", layout="wide")

# --- Custom CSS (RTL + Wider Sidebar + Math Isolation) ---
st.markdown("""
<style>
    /* 1. Global RTL for Hebrew */
    .stApp {
        direction: rtl;
        text-align: right;
    }
    
    /* 2. Force Sidebar Width to be wide enough for formulas */
    section[data-testid="stSidebar"] {
        width: 450px !important;
    }
    
    /* 3. CRITICAL FIX: Isolate Math (KaTeX) so it stays LTR */
    .katex, .katex-display {
        direction: ltr !important; 
        unicode-bidi: isolate !important;
        text-align: left;
    }
    
    /* 4. Align standard text elements to the right */
    h1, h2, h3, p, .stMarkdown, .stRadio, .stNumberInput, .stSelectbox {
        text-align: right;
    }
    
    /* 5. Fix bullet points in lists */
    ul {
        direction: rtl;
        text-align: right;
        list-style-position: inside;
    }
</style>
""", unsafe_allow_html=True)

# --- Header Section ---
st.title("🧩 מפעל הדבקת פתרונות")
st.markdown("**המטרה:** לבנות פתרון חוקי לבעיית ההתחלה:")

# Centered, Large Equation using HTML wrapper to force alignment and size
st.markdown(r"""
<div style="direction: ltr; text-align: center; margin-bottom: 20px;">
    <h2>$$xy' = 2y - 6x^4\sqrt{y}, \quad y(0)=0$$</h2>
</div>
""", unsafe_allow_html=True)


# --- Session State ---
if 'pieces' not in st.session_state:
    st.session_state.pieces = []

# --- Sidebar: The Toolbox ---
st.sidebar.header("🛠️ ארגז כלים")

# Options cleaned up (removed the confusing domain comments)
option_map = {
    "zero": r"פתרון האפס: $y=0$",
    "pos": r"ענף חיובי ($x_0 > 0$): $y = x^2(x^3 - x_0^3)^2$",
    "neg": r"ענף שלילי ($x_0 < 0$): $y = x^2(x^3 - x_0^3)^2$"
}

selection_label = st.sidebar.radio(
    "בחר את צורת הפתרון:",
    list(option_map.values())
)

# Identify selected type
solution_type = [k for k, v in option_map.items() if v == selection_label][0]

# --- Input Logic ---
if solution_type == "zero":
    col1, col2 = st.sidebar.columns(2)
    b = col1.number_input("סוף (b)", value=2.0, step=0.1)
    a = col2.number_input("התחלה (a)", value=-2.0, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        st.session_state.pieces.append({
            "type": "zero", 
            "range": [a, b], 
            "color": "black", 
            "label": r"$y=0$",
            "desc": f"y=0 בטווח [{a}, {b}]"
        })

elif solution_type == "pos":
    # User chooses x0 (Must be positive)
    x0 = st.sidebar.number_input("נקודת הדבקה (x₀ > 0)", value=1.5, min_value=0.1, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        label = fr"$y = x^2(x^3 - ({x0})^3)^2$"
        desc = f"ענף חיובי, x₀={x0}"
        st.session_state.pieces.append({
            "type": "pos", 
            "x0": x0, 
            "range": [0, x0], 
            "color": "blue", 
            "label": label,
            "desc": desc
        })

elif solution_type == "neg":
    # User chooses x0 (Must be negative)
    x0 = st.sidebar.number_input("נקודת הדבקה (x₀ < 0)", value=-1.5, max_value=-0.1, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        label = fr"$y = x^2(x^3 - ({x0})^3)^2$"
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

# Use columns to constrain width to ~75%
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
        if piece["type"] == "zero":
            x = np.linspace(piece["range"][0], piece["range"][1], 100)
            y = np.zeros_like(x)
            ax.plot(x, y, color=piece["color"], linewidth=3, label=piece["label"])
            
        elif piece["type"] == "pos":
            # Plot only within [0, x0]
            x = np.linspace(0, piece["x0"], 100)
            y = (x**2) * ((x**3 - piece["x0"]**3)**2)
            ax.plot(x, y, color=piece["color"], linewidth=2, label=piece["label"])

        elif piece["type"] == "neg":
            # Plot only within [x0, 0]
            x = np.linspace(piece["x0"], 0, 100)
            y = (x**2) * ((x**3 - piece["x0"]**3)**2)
            ax.plot(x, y, color=piece["color"], linewidth=2, label=piece["label"])

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
    for p in st.session_state.pieces:
        desc = p.get('desc', "מקטע")
        label = p.get('label', "")
        
        # HTML Injection to force correct directionality: 
        # Hebrew on Right, Bullet, Math on Left
        st.markdown(
            f"""
            <div style="direction: rtl; text-align: right;">
                • {desc} : &nbsp; <span style="direction: ltr; unicode-bidi: isolate;">{label}</span>
            </div>
            """, 
            unsafe_allow_html=True
        )
else:
    st.write("אנא הוסף מקטעים מארגז הכלים בצד כדי לבנות את הפתרון.")
