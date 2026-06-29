
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

# PAGE CONFIG
st.set_page_config(layout="wide")

# HEADER
col1, col2 = st.columns([6, 1])

with col1:
    st.title("Pipeline Transient Analysis & Design Tool")

st.markdown("""
### 📘 About This Tool
The **Pipeline Transient Analysis & Design Tool** is developed to help engineers understand 
and evaluate pressure surge (water hammer) effects in pipeline systems during transient events 
such as valve closure and pump shutdown.

This tool performs simplified transient calculations based on fundamental hydraulic principles 
and provides quick insights into system behavior under varying operating conditions.

### 🔧 Key Features

• Calculates wave speed based on fluid and pipe properties  
• Estimates surge pressure considering flow conditions and stopping time  
• Evaluates system safety using pressure ratio and risk classification  
• Visualizes pressure response through Pressure vs Time graph  
• Provides engineering interpretation and system impact assessment  

### 🎯 Purpose

The main objective of this tool is to support **preliminary design evaluation**, 
**risk identification**, and **engineering decision-making** in pipeline systems, 
in accordance with common industry practices.

### ⚠️ Note

This is a **simplified analytical tool** intended for conceptual and preliminary design. Detailed transient analysis may require advanced simulation software and system-specific modeling.
""")


with col2:
    logo = os.path.join("images", "logo.png")
    if os.path.exists(logo):
        st.image(logo, width=120)

st.markdown("---")

# TABS
tab1, tab2 = st.tabs(["🔧 Pipeline Transient Analysis Tool", "📚 Theory & Guidelines"])

# ==================================
# TAB 1
# ==================================
with tab1:

    st.subheader("Input Data")

    colA, colB = st.columns(2)

    # ✅ LEFT COLUMN (Geometry + Elevation)
    with colA:
        L = st.number_input("Pipe Length (m)", value=5.0, help="Total pipeline length")

        D = st.number_input("Pipe Diameter (mm)", value=25.0, help="Internal pipe diameter") / 1000

        t_pipe = st.number_input("Pipe Thickness (mm)", value=2.0, help="Pipe wall thickness") / 1000

        H = st.number_input(
            "Elevation Difference (m)",
            value=0.0,
            help="(+ve → pipe goes upward, -ve → pipe goes downward)"
        )

    # ✅ RIGHT COLUMN (Flow + Limits)
    with colB:
        V = st.number_input("Flow Velocity (m/s)", value=2.0, help="Higher velocity increases surge pressure")

        t_stop = st.number_input(
            "Flow Stopping Time (sec)",
            value=3.0,
            help="""
How fast the flow stops.

• Fast stop → high surge (danger)  
• Slow stop → low surge (safe)

✅ Recommended:
• Keep stopping time greater than critical time (2L/a)

Where:
• L = pipeline length  
• a = wave speed (speed of pressure wave in pipe)

• Typical range: 3–10 seconds (based on Hydraulic Institute practice)

⚠ Very fast stopping (< 1 sec) = high risk
"""
        )

        allowable = st.number_input(
            "Allowable Pressure (bar)",
            value=10.0,
            help="Maximum safe pressure"
        )

        material = st.selectbox("Material", ["DI", "MS", "HDPE"], 
    help="""
Material affects wave speed and surge pressure.

✅ Typical use:\n
• DI / MS → rigid pipelines (high pressure systems)  
• HDPE → flexible pipelines (less surge impact)
"""
)

    # ✅ MATERIAL DATA
    materials = {
        "DI": {"E": 1.7e11, "rho": 1000, "K": 2.2e9},
        "MS": {"E": 2.0e11, "rho": 1000, "K": 2.2e9},
        "HDPE": {"E": 1.0e9, "rho": 1000, "K": 2.2e9},
    }

    mat = materials[material]
    E, rho, K = mat["E"], mat["rho"], mat["K"]

    run = st.button("▶ Run Analysis")


    if run:

        # CALCULATIONS
        a = np.sqrt(K / (rho * (1 + (K * D) / (E * t_pipe))))
        deltaP = rho * L * V / t_stop
        deltaP_bar = deltaP / 1e5
        head = deltaP / (rho * 9.81)

        static_pressure = rho * 9.81 * H
        static_bar = static_pressure / 1e5

        total_pressure = deltaP_bar + static_bar
        ratio = total_pressure / allowable

        col1, col2 = st.columns([2, 1])

        # LEFT PANEL
        with col1:
            st.header("Results")

            st.write(f"Wave Speed: {a:.2f} m/s")
            st.write(f"Surge Pressure: {deltaP_bar:.2f} bar")
            st.write(f"Head Rise: {head:.2f} m")
            st.write(f"Static Pressure: {static_bar:.2f} bar")
            st.write(f"Total Pressure: {total_pressure:.2f} bar")

            st.header("Risk Assessment")

            if ratio > 1.5:
                st.error("🔴 Critical – Exceeds safe limit")
            elif ratio > 1.0:
                st.warning("🟡 High – Needs mitigation")
            elif ratio > 0.7:
                st.info("🟢 Moderate – Review recommended")
            else:
                st.success("✅ Safe")

        # RIGHT PANEL
        with col2:
            st.header("Transient Pressure vs Time")

            time = np.linspace(0, 2, 100)
            Transient_pressure = deltaP_bar * np.exp(-2 * time) * np.cos(10 * time)

            fig, ax = plt.subplots()
            ax.plot(time, Transient_pressure)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Transient_pressure (bar)")
            ax.grid()

            st.pyplot(fig)

    else:
        st.info("Click Run Analysis to generate graph")
# ---------------- IMPACT ----------------
st.header("Impact on System")

# 🔴 CRITICAL
if ratio > 1.5:
    st.error("🔴 Severe Impact on System")

    st.markdown("""
**Structural / Mechanical:**
• High risk of pipe rupture or burst  
• Failure of joints, fittings, and supports  

**Hydraulic:**
• Extreme pressure surge and oscillations  
• Possible column separation and vacuum formation  

**Operational:**
• System failure / shutdown likely  
• Immediate protection required  
""")

# 🟡 HIGH
elif ratio > 1.0:
    st.warning("🟡 High Impact on System")

    st.markdown("""
**Structural / Mechanical:**
• Significant stress in pipeline and components  
• Risk of leakage or damage  

**Hydraulic:**
• Noticeable pressure fluctuations  
• Risk of transient instability  

**Operational:**
• Reduced system reliability  
• Surge protection recommended  
""")

# 🟢 MODERATE
elif ratio > 0.7:
    st.info("🟢 Moderate Impact on System")

    st.markdown("""
**Structural / Mechanical:**
• Moderate stress levels in pipeline  

**Hydraulic:**
• Minor pressure fluctuations  

**Operational:**
• System generally stable  
• Review conditions for safety margin  
""")

# ✅ SAFE
else:
    st.success("✅ Minimal Impact on System")

    st.markdown("""
**Structural / Mechanical:**
• No significant stress on pipeline  

**Hydraulic:**
• Stable flow conditions  

**Operational:**
• System operating safely  
• No action required  
""")

# ==================================
# ✅ TAB 2 - THEORY
# ==================================
with tab2:

    # ----------------------------------
    # THEORY (ENHANCED)
    # ----------------------------------
    st.header("📚 Transient Theory (Detailed Explanation)")

    st.subheader("1. What is Transient Flow (Water Hammer)?")

    st.write(
        "Transient flow, commonly known as water hammer, occurs when there is a sudden change "
        "in flow conditions within a pipeline system such as rapid valve closure, pump shutdown, "
        "or sudden change in operating conditions."
    )

    st.write(
        "Under normal steady-state operation, flow velocity and pressure remain constant. "
        "However, when a disturbance occurs, the fluid experiences a rapid change in momentum, "
        "resulting in the formation of pressure waves."
    )

    st.write(
        "These pressure waves travel along the pipeline, reflect at boundaries such as valves, "
        "tanks, and reservoirs, and create oscillating pressure conditions within the system."
    )

    st.write(
        "👉 In simple terms: **Change in velocity → Momentum change → Pressure wave → System response**"
    )

    st.markdown("---")

    st.subheader("2. How Pressure Waves Travel")

    st.write(
        "When the flow is suddenly disturbed, a high-pressure wave is generated and travels along "
        "the pipeline at a finite speed called wave speed."
    )

    st.write(
        "The wave continues to travel until it reaches a boundary, where it reflects back into the system. "
        "This repeated reflection creates oscillations in pressure inside the pipe."
    )

    st.write(
        "Over time, these oscillations reduce due to friction and energy losses, bringing the system "
        "back to steady-state conditions."
    )

    st.markdown("---")

    st.subheader("3. Wave Speed (a)")

    st.latex(r"a = \sqrt{\frac{K}{\rho \left(1 + \frac{K D}{E t} \right)}}")

    st.write(
        "Wave speed represents how fast the pressure disturbance propagates through the pipeline."
    )

    st.write(
        "It depends on both fluid properties (compressibility) and pipe properties (elasticity and thickness)."
    )

    st.write(
        "👉 Higher stiffness (metal pipes) → higher wave speed → higher surge pressure\n"
        "👉 Flexible pipes (HDPE) → lower wave speed → reduced surge effect"
    )

    st.markdown("---")

    st.subheader("4. Surge Pressure Development")

    st.latex(r"\Delta P = \frac{\rho L V}{t}")

    st.write(
        "Surge pressure is generated due to the change in velocity of the fluid. "
        "The magnitude of surge pressure depends on pipeline length, flow velocity, stopping time and elevation difference."
    )

    st.write("👉 Higher velocity → higher momentum → higher surge pressure")
    st.write("👉 Short stopping time → rapid deceleration → higher surge")
    st.write("👉 Longer pipelines → greater pressure build-up")

    st.write("👉Transient Pressure = Surge Pressure = ΔP")
    st.write("👉Static Pressure = due to elevation")
    st.write("👉Total Pressure = Transient Pressure + Static Pressure")
    

    st.markdown("---")

            # ---------------- IMPACT ----------------
    st.header("How transient pressure (surge / water hammer) affects the pipeline, equipment, and operation of the system")

    st.subheader("Structural / Mechanical Impact")
    st.markdown("""
• Risk of pipe rupture or failure  
• High stresses in pipe walls, joints and fittings  
• Fatigue damage due to repeated transient events  
• Leakage or joint separation  
• Failure of supports or anchors  
""")

    st.subheader("Hydraulic Impact")
    st.markdown("""
• Pressure wave propagation in pipeline  
• Flow instability during transient events  
• Possible vacuum (negative pressure) conditions  
• Column separation in extreme cases  
• Pressure oscillations  
""")

    st.subheader("Operational Impact")
    st.markdown("""
• Reduced system reliability  
• Increased chances of shutdown  
• Difficulty maintaining steady flow  
• Reduced efficiency under transient conditions  
""")
   
    # ----------------------------------
    # FLOW STOPPING TIME (ENHANCED)
    # ----------------------------------
    st.subheader("⏱️ Flow Stopping Time (Valve Closure / Pump Trip)")

    st.write(
        "Flow stopping time is the time required for the fluid velocity to reduce from its operating value "
        "to zero due to valve closure or pump shutdown."
    )

    st.write(
        "This is one of the most critical parameters in transient analysis because it directly controls "
        "the magnitude of pressure surge generated in the system."
    )

    st.markdown("---")

    st.subheader("1. Why is Flow Stopping Time Important?")

    st.write(
        "When flow is stopped suddenly, the fluid momentum is converted into pressure energy almost instantly, "
        "resulting in a sharp rise in pressure."
    )

    st.write(
        "If the stopping process is gradual, the energy is released slowly, reducing the magnitude of surge pressure."
    )

    st.markdown("""
👉 Short time (fast closure) → **Very high surge pressure**  
👉 Long time (slow closure) → **Reduced and controlled pressure rise**  
""")

    st.markdown("---")

    st.subheader("2. Physical Understanding")

    st.write(
        "Fluid flowing inside a pipeline possesses kinetic energy. When the flow is interrupted, "
        "this energy needs to be dissipated."
    )

    st.write(
        "Rapid stopping forces the energy to convert into pressure instantly, creating a strong pressure wave. "
        "Gradual stopping distributes this energy over time, reducing peak pressure."
    )

    st.markdown("---")

    st.subheader("3. Critical Time Concept")

    st.latex(r"t_c = \frac{2L}{a}")

    st.write(
        "Critical time represents the time taken for a pressure wave to travel to the end of the pipeline "
        "and return back."
    )

    st.markdown("""
• If stopping time < critical time → rapid event (high surge)  
• If stopping time > critical time → gradual event (lower surge)  
""")

    st.markdown("---")

    st.subheader("4. Practical Engineering Cases")

    st.markdown("""
• Manual valve operation → usually slower (less critical)  
• Motorized / automatic valves → faster, requires control  
• Pump trip (power failure) → very fast, often worst-case condition  
""")

    st.markdown("---")

    st.subheader("5. Methods to Control Stopping Time")

    st.markdown("""
• Use slow-closing valves  
• Use actuators with controlled closing speed  
• Provide VFD for controlled pump shutdown  
• Install surge protection if fast closure cannot be avoided  
""")

    st.markdown("---")

    st.subheader("6. Engineering Insight")


    # ----------------------------------
    # DESIGN GUIDELINES
    # ----------------------------------
    st.header("📘 Design Guidelines (HI / BS EN / SSG)")

    st.info(
        "Based on general engineering practices from Hydraulic Institute (HI), "
        "BS EN standards, and SSG (UK water industry guidance)."
    )

    st.subheader("Transient Pressure Limits")

    st.markdown("""
• Transient pressure shall not exceed allowable pipe pressure  
• Consider both positive surge and negative pressure  
• Maximum pressure = steady pressure + transient pressure  
• Safety margin must be included in design  
""")

    st.subheader("Control of Sudden Flow Changes")

    st.markdown("""
• Sudden velocity changes must be avoided  
• Rapid valve closure should be minimized  
• Pump start/stop should be controlled  
• Slower closure → lower surge pressure  
""")

    st.subheader("Surge Protection Requirements")

    st.markdown("""
• Surge protection devices shall be used if pressure exceeds limits  
• Required for long pipelines and high head systems  
• Typical devices include:  
    • Surge tank  
    • Air vessel  
    • Pressure relief valve  
    • Surge anticipation valve  
""")

    st.subheader("Air & Vacuum Protection")

    st.markdown("""
• Negative pressure conditions must be prevented  
• Air valves shall be installed at high points  
• Vacuum breakers required for long pipelines  
• Prevent column separation and pipe collapse  
""")

    st.subheader("Check Valve (NRV) Selection")

    st.markdown("""
• Sudden valve closure must be avoided  
• Non-slam check valves are recommended  
• Reduce reverse flow impact and pressure spikes  
""")

    st.subheader("Velocity Control")

    st.markdown("""
• Flow velocity should be controlled within limits  
• Recommended range: 0.7 – 2.5 m/s  
• Higher velocity → higher surge pressure  
• Lower velocity improves system safety  
""")

    st.subheader("Transient Design Consideration")

    st.markdown("""
• Transient conditions must be considered in design  
• Steady-state analysis alone is not sufficient  
• Critical cases to evaluate:  
    • Pump trip  
    • Valve closure  
    • Power failure  
""")
# ----------------------------------
# FOOTER
# ----------------------------------
st.markdown("---")
st.caption("Engineering tool for preliminary transient analysis")

    # (rest of your content continues exactly same… no changes)
