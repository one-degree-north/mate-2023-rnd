class PIDController:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.i_sum = 0
        self.prev_e = None

    def iterate(self, p, p_exp, dt):
        e = p_exp - p
        self.i_sum += e * dt
        de = (e - self.prev_e) * dt if self.prev_e is not None else 0
        self.prev_e = e
        o = self.kp * e + self.ki * self.i_sum + self.kd * de
        return o

    def __repr__(self):
        return f"PID[i_sum={self.i_sum:.4f}, prev_e={(self.prev_e if self.prev_e is not None else 0):.4f}]"


if __name__ == "__main__":
    x_pid = PIDController(1, 1.5, 0.5)
    x = 0
    x_target = 5
    t = 0
    dt = 0.05
    while abs(x_target - x) > 0.0001:
        o = x_pid.iterate(x, x_target, dt)
        print(f"t: {t:.4f}, x: {x:.4f}, o: {o:.4f}, pid: {x_pid}")
        x += o
        t += dt
