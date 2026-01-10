from ament_index_python.packages import get_package_share_path

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.substitutions import LaunchConfiguration, Command
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _rgba_string_from_user_value(user_value: str) -> str:
    s = (user_value or "").strip()
    if not s:
        raise ValueError("Empty color string")

    # RGBA numeric input (space or comma separated)
    parts = s.replace(",", " ").split()
    if len(parts) == 4:
        nums = [float(p) for p in parts]
        if any(v > 1.0 for v in nums):
            nums = [v / 255.0 for v in nums]
        nums = [min(1.0, max(0.0, v)) for v in nums]
        return f"{nums[0]} {nums[1]} {nums[2]} {nums[3]}"

    # Hex input
    if s.startswith("#") and len(s) in (7, 9):
        hexv = s[1:]
        r = int(hexv[0:2], 16)
        g = int(hexv[2:4], 16)
        b = int(hexv[4:6], 16)
        a = int(hexv[6:8], 16) if len(hexv) == 8 else 255
        return f"{r/255.0} {g/255.0} {b/255.0} {a/255.0}"

    # Color names 
    name = s.lower().replace("_", "").replace("-", "")
    try:
        from PIL import ImageColor
        r, g, b, a = ImageColor.getcolor(name, "RGBA")
        return f"{r/255.0} {g/255.0} {b/255.0} {a/255.0}"
    except Exception:
        fallback = {
            "lightblue": "0.16 0.65 0.98 1.0",
            "blue":      "0.00 0.35 0.90 1.0",
            "yellow":    "1.00 1.00 0.00 1.0",
            "black":     "0.10 0.10 0.10 1.0",
            "purple":    "0.45 0.20 0.65 1.0",
            "gray":      "0.75 0.75 0.75 1.0",
            "darkgreen": "0.00 0.45 0.25 1.0",
            "green":     "0.00 0.80 0.30 1.0",
        }
        if name in fallback:
            return fallback[name]
        raise ValueError(
            f"Unknown color '{user_value}'. Provide RGBA ('0 1 0 1' or '0 255 0 255'), "
            f"hex ('#00ff00' or '#00ff00ff'), or install Pillow for CSS color names."
        )


def _setup(context, *args, **kwargs):
    pkg = get_package_share_path("robotont_nuc_description")

    model = LaunchConfiguration("model").perform(context).strip()
    generation = LaunchConfiguration("generation").perform(context).strip()

    primary_in = LaunchConfiguration("primary_color").perform(context)
    secondary_in = LaunchConfiguration("secondary_color").perform(context)

    if model:
        robot_model_path = model
    else:
        if generation == "2.1":
            robot_model_path = str(pkg / "urdf/gen2_1/robotont_realsense.urdf.xacro")
        else:
            # Default to gen3
            robot_model_path = str(pkg / "urdf/gen3/robotont_realsense.urdf.xacro")

    primary_rgba = _rgba_string_from_user_value(primary_in)
    secondary_rgba = _rgba_string_from_user_value(secondary_in)

    robot_description = ParameterValue(
        Command([
            "xacro ", robot_model_path,
            ' main_color:="', primary_rgba, '"',
            ' second_color:="', secondary_rgba, '"',
        ]),
        value_type=str,
    )

    rsp = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}],
    )

    jsp = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=[
            "-d", LaunchConfiguration("rviz_config"),
            "--fixed-frame", LaunchConfiguration("rviz_fixed_frame"),
        ],
    )

    return [jsp, rsp, rviz]


def generate_launch_description():
    pkg = get_package_share_path("robotont_nuc_description")
    default_rviz_config_path = pkg / "config/robotont_description.rviz"

    return LaunchDescription([
        DeclareLaunchArgument("rviz_config", default_value=str(default_rviz_config_path)),
        DeclareLaunchArgument("rviz_fixed_frame", default_value="base_link"),
        DeclareLaunchArgument("generation", default_value="3"),
        DeclareLaunchArgument("model", default_value=""),

        DeclareLaunchArgument("primary_color", default_value="0.16 0.65 0.98 1.0"),
        DeclareLaunchArgument("secondary_color", default_value="0.75 0.75 0.75 1.0"),

        OpaqueFunction(function=_setup),
    ])
