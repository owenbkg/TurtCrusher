# TurtCrusher 🐢

A small ROS 2 game built on turtlesim. A spawner node scatters turts around the map, and **Mario** (`turt1`) hunts them down one by one: he always goes for the closest turt, crushes it, and a new one spawns in its place.

## Packages

| Package | Contents |
|---|---|
| `turtle_robot` | Python nodes: `spawn_turts` and `mario` |
| `turtle_robot_interfaces` | Custom interfaces: `TurtInfo.msg`, `UpdateTurts.srv` |
| `turtle_robot_bringup` | Launch file that starts the whole game |

## How it works

- **`spawn_turts`** spawns 10 turts at random, non-overlapping positions using turtlesim's `/spawn` service, and keeps track of which ones are alive. It provides the `turt_locs` service (`UpdateTurts`):
  - request with an empty name → returns the list of alive turts
  - request with a turt's name → kills that turt via `/kill`, spawns a replacement, and returns the updated list
- **`mario`** subscribes to `/turt1/pose`, picks the closest turt from the list, and drives toward it with a proportional controller on `/turt1/cmd_vel`. When he's close enough, he sends a crush request and moves on to the next target.

```
turtlesim  <── /spawn, /kill ──  spawn_turts
    │                                 ▲
/turt1/pose                    turt_locs (UpdateTurts)
    ▼                                 │
  mario  ── /turt1/cmd_vel ──>  turtlesim
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
ros2 launch turtle_robot_bringup turt_crusher.launch.xml
```

Or start the nodes individually:

```bash
ros2 run turtlesim turtlesim_node
ros2 run turtle_robot spawn_turts
ros2 run turtle_robot mario
```

## Notes

- All service calls are asynchronous (`call_async` + done-callbacks), so no node ever blocks inside the executor.
- Restart turtlesim between runs. turt names are reused from `turt_0` upward, so leftover turts from a previous run will clash.
