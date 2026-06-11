from __future__ import annotations
from typing import List, Tuple
from vector import Vector3, Vector2
from rocket import Rocket
from thrustCurve import ThrustCurve
from math import sin, cos, sqrt, atan2, asin, degrees
from collections import deque
import random
import csv

class Quaternion:
	def __init__(self, w: float = 1.0, x: float = 0.0, y:float = 0.0, z: float = 0.0) -> None:
		self.w: float = w
		self.x: float = x
		self.y: float = y
		self.z: float = z

	def normalize(self) -> "Quaternion":
		n = sqrt(self.w**2 + self.x**2 + self.y**2 + self.z**2)
		return Quaternion(self.w/n, self.x/n, self.y/n, self.z/n)

	def rotate(self, v: Vector3) -> Vector3:
		qv = Quaternion(0, v.x, v.y, v.z)
		q_conj = Quaternion(self.w, -self.x, -self.y, -self.z)
		r = self._mul(qv)._mul(q_conj)
		return Vector3(r.x, r.y, r.z)

	def _mul(self, other: "Quaternion") -> "Quaternion":
		return Quaternion(
			self.w*other.w - self.x*other.x - self.y*other.y - self.z*other.z,
			self.w*other.x + self.x*other.w + self.y*other.z - self.z*other.y,
			self.w*other.y - self.x*other.z + self.y*other.w + self.z*other.x,
			self.w*other.z + self.x*other.y - self.y*other.x + self.z*other.w,
		)

	def integrate(self, omega: Vector3, dt: float) -> "Quaternion":
		omega_quat = Quaternion(0, omega.x, omega.y, omega.z)
		q_dot = self._mul(omega_quat)
		return Quaternion(
			self.w + 0.5 * q_dot.w * dt,
			self.x + 0.5 * q_dot.x * dt,
			self.y + 0.5 * q_dot.y * dt,
			self.z + 0.5 * q_dot.z * dt,
		).normalize()

	def to_euler(self) -> Tuple[float, float, float]:
		sinr_cosp = 2 * (self.w * self.x + self.y * self.z)
		cosr_cosp = 1 - 2 * (self.x * self.x + self.y * self.y)
		roll = atan2(sinr_cosp, cosr_cosp)

		sinp = 2 * (self.w * self.y - self.z * self.x)
		if abs(sinp) >= 1:
			pitch = (3.141592653589793 / 2) * (1 if sinp > 0 else -1)
		else:
			pitch = asin(sinp)

		siny_cosp = 2 * (self.w * self.z + self.x * self.y)
		cosy_cosp = 1 - 2 * (self.y * self.y + self.z * self.z)
		yaw = atan2(siny_cosp, cosy_cosp)

		return (
			degrees(pitch),
			degrees(roll),
			degrees(yaw)
		)

class Sim:
	def __init__(self, curve: str, dt: float) -> None:
		self.dt = dt
		self.thrustCurve = ThrustCurve(curve)
		self.position = Vector3()
		self.velocity = Vector3()
		self.acceleration = Vector3()
		self.orientation = Quaternion() # WORLD FRAME
		self.orientalVelocity = Vector3() # BODY FRAME
		self.orientalAcceleration = Vector3() # BODY FRAME
		self.mass = 1
		self.motor_mass = 0.095
		self.motor_mass_end = 0.095 * (1 - 0.06) # 6% loss
		self.motor_mass_initial = self.motor_mass
		self.thrust_steps = max(1, round(3.45 / dt))
		self.motor_mass_step = (self.motor_mass_initial - self.motor_mass_end) / self.thrust_steps
		self.inertia_initial = 0.009365
		self.inertia = self.inertia_initial
		self.cm_tvc = 0.335
		self.Cd = 1.2
		self.A = 0.00456
		self.wind_noise = 0.05
		self.rocket = Rocket(
			0.4, 0.1, 0.1,
			0.4, 0.1, 0.1,
		)
		self.gimbal_delay_steps = max(1, round(0.03 / self.dt))
		self.gimbal_buffer = deque([Vector2(0.001, 0.001) for _ in range(self.gimbal_delay_steps)])
		self.gimbal_query_interval = max(1, round(0.01 / self.dt))
		self.last_gimbal_cmd = Vector2(0.001, 0.001)

	def compute_drag(self, rho: float = 1.225) -> Vector3:
		v = self.velocity.z
	
		drag = 0.5 * rho * abs(v) * v * self.Cd * self.A
	
		return Vector3(0, 0, -drag)

	def simulate(self, time: float, filename: str) -> Tuple[List[float], List[float], List[float], List[Quaternion]]:
		x = []
		y = []
		z = []
		q = []
		xbias = random.randint(-10, 10) / 10;
		ybias = random.randint(-10, 10) / 10;
		apogee = 0
		for i in range(int(time / self.dt)):
			if i % self.gimbal_query_interval == 0:
				gimbal_cmd = self.rocket.guide(
					self.dt*self.gimbal_query_interval,
					self.orientation.to_euler(),
					self.acceleration
				)
				gimbal_cmd.x += xbias
				gimbal_cmd.y += ybias
				gimbal_cmd = gimbal_cmd.to_radians()
				self.last_gimbal_cmd = gimbal_cmd
			else:
				gimbal_cmd = self.last_gimbal_cmd
			
			self.gimbal_buffer.append(gimbal_cmd)
			gimbal = self.gimbal_buffer.popleft()
	
			thrust = self.thrustCurve.get_thrust(int((i * self.dt) * 1000))
			if thrust > 0:
				self.motor_mass -= self.motor_mass_step
			self.mass = 1.0 + self.motor_mass
			self.inertia = self.inertia_initial * (self.mass / (1.0 + self.motor_mass_initial))

			#thrust = 15.0
			force_body = Vector3(
				sin(gimbal.x) * thrust, # lateral X (pitch)
				sin(gimbal.y) * thrust,	# lateral Y (yaw)
				cos(gimbal.x) * cos(gimbal.y) * thrust # axial
			)
			force_world = self.orientation.rotate(force_body) # BODY FRAME -> WORLD FRAME
			force_world += Vector3(0, 0, -9.81 * self.mass) # gravity in WORLD FRAME
			force_world += self.compute_drag()
			self.acceleration = force_world / self.mass
			# due to floating point errors+integration timestep it's -1 not 0
			if self.position.z < -1:
				print("Highest recorded point in flight: ", apogee)
				self.saveToCSV(x,y,z,q, filename)
				return x, y, z, q
			self.velocity += self.acceleration * self.dt
			self.position += self.velocity * self.dt
			print(f"t={i} alt={self.position.z} orientation={self.orientation.to_euler()} gimbal={gimbal}")
			if self.position.z > apogee:
				apogee = self.position.z
			torque_body = Vector3(
				force_body.y * self.cm_tvc + random.uniform(-self.wind_noise, self.wind_noise),
				force_body.x * self.cm_tvc + random.uniform(-self.wind_noise, self.wind_noise),
				0.0
			)
			
			self.orientalAcceleration = torque_body / self.inertia
			self.orientalVelocity += self.orientalAcceleration * self.dt
			self.orientation = self.orientation.integrate(self.orientalVelocity, self.dt) # BODY FRAME omega
			x.append(self.position.x)
			y.append(self.position.y)
			z.append(self.position.z)
			q.append(self.orientation)

		self.saveToCSV(x,y,z,q, filename)
		return x, y, z, q

	def saveToCSV(self, x: List[float], y: List[float], z: List[float], q: List[Quaternion], filename) -> None:
		with open(filename, "w", newline="") as f:
			writer = csv.writer(f)

			# header
			writer.writerow(["x", "y", "z", "qw", "qx", "qy", "qz"])
			for i in range(len(x)):
				quat = q[i]
				writer.writerow([
					x[i],
					y[i],
					z[i],
					quat.w,
					quat.x,
					quat.y,
					quat.z
				])
