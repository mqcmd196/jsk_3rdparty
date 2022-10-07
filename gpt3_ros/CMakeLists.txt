cmake_minimum_required(VERSION 3.0.2)
project(gpt3_ros)

find_package(
  catkin REQUIRED COMPONENTS
  catkin_virtualenv REQUIRED
  rospy
  actionlib_msgs
  std_msgs
  message_generation
  )

# catkin_python_setup()

# add_message_files(
#   # TODO
#   )

# add_action_files(
#   # TODO
#   )

generate_messages(
  DEPENDENCIES
  std_msgs
  actionlib_msgs
  )

catkin_package()

# generate the virtualenv
catkin_generate_virtualenv(
  INPUT_REQUIREMENTS requirements.in
  PYTHON_INTERPRETER python3.7
  USE_SYSTEM_PACKAGES FALSE
  )

# install
# python
file(GLOB PYTHON_SCRIPTS scripts/*.py)
catkin_install_python(
  PROGRAMS ${PYTHON_SCRIPTS}
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
  )
# python requirements
install(FILES requirements.txt
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
  )

# launch
install(DIRECTORY launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
  )
