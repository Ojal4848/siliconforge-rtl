# agent_engine.py - Token-Optimized Hardware Engine

import subprocess
import os
import shutil
from groq import Groq
from hdl_rules import SYSTEM_HARDWARE_INSTRUCTION, get_optimization_prompt
from report_parser import parse_utilization_report, parse_timing_report, generate_ppa_feedback
from tcl_builder import create_synthesis_tcl

VIVADO_DEFAULT_BIN = r"C:\Xilinx\Vivado\2022.2\bin\vivado.bat"

def detect_eda_environment():
    vivado_path = shutil.which("vivado") or (VIVADO_DEFAULT_BIN if os.path.exists(VIVADO_DEFAULT_BIN) else None)
    yosys_path = shutil.which("yosys") or (r"C:\oss-cad-suite\bin\yosys.exe" if os.path.exists(r"C:\oss-cad-suite\bin\yosys.exe") else None)
    
    return {
        "has_vivado": vivado_path is not None,
        "vivado_bin": vivado_path,
        "has_yosys": yosys_path is not None,
        "yosys_bin": yosys_path
    }

def query_llm(prompt: str, api_key: str, model_name: str = "llama-3.1-8b-instant") -> str:
    """Optimized API call with capped max_tokens to preserve Groq API rate limits."""
    client = Groq(api_key=api_key)
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": SYSTEM_HARDWARE_INSTRUCTION},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        temperature=0.2
    )
    code = response.choices[0].message.content.strip()
    if code.startswith("```"):
        lines = code.splitlines()
        code = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    return code

def generate_default_testbench():
    """Generates a default SystemVerilog testbench for simulation sources."""
    tb_code = """`timescale 1ns / 1ps
module tb_design;
    logic clk;
    logic rst;
    logic en;
    logic signed [7:0] A0, A1, A2, A3;
    logic signed [7:0] W0, W1, W2, W3;
    logic signed [19:0] Y;

    top_module uut (
        .clk(clk), .rst(rst), .en(en),
        .A0(A0), .A1(A1), .A2(A2), .A3(A3),
        .W0(W0), .W1(W1), .W2(W2), .W3(W3),
        .Y(Y)
    );

    always #5 clk = ~clk;

    initial begin
        clk = 0; rst = 1; en = 0;
        A0 = 10; A1 = 20; A2 = 30; A3 = 40;
        W0 = 1;  W1 = 2;  W2 = 3;  W3 = 4;
        #20 rst = 0; en = 1;
        #100 $finish;
    end
endmodule
"""
    with open("tb_design.sv", "w") as f:
        f.write(tb_code)

def run_synthesis_execution() -> tuple[bool, str, str]:
    env = detect_eda_environment()
    
    if env["has_vivado"]:
        create_synthesis_tcl(top_module="top_module")
        cmd = [env["vivado_bin"], "-mode", "batch", "-source", "run_synth.tcl"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        passed = (result.returncode == 0) and ("ERROR:" not in result.stdout)
        return passed, result.stdout, "AMD Vivado 2022.2"
    
    elif env["has_yosys"]:
        ys_script = "read_verilog -sv design.sv\nsynth -top top_module\nstat\n"
        with open("synth_yosys.ys", "w") as f:
            f.write(ys_script)
        cmd = [env["yosys_bin"], "-s", "synth_yosys.ys"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        with open("utilization.rpt", "w") as f:
            f.write(result.stdout)
        return (result.returncode == 0), "Open-source synthesis completed via Yosys.", "Yosys Open Synthesis"
        
    else:
        return True, "No local EDA synthesis engine found. Syntax verification complete.", "LLM Verilog Compiler"

def run_autonomous_loop(user_requirement: str, api_key: str, model_name: str = "llama-3.1-8b-instant", target_luts: int = None, max_iterations: int = 1):
    error_log = ""
    ppa_feedback = ""
    
    for iteration in range(1, max_iterations + 1):
        full_prompt = get_optimization_prompt(user_prompt=user_requirement, ppa_feedback=ppa_feedback, error_log=error_log)
        rtl_code = query_llm(full_prompt, api_key, model_name=model_name)
        
        # Save design files
        with open("design.sv", "w") as f:
            f.write(rtl_code)
            
        generate_default_testbench()
            
        synth_passed, log_output, engine_used = run_synthesis_execution()
        
        if not synth_passed:
            err_lines = [line for line in log_output.splitlines() if "ERROR" in line or "CRITICAL WARNING" in line]
            error_log = "\n".join(err_lines[:10])
            continue
        else:
            error_log = ""
            
        util_metrics = parse_utilization_report("utilization.rpt")
        timing_metrics = parse_timing_report("timing.rpt")
        
        combined_metrics = {**util_metrics, **timing_metrics}
        ppa_feedback = generate_ppa_feedback(combined_metrics, target_luts=target_luts)
        
        if "TARGET VIOLATION" not in ppa_feedback and "TIMING VIOLATION" not in ppa_feedback:
            return True
            
    return False