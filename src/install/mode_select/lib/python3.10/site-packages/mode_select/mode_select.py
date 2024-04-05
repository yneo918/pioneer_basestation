import rclpy
from rclpy.node import Node

from std_msgs.msg import Int16
from std_srvs.srv import SetBool
from geometry_msgs.msg import Twist
from sensor_msgs.msg import Joy
from std_msgs.msg import Bool
from std_msgs.msg import String

import time

global joy_lx, joy_az, u_lx1, u_az1, nav_lx1, nav_az1, u_lx2, u_az2, nav_lx2, nav_az2, \
    u_lx3, u_az3, nav_lx3, nav_az3, deadmanButtonState

joy_lx = 0.0; joy_az = 0.0; nav_lx1 = 0.0; nav_az1 = 0.0; u_lx1 = 0.0; u_az1 = 0.0; \
    nav_lx2 = 0.0; nav_az2 = 0.0; u_lx2 = 0.0; u_az2 = 0.0; \
    nav_lx3 = 0.0; nav_az3 = 0.0; u_lx3 = 0.0; u_az3 = 0.0

deadmanButtonState = False

class get_move_cmds(Node):

    def __init__(self):
        super().__init__('rover_state_controler')
        self.subscription = self.create_subscription(
            Twist,
            'joy_cmd_vel',
            self.joy_cmd_callback,
            5)
        self.subscription  # prevent unused variable warning

        self.subscription = self.create_subscription(
            Joy,
            'joy',
            self.joy_callback,
            5)
        self.subscription  # prevent unused variable warning

        self.subscription = self.create_subscription(
            Twist,
            '/robot1/nav_cmd_vel',
            self.nav_cmd_callback1,
            5)
        self.subscription  # prevent unused variable warning

        self.subscription = self.create_subscription(
            Twist,
            '/robot2/nav_cmd_vel',
            self.nav_cmd_callback2,
            5)
        self.subscription  # prevent unused variable warning

        self.subscription = self.create_subscription(
            Twist,
            '/robot3/nav_cmd_vel',
            self.nav_cmd_callback3,
            5)
        self.subscription  # prevent unused variable warning

        self.toggle_button = 0  # Toggle button to cycle between states.
        self.rover_modeC = "NEU_M"  # Assigned state of the rover.
        self.toggle_flag = 0     # if flag = 1; locked, flag = 0; free

        self.pub_robot1_cmd_vel = self.create_publisher(Twist, '/robot1/cmd_vel', 5)
        timer_period = 0.05  # seconds
        self.timer = self.create_timer(timer_period, self.core_cmd_vel_callback1)
        self.i = 0

        self.pub_robot2_cmd_vel = self.create_publisher(Twist, '/robot2/cmd_vel', 5)
        timer_period = 0.05  # seconds
        self.timer = self.create_timer(timer_period, self.core_cmd_vel_callback2)
        self.i = 0

        self.pub_robot3_cmd_vel = self.create_publisher(Twist, '/robot3/cmd_vel', 5)
        timer_period = 0.05  # seconds
        self.timer = self.create_timer(timer_period, self.core_cmd_vel_callback3)
        self.i = 0

        # self.pub_rover_en = self.create_publisher(Bool, 'r4/enable', 1)
        # timer_period = 0.2  # seconds
        # self.timer = self.create_timer(timer_period, self.rover_en_callback)
        # self.i = 0

        self.pub_robot_modeC = self.create_publisher(String, 'r4/modeC', 1)
        timer_period = 0.1  # seconds
        self.timer = self.create_timer(timer_period, self.robot_modeC_callback)
        self.i = 0
        self.prev_state = False

        # Client initialization section.
        self.en_cli = self.create_client(SetBool, '/rov/en')
        while not self.en_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Service not avail, waiting again ...')
        self.req  = SetBool.Request()
        
    def toggle(self, state):
        if state == 0:
            self.rover_modeC = "NEU_M"
            self.toggle_button = 1
        elif state == 1:
            self.rover_modeC = "JOY_M"
            self.toggle_button = 2
        else:
            self.rover_modeC = "NAV_M"
            self.toggle_button = 0
        
    def joy_callback(self, data):

        global deadmanButtonState
        deadmanButtonState = False
        if (data.buttons[4] == 1 or data.buttons[5] == 1):
            if (self.rover_modeC == "JOY_M" or self.rover_modeC == "NAV_M"):
                deadmanButtonState = True
                self.prev_state = deadmanButtonState
                self.req.data = deadmanButtonState
                self.en_cli.call_async(self.req)
        if self.prev_state == True:
            self.prev_state = deadmanButtonState
            self.req.data = deadmanButtonState
            self.en_cli.call_async(self.req)
        print(self.req.data)
        toggle_button = data.buttons[0]
        if toggle_button == 1:
            if self.toggle_flag == 0:
                self.toggle(self.toggle_button)
                print(self.rover_modeC)
                self.toggle_flag = 1
        else:
            self.toggle_flag = 0
        
    def joy_cmd_callback(self, msg):
        global joy_lx, joy_az
        joy_lx = msg.linear.x
        joy_az = msg.angular.z
    
    def nav_cmd_callback1(self, msg):
        global nav_lx1, nav_az1
        nav_lx1 = msg.linear.x
        nav_az1 = msg.angular.z

    def nav_cmd_callback2(self, msg):
        global nav_lx2, nav_az2
        nav_lx2 = msg.linear.x
        nav_az2 = msg.angular.z

    def nav_cmd_callback3(self, msg):
        global nav_lx3, nav_az3
        nav_lx3 = msg.linear.x
        nav_az3 = msg.angular.z
    
    def core_cmd_vel_callback1(self):
        global u_lx1, u_az1, joy_lx, joy_az, nav_lx1, nav_az1
        msg = Twist()

        if (self.rover_modeC == "JOY_M"):
            u_lx1 = joy_lx
            u_az1 = joy_az
        
        elif (self.rover_modeC == "NAV_M"):
            u_lx1 = nav_lx1
            u_az1 = nav_az1
        
        elif (self.rover_modeC == "NEU_M"):
            u_lx1 = 0.0
            u_az1 = 0.0
        
        msg.linear.x = u_lx1
        msg.angular.z = u_az1
        self.pub_robot1_cmd_vel(msg)
        self.i += 1

    def core_cmd_vel_callback2(self):
        global u_lx2, u_az2, joy_lx, joy_az, nav_lx2, nav_az2
        msg = Twist()

        if (self.rover_modeC == "JOY_M"):
            u_lx2 = joy_lx
            u_az2 = joy_az
        
        elif (self.rover_modeC == "NAV_M"):
            u_lx2 = nav_lx2
            u_az2 = nav_az2
        
        elif (self.rover_modeC == "NEU_M"):
            u_lx2 = 0.0
            u_az2 = 0.0
        
        msg.linear.x = u_lx2
        msg.angular.z = u_az2
        self.pub_robot2_cmd_vel(msg)
        self.i += 1

    def core_cmd_vel_callback3(self):
        global u_lx3, u_az3, joy_lx, joy_az, nav_lx3, nav_az3
        msg = Twist()

        if (self.rover_modeC == "JOY_M"):
            u_lx3 = joy_lx
            u_az3 = joy_az
        
        elif (self.rover_modeC == "NAV_M"):
            u_lx3 = nav_lx3
            u_az3 = nav_az3
        
        elif (self.rover_modeC == "NEU_M"):
            u_lx3 = 0.0
            u_az3 = 0.0
        
        msg.linear.x = u_lx3
        msg.angular.z = u_az3
        self.pub_robot3_cmd_vel(msg)
        self.i += 1

    def robot_modeC_callback(self):
        msg = String()
        msg.data = self.rover_modeC
        self.pub_robot_modeC.publish(msg)
        self.i += 1

    # def rover_en_callback(self):
    #     global deadmanButtonState
    #     msg = Bool()
    #     msg.data = deadmanButtonState
    #     self.pub_rover_en.publish(msg)
    #     self.i += 1

def main(args=None):
    rclpy.init(args=args)

    sub_move_cmds = get_move_cmds()
    rclpy.spin(sub_move_cmds)

    sub_move_cmds.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()