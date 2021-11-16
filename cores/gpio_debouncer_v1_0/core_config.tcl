set display_name {GPIO Debouncer}

set core [ipx::current_core]

set_property DISPLAY_NAME $display_name $core
set_property DESCRIPTION $display_name $core

set_property VENDOR {pavel-demin} $core
set_property VENDOR_DISPLAY_NAME {Pavel Demin} $core
set_property COMPANY_URL {https://github.com/pavel-demin/red-pitaya-notes} $core

core_parameter DATA_WIDTH {DATA WIDTH} {Width of the input and output ports.}
core_parameter CNTR_WIDTH {CNTR WIDTH} {Width of the counter register.}