project( Sugar )

cmake_minimum_required(VERSION 3.1)

set(CMAKE_CXX_STANDARD 14)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# ------------------ Boilerplate 
set(CMAKE_ALLOW_LOOSE_LOOP_CONSTRUCTS true)
 
if ( COMMAND cmake_policy )
  cmake_policy( SET CMP0003 NEW )  
endif()


# ==== Packages

find_package(Eigen3 REQUIRED NO_MODULE)

message("Eigen: ${EIGEN3_INCLUDE_DIR}")

if (TARGET Eigen3::Eigen)
  # Use the imported target
else()
  message("FUCK")
endif()


#include_directories( ${EIGEN3_INCLUDE_DIR} )

# RPATH issue
set(CMAKE_MACOSX_RPATH TRUE)

# Include...
include_directories(
    /usr/local/include
    ${EIGEN3_INCLUDE_DIR}
)
add_library( sugar SHARED
    sugar.cpp
    sugar.h
)
target_link_libraries(sugar PUBLIC Eigen3::Eigen)

add_executable( tester
    main.cpp
)
target_link_libraries(tester sugar )





