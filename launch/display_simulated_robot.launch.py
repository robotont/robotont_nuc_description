from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def generate_launch_description():
    package = get_package_share_path('robotont_nuc_description')
    default_rviz_config_path = package / 'config/robotont_description.rviz'

    rviz_config_decl = DeclareLaunchArgument(name='rviz_config', default_value=str(default_rviz_config_path))
    rviz_fixed_frame_decl = DeclareLaunchArgument(name='rviz_fixed_frame', default_value='base_link')
    generation_decl = DeclareLaunchArgument(name='generation', default_value='3')
    model_decl = DeclareLaunchArgument(name='model', default_value='')

    model_arg = LaunchConfiguration('model')
    rviz_config_arg = LaunchConfiguration('rviz_config')
    rviz_fixed_frame_arg = LaunchConfiguration('rviz_fixed_frame')
    generation_arg = LaunchConfiguration('generation')

    robot_model_path = PythonExpression([
        '"" if "', model_arg,
        '" else "', str(package / "urdf/"), '" + (',
        '"/gen2_1/robotont_realsense.urdf.xacro" if "', generation_arg, '" == "2.1" else "/gen3/robotont_realsense.urdf.xacro")'
    ])

    robot_description = ParameterValue(Command(['xacro ', robot_model_path]), value_type=str)

    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{ 'robot_description': robot_description }]
    )

    joint_state_publisher_node = Node(
        package='joint_state_publisher',
        executable='joint_state_publisher'
    )

    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        output='screen',
        arguments=[
            '-d',
            rviz_config_arg,
            '--fixed-frame',
            rviz_fixed_frame_arg
        ]
    )

    return LaunchDescription(
        [
            generation_decl,
            rviz_config_decl,
            rviz_fixed_frame_decl,
            model_decl,
            joint_state_publisher_node,
            robot_state_publisher_node,
            rviz_node
        ]
    )
