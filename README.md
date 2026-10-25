# Turtle Crusher 🐢

A small ROS 2 game built on turtlesim. A spawner node scatters turtles around the map, and **Mario** (`turtle1`) hunts them down one by one: he always goes for the closest turtle, crushes it, and a new one spawns in its place.

## Packages

| Package | Contents |
|---|---|
| `turtle_robot` | Python nodes: `spawn_turtles` and `mario` |
| `turtle_robot_interfaces` | Custom interfaces: `TurtInfo.msg`, `UpdateTurts.srv` |
| `turtle_robot_bringup` | Launch file that starts the whole game |

## How it works

- **`spawn_turtles`** spawns 10 turtles at random, non-overlapping positions using turtlesim's `/spawn` service, and keeps track of which ones are alive. It provides the `turt_locs` service (`UpdateTurts`):
  - request with an empty name → returns the list of alive turtles
  - request with a turtle's name → kills that turtle via `/kill`, spawns a replacement, and returns the updated list
- **`mario`** subscribes to `/turtle1/pose`, picks the closest turtle from the list, and drives toward it with a proportional controller on `/turtle1/cmd_vel`. When he's close enough, he sends a crush request and moves on to the next target.

```
turtlesim  <── /spawn, /kill ──  spawn_turtles
    │                                 ▲
/turtle1/pose                    turt_locs (UpdateTurts)
    ▼                                 │
  mario  ── /turtle1/cmd_vel ──>  turtlesim
```

## Requirements

- ROS 2 (developed on Lyrical)
- `turtlesim`

## Build

```bash
cd ~/turtlesim_proj
colcon build
source install/setup.bash
```

## Run

```bash
ros2 launch turtle_robot_bringup turtle_game.launch.xml
```

Or start the nodes individually:

```bash
ros2 run turtlesim turtlesim_node
ros2 run turtle_robot spawn_turtles
ros2 run turtle_robot mario
```

## Notes

- All service calls are asynchronous (`call_async` + done-callbacks), so no node ever blocks inside the executor.
- Restart turtlesim between runs. Turtle names are reused from `turt_0` upward, so leftover turtles from a previous run will clash.
