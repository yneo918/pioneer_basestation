import os

from ament_index_python import get_package_share_directory

from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node



def generate_launch_description():
    ld = LaunchDescription()
    
    # Nodes to launch
    target = Node(
        package="gps_target_push",
        executable="push_target",
    )

    state_control = Node(
        package="mode_select",
        executable="mode_select",
        output='screen',
        emulate_tty=True,
    )
    nav1 = Node(
        package="navigation_core1",
        executable="run_navigation",
        
    )
    nav2 = Node(
        package="navigation_core2",
        executable="run_navigation",
    )
    nav3 = Node(
        package="navigation_core3",
        executable="run_navigation",
        output='screen',
        emulate_tty=True,
    )

    teleop = Node(
        package="rover_teleop_joy",
        executable="rover_joy",
    )

    # include another launch file
    launch_joy = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('teleop_twist_joy'),
                'launch/teleop-launch.py'))
    )

    ld.add_action(launch_joy)
    ld.add_action(target)
    ld.add_action(state_control)
    ld.add_action(nav1)
    ld.add_action(nav2)
    ld.add_action(nav3)
    ld.add_action(teleop)

    return ld


