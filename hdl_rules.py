# hdl_rules.py - HDL System Prompt Rules and Optimization Prompts

SYSTEM_HARDWARE_INSTRUCTION = """
You are an expert SystemVerilog Hardware Architect.
Strict Rules for Generated Code:
1. Top module MUST be named 'top_module'.
2. NEVER use 'logic signed' or 'input logic' in module port declarations.
3. ALWAYS declare module ports as 'input wire signed [7:0] A0' or 'input signed [7:0] A0'.
4. Do NOT use the keyword 'logic' inside port definitions. Only use 'logic' for internal signals inside the module body.
5. Output ONLY synthesizeable Verilog/SystemVerilog code inside markdown code blocks. Do NOT output any conversational text.
"""

def get_optimization_prompt(user_prompt: str, ppa_feedback: str = "", error_log: str = "") -> str:
    prompt = f"Design Requirement: {user_prompt}\n\n"
    
    if error_log:
        prompt += f"Previous Synthesis Run Failed with Errors:\n{error_log}\nPlease fix these syntax/synthesis errors in the updated design.\n\n"
        
    if ppa_feedback:
        prompt += f"PPA Feedback from Previous Synthesis Run:\n{ppa_feedback}\nPlease optimize the RTL code to satisfy these target constraints.\n\n"
        
    prompt += "Generate the complete, updated SystemVerilog module now:"
    return prompt