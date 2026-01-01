import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# --- Page Config (Layout & Title) ---
st.set_page_config(page_title="מפעל הדבקת פתרונות", layout="wide")

# Force RTL direction for Hebrew text
st.markdown("""
<style>
    .stApp {
        direction: rtl;
        text-align: right;
    }
    /* Fix alignment for headers and widgets to right */
    h1, h2, h3, .stMarkdown, .stRadio, .stNumberInput {
        text-align: right;
    }
    /* Keep math (LTR) distinct */
    .katex {
        direction: ltr; 
        text-align: left;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧩 מפעל הדבקת פתרונות מד״ר")
st.markdown(r"""
**המטרה:** לבנות פתרון חוקי לבעיית ההתחלה על הקטע $[-2, 2]$.
$$xy' = 2y - 6x^4\sqrt{y}, \quad y(0)=0$$
""")

# --- Session State to store the "glued" pieces ---
if 'pieces' not in st.session_state:
    st.session_state.pieces = []

# --- Sidebar: The Toolbox ---
st.sidebar.header("🛠️ ארגז כלים")

# Using a generic key so we can map Hebrew options to logic
option_map = {
    "פתרון האפס (y=0)": "zero",
    "ענף ימני (מוגדר עבור x > x₀)": "right",
    "ענף שמאלי (מוגדר עבור x < x₀)": "left"
}

selection = st.sidebar.radio(
    "בחר את צורת הפתרון:",
    list(option_map.keys())
)
solution_type = option_map[selection]

# Dynamic inputs based on choice
if solution_type == "zero":
    col1, col2 = st.sidebar.columns(2)
    b = col1.number_input("סוף (b)", value=1.0, step=0.1)
    a = col2.number_input("התחלה (a)", value=-1.0, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        label = r"$y=0$"
        desc = f"y=0 בטווח [{a}, {b}]"
        st.session_state.pieces.append({
            "type": "zero", 
            "range": [a, b], 
            "color": "black", 
            "label": label,
            "desc": desc
        })

elif solution_type == "right":
    x0 = st.sidebar.number_input("נקודת הדבקה (x₀)", value=1.0, step=0.1)
    limit = st.sidebar.number_input("גבול עליון לציור (x max)", value=2.0, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        # Create explicit formula string: x^2(x^3 - (x0)^3)^2
        # We use {{ and }} to escape curly braces in f-strings for LaTeX
        label = fr"$y = x^2(x^3 - ({x0})^3)^2$"
        desc = f"ענף ימני, x₀={x0}"
        st.session_state.pieces.append({
            "type": "right", 
            "x0": x0, 
            "range": [x0, limit], 
            "color": "blue", 
            "label": label,
            "desc": desc
        })

elif solution_type == "left":
    x0 = st.sidebar.number_input("נקודת הדבקה (x₀)", value=-1.0, step=0.1)
    limit = st.sidebar.number_input("גבול תחתון לציור (x min)", value=-2.0, step=0.1)
    
    if st.sidebar.button("הוסף מקטע"):
        label = fr"$y = x^2(x^3 - ({x0})^3)^2$"
        desc = f"ענף שמאלי, x₀={x0}"
        st.session_state.pieces.append({
            "type": "left", 
            "x0": x0, 
            "range": [limit, x0], 
            "color": "red", 
            "label": label,
            "desc": desc
        })

# Button to clear graph
if st.sidebar.button("נקה הכל (התחל מחדש)"):
    st.session_state.pieces = []

# --- Plotting Logic ---
# Changed figsize to (8, 5) for a slightly more compact look
# Added dpi=300 for "High Definition" crispness
fig, ax = plt.subplots(figsize=(8, 5), dpi=300)

# Set fixed plotting window
ax.set_xlim(-2.5, 2.5)
ax.set_ylim(-0.5, 5)
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
        # Use the explicit formula label for the legend
        ax.plot(x, y, color=piece["color"], linewidth=3, label=piece["label"])
        
    elif piece["type"] == "right":
        x = np.linspace(piece["range"][0], piece["range"][1], 100)
        x_valid = x[x >= piece["x0"]] 
        if len(x_valid) > 0:
            y = (x_valid**2) * ((x_valid**3 - piece["x0"]**3)**2)
            ax.plot(x_valid, y, color=piece["color"], linewidth=2, label=piece["label"])

    elif piece["type"] == "left":
        x = np.linspace(piece["range"][0], piece["range"][1], 100)
        x_valid = x[x <= piece["x0"]]
        if len(x_valid) > 0:
            y = (x_valid**2) * ((x_valid**3 - piece["x0"]**3)**2)
            ax.plot(x_valid, y, color=piece["color"], linewidth=2, label=piece["label"])

# Legend handling to avoid duplicates in the plot
handles, labels = plt.gca().get_legend_handles_labels()
by_label = dict(zip(labels, handles))
ax.legend(by_label.values(), by_label.keys(), loc='upper center')

st.pyplot(fig)

# --- Analysis Text (Hebrew) ---
st.markdown("### 🧐 ניתוח הפתרון שנבנה")
if len(st.session_state.pieces) > 0:
    st.write("המקטעים שנבחרו כרגע:")
    for p in st.session_state.pieces:
        # Display the description in Hebrew + the Math formula
        st.write(f"- {p['desc']} :  {p['label']}")
else:
    st.write("אנא הוסף מקטעים מארגז הכלים בצד כדי לבנות את הפתרון.")
