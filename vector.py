import math

class Vector3:
	def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> None:
		self.x: float = float(x)
		self.y: float = float(y)
		self.z: float = float(z)

	def __repr__(self) -> str:
		return f"Vector3({self.x}, {self.y}, {self.z})"

	def __add__(self, other: "Vector3") -> "Vector3":
		return Vector3(self.x + other.x, self.y + other.y, self.z + other.z)

	def __sub__(self, other: "Vector3") -> "Vector3":
		return Vector3(self.x - other.x, self.y - other.y, self.z - other.z)

	def __mul__(self, scalar: float) -> "Vector3":
		return Vector3(self.x * scalar, self.y * scalar, self.z * scalar)

	def __truediv__(self, scalar: float) -> "Vector3":
		return Vector3(self.x / scalar, self.y / scalar, self.z / scalar)

	def __iadd__(self, other: "Vector3") -> "Vector3":
		self.x += other.x
		self.y += other.y
		self.z += other.z
		return self

	def __isub__(self, other: "Vector3") -> "Vector3":
		self.x -= other.x
		self.y -= other.y
		self.z -= other.z
		return self

	def __imul__(self, scalar: float) -> "Vector3":
		self.x *= scalar
		self.y *= scalar
		self.z *= scalar
		return self

	def __itruediv__(self, scalar: float) -> "Vector3":
		self.x /= scalar
		self.y /= scalar
		self.z /= scalar
		return self

	def length(self) -> float:
		return math.sqrt(self.x**2 + self.y**2 + self.z**2)

	def length_squared(self) -> float:
		return self.x**2 + self.y**2 + self.z**2

	def normalized(self) -> "Vector3":
		l = self.length()
		if l == 0:
			return Vector3()
		return self / l

	def dot(self, other: "Vector3") -> float:
		return self.x * other.x + self.y * other.y + self.z * other.z

	def cross(self, other: "Vector3") -> "Vector3":
		return Vector3(
			self.y * other.z - self.z * other.y,
			self.z * other.x - self.x * other.z,
			self.x * other.y - self.y * other.x
		)

	def to_radians(self) -> "Vector3":
		return Vector3(
			math.radians(self.x),
			math.radians(self.y),
			math.radians(self.z)
		)


class Vector2:
	def __init__(self, x: float = 0.0, y: float = 0.0) -> None:
		self.x: float = float(x)
		self.y: float = float(y)

	def __repr__(self) -> str:
		return f"Vector2({self.x}, {self.y})"

	def __add__(self, other: "Vector2") -> "Vector2":
		return Vector2(self.x + other.x, self.y + other.y)

	def __sub__(self, other: "Vector2") -> "Vector2":
		return Vector2(self.x - other.x, self.y - other.y)

	def __mul__(self, scalar: float) -> "Vector2":
		return Vector2(self.x * scalar, self.y * scalar)

	def __truediv__(self, scalar: float) -> "Vector2":
		return Vector2(self.x / scalar, self.y / scalar)

	def __iadd__(self, other: "Vector2") -> "Vector2":
		self.x += other.x
		self.y += other.y
		return self

	def __isub__(self, other: "Vector2") -> "Vector2":
		self.x -= other.x
		self.y -= other.y
		return self

	def __imul__(self, scalar: float) -> "Vector2":
		self.x *= scalar
		self.y *= scalar
		return self

	def __itruediv__(self, scalar: float) -> "Vector2":
		self.x /= scalar
		self.y /= scalar
		return self

	def length(self) -> float:
		return math.sqrt(self.x * self.x + self.y * self.y)

	def length_squared(self) -> float:
		return self.x * self.x + self.y * self.y

	def normalize(self) -> "Vector2":
		l = self.length()
		if l == 0:
			return Vector2()
		return self / l

	def dot(self, other: "Vector2") -> float:
		return self.x * other.x + self.y * other.y

	def cross(self, other: "Vector2") -> float:
		return self.x * other.y - self.y * other.x

	def to_radians(self) -> "Vector2":
		return Vector2(
			math.radians(self.x),
			math.radians(self.y),
		)
