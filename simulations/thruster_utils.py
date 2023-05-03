import math

# us (s) to force (N)
def thrust_to_force(s):
    t = s - 0.0015
    return 5533.58 * t + 2.3281e11 * (t ** 3)

# us (s) to current (A)
def thrust_to_current(s):
    t = s - 0.0015
    return 4.6883e7 * (t ** 2) + 2.6537e14 * (t ** 4)

# force (N) to us (s)
def force_to_thrust(F):
    k = (590.944 * ((1.96433e17*F*F+2.11801e16) ** (1/2)) - 2.61911e11 * F) ** (1/3)
    t = 0.392897 / k - 2.01653e-8 * k
    return t + 0.0015


if __name__ == "__main__":
    # unit test
    print(force_to_thrust(thrust_to_force(0.0015)))
    print(force_to_thrust(thrust_to_force(0.0012)))
    print(force_to_thrust(thrust_to_force(0.0018)))
    print(force_to_thrust(thrust_to_force(0.0014)))
    print(force_to_thrust(thrust_to_force(0.0016)))
    print(thrust_to_force(force_to_thrust(0)))
    print(thrust_to_force(force_to_thrust(5)))
    print(thrust_to_force(force_to_thrust(10)))
    print(thrust_to_force(force_to_thrust(-5)))
    print(thrust_to_force(force_to_thrust(-10)))
