cmake_minimum_required(VERSION 2.8)
project(DBoW2)
include(ExternalProject)

option(BUILD_DBoW2   "Build DBoW2"   ON)
option(BUILD_surfdb  "Build surf db" ON)
option(BUILD_query   "Build surf query" ON)
option(BUILD_cnnvoc  "Build cnn voc" ON)
option(BUILD_cnndb   "Build cnn voc" ON)
option(BUILD_cnnquery "Build cnn query" ON)

if(NOT CMAKE_BUILD_TYPE AND NOT CMAKE_CONFIGURATION_TYPES)
  set(CMAKE_BUILD_TYPE Release CACHE STRING "Choose the type of build." FORCE)
  set_property(CACHE CMAKE_BUILD_TYPE PROPERTY STRINGS "Debug" "Release"
    "MinSizeRel" "RelWithDebInfo")
endif()

if(MSVC)
  if(CMAKE_CXX_FLAGS MATCHES "/W[0-4]")
    string(REGEX REPLACE "/W[0-4]" "/W4" CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS}")
  else()
    set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} /W4")
  endif()
elseif(CMAKE_COMPILER_IS_GNUCC OR CMAKE_COMPILER_IS_GNUCXX)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -pedantic")
endif()

set(HDRS
  include/DBoW2/BowVector.h           include/DBoW2/FBrief.h              include/DBoW2/FSurf64.h
  include/DBoW2/QueryResults.h        include/DBoW2/TemplatedDatabase.h   include/DBoW2/FORB.h
  include/DBoW2/DBoW2.h               include/DBoW2/FClass.h              include/DBoW2/FeatureVector.h
  include/DBoW2/ScoringObject.h       include/DBoW2/TemplatedVocabulary.h include/DBoW2/FCNN256.h)
set(SRCS 
  src/BowVector.cpp     src/FBrief.cpp        src/FSurf64.cpp       src/FORB.cpp
  src/FeatureVector.cpp src/QueryResults.cpp  src/ScoringObject.cpp src/FCNN256.cpp)

set(DEPENDENCY_DIR ${CMAKE_CURRENT_BINARY_DIR}/dependencies)
set(DEPENDENCY_INSTALL_DIR ${DEPENDENCY_DIR}/install)

find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})

find_package(Boost REQUIRED)
include_directories(${Boost_INCLUDE_DIR})

find_package(DLib QUIET 
  PATHS ${DEPENDENCY_INSTALL_DIR})
if(${DLib_FOUND})
  message("DLib library found, using it from the system")
  include_directories(${DLib_INCLUDE_DIRS})
  add_custom_target(Dependencies)
else(${DLib_FOUND})
  message("DLib library not found in the system, it will be downloaded on build")
  option(DOWNLOAD_DLib_dependency "Download DLib dependency" ON)
  if(${DOWNLOAD_DLib_dependency})
    ExternalProject_Add(DLib
      PREFIX ${DEPENDENCY_DIR}
      GIT_REPOSITORY http://github.com/dorian3d/DLib
      GIT_TAG v1.1-nonfree
      INSTALL_DIR ${DEPENDENCY_INSTALL_DIR}
      CMAKE_ARGS -DCMAKE_INSTALL_PREFIX=<INSTALL_DIR>)
    add_custom_target(Dependencies ${CMAKE_COMMAND} ${CMAKE_SOURCE_DIR} DEPENDS DLib)
  else()
    message(SEND_ERROR "Please, activate DOWNLOAD_DLib_dependency option or download manually")
  endif(${DOWNLOAD_DLib_dependency})
endif(${DLib_FOUND})

if(BUILD_DBoW2)
  add_library(${PROJECT_NAME} SHARED ${SRCS})
  include_directories(include/DBoW2/)
  add_dependencies(${PROJECT_NAME} Dependencies)
  target_link_libraries(${PROJECT_NAME} ${OpenCV_LIBS} ${DLib_LIBS})
endif(BUILD_DBoW2)

if(BUILD_surfdb)
  add_executable(surfdb demo/surfdb.cpp)
  target_link_libraries(surfdb ${PROJECT_NAME} ${OpenCV_LIBS} ${DLib_LIBS} leveldb)
endif(BUILD_surfdb)

if(BUILD_query)
  add_executable(query demo/query.cpp)
  target_link_libraries(query ${PROJECT_NAME} ${OpenCV_LIBS} ${DLib_LIBS} leveldb)
endif(BUILD_query)

if(BUILD_cnnvoc)
  add_executable(cnnvoc demo/cnnvoc.cpp)
  target_link_libraries(cnnvoc ${PROJECT_NAME} ${OpenCV_LIBS} ${DLib_LIBS} leveldb)
endif(BUILD_cnnvoc)

if(BUILD_cnndb)
  add_executable(cnndb demo/cnndb.cpp)
  target_link_libraries(cnndb ${PROJECT_NAME} ${OpenCV_LIBS} ${DLib_LIBS} leveldb)
endif(BUILD_cnndb)

if(BUILD_cnnquery)
  add_executable(cnnquery demo/cnnquery.cpp)
  target_link_libraries(cnnquery ${PROJECT_NAME} ${OpenCV_LIBS} ${DLib_LIBS} leveldb)
endif(BUILD_cnnquery)


configure_file(src/DBoW2.cmake.in
  "${PROJECT_BINARY_DIR}/DBoW2Config.cmake" @ONLY)

install(TARGETS ${PROJECT_NAME} DESTINATION ${CMAKE_INSTALL_PREFIX}/lib)
if(BUILD_DBoW2)
  install(DIRECTORY include/DBoW2 DESTINATION ${CMAKE_INSTALL_PREFIX}/include)
endif()
install(FILES "${CMAKE_CURRENT_BINARY_DIR}/DBoW2Config.cmake"
  DESTINATION ${CMAKE_INSTALL_PREFIX}/include/${PROJECT_NAME})
install(FILES "${PROJECT_BINARY_DIR}/DBoW2Config.cmake" 
  DESTINATION ${CMAKE_INSTALL_PREFIX}/lib/cmake/DBoW2/)
install(DIRECTORY ${DEPENDENCY_INSTALL_DIR}/ DESTINATION ${CMAKE_INSTALL_PREFIX} OPTIONAL)
