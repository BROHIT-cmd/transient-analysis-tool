import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import os

# ----------------------------------
# PAGE CONFIG
# ----------------------------------
st.set_page_config(layout="wide")

# ----------------------------------
# HEADER
# ----------------------------------
col1, col2 = st.columns([6, 1])

with col1:
    st.title("Pipeline Transient Analysis & Design Tool")

with col2:
    logo = os.path.join("images", "logo.png")
    if os.path.exists(logo):
        st.image(logo, width=120)

st.markdown("---")

# ----------------------------------
# TABS
# ----------------------------------
tab1, tab2 = st.tabs(["🔧 Analysis Tool", "📚 Theory & Guidelines"])

# ==================================
# ✅ TAB 1 - ANALYSIS
# ==================================
with tab1:

    # INPUTS
    st.subheader("Input Data")

    colA, colB = st.columns(2)

    with colA:
        L = st.number_input("Pipe Length (m)", value=5.0, help="Total pipeline length")
        D = st.number_input("Pipe Diameter (mm)", value=25.0, help="Internal pipe diameter") / 1000
        t_pipe = st.number_input("Pipe Thickness (mm)", value=2.0, help="Pipe wall thickness") / 1000

    with colB:
        V = st.number_input("Flow Velocity (m/s)", value=2.0, help="Higher velocity increases surge pressure")
        t_stop = st.number_input("Flow Stopping Time (sec)", value=3.0, help="Valve closure or pump trip time")
        allowable = st.number_input("Allowable Pressure (bar)", value=10.0, help="Maximum safe pressure")

    # MATERIAL
    materials = {
        "DI": {"E": 1.7e11, "rho": 1000, "K": 2.2e9},
        "MS": {"E": 2.0e11, "rho": 1000, "K": 2.2e9},
        "HDPE": {"E": 1.0e9, "rho": 1000, "K": 2.2e9},
    }

    material = st.selectbox("Material", list(materials.keys()))
    mat = materials[material]
    E, rho, K = mat["E"], mat["rho"], mat["K"]

    run = st.button("▶ Run Analysis")

    # ----------------------------------
    # CALCULATION + RESULTS
    # ----------------------------------
    if run:

        # CALCULATIONS
        a = np.sqrt(K / (rho * (1 + (K * D) / (E * t_pipe))))
        deltaP = rho * L * V / t_stop
        deltaP_bar = deltaP / 1e5
        head = deltaP / (rho * 9.81)

        ratio = deltaP_bar / allowable

        col1, col2 = st.columns([2, 1])

        # ---------------- LEFT PANEL ----------------
        with col1:
            st.header("Results")

            st.write(f"Wave Speed: {a:.2f} m/s")
            st.write(f"Surge Pressure: {deltaP_bar:.2f} bar")
            st.write(f"Head Rise: {head:.2f} m")

            # RISK
            st.header("Risk Assessment")

            if ratio > 1.5:
                st.error("🔴 Critical – Exceeds safe limit")
            elif ratio > 1.0:
                st.warning("🟡 High – Needs mitigation")
            elif ratio > 0.7:
                st.info("🟢 Moderate – Review recommended")
            else:
                st.success("✅ Safe")

            # ---------------- IMPACT ----------------
            st.header("Impact on System")

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

            # ---------------- RECOMMENDATIONS ----------------
            st.header("Recommendations")

            if ratio > 1.0:
                st.write("✅ Provide surge tank or air vessel")
                st.write("✅ Install pressure relief valve")
                st.write("✅ Increase stopping time (slow operation)")
            elif ratio > 0.7:
                st.write("✅ Review transient conditions")
                st.write("✅ Consider protection if system is critical")
            else:
                st.write("✅ No action required")

        # ---------------- RIGHT PANEL ----------------
        with col2:
            st.header("Pressure vs Time")

            time = np.linspace(0, 2, 100)
            pressure = deltaP_bar * np.exp(-2 * time) * np.cos(10 * time)

            fig, ax = plt.subplots()
            ax.plot(time, pressure)
            ax.set_xlabel("Time (s)")
            ax.set_ylabel("Pressure (bar)")
            ax.grid()

            st.pyplot(fig)

            st.subheader("📘 Graph Interpretation")

            st.markdown("""
• The curve represents pressure variation due to a transient event (valve closure or pump trip)  
• Oscillations indicate pressure waves traveling in the pipeline  
• Peaks represent high surge pressure  
• Troughs indicate low pressure or vacuum conditions  
• Amplitude decreases due to damping effects  
""")

            st.info(
                "This is a simplified representation of transient response. Actual systems may show more complex behavior."
            )

    else:
        st.info("Click Run Analysis to generate graph")


# ==================================
# ✅ TAB 2 - THEORY
# ==================================
with tab2:

    st.header("📚 Transient Theory (Detailed Explanation)")

    # ----------------------------------
    # 1. INTRODUCTION
    # ----------------------------------
    st.subheader("1. What is Transient Flow (Water Hammer)?")

    st.write(
        "Transient flow, commonly known as water hammer, occurs when there is a sudden change "
        "in flow conditions within a pipeline system. This change may happen due to valve closure, "
        "pump shutdown, or any rapid variation in velocity."
    )

    st.write(
        "When flowing water is suddenly slowed down or stopped, the momentum of the fluid is converted "
        "into pressure energy. This results in a rapid rise in pressure, creating a wave that travels "
        "through the pipeline."
    )

    st.write("👉 In simple terms: **Change in velocity → Pressure wave → System response**")

    st.markdown("---")

    # ----------------------------------
    # 2. PHYSICAL MECHANISM
    # ----------------------------------
    st.subheader("2. Physical Mechanism")

    st.write(
        "Fluid flowing inside a pipe possesses mass and velocity, and therefore momentum. "
        "When the flow is reduced, this momentum does not disappear instantly. Instead, it gets "
        "converted into pressure energy, causing a pressure rise."
    )

    st.write(
        "This pressure rise travels in the form of a wave along the pipeline. The wave reflects at "
        "boundaries such as closed valves, reservoirs, or pipe ends, creating oscillations."
    )

    st.write(
        "Similarly, if flow drops rapidly (for example during pump trip), pressure may fall below "
        "atmospheric levels, creating vacuum conditions."
    )

    st.markdown("---")

    # ----------------------------------
    # 3. WAVE SPEED
    # ----------------------------------
    st.subheader("3. Wave Speed (a)")

    st.latex(r"a = \sqrt{\frac{K}{\rho \left(1 + \frac{K D}{E t} \right)}}")

    st.write("Where:")
    st.write("• a = Pressure wave speed (m/s)")
    st.write("• K = Bulk modulus of fluid (compressibility)")
    st.write("• ρ = Fluid density")
    st.write("• E = Pipe material elasticity")
    st.write("• D = Pipe diameter")
    st.write("• t = Pipe thickness")

    st.write(
        "Wave speed determines how fast the pressure disturbance travels through the pipeline."
    )

    st.write(
        "👉 Stiffer pipes and less compressible fluids lead to higher wave speed and higher surge pressure."
    )

    st.markdown("---")

    # ----------------------------------
    # 4. SURGE PRESSURE
    # ----------------------------------
    st.subheader("4. Surge Pressure (Realistic Condition)")

    st.latex(r"\Delta P = \frac{\rho L V}{t}")

    st.write("Where:")
    st.write("• ΔP = Surge pressure")
    st.write("• L = Pipe length")
    st.write("• V = Flow velocity")
    st.write("• t = Flow stopping time")

    st.write(
        "This equation represents a more realistic condition where flow is reduced over a finite time period."
    )
    st.write("* Faster stopping time → higher surge pressure")
    st.write("* Longer pipeline → higher pressure")
    st.write("* Higher velocity → higher surge")
    
    
    st.markdown("---")

    # ----------------------------------
    # 5. TYPES OF TRANSIENT EVENTS
    # ----------------------------------
    st.subheader("5. Common Causes of Transients")

    st.write("• Rapid valve closure")
    st.write("• Pump start or sudden shutdown")
    st.write("• Power failure at pumping stations")
    st.write("• Sudden change in demand conditions")

    st.markdown("---")

    # ----------------------------------
    # 6. EFFECTS OF TRANSIENTS
    # ----------------------------------
    st.subheader("6. Effects on Pipeline System")

    st.write(
        "Transient events can lead to pressure rise, pressure drop, oscillations, "
        "and unstable system behaviour."
    )

    st.write(
        "These effects may cause structural damage, operational difficulties, and "
        "reduced system life."
    )

    st.markdown("---")

    # ----------------------------------
    # 7. HOW TO CONTROL TRANSIENTS
    # ----------------------------------
    st.subheader("7. Methods to Control Transients")

    st.write("• Increase valve closing time (slow operation)")
    st.write("• Provide surge tanks or air vessels")
    st.write("• Install pressure relief valves")
    st.write("• Use non-slam check valves")
    st.write("• Maintain proper system velocity")

    st.markdown("---")

    # ----------------------------------
    # 8. ENGINEERING OBJECTIVE
    # ----------------------------------
    st.subheader("8. Engineering Objective")

    st.write(
        "The main goal of transient analysis is to ensure that the maximum pressure during any "
        "operating condition remains within the allowable limits of the pipeline system."
    )

    st.write(
        "This is achieved by combining proper system design, controlled operation, and use of "
        "surge protection devices."
    )

    st.success("✅ Design Goal: Keep transient pressure within safe limits under all conditions")



st.markdown("---")

# ----------------------------------
# WHY IT IS IMPORTANT
# ----------------------------------
st.subheader("1. Why is Flow Stopping Time Important?")

st.write(
    "Flow stopping time directly controls the magnitude of transient pressure. "
    "A rapid reduction in flow causes a sudden change in momentum, resulting in high pressure surge."
)

st.write(
    "👉 Short time (fast closure) → large surge pressure\n"
    "👉 Long time (slow closure) → smaller surge pressure"
)

st.markdown("---")

# ----------------------------------
# PHYSICAL UNDERSTANDING
# ----------------------------------
st.subheader("2. Physical Understanding")

st.write(
    "Fluid flowing in a pipe has momentum. When flow is stopped, this momentum must be dissipated. "
    "If the stopping occurs quickly, the energy converts into pressure almost instantly, "
    "creating a high pressure wave."
)

st.write(
    "If the stopping is gradual, the energy is released slowly, resulting in a lower pressure rise."
)

st.markdown("---")

# ----------------------------------
# CRITICAL TIME CONCEPT
# ----------------------------------
st.subheader("3. Critical Time Concept")

st.write(
    "In transient theory, there is a concept of critical time based on wave travel in the pipeline."
)

st.latex(r"t_c = \frac{2L}{a}")

st.write(
    "Where:\n"
    "• t_c = Critical time (sec)\n"
    "• L = Pipe length (m)\n"
    "• a = Wave speed (m/s)"
)

st.write(
    "👉 If closure time is LESS than critical time → high surge (rapid event)\n"
    "👉 If closure time is GREATER than critical time → reduced surge (gradual event)"
)

st.markdown("---")

# ----------------------------------
# PRACTICAL RANGE
# ----------------------------------
st.subheader("4. Practical Engineering Values")

st.write(
    "In real systems:\n"
    "• Manual valves → typically slower closure (higher time)\n"
    "• Automatic valves → faster closure, requires control\n"
    "• Pump trip → often very fast (critical transient condition)"
)

st.write(
    "Pump trip due to power failure is one of the most severe transient cases because "
    "flow reduction occurs almost instantly."
)

st.markdown("---")

# ----------------------------------
# ENGINEERING CONTROL
# ----------------------------------
st.subheader("5. How Engineers Control Stopping Time")

st.write(
    "Engineers manage stopping time to control surge pressure using:"
)

st.write(
    "• Actuated valves with controlled closing speed\n"
    "• Variable frequency drives (VFD) for controlled pump shutdown\n"
    "• Surge control devices (if fast closure cannot be avoided)"
)

st.markdown("---")

# ----------------------------------
# DESIGN INSIGHT
# ----------------------------------
st.subheader("6. Key Design Insight")

st.write(
    "Flow stopping time is one of the most effective parameters engineers can control to reduce surge pressure. "
    "Increasing closure time is often the first and simplest method to improve system safety."
)

st.success(
    "✅ Design Rule: Always aim for controlled and gradual flow reduction to minimize transient effects."
)

st.markdown("---")

# ----------------------------------
# DESIGN GUIDELINES
# ----------------------------------
st.header("📘 Design Guidelines (HI / BS EN / SSG)")

st.info(
    "Based on general engineering practices from Hydraulic Institute (HI), "
    "BS EN standards, and SSG (UK water industry guidance)."
)

# -------------------------------
# TRANSIENT PRESSURE LIMITS
# -------------------------------
st.subheader("Transient Pressure Limits")

st.markdown("""
• Transient pressure shall not exceed allowable pipe pressure  
• Consider both positive surge and negative pressure  
• Maximum pressure = steady pressure + transient pressure  
• Safety margin must be included in design  
""")

# -------------------------------
# CONTROL OF FLOW CHANGE
# -------------------------------
st.subheader("Control of Sudden Flow Changes")

st.markdown("""
• Sudden velocity changes must be avoided  
• Rapid valve closure should be minimized  
• Pump start/stop should be controlled  
• Slower closure → lower surge pressure  
""")

# -------------------------------
# SURGE PROTECTION
# -------------------------------
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

# -------------------------------
# AIR & VACUUM PROTECTION
# -------------------------------
st.subheader("Air & Vacuum Protection")

st.markdown("""
• Negative pressure conditions must be prevented  
• Air valves shall be installed at high points  
• Vacuum breakers required for long pipelines  
• Prevent column separation and pipe collapse  
""")

# -------------------------------
# CHECK VALVE SELECTION
# -------------------------------
st.subheader("Check Valve (NRV) Selection")

st.markdown("""
• Sudden valve closure must be avoided  
• Non-slam check valves are recommended  
• Reduce reverse flow impact and pressure spikes  
""")

# -------------------------------
# VELOCITY CONTROL
# -------------------------------
st.subheader("Velocity Control")

st.markdown("""
• Flow velocity should be controlled within limits  
• Recommended range: 0.7 – 2.5 m/s  
• Higher velocity → higher surge pressure  
• Lower velocity improves system safety  
""")

# -------------------------------
# TRANSIENT DESIGN CONSIDERATION
# -------------------------------
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
