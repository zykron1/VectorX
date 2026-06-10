import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from vector import Vector3

class Renderer:
	def __init__(self, x, y, z, orientations=None):
		self.x = x
		self.y = y
		self.z = z
		self.orientations = orientations 

	def show(self):
		fig = plt.figure()
		ax = fig.add_subplot(111, projection='3d')
		ax.plot(self.x, self.y, self.z)
		ax.set_xlabel("X")
		ax.set_ylabel("Y")
		ax.set_zlabel("Z")
		plt.show()

	def animate(self, dt, interval=50):
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
