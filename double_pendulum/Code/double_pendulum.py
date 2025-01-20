import math
import random

clock_rate = 30 #How many times we update the simulation per second

m_1 = 0.8 # mass of pendulum 1 (kg)
l_1 = 0.5 # length of pendulum 1 (m)

m_2 = 0.8 # mass of pendulum 2 (kg)
l_2 = 0.5 # length of pendulum 2 (m)

# g = 9.81 # gravity (m/s)
g = 0
frictionCoefficient = 0.0 # (dimensionless)

theta_1_0 = 1 #Start angle of pendulum 1
theta_2_0 = 1 #Start angle of pendulum 2
thetaDot_1_0 = 0 #Start angular velocity of pendulum 1
thetaDot_2_0 = 0 #Start angular velocity of pendulum 2

#----------------------------------------------------------------------------------------------------------------------------------
def sign(x):
    if x > 0:
        return 1
    elif x < 0:
        return -1
    else:
        return 0

u_vector = [theta_1_0, theta_2_0, thetaDot_1_0, thetaDot_2_0]

def Euler_method_one_step(u_vector, deltaT):
    def findThetaDoubleDot_1(theta_1, theta_2, thetaDot_1, thetaDot_2):
        return (-m_2*l_1*thetaDot_1**2*math.sin(theta_1 - theta_2)*math.cos(theta_1 - theta_2) + m_2*g*math.sin(theta_2)*math.cos(theta_1 - theta_2) - m_2*l_2*thetaDot_2**2*math.sin(theta_1 - theta_2) - (m_1 + m_2)*g*math.sin(theta_1)) / ((m_1 + m_2)*l_1 - m_2*l_1*math.cos(theta_1 - theta_2)**2) - frictionCoefficient * sign(thetaDot_1)

    def findThetaDoubleDot_2(theta_1, theta_2, thetaDot_1, thetaDot_2):
        return (m_2*l_2*thetaDot_2**2*math.sin(theta_1 - theta_2)*math.cos(theta_1 - theta_2) + (m_1 + m_2)*g*math.sin(theta_1)*math.cos(theta_1 - theta_2) + l_1*thetaDot_1**2*math.sin(theta_1-theta_2)*(m_1 + m_2) - g*math.sin(theta_2)*(m_1 + m_2)) / (l_2*(m_1 + m_2) - m_2*l_2*math.cos(theta_1 - theta_2)**2) - frictionCoefficient * sign(thetaDot_2)

    u_vector[2] += findThetaDoubleDot_1(u_vector[0], u_vector[1], u_vector[2], u_vector[3]) * deltaT
    u_vector[3] += findThetaDoubleDot_2(u_vector[0], u_vector[1], u_vector[2], u_vector[3]) * deltaT

    u_vector[0] += u_vector[2] * deltaT
    u_vector[1] += u_vector[3] * deltaT

    return u_vector

def u_vector_to_x_y_coordinate(u_vector):
    first_pendulum_x = -l_1*math.cos(u_vector[0])
    first_pendulum_y = l_1*math.sin(u_vector[0])
    second_pendulum_x = l_1*math.sin(u_vector[0]) + l_2*math.sin(u_vector[1])
    second_pendulum_y = -l_1*math.cos(u_vector[0]) - l_2*math.cos(u_vector[1])

    return first_pendulum_x, first_pendulum_y, second_pendulum_x, second_pendulum_y

def scale_x_y_coordinate(x, y, l1, l2, max_dac_code):
    shifted_x = x + (l1 + l2)
    shifted_y = y + (l1 + l2)
    return int(shifted_x / (2*(l1 + l2)) * max_dac_code), int(shifted_y / (2*(l1 + l2)) * max_dac_code)

if __name__ == "__main__":
    pass
    # storage = []

    # for i in range(300):
    #     u_vector = Euler_method_one_step(u_vector, 1/30)
    #     storage.append(u_vector_to_x_y_coordinate(u_vector))

    # storage = np.array(storage)

    # plt.figure()
    # plt.scatter(storage[:,2],storage[:,3])