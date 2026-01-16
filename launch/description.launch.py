from ament_index_python.packages import get_package_share_path
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import Command, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue

def launch_setup(context, *args, **kwargs):
    package = get_package_share_path('robotont_nuc_description')
    
    generation = LaunchConfiguration('generation').perform(context)
    model = LaunchConfiguration('model').perform(context)
    namespace = LaunchConfiguration('namespace').perform(context)
    frame_prefix = LaunchConfiguration('frame_prefix').perform(context)
    
    # Determine URDF path
    if model:
        urdf_path = model
    elif generation == '2.1':
        urdf_path = str(package / 'urdf/gen2_1/robotont_realsense.urdf.xacro')
    else:
        urdf_path = str(package / 'urdf/gen3/robotont_realsense.urdf.xacro')
    
    # Pass prefix to xacro
    robot_description = ParameterValue(
        Command(['xacro ', urdf_path, ' prefix:=', frame_prefix]),
        value_type=str
    )
    
    return [
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            namespace=namespace,
            parameters=[{
                'robot_description': robot_description,
                #'frame_prefix': frame_prefix
            }]
        ),
        Node(
            package='joint_state_publisher',
            executable='joint_state_publisher',
            namespace=namespace
        )
        # TODO: Add fake joint state publisher only if no real joints are being published, we can have param e.g. real_hardware:=true
    ]

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument('generation', default_value='3'),
        DeclareLaunchArgument('model', default_value=''),
        DeclareLaunchArgument('namespace', default_value=''),
        DeclareLaunchArgument('frame_prefix', default_value=''),
        OpaqueFunction(function=launch_setup)
    ])