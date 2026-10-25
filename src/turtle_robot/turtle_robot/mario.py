 #!/usr/bin/env python3
import rclpy
from rclpy.node import Node 
import math

from turtle_robot_interfaces.msg import TurtInfo
from turtle_robot_interfaces.srv import UpdateTurts

from turtlesim_msgs.msg import Pose
from geometry_msgs.msg import Twist


class Mario(Node): 

    def __init__(self):
        super().__init__("mario")
        self.client_ = self.create_client(UpdateTurts, "turt_locs")
        self.subscriber_ = self.create_subscription(Pose, "/turtle1/pose", self.callback_pose, 10)
        self.cmd_pub_ = self.create_publisher(Twist, "/turtle1/cmd_vel", 10)
        
        self.mario_coords_ = None
        self.target_info_ = None
        self.turt_locs_ = []
        self.request_pending_ = False

        self.timer_ = self.create_timer(0.05, self.control_loop)


    def callback_pose(self, msg):
        self.mario_coords_ = msg


    def control_loop(self):
        if self.mario_coords_ is None:
            return
        if self.target_info_ is None:
            self.demand_turts("")
            return

        dx = self.target_info_.x - self.mario_coords_.x
        dy = self.target_info_.y - self.mario_coords_.y
        dist = math.hypot(dx, dy)
        cmd_vel = Twist()
        if dist < 0.3:
            name = self.target_info_.name
            self.target_info_ = None
            self.demand_turts(name)
        else:
            angle_err = math.atan2(dy, dx) - self.mario_coords_.theta
            angle_err = math.atan2(math.sin(angle_err), math.cos(angle_err))
            cmd_vel.linear.x = 2.0 * dist
            cmd_vel.angular.z = 6.0 * angle_err
        self.cmd_pub_.publish(cmd_vel) 

        

    def demand_turts(self, name):
        if self.request_pending_:
            return

        while not self.client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().warning('Waiting for more turts to crush...')

        request = UpdateTurts.Request()
        request.name = name
        future = self.client_.call_async(request)
        self.request_pending_ = True
        future.add_done_callback(self.handle_turts_response)

    def handle_turts_response(self, future):
        self.request_pending_ = False
        response = future.result()
        if response is not None:
            r = future.result()
            self.turt_locs_ = [
                TurtInfo(name=n, x=x, y=y) for n, x, y in zip(r.names, r.xs, r.ys)
            ]
            self.get_logger().info('Yes! More turts to crush!')
            self.find_turts()
        else:
            self.get_logger().error('Something went wrong, theres not enough turts...')


    def find_turts(self):
        if not self.turt_locs_:
            self.target_info_ = None
            return
        
        min_dist = float('inf')
        name = ""
        x = 0
        y= 0 
        for turt in self.turt_locs_:
            dist = math.hypot(turt.x - self.mario_coords_.x, turt.y - self.mario_coords_.y)
            if dist < min_dist:
                min_dist = dist
                name = turt.name
                x = turt.x
                y = turt.y
        self.target_info_ = TurtInfo(name = name, x = x, y = y)

    
def main(args=None): 
    rclpy.init(args=args)
    node = Mario()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()