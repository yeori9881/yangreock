import streamlit as st
import math
import pandas as pd
import numpy as np

# 페이지 설정
st.set_page_config(page_title="비행기 이륙 시뮬레이터", layout="wide")
st.title("✈️ 비행기 이륙 시뮬레이터 (자동 가속 버전)")
st.markdown("""
비행기의 질량, 날개 면적, 기압, 온도 등을 입력하면  
비행기가 **자동으로 이륙 속도의 1.5배까지 가속**하는 과정을 시뮬레이션합니다.  
그래프를 통해 속도, 가속도, 고도, 양력·중력의 변화를 볼 수 있습니다.
""")

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
    Cl_takeoff = st.number_input("이륙 여유 배수 (최종속도/이륙속도)", 1.0, 3.0, 1.5, 0.1)

# === 상수 ===
R = 287.05
g = 9.81
T = T_C + 273.15
rho = P / (R * T)
W = mass * g

# === 이륙 최소 속도 ===
v_takeoff = math.sqrt((2 * W) / (rho * wing_area * Cl))
v_target = v_takeoff * Cl_takeoff
st.metric("이륙 최소 속도 (m/s)", f"{v_takeoff:.2f}")
st.metric("시뮬레이션 최대 속도 (m/s)", f"{v_target:.2f}")
st.write("---")

# === 시뮬레이션 ===
dt = 0.1  # 시간 간격 (초)
time_list, velocity_list, accel_list, lift_list, weight_list, altitude_list = [], [], [], [], [], []

velocity = 0.0
altitude = 0.0

while velocity < v_target:
    drag = 0.5 * rho * velocity**2 * wing_area * Cd
    F_net = thrust - drag
    a = F_net / mass
    velocity += a * dt
    lift = 0.5 * rho * velocity**2 * wing_area * Cl
    if lift > W:  # 양력이 중력보다 크면 상승 시작
        vertical_accel = (lift - W) / mass
        altitude += vertical_accel * dt * dt * 0.5 + velocity * 0.1  # 단순 상승 모델
    else:
        vertical_accel = 0.0
        altitude += 0

    time_list.append(len(time_list) * dt)
    velocity_list.append(velocity)
    accel_list.append(a)
    lift_list.append(lift)
    weight_list.append(W)
    altitude_list.append(altitude)

# === DataFrame ===
df = pd.DataFrame({
    "Time (s)": time_list,
    "Velocity (m/s)": velocity_list,
    "Acceleration (m/s²)": accel_list,
    "Lift (N)": lift_list,
    "Weight (N)": weight_list,
    "Altitude (m)": altitude_list
})

# === 그래프 출력 ===
st.subheader("📊 시뮬레이션 결과 그래프")

col_a, col_b = st.columns(2)
with col_a:
    st.line_chart(df.set_index("Time (s)")[["Velocity (m/s)"]], height=250, use_container_width=True)
    st.line_chart(df.set_index("Time (s)")[["Acceleration (m/s²)"]], height=250, use_container_width=True)
with col_b:
    st.line_chart(df.set_index("Time (s)")[["Altitude (m)"]], height=250, use_container_width=True)
    st.line_chart(df.set_index("Time (s)")[["Lift (N)", "Weight (N)"]], height=250, use_container_width=True)

# === 최종 메시지 ===
if df["Lift (N)"].iloc[-1] > W:
    st.success("🛫 시뮬레이션 완료 — 충분한 양력이 발생했습니다! 비행기가 이륙합니다.")
else:
    st.warning("⚠️ 시뮬레이션 완료 — 아직 양력이 중력보다 작습니다. 이륙 불가.")
