# CMAKE generated file: DO NOT EDIT!
# Generated by "Unix Makefiles" Generator, CMake Version 3.16

# Delete rule output on recipe failure.
.DELETE_ON_ERROR:


#=============================================================================
# Special targets provided by cmake.

# Disable implicit rules so canonical targets will work.
.SUFFIXES:


# Remove some rules from gmake that .SUFFIXES does not remove.
SUFFIXES =

.SUFFIXES: .hpux_make_needs_suffix_list


# Suppress display of executed commands.
$(VERBOSE).SILENT:


# A target that is always out of date.
cmake_force:

.PHONY : cmake_force

#=============================================================================
# Set environment variables for the build.

# The shell in which to execute make rules.
SHELL = /bin/sh

# The CMake executable.
CMAKE_COMMAND = /usr/bin/cmake

# The command to remove a file.
RM = /usr/bin/cmake -E remove -f

# Escaping for special characters.
EQUALS = =

# The top-level source directory on which CMake was run.
CMAKE_SOURCE_DIR = /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation

# The top-level build directory on which CMake was run.
CMAKE_BINARY_DIR = /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build

# Include any dependencies generated for this target.
include swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/depend.make

# Include the progress variables for this target.
include swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/progress.make

# Include the compile flags for this target's objects.
include swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/flags.make

swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.o: swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/flags.make
swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.o: swig/_mimo_ofdm_jrc_swig_doc_tag.cpp
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --progress-dir=/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_1) "Building CXX object swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.o"
	cd /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig && /usr/bin/c++  $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -o CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.o -c /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig/_mimo_ofdm_jrc_swig_doc_tag.cpp

swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.i: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Preprocessing CXX source to CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.i"
	cd /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -E /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig/_mimo_ofdm_jrc_swig_doc_tag.cpp > CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.i

swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.s: cmake_force
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green "Compiling CXX source to assembly CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.s"
	cd /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig && /usr/bin/c++ $(CXX_DEFINES) $(CXX_INCLUDES) $(CXX_FLAGS) -S /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig/_mimo_ofdm_jrc_swig_doc_tag.cpp -o CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.s

# Object files for target _mimo_ofdm_jrc_swig_doc_tag
_mimo_ofdm_jrc_swig_doc_tag_OBJECTS = \
"CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.o"

# External object files for target _mimo_ofdm_jrc_swig_doc_tag
_mimo_ofdm_jrc_swig_doc_tag_EXTERNAL_OBJECTS =

swig/_mimo_ofdm_jrc_swig_doc_tag: swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/_mimo_ofdm_jrc_swig_doc_tag.cpp.o
swig/_mimo_ofdm_jrc_swig_doc_tag: swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/build.make
swig/_mimo_ofdm_jrc_swig_doc_tag: swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/link.txt
	@$(CMAKE_COMMAND) -E cmake_echo_color --switch=$(COLOR) --green --bold --progress-dir=/home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/CMakeFiles --progress-num=$(CMAKE_PROGRESS_2) "Linking CXX executable _mimo_ofdm_jrc_swig_doc_tag"
	cd /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig && $(CMAKE_COMMAND) -E cmake_link_script CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/link.txt --verbose=$(VERBOSE)

# Rule to build all files generated by this target.
swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/build: swig/_mimo_ofdm_jrc_swig_doc_tag

.PHONY : swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/build

swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/clean:
	cd /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig && $(CMAKE_COMMAND) -P CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/cmake_clean.cmake
.PHONY : swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/clean

swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/depend:
	cd /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build && $(CMAKE_COMMAND) -E cmake_depends "Unix Makefiles" /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/swig /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig /home/xin/MIMO-OFDM-JRC-Optimal-Beam-and-Resource-Allocation/build/swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/DependInfo.cmake --color=$(COLOR)
.PHONY : swig/CMakeFiles/_mimo_ofdm_jrc_swig_doc_tag.dir/depend

