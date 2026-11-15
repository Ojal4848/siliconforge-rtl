# tcl_builder.py - Absolute Path Vivado Project Generator
import os

def create_synthesis_tcl(top_module="top_module"):
    # Convert file paths to absolute paths with forward slashes for Vivado TCL
    design_path = os.path.abspath("design.sv").replace("\\", "/")
    tb_path = os.path.abspath("tb_design.sv").replace("\\", "/")

    tcl_content = f"""
    # Create or overwrite a persistent Vivado Project
    create_project -force agent_project ./agent_project -part xcku035-fbva900-2-e
    
    # Import design file into Vivado Design Sources
    if {{[file exists "{design_path}"]}} {{
        add_files -norecurse "{design_path}"
        set_property file_type {{SystemVerilog}} [get_files "{design_path}"]
    }}
    
    # Import testbench into Vivado Simulation Sources
    if {{[file exists "{tb_path}"]}} {{
        add_files -fileset sim_1 -norecurse "{tb_path}"
        set_property file_type {{SystemVerilog}} [get_files "{tb_path}"]
    }}
    
    update_compile_order -fileset sources_1
    update_compile_order -fileset sim_1
    
    # Run Synthesis
    synth_design -top {top_module} -part xcku035-fbva900-2-e
    
    # Write Out PPA Metric Reports
    report_utilization -file utilization.rpt
    report_timing_summary -file timing.rpt
    
    # Save the project state permanently
    save_project_as -force agent_project ./agent_project
    """
    with open("run_synth.tcl", "w") as f:
        f.write(tcl_content)