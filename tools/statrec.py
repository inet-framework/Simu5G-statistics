# Records the run-0 statistical baselines of a Simu5G tree, headless (opp_repl without its MCP server).
#
#   SIMU5G_ROOT=<tree> STATS=<statistics dir> PYTHONPATH="$PYTHONPATH:<opp_repl source dir>" python3 statrec.py
#
# Two passes: every working directory except cars, d2d_multihop, mec and videostreaming_dataset_generator
# (EXCL2), then rnisTest, which the mec exclusion would hide. FILTER=<regex> runs one pass on the
# matching working directories instead. OPP_FILE overrides $SIMU5G_ROOT/simu5g.opp. Prints the
# KEEP/UPDATE/INSERT/SKIP/ERROR counts and every non-KEEP configuration. The python must load
# OMNeT++'s scave bindings ($OMNETPP_ROOT/python on PYTHONPATH); a NameError on read_result_files
# means they are missing, not that the simulations failed.
import os, sys, collections
from opp_repl import *
initialize_logging("INFO", "ERROR", None)
load_opp_file("@opp")
load_opp_file(os.environ.get("OPP_FILE", os.environ["SIMU5G_ROOT"] + "/simu5g.opp"))
v = get_simulation_project_variables()
p = v["simu5g_project"]
p.statistics_folder = os.environ.get("STATS", "statistics")
EXCL2 = r"(^|/)(cars|d2d_multihop|mec|videostreaming_dataset_generator)(/|$)"

def summarize(u, label):
    c = collections.Counter()
    lines = []
    for r in u.results:
        res = r.result
        c[res] += 1
        cfg = r.task.simulation_task.simulation_config
        lines.append(f"{res} {cfg.working_directory} {cfg.config}")
    print(f"== {label}: " + ", ".join(f"{k} {n}" for k, n in sorted(c.items())))
    for l in sorted(lines):
        if not l.startswith("KEEP"):
            print("   " + l)
    sys.stdout.flush()

if os.environ.get("FILTER"):
    u = update_statistical_test_results(simulation_project=p, run_number=0, working_directory_filter=os.environ["FILTER"])
    summarize(u, "filter " + os.environ["FILTER"])
    sys.exit(0)
u = update_statistical_test_results(simulation_project=p, run_number=0, exclude_working_directory_filter=EXCL2)
summarize(u, "main pass")
u2 = update_statistical_test_results(simulation_project=p, run_number=0, working_directory_filter="rnisTest")
summarize(u2, "rnisTest pass")
