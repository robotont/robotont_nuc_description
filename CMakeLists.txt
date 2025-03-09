cmake_minimum_required(VERSION 3.5)
project(robotont_nuc_description)

if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)

# Disable tests
set(BUILD_TESTING OFF)

install(
  DIRECTORY meshes urdf config launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
