find_package(PkgConfig)

PKG_CHECK_MODULES(PC_GR_ECSS gnuradio-ecss)

FIND_PATH(
    GR_ECSS_INCLUDE_DIRS
    NAMES gnuradio/ecss/api.h
    HINTS $ENV{ECSS_DIR}/include
        ${PC_ECSS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    GR_ECSS_LIBRARIES
    NAMES gnuradio-ecss
    HINTS $ENV{ECSS_DIR}/lib
        ${PC_ECSS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/gnuradio-ecssTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(GR_ECSS DEFAULT_MSG GR_ECSS_LIBRARIES GR_ECSS_INCLUDE_DIRS)
MARK_AS_ADVANCED(GR_ECSS_LIBRARIES GR_ECSS_INCLUDE_DIRS)
