import streamlit as st
import math
import pandas as pd

# 페이지 설정
st.set_page_config(page_title="비행기 이륙 시뮬레이터", layout="wide")
st.title("✈️ 비행기 이륙 시뮬레이터 (Streamlit Cloud 버전)")
st.markdown("""
스페이스바 대신 **'🚀 가속하기' 버튼**을 눌러 비행기를 가속시켜보세요.  
속도, 가속도, 공기저항, 양력 변화를 실시간으로 볼 수 있습니다.
""")

# 세션 상태 초기화
if "velocity" not in st.session_state:
    st.session_state.velocity = 0.0
if "time" not in st.session_state:
    st.session_state.time = 0.0
if "data" not in st.session_state:
    st.session_state.data = []
if "running" not in st.session_state:
    st.session_state.running = False

# === 입력값 ===
col1, col2 = st.columns(2)
with col1:
    mass = st.number_input("비행기 질량 (kg)", 1000.0, 500000.0, 70000.0)
    wing_area = st.number_input("날개 면적 (m²)", 10.0, 500.0, 124.6)
    Cl = st.number_input("양력계수 (Cl)", 0.1, 3.0, 1.5, 0.1)
    Cd = st.number_input("공기저항계수 (Cd)", 0.01, 0.2, 0.03, 0.005)
with col2:
    P = st.number_input("기압 (Pa)", 50000.0, 120000.0, 101325.0)
    T_C = st.number_input("온도 (°C)", -50.0, 50.0, 15.0)
    thrust = st.number_input("엔진 추력 (N)", 1000.0, 1000000.0, 200000.0)
    lift_margin = st.number_input("이륙 여유 비율", 1.0, 2.0, 1.1)

# === 상수 및 계산 ===
R = 287.05
g = 9.81
T = T_C + 273.15
rho = P / (R * T)
W = mass * g
v_takeoff = math.sqrt((2 * W) / (rho * wing_area * Cl))
st.metric("이륙 최소 속도 (m/s)", f"{v_takeoff:.2f}")
st.write("---")

# === 시뮬레이션 ===
dt = 0.1  # 0.1초 간격

if st.button("🚀 가속하기"):
    # 현재 상태 가져오기
    v = st.session_state.velocity
    t = st.session_state.time

    # 물리 계산
    drag = 0.5 * rho * v**2 * wing_area * Cd
    F_net = thrust - drag
    a = F_net / mass
    v += a * dt
    t += dt
    lift = 0.5 * rho * v**2 * wing_area * Cl

    # 데이터 저장
    st.session_state.data.append({
        "time": t,
        "velocity": v,
        "acceleration": a,
        "drag": drag,
        "lift": lift,
        "weight": W
    })

    # 상태 업데이트
    st.session_state.velocity = v
    st.session_state.time = t

# === 데이터 시각화 ===
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)

    st.subheader("📈 비행 데이터 그래프")
    col_a, col_b = st.columns(2)

    with col_a:
        st.line_chart(df.set_index("time")[["velocity"]], height=250, use_container_width=True)
        st.line_chart(df.set_index("time")[["acceleration"]], height=250, use_container_width=True)

    with col_b:
        st.line_chart(df.set_index("time")[["drag"]], height=250, use_container_width=True)
        lift_df = df[["time", "lift"]].copy()
        lift_df["weight"] = W
        st.line_chart(lift_df.set_index("time"), height=250, use_container_width=True)

    if st.session_state.velocity >= v_takeoff * lift_margin:
        st.success("🛫 충분한 양력이 발생했습니다! 비행기가 이륙합니다.")
    else:
        st.warning("아직 이륙 속도에 도달하지 못했습니다.")

# === 리셋 버튼 ===
if st.button("🔁 초기화"):
    st.session_state.velocity = 0.0
    st.session_state.time = 0.0
    st.session_state.data = []
    st.rerun()
