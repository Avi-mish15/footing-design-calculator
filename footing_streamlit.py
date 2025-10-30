

import streamlit as st
import math
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from utils.is456_tables import get_tau_c, round_to_0_1, round_to_10

st.set_page_config(page_title="Isolated Footing Designer", page_icon="🧱", layout="centered")
st.markdown("""
<style>
html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}
</style>
""", unsafe_allow_html=True)
st.title("🧱 Isolated Footing Design Calculator")
st.caption("Based on IS 456:2000 – Module V (RCC Design)")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    P = st.number_input("Column Load P (kN)", 0.0, 10000.0, 1000.0)
    SBC = st.number_input("Safe Bearing Capacity (kN/m²)", 0.0, 1000.0, 200.0)
    fck = st.selectbox("Concrete Grade fck (N/mm²)", [15, 20, 25, 30, 35, 40], index=2)
    fy = st.selectbox("Steel Grade fy (N/mm²)", [250, 415, 500], index=1)
with col2:
    cb = st.number_input("Column Breadth (mm)", 100.0, 2000.0, 400.0)
    cd = st.number_input("Column Depth (mm)", 100.0, 2000.0, 400.0)
    cover = st.number_input("Clear Cover (mm)", 20.0, 100.0, 50.0)
    shape = st.selectbox("Footing Shape", ["Square", "Rectangular"])

def suggest_reinf(Ast):
    for dia in [12, 16, 20]:
        area_bar = math.pi * dia**2 / 4
        spacing = (1000 * area_bar) / Ast
        spacing = round_to_10(spacing)
        if spacing <= 250:
            return f"Provide {dia} mm φ bars @ {spacing} mm c/c both ways"
    return "Provide 20 mm φ bars @ 200 mm c/c"

if st.button("Calculate Design"):
    Pu = 1.5 * P
    A = Pu / SBC
    if shape == "Square":
        B = L = round_to_0_1(math.sqrt(A))
    else:
        B = round_to_0_1(math.sqrt(A/1.5))
        L = round_to_0_1(1.5*B)
    q = Pu / (B*L)
    e = (B - cb/1000)/2
    M = q*e**2/2
    d = round_to_10(max(math.sqrt((M*1e6)/(0.138*fck*1000)),150))
    z = 0.9*d
    Ast = (M*1e6)/(0.87*fy*z)
    pct = Ast/(1000*d)*100
    tau_c = get_tau_c(fck,pct)
    V = q*max(0,e-d/1000)
    v1 = (V*1000)/(1000*d)
    u = 2*(cb+cd)+8*d
    vp = (Pu*1000)/(u*d)
    reinf = suggest_reinf(Ast)

    st.markdown("### 🔹 Results")
    st.write(f"**Factored Load (Pu)** = {Pu:.1f} kN")
    st.write(f"**Footing Size (L × B)** = {L:.1f} m × {B:.1f} m (Area = {A:.3f} m²)")
    st.write(f"**Soil Pressure (q)** = {q:.1f} kN/m²")
    st.write(f"**Effective Depth (d)** = {d:.0f} mm")
    st.write(f"**Bending Moment** = {M:.2f} kNm/m width")
    st.write(f"**Required Ast** = {Ast:.1f} mm²/m  (p = {pct:.3f}%)")
    st.write(f"**τc (IS 456 Table 19)** = {tau_c:.3f} N/mm²")
    st.write(f"**One-way Shear** = {v1:.4f} → {'✅ OK' if v1<=tau_c else '❌ NOT OK'}")
    st.write(f"**Punching Shear** = {vp:.4f} → {'✅ OK' if vp<=tau_c else '❌ NOT OK'}")
    st.success(reinf)

    # PDF report
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    y = 800
    c.setFont("Helvetica-Bold", 14)
    c.drawString(100, y, "ISOLATED FOOTING DESIGN REPORT")
    c.setFont("Helvetica", 11)
    y -= 40
    lines = [
        f"Factored Load (Pu): {Pu:.1f} kN",
        f"Footing Size (L×B): {L:.1f} m × {B:.1f} m",
        f"Soil Pressure q: {q:.1f} kN/m²",
        f"Effective Depth d: {d:.0f} mm",
        f"Bending Moment: {M:.2f} kNm/m",
        f"Required Ast: {Ast:.1f} mm²/m",
        f"τc (Table 19): {tau_c:.3f} N/mm²",
        f"One-way Shear: {v1:.4f} → {'OK' if v1<=tau_c else 'NOT OK'}",
        f"Punching Shear: {vp:.4f} → {'OK' if vp<=tau_c else 'NOT OK'}",
        f"Reinforcement: {reinf}",
    ]
    for line in lines:
        c.drawString(100, y, line); y -= 20
    c.save()
    pdf = buf.getvalue()
    st.download_button("📄 Download PDF Report", pdf, file_name="Footing_Design_Report.pdf")
