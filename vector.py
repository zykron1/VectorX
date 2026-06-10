import math

class Vector3:
	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.x = float(x)
		self.y = float(y)
		self.z = float(z)

	def __repr__(self):
		return f"Vector3({self.x}, {self.y}, {self.z})"
	def __add__(self, other):
		return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)
	def __sub__(self, other):
		return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)
	def __mul__(self, scalar):
		return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)
	def __truediv__(self, scalar):
		return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)
	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		self.z += other.z
		return self
	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		self.z -= other.z
		return self
	def __imul__(self, scalar):
		self.x *= scalar
		self.y *= scalar
		self.z *= scalar
		return self
	def __itruediv__(self, scalar):
		self.x /= scalar
		self.y /= scalar
		self.z /= scalar
		return self
	def length(self):
		return math.sqrt(self.x**2 + self.y**2 + self.z**2)
	def length_squared(self):
		return self.x**2 + self.y**2 + self.z**2
	def normalized(self):
		l = self.length()
		if l == 0:
			return Vector3()
		return self / l
	def dot(self, other):
		return self.x * other.x + self.y * other.y + self.z * other.z
	def cross(self, other):
		return Vector3(
			self.y * other.z - self.z * other.y,
			self.z * other.x - self.x * other.z,
			self.x * other.y - self.y * other.x
		)
	def to_radians(self):
		return Vector3(
			math.radians(self.x),
			math.radians(self.y),
			math.radians(self.z)
		)

class Vector2:
	def __init__(self, x=0.0, y=0.0):
		self.x = float(x)
		self.y = float(y)
	def __repr__(self):
		return f"Vector2({self.x}, {self.y})"
	def __add__(self, other):
		return Vector2(self.x + other.x, self.y + other.y)
	def __sub__(self, other):
		return Vector2(self.x - other.x, self.y - other.y)
	def __mul__(self, scalar):
		return Vector2(self.x * scalar, self.y * scalar)
	def __truediv__(self, scalar):
		return Vector2(self.x / scalar, self.y / scalar)

	def __iadd__(self, other):
		self.x += other.x
		self.y += other.y
		return self
	def __isub__(self, other):
		self.x -= other.x
		self.y -= other.y
		return self
	def __imul__(self, scalar):
		self.x *= scalar
		self.y *= scalar
		return self
	def __itruediv__(self, scalar):
		self.x /= scalar
		self.y /= scalar
		return self
	# Math
	def length(self):
		return math.sqrt(self.x * self.x + self.y * self.y)
	def length_squared(self):
		return self.x * self.x + self.y * self.y
	def normalize(self):
		l = self.length()
		if l == 0:
			return Vector2()
		return self / l
	def dot(self, other):
		return self.x * other.x + self.y * other.y
	def cross(self, other):
		return self.x * other.y - self.y * other.x
	def to_radians(self):
		return Vector2(
			math.radians(self.x),
			math.radians(self.y),
		)
