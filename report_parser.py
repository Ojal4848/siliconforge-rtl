# report_parser.py - Reads and extracts PPA metrics from Vivado report files

import re
import os

def parse_utilization_report(util_file="utilization.rpt") -> dict:
    """Extracts LUT, FF, and BRAM usage from Vivado utilization report."""
    metrics = {"luts": None, "ffs": None, "brams": None}
    if not os.path.exists(util_file):
        return metrics

    with open(util_file, "r") as f:
        content = f.read()

    # Search for Slice LUTs count
    lut_match = re.search(r"\|\s*Slice LUTs\s*\|\s*(\d+)\s*\|", content)
    if lut_match:
        metrics["luts"] = int(lut_match.group(1))

    # Search for Register as Flip Flop count
    ff_match = re.search(r"\|\s*Register as Flip Flop\s*\|\s*(\d+)\s*\|", content)
    if ff_match:
        metrics["ffs"] = int(ff_match.group(1))

    # Search for Block RAM count
    bram_match = re.search(r"\|\s*Block RAM Tile\s*\|\s*([\d\.]+)\s*\|", content)
    if bram_match:
        metrics["brams"] = float(bram_match.group(1))

    return metrics

def parse_timing_report(timing_file="timing.rpt") -> dict:
    """Extracts Worst Negative Slack (WNS) to verify timing closure."""
    metrics = {"wns": None, "timing_met": False}
    if not os.path.exists(timing_file):
        return metrics

    with open(timing_file, "r") as f:
        content = f.read()

    # Search for WNS value in summary table
    wns_match = re.search(r"WNS\(ns\)\s+TNS\(ns\).*\n[-+\s]+\n\s*([-\d\.]+)", content)
    if wns_match:
        wns = float(wns_match.group(1))
        metrics["wns"] = wns
        metrics["timing_met"] = wns >= 0.0

    return metrics

def generate_ppa_feedback(metrics: dict, target_luts: int = None, target_freq_mhz: float = None) -> str:
    """Generates feedback string comparing actual metrics to user targets."""
    feedback_lines = []
    
    if metrics.get("luts") is not None:
        luts = metrics["luts"]
        feedback_lines.append(f"- Area Usage: {luts} LUTs.")
        if target_luts and luts > target_luts:
            feedback_lines.append(
                f"  ⚠️ TARGET VIOLATION: Used {luts} LUTs, exceeding target max of {target_luts} LUTs. "
                f"Reduce logic width or share hardware resources."
            )

    if metrics.get("wns") is not None:
        wns = metrics["wns"]
        feedback_lines.append(f"- Timing WNS: {wns} ns.")
        if wns < 0:
            feedback_lines.append(
                f"  ⚠️ TIMING VIOLATION: Negative slack detected ({wns} ns). "
                f"Add pipeline register stages to break critical paths."
            )
            
    return "\n".join(feedback_lines)