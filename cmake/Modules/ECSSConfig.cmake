INCLUDE(FindPkgConfig)
PKG_CHECK_MODULES(PC_ECSS ECSS)

FIND_PATH(
    ECSS_INCLUDE_DIRS
    NAMES ECSS/api.h
    HINTS $ENV{ECSS_DIR}/include
        ${PC_ECSS_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    ECSS_LIBRARIES
    NAMES gnuradio-ECSS
    HINTS $ENV{ECSS_DIR}/lib
        ${PC_ECSS_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
)

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(ECSS DEFAULT_MSG ECSS_LIBRARIES ECSS_INCLUDE_DIRS)
MARK_AS_ADVANCED(ECSS_LIBRARIES ECSS_INCLUDE_DIRS)

