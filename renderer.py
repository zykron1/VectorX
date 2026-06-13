import matplotlib.pyplot as plt
import matplotlib.animation as animation
from sim import Quaternion
from vector import Vector3
import numpy as np
import pandas as pd

class Renderer:
	def __init__(self, filename: str) -> None:
		dataframe = pd.read_csv(filename)
		self.x = dataframe["x"].values
		self.y = dataframe["y"].values
		self.z = dataframe["z"].values
		self.xg = dataframe["xg"].values
		self.yg = dataframe["yg"].values
		self.orientations = [
			Quaternion(qw, qx, qy, qz)
			for qw, qx, qy, qz in zip(
				dataframe["qw"],
				dataframe["qx"],
				dataframe["qy"],
				dataframe["qz"]
			)
		]

	def trajectory(self) -> None:
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		ax.plot(self.x, self.y, self.z)
		ax.set_xlabel("X")
		ax.set_ylabel("Y")
		ax.set_zlabel("Z")

	def animate(self, dt: float, interval: int = 50) -> animation.FuncAnimation:
		plt.style.use('dark_background')
		steps = max(1, round(interval / (dt * 1000)))
		has_orientation = self.orientations is not None and len(self.orientations) > 0
		fig = plt.figure(figsize=(12, 6) if has_orientation else (6, 6))
		ax = fig.add_subplot(121 if has_orientation else 111, projection='3d')
		mid_x = (max(self.x) + min(self.x)) / 2
		mid_y = (max(self.y) + min(self.y)) / 2
		mid_z = (max(self.z) + min(self.z)) / 2
		max_range = max(
			max(self.x) - min(self.x),
			max(self.y) - min(self.y),
			max(self.z) - min(self.z)
		) / 2 + 0.1
		
		ax.set_xlim(mid_x - max_range, mid_x + max_range)
		ax.set_ylim(mid_y - max_range, mid_y + max_range)
		ax.set_zlim(mid_z - max_range, mid_z + max_range)
		ax.set_title("Flight Path")
		line, = ax.plot([], [], [])

		# Orientation
		if has_orientation:
			ax_r = fig.add_subplot(122, projection='3d')
			ax_r.set_xlim(-0.4, 0.4)
			ax_r.set_ylim(-0.4, 0.4)
			ax_r.set_zlim(-0.4, 0.4)
			ax_r.set_xlabel("X"); ax_r.set_ylabel("Y"); ax_r.set_zlabel("Z")
			rl = 0.3  # rocket length
			rr = 0.05  # rocket radius
			body_pts = np.array([[0, 0, -rl/2], [0, 0, rl/2]])
			fin_pts = [
				np.array([[ rr, 0,	-rl/2], [0, 0, rl/4]]),
				np.array([[-rr, 0,	-rl/2], [0, 0, rl/4]]),
				np.array([[0,  rr,	-rl/2], [0, 0, rl/4]]),
				np.array([[0, -rr,	-rl/2], [0, 0, rl/4]]),
			]
			def rotate_pts(pts, q):
				result = []
				for p in pts:
					v = q.rotate(Vector3(p[0], p[1], p[2]))
					result.append([v.x, v.y, v.z])
				return np.array(result)
			rocket_line, = ax_r.plot([], [], [], 'b-', linewidth=3)
			fin_lines = [ax_r.plot([], [], [], 'r-', linewidth=2)[0] for _ in fin_pts]
		
		#LSP bugs out for some reason... My guess it's some C extension of matplotlib
		def update(i):
			idx = min(i * steps, len(self.x))
			line.set_data(self.x[:idx], self.y[:idx])
			line.set_3d_properties(self.z[:idx])
			if idx > 0:
				ax.set_title(f'x={self.x[idx-1]:.2f}  y={self.y[idx-1]:.2f}  z={self.z[idx-1]:.2f}')
			if has_orientation:
				q_idx = min(idx, len(self.orientations) - 1)
				q = self.orientations[q_idx]
				rotated_body = rotate_pts(body_pts, q)
				rocket_line.set_data(rotated_body[:, 0], rotated_body[:, 1])
				rocket_line.set_3d_properties(rotated_body[:, 2])
				for fin_line, fp in zip(fin_lines, fin_pts):
					rotated_fin = rotate_pts(fp, q)
					fin_line.set_data(rotated_fin[:, 0], rotated_fin[:, 1])
					fin_line.set_3d_properties(rotated_fin[:, 2])
				t = q_idx * dt
				euler = [round(e, 1) for e in q.to_euler()]
				ax_r.set_title(f't={t:.2f}s  euler={euler}')
				return line, rocket_line, *fin_lines
			return line,

		total_frames = len(self.x) // steps + 1
		ani = animation.FuncAnimation(
			fig, update,
			frames=total_frames,
			interval=interval,
			blit=False,
			repeat=False
		)
		plt.tight_layout()
		plt.show()
		return ani

	def plot_2d(self, dt: float) -> None:
		t = np.arange(len(self.x)) * dt
	
		pitch = [q.to_euler()[0] for q in self.orientations]
		roll  = [q.to_euler()[1] for q in self.orientations]
		yaw   = [q.to_euler()[2] for q in self.orientations]
	
		fig, axes = plt.subplots(4, 2, figsize=(14, 18), constrained_layout=True)
		fig.suptitle("Flight Data")
	
		axes[0, 0].plot(t, pitch)
		axes[0, 0].set_title("Pitch (deg)")
		axes[0, 0].set_xlabel("Time (s)")
	
		axes[1, 0].plot(t, roll)
		axes[1, 0].set_title("Roll (deg)")
		axes[1, 0].set_xlabel("Time (s)")
	
		axes[2, 0].plot(t, yaw)
		axes[2, 0].set_title("Yaw (deg)")
		axes[2, 0].set_xlabel("Time (s)")
	
		axes[0, 1].plot(t, self.z)
		axes[0, 1].set_title("Altitude (m)")
		axes[0, 1].set_xlabel("Time (s)")
	
		axes[1, 1].plot(t, self.x, label="x")
		axes[1, 1].plot(t, self.y, label="y")
		axes[1, 1].set_title("Horizontal Position (m)")
		axes[1, 1].set_xlabel("Time (s)")
		axes[1, 1].legend()
	
		axes[2, 1].plot(t, self.xg, color="tab:blue")
		axes[2, 1].set_title("Gimbal X (deg)")
		axes[2, 1].set_xlabel("Time (s)")
		axes[2, 1].set_xlim(0, 3.5)
	
		axes[3, 1].plot(t, self.yg, color="tab:orange")
		axes[3, 1].set_title("Gimbal Y (deg)")
		axes[3, 1].set_xlabel("Time (s)")
		axes[3, 1].set_xlim(0, 3.5)
	
		axes[3, 0].axis("off")
	

	def show(self):
		plt.show()
