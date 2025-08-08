  cmake_minimum_required(VERSION 3.5)

  project(cvbasic C)

  set(CMAKE_C_STANDARD 11)
  set(CMAKE_C_STANDARD_REQUIRED ON)

  # enable compiler warnings
  if(MSVC)
      add_compile_options(/W4)
  else()
      add_compile_options(-Wall -Wextra -Wpedantic)
  endif()

  # set default build type
  if(NOT CMAKE_BUILD_TYPE)
      set(CMAKE_BUILD_TYPE Release)
  endif()

  # add optimization flags for Release builds
  if(CMAKE_BUILD_TYPE STREQUAL Release)
      if(MSVC)
          add_compile_options(/O2)
      else()
          add_compile_options(-O2)
      endif()
  endif()

  # CVBasic does use old APIs
  if(MSVC)
      add_definitions(-D_CRT_SECURE_NO_WARNINGS)
  endif()

  add_executable(${PROJECT_NAME}
      cvbasic.c
      node.c
      driver.c
      cpuz80.c
      cpu6502.c
      cpu9900.c
  )

  # Install the executable
  install(TARGETS ${PROJECT_NAME}
      RUNTIME DESTINATION bin
  )