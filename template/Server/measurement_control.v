`timescale 1 ns / 1 ps

module measurement_control #
(
  parameter MAX_SAMPLE_RATE_WIDTH = 16,
  parameter MAX_SAMPLE_NR_WIDTH = 10
)
(
  // Inputs
  input  wire                        aclk,
  input  wire  [31:0]                conf,
  input  wire                        aresetn,
	
  // Outputs
  output wire                        writer_clk,
  output wire                        writer_resetn,
  output wire [31:0]                 ready,
  output wire [31:0]                 sample
);
  
  reg [MAX_SAMPLE_RATE_WIDTH-1:0] count_rate_reg = {(MAX_SAMPLE_RATE_WIDTH){1'b0}};
  reg [MAX_SAMPLE_NR_WIDTH-1:0] count_nr_reg = {(MAX_SAMPLE_NR_WIDTH){1'b0}};
  reg clk_reg = 1'b0;
  reg ready_reg = 1'b0;
  
  assign writer_clk = clk_reg; //~ready_reg && aresetn ? clk_reg : 1'b0;
  assign writer_resetn = ~ready_reg && aresetn;
  assign ready[31:31] = ready_reg;
  assign sample[MAX_SAMPLE_NR_WIDTH-2:1] = ~ready_reg ? count_nr_reg : {(MAX_SAMPLE_NR_WIDTH){1'b0}};
  assign sample[0:0] = ready_reg;

  always @ (aclk)
  begin
    count_rate_reg <= count_rate_reg + 1;
    if (count_rate_reg>=(1<<conf[28:24])-1)
    begin
        count_rate_reg <= {(MAX_SAMPLE_RATE_WIDTH){1'b0}};
        clk_reg <= ~clk_reg;
    end
  end
  
  always @ (posedge clk_reg)
  begin  
      if(~aresetn)
      begin
        ready_reg <= 1'b0;
        count_nr_reg <= {(MAX_SAMPLE_NR_WIDTH){1'b0}};
      end
      else
      begin
          count_nr_reg <= count_nr_reg + 1;
          if (count_nr_reg>=(1<<conf[23:16])-1)
          begin
              ready_reg <= 1'b1;
              count_nr_reg <= {(MAX_SAMPLE_NR_WIDTH){1'b0}};
          end
      end
  end
  
endmodule