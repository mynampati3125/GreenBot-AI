import streamlit as st
from auth import login, register
from database import create_user_table
from prediction import predict
import streamlit.components.v1 as components

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from PIL import Image
import io

# ---------------- CARE PLAN DATA ----------------
CARE_PLAN = {
    "Healthy Crop": {
        "description": "The crop is healthy and shows no visible disease symptoms.",
        "treatment": [
            "No treatment required at this stage."
        ],
        "prevention": [
            "Continue regular crop monitoring.",
            "Maintain proper irrigation schedule."
        ],
        "soil": {
            "fertilizer": "Routine fertilization as per crop growth stage.",
            "ideal": "Well-maintained fertile soil."
        }
    },
    "Crop Disease Detected": {
        "description": "The crop shows signs of disease and requires immediate care.",
        "treatment": [
            "Remove infected plant parts immediately.",
            "Apply suitable fungicides or pesticides."
        ],
        "prevention": [
            "Avoid water stagnation.",
            "Use certified seeds and crop rotation."
        ],
        "soil": {
            "fertilizer": "Apply balanced NPK fertilizer and organic compost.",
            "ideal": "Well-drained soil with good aeration."
        }
    }
}

# ---------------- PDF FUNCTION ----------------
def generate_pdf(user, healthy, diseased, condition, info, uploaded_file):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    def new_page():
        c.showPage()
        return height - 50

    y_cursor = height - 40

    # ---------- IMAGE (TOP CENTER) ----------
    img = Image.open(uploaded_file)
    img = img.resize((220, 220))
    img_reader = ImageReader(img)

    c.drawImage(
        img_reader,
        (width - 220) / 2,
        y_cursor - 220,
        width=220,
        height=220,
        preserveAspectRatio=True,
        mask='auto'
    )

    y_cursor -= 260

    # ---------- TITLE ----------
    c.setFont("Helvetica-Bold", 16)
    c.drawCentredString(width / 2, y_cursor, "GreenBot Analysis Report")
    y_cursor -= 25

    # ---------- BASIC INFO ----------
    c.setFont("Helvetica", 10)
    c.drawString(50, y_cursor, f"User: {user}")
    y_cursor -= 15
    c.drawString(50, y_cursor, f"Detected Condition: {condition}")
    y_cursor -= 25

    # ---------- PROGRESS BAR ----------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_cursor, "Prediction Confidence")
    y_cursor -= 15

    bar_x = 50
    bar_y = y_cursor
    bar_width = width - 100
    bar_height = 12

    c.setFillColor(colors.lightgrey)
    c.rect(bar_x, bar_y, bar_width, bar_height, fill=1, stroke=0)

    c.setFillColor(colors.HexColor("#1f77b4"))
    c.rect(bar_x, bar_y, bar_width * (healthy / 100), bar_height, fill=1, stroke=0)

    y_cursor -= 20
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawString(50, y_cursor, f"Healthy: {healthy}%")
    c.drawString(200, y_cursor, f"Diseased: {diseased}%")
    y_cursor -= 30

    # ---------- BAR GRAPH ----------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_cursor, "Confidence Comparison")
    y_cursor -= 15

    graph_x = 100
    graph_y = y_cursor - 160
    graph_height = 150
    bar_w = 40

    c.line(graph_x - 20, graph_y, graph_x - 20, graph_y + graph_height)

    for i in range(0, 101, 20):
        y = graph_y + (i / 100) * graph_height
        c.setFont("Helvetica", 8)
        c.drawString(graph_x - 40, y - 3, str(i))
        c.line(graph_x - 22, y, graph_x - 18, y)

    healthy_h = (healthy / 100) * graph_height
    c.setFillColor(colors.green)
    c.rect(graph_x, graph_y, bar_w, healthy_h, fill=1)
    c.drawCentredString(graph_x + bar_w / 2, graph_y - 12, "Healthy")

    diseased_h = (diseased / 100) * graph_height
    c.setFillColor(colors.red)
    c.rect(graph_x + 80, graph_y, bar_w, diseased_h, fill=1)
    c.drawCentredString(graph_x + 80 + bar_w / 2, graph_y - 12, "Diseased")

    y_cursor = graph_y - 40

    # ---------- PAGE BREAK CHECK ----------
    if y_cursor < 120:
        y_cursor = new_page()

    # ---------- TREATMENT & CARE ----------
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y_cursor, "Treatment & Care Plan")
    y_cursor -= 18

    c.setFont("Helvetica", 10)
    c.drawString(50, y_cursor, info["description"])
    y_cursor -= 18

    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_cursor, "Treatment:")
    y_cursor -= 14
    c.setFont("Helvetica", 10)

    for t in info["treatment"]:
        if y_cursor < 80:
            y_cursor = new_page()
            c.setFont("Helvetica", 10)
        c.drawString(65, y_cursor, f"- {t}")
        y_cursor -= 12

    y_cursor -= 6
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_cursor, "Prevention:")
    y_cursor -= 14
    c.setFont("Helvetica", 10)

    for p in info["prevention"]:
        if y_cursor < 80:
            y_cursor = new_page()
            c.setFont("Helvetica", 10)
        c.drawString(65, y_cursor, f"- {p}")
        y_cursor -= 12

    y_cursor -= 6
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y_cursor, "Soil / Fertilizer:")
    y_cursor -= 14
    c.setFont("Helvetica", 10)

    if y_cursor < 80:
        y_cursor = new_page()

    c.drawString(65, y_cursor, f"Fertilizer: {info['soil']['fertilizer']}")
    y_cursor -= 12
    c.drawString(65, y_cursor, f"Ideal Soil: {info['soil']['ideal']}")

    # ---------- FOOTER ----------
    c.setFont("Helvetica-Oblique", 8)
    c.drawString(
        50, 30,
        "Note: This report is generated by an AI model. Consult agricultural experts for final decisions."
    )

    c.save()
    buffer.seek(0)
    return buffer



# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="GreenBot AI", layout="wide")
create_user_table()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user" not in st.session_state:
    st.session_state.user = None

st.sidebar.title("Navigation")
page = (
    st.sidebar.radio("Go to", ["Login", "Register"])
    if not st.session_state.authenticated
    else st.sidebar.radio("Go to", ["Upload & Prediction", "Logout"])
)

left_col, right_col = st.columns([2, 1])

# ---------------- LEFT COLUMN ----------------
with left_col:
    if not st.session_state.authenticated:
        st.title("Home")
        login() if page == "Login" else register()

    else:
        if page == "Upload & Prediction":
            st.title("Upload & Prediction")
            st.write(f"Welcome, **{st.session_state.user}** 👋")

            file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg"])

            if file and st.button("Predict"):
                result = predict(file)

                healthy = result["Healthy (%)"]
                diseased = result["Diseased (%)"]

                if diseased >= 30:
                    condition = "Crop Disease Detected"
                    confidence = diseased
                else:
                    condition = "Healthy Crop"
                    confidence = healthy

                info = CARE_PLAN[condition]

                st.subheader("Prediction Confidence")
                st.progress(healthy / 100)

                st.markdown(
                    f"""
                    <p style="color:green;">🟢 Healthy: {healthy}%</p>
                    <p style="color:red;">🔴 Diseased: {diseased}%</p>
                    """,
                    unsafe_allow_html=True
                )

                st.bar_chart({
                    "Healthy": healthy,
                    "Diseased": diseased
                })

                st.subheader("🌿 Prediction Result")
                col1, col2 = st.columns(2)
                with col1:
                    st.success(f"Detected Condition: {condition}")
                with col2:
                    st.info(f"Confidence Score: {confidence:.2f}%")

                st.subheader("💊 Treatment & Care Plan")
                tab1, tab2, tab3 = st.tabs(["Treatment", "Prevention", "Soil / Fertilizer"])

                with tab1:
                    st.write(info["description"])
                    for t in info["treatment"]:
                        st.write(f"• {t}")

                with tab2:
                    for p in info["prevention"]:
                        st.write(f"• {p}")

                with tab3:
                    st.info(f"Fertilizer: {info['soil']['fertilizer']}")
                    st.success(f"Ideal Soil: {info['soil']['ideal']}")

                pdf = generate_pdf(
                    st.session_state.user,
                    healthy,
                    diseased,
                    condition,
                    info,
                    file
                )

                st.download_button(
                    "📄 Download Detailed PDF Report",
                    pdf,
                    "GreenBot_Report.pdf",
                    "application/pdf"
                )

        else:
            st.session_state.authenticated = False
            st.session_state.user = None
            st.success("Logged out successfully")

# ---------------- RIGHT COLUMN ----------------
with right_col:
    components.html(
        """
        <div style="height:85vh;">
            <script src="https://cdn.botpress.cloud/webchat/v3.5/inject.js"></script>
            <script src="https://files.bpcontent.cloud/2026/01/05/13/20260105132457-GZX2MBYY.js" defer></script>
        </div>
        """,
        height=550
    )
