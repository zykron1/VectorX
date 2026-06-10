from math import sin, cos
from thrustCurve import ThrustCurve

# Params
mass = 0.6
inertia = 1.0
cm_tvc = 0.1
gimbal_x_rad = sin(0.0175)  # 1 degree
gimbal_y_rad = sin(0.0698)  # 4 degrees
gravity = 9.81
dt = 0.01
time = 120.0

# Initial state
pos_x, pos_y, pos_z = 0.0, 0.0, 0.0
vel_x, vel_y, vel_z = 0.0, 0.0, 0.0

curve = ThrustCurve("F15.eng")
apogee = 0.0

print(f"{'t':>6} {'pos_x':>10} {'pos_y':>10} {'pos_z':>10} {'vel_z':>10} {'thrust':>10}")
print("-" * 66)

for i in range(int(time / dt)):
    t = i * dt
    thrust = curve.get_thrust(int(t * 1000))

    # Force in body frame (fixed gimbal, small angle: body ≈ world)
    f_world_x = gimbal_x_rad * thrust
    f_world_y = gimbal_y_rad * thrust
    f_world_z = thrust - gravity * mass

    a_x = f_world_x / mass
    a_y = f_world_y / mass
    a_z = f_world_z / mass

    vel_x += a_x * dt
    vel_y += a_y * dt
    vel_z += a_z * dt
    pos_x += vel_x * dt
    pos_y += vel_y * dt
    pos_z += vel_z * dt

    if pos_z > apogee:
        apogee = pos_z

    if pos_z < -1 and t > 1.0:
        print(f"\nLanded at t={t:.2f}s")
        break

    if i % 100 == 0:
        print(f"{t:>6.2f} {pos_x:>10.2f} {pos_y:>10.2f} {pos_z:>10.2f} {vel_z:>10.2f} {thrust:>10.2f}")

print(f"\nApogee: {apogee:.2f}m")
print(f"Final position: x={pos_x:.2f}m  y={pos_y:.2f}m")
