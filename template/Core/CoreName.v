
`timescale 1 ns / 1 ps

module <CoreName> #
(
  parameter integer <PARAMETER_SAMPLE> = 32,
)
(
  // Bus signals (Slave)
  output wire           s_axis_tready,
  input  wire [32:0] 	s_axis_tdata,
  input  wire           s_axis_tvalid,
  
  //Inputs
  input  wire           sig1,
  
  //Outputs
  input  wire           sig2
);

endmodule
