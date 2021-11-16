#========================================================
#Tamplate for Core Configuration core_config.tcl
#
#Everyting within <> have to be adapted
#
#by Robert Reichert, 2021
#========================================================

###Core Block Settings

set display_name {<CoreName>}

set core [ipx::current_core]
set_property DISPLAY_NAME $display_name $core
set_property DESCRIPTION $display_name $core

set_property VENDOR {Robert_Reichert} $core
set_property VENDOR_DISPLAY_NAME {Robert Reichert} $core
set_property COMPANY_URL {https://https://github.com/RobReichert/red-pitaya} $core

###Implement Parameter
core_parameter <PARAMETER_SAMPLE>{<Displayed Name>} {<Discription>}

###Implement Bus Interfaces
set bus [ipx::get_bus_interfaces -of_objects $core s_axis]
set_property NAME S_AXIS $bus
set_property INTERFACE_MODE slave $bus
