cmake_minimum_required(VERSION 3.19)

project(razer-mouse-battery LANGUAGES CXX)

find_package(libusb CONFIG REQUIRED)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

add_executable(${PROJECT_NAME}
    ${CMAKE_CURRENT_SOURCE_DIR}/main.cpp
)
target_compile_options(${PROJECT_NAME} PRIVATE
)
target_include_directories(${PROJECT_NAME}
    PRIVATE ${LIBUSB_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME}
    PRIVATE ${LIBUSB_LIBRARIES})

install(
    TARGETS ${PROJECT_NAME}
    RUNTIME DESTINATION ${CMAKE_BUILD_TYPE}
)
