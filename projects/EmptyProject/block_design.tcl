
#==================================================================================================
# block_design.tcl - Create Vivado Project
#
# This script is modification of Anton Potocnik's block_design file
# by Robert Reichert, 2021
#==================================================================================================

### Create all custom IP cores
#source make_cores.tcl 
### Or create specific custom IP cores
#set cores [list \ core1 \ core2]
set cores [list]
foreach core_name $cores {
  set argv [list $core_name $part_name]
  source scripts/core.tcl
}

### Create basic Red Pitaya Block Design
source projects/_basic_block_design/basic_block_design.tcl

#====================================================================================
# IP cores
#====================================================================================

###AXI GPIO IP core
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:axi_gpio axi_gpio_0
set_property -dict [list CONFIG.C_IS_DUAL {1} CONFIG.C_ALL_INPUTS_2 {1}] [get_bd_cells axi_gpio_0]
endgroup

###axis_red_pitaya_adc
startgroup
create_bd_cell -type ip -vlnv pavel-demin:user:axis_red_pitaya_adc axis_red_pitaya_adc_0
endgroup

###axis_red_pitaya_dac
startgroup
create_bd_cell -type ip -vlnv pavel-demin:user:axis_red_pitaya_dac axis_red_pitaya_dac_0
endgroup

###Create clocking_wizard
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:clk_wiz clk_wiz_0
set_property -dict [list CONFIG.PRIM_IN_FREQ.VALUE_SRC USER] [get_bd_cells clk_wiz_0]
set_property -dict [list CONFIG.PRIM_IN_FREQ {125.000} CONFIG.CLKOUT1_REQUESTED_OUT_FREQ {250.000} CONFIG.USE_RESET {false} CONFIG.CLKIN1_JITTER_PS {80.0} CONFIG.MMCM_DIVCLK_DIVIDE {1} CONFIG.MMCM_CLKFBOUT_MULT_F {8.000} CONFIG.MMCM_CLKIN1_PERIOD {8.000} CONFIG.MMCM_CLKOUT0_DIVIDE_F {4.000} CONFIG.CLKOUT1_JITTER {104.759} CONFIG.CLKOUT1_PHASE_ERROR {96.948}] [get_bd_cells clk_wiz_0]
endgroup

###Add IP core: dds
startgroup
create_bd_cell -type ip -vlnv xilinx.com:ip:dds_compiler dds_compiler_0
set_property -dict [list CONFIG.PartsPresent {Phase_Generator_and_SIN_COS_LUT} CONFIG.Parameter_Entry {System_Parameters} CONFIG.Spurious_Free_Dynamic_Range {84} CONFIG.Frequency_Resolution {0.5} CONFIG.Amplitude_Mode {Unit_Circle} CONFIG.DDS_Clock_Rate {125} CONFIG.Noise_Shaping {Auto} CONFIG.Phase_Width {28} CONFIG.Output_Width {14} CONFIG.Has_Phase_Out {false} CONFIG.DATA_Has_TLAST {Not_Required} CONFIG.S_PHASE_Has_TUSER {Not_Required} CONFIG.M_DATA_Has_TUSER {Not_Required} CONFIG.Latency {8} CONFIG.Output_Frequency1 {3.90625}] [get_bd_cells dds_compiler_0]
endgroup


#====================================================================================
# RTL modules 
#====================================================================================


#====================================================================================
# Connections 
#====================================================================================

###connections for ADC IP core
connect_bd_net [get_bd_ports adc_dat_a_i] [get_bd_pins axis_red_pitaya_adc_0/adc_dat_a]
connect_bd_net [get_bd_ports adc_dat_b_i] [get_bd_pins axis_red_pitaya_adc_0/adc_dat_b]

###connections for DAC IP core and more
connect_bd_net [get_bd_ports dac_clk_o] [get_bd_pins axis_red_pitaya_dac_0/dac_clk]
connect_bd_net [get_bd_ports dac_rst_o] [get_bd_pins axis_red_pitaya_dac_0/dac_rst]
connect_bd_net [get_bd_ports dac_sel_o] [get_bd_pins axis_red_pitaya_dac_0/dac_sel]
connect_bd_net [get_bd_ports dac_wrt_o] [get_bd_pins axis_red_pitaya_dac_0/dac_wrt]
connect_bd_net [get_bd_ports dac_dat_o] [get_bd_pins axis_red_pitaya_dac_0/dac_dat]
connect_bd_net [get_bd_pins clk_wiz_0/locked] [get_bd_pins axis_red_pitaya_dac_0/locked]
connect_bd_net [get_bd_pins clk_wiz_0/clk_in1] [get_bd_pins axis_red_pitaya_dac_0/aclk]
connect_bd_net [get_bd_pins clk_wiz_0/clk_out1] [get_bd_pins axis_red_pitaya_dac_0/ddr_clk]
connect_bd_net [get_bd_pins clk_wiz_0/clk_out1] [get_bd_pins axis_red_pitaya_dac_0/wrt_clk]
connect_bd_intf_net [get_bd_intf_pins dds_compiler_0/M_AXIS_DATA] [get_bd_intf_pins axis_red_pitaya_dac_0/S_AXIS]
connect_bd_net [get_bd_pins clk_wiz_0/clk_in1] [get_bd_pins dds_compiler_0/aclk]
connect_bd_net [get_bd_pins dds_compiler_0/aclk] [get_bd_pins axis_red_pitaya_adc_0/aclk]

###Autoconnect AXI GPIO
apply_bd_automation -rule xilinx.com:bd_rule:axi4 -config {Master "/processing_system7_0/M_AXI_GP0" Clk "Auto" }  [get_bd_intf_pins axi_gpio_0/S_AXI]

# ====================================================================================
# Propertys
# ====================================================================================

###Set GPIO register
set_property offset 0x42000000 [get_bd_addr_segs {processing_system7_0/Data/SEG_axi_gpio_0_Reg}]
set_property range 4K [get_bd_addr_segs {processing_system7_0/Data/SEG_axi_gpio_0_Reg}]

# ====================================================================================
# Hierarchies
# ====================================================================================

group_bd_cells SignalGenerator [get_bd_cells axis_red_pitaya_dac_0] [get_bd_cells dds_compiler_0] [get_bd_cells clk_wiz_0] 

group_bd_cells PS7 [get_bd_cells processing_system7_0] [get_bd_cells rst_ps7_0_125M] [get_bd_cells ps7_0_axi_periph]

# ====================================================================================
# Regenerate Layout
# ====================================================================================
regenerate_bd_layout

