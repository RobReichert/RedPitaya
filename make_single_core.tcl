# ==================================================================================================
# make_cores.tcl
#
# Simple script for creating all the IPs in the cores/ folder of the red-pitaya-notes-master/ folder.
# Make sure the script is run from the red-pitaya-notes-master/ folder.
#
# by Anton Potocnik, 01.10.2016
# modifyed by Robert Reichert, 04.11.2020
# ==================================================================================================

set part_name xc7z010clg400-1
set core axis_ram_writer_v2_0

if {! [file exists cores]} {
	puts "Failed !";
	puts "Please change directory to red-pitaya-notes-master/";
	return
} 


# generate core

set argv "$core $part_name"
set core_short [string trimright $core "v_1234567890"]

puts "Generating $core";
puts "===========================";

file delete -force tmp/cores/$core_short.cache 
file delete -force tmp/cores/$core_short.hw 
file delete -force tmp/cores/$core_short.ip_user_files
file delete -force tmp/cores/$core_short.sim
file delete -force tmp/cores/$core_short.xpr
file delete -force tmp/cores/$core

source scripts/core.tcl

