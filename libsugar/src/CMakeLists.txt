project( Sugar )

cmake_minimum_required(VERSION 2.4.5)

# ------------------ Boilerplate 
set(CMAKE_ALLOW_LOOSE_LOOP_CONSTRUCTS true)
 
if ( COMMAND cmake_policy )
  cmake_policy( SET CMP0003 NEW )  
endif()


# RPATH issue

#set(CMAKE_SKIP_RPATH TRUE)
set(CMAKE_MACOSX_RPATH TRUE)
#set(CMAKE_SKIP_BUILD_RPATH  FALSE)
#set(CMAKE_BUILD_WITH_INSTALL_RPATH FALSE) # TRUE
#set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")
#set(CMAKE_INSTALL_RPATH_USE_LINK_PATH TRUE)
#set(CMAKE_INSTALL_RPATH "${CMAKE_INSTALL_PREFIX}/lib")


# Include...
include_directories(
    /usr/local/include
)

# Lib
#link_directories(
#    /usr/local/lib
#)

add_library( sugar SHARED
    sugar.cpp
    sugar.h
)
#target_link_libraries(stkcontrol stk)


#message( "Doing really stupid thing" )
#add_custom_command(TARGET stkcontrol 
#    POST_BUILD COMMAND 
#    ${CMAKE_INSTALL_NAME_TOOL} -change libstk-4.6.0.dylib /usr/local/lib/libstk-4.6.0.dylib 
#    #${CMAKE_INSTALL_NAME_TOOL} -change libstk.dylib /usr/local/lib/libstk.dylib 
#    $<TARGET_FILE:stkcontrol>)


add_executable( tester
    main.cpp
)
target_link_libraries(tester sugar )


#install(TARGETS stkcontrol DESTINATION /usr/local/lib)
