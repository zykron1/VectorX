class PID:
    def __init__(self, kp: float, ki: float, kd: float):
        self.Kp = kp
        self.Ki = ki
        self.Kd = kd

        self.integral = 0.0
        self.prev_error = 0.0

    def update_loop(self, state: float, setpoint: float, dt: float) -> float:
        error = setpoint - state

        self.integral += error * dt

        derivative = (error - self.prev_error) / dt
        self.prev_error = error

        return (self.Kp * error +
            self.Ki * self.integral +
            self.Kd * derivative
		)
