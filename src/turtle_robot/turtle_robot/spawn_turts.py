#!/usr/bin/env python3
import rclpy
import random
from rclpy.node import Node 

from turtlesim_msgs.srv import Spawn
from turtlesim_msgs.srv import Kill


from turtle_robot_interfaces.msg import TurtInfo
from turtle_robot_interfaces.srv import UpdateTurts


class SpawnTurtsNode(Node): 

    def __init__(self):
        super().__init__("spawn_turts")

        #spawn 10 turts
        self.turt_locs_ = []#name -> TurtLoc msg (x,y)
        self.turt_counter_ = 0

        self.spawn_client_ = self.create_client(Spawn, "/spawn")
        self.kill_client_ = self.create_client(Kill, "/kill")
        while not self.spawn_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info("Waiting for /spawn...")
        for i in range(10):
            self.spawn_turt()
        self.get_logger().info("Turts successfully spawned")

        self.server_ = self.create_service(UpdateTurts, "turt_locs", self.callback_turt_location)


    def new_turt_loc(self):
        while True: 
            success = True        
            temp_x = random.uniform(0.5, 10.5)
            temp_y = random.uniform(0.5, 10.5)
            for turt in self.turt_locs_:
                if abs(turt.x - temp_x) < 0.3 and abs(turt.y - temp_y) < 0.3:
                    success = False
            if success:
                break 
        return (temp_x, temp_y)    


    def spawn_turt(self):
        req = Spawn.Request()
        req.name = f"turt_{self.turt_counter_}"
        self.turt_counter_ += 1
        x,y = self.new_turt_loc()
        req.x, req.y = x, y
    
        future = self.spawn_client_.call_async(req)
        future.add_done_callback(
            lambda f, r=req: self.on_spawned(f, r))


    def callback_turt_location(self, request, response): 
        if request.name:
            req = Kill.Request()
            req.name = request.name
            future = self.kill_client_.call_async(req)

            future.add_done_callback(lambda f, n = request.name: self.on_killed(f,n))

            self.turt_locs_ = [t for t in self.turt_locs_ if t.name != request.name]
            self.spawn_turt()
        response.names = [t.name for t in self.turt_locs_]
        response.xs = [float(t.x) for t in self.turt_locs_]
        response.ys = [float(t.y) for t in self.turt_locs_]
        return response


    def on_killed(self, future, name):
        try:
            future.result()
            self.get_logger().info(f"{name} has been crushed")
        except Exception as e:
            self.get_logger().error(f"Kill failed for {name}: {e}")


    def on_spawned(self, future, req):
        try:
            name = future.result().name
        except Exception as e:
            self.get_logger().error(f"Spawn failed: {e}")
            return
        self.turt_locs_.append(TurtInfo(name=name, x=req.x, y=req.y))
        self.get_logger().info(f"Spawned {name}")

def main(args=None): 
    rclpy.init(args=args)
    node = SpawnTurtsNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()