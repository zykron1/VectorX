from pid import PID
from vector import Vector3, Vector2
import random

class Rocket:
	def __init__(self, XKp, XKi, XKd, YKp, YKi, YKd):
		self.xPID = PID(XKp, XKi, XKd)
		self.yPID = PID(YKp, YKi, YKd)

		self.acceleration = Vector3()
		self.orientalVelocity = Vector3()

	def guide(self, dt, orientation, acceleration):
		# In a real rocket, the control algorithm recieves angular velocity not orientation
		# For simplicity sake and the verification of if PID algorithms work I chose to use this simple boilerplate
		# TODO: Implement HIL simulation with a real flight computer
		x = self.xPID.update_loop(orientation[0], 0, dt)
		y = self.yPID.update_loop(orientation[1], 0, dt)
	
		x = max(-7.5, min(7.5, x))
		y = max(-7.5, min(7.5, y))

		return Vector2(x, y)
