cmake_minimum_required(VERSION 3.19)

project(razer-mouse-battery LANGUAGES CXX)

find_package(libusb REQUIRED)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(${PROJECT_NAME}
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
)
target_compile_options(${PROJECT_NAME} PRIVATE
)
target_link_libraries(${PROJECT_NAME}
    PRIVATE libusb::libusb)

install(
    TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_BUILD_TYPE}
)
