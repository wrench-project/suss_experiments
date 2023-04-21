#!/usr/bin/env python3
import glob
import subprocess
import shlex
import sys
import json
import time





def main():
    workflows = glob.glob("../workflows/*.json")
    platform = "48:10:3.21Gf:1:100Gbps:10Gbps,32:16:4.0125Gf:1:100Gbps:7Gbps,10:48:6.4842Gf:1:100Gbps:8Gbps"

    # Running A_11 for each workflow
    num_trials = 10
    for workflow in workflows:
        command = f"/usr/bin/time -v scheduling_using_simulation_simulator --algorithm_selection_scheme makespan  --cluster_selection_schemes most_local_data --clusters {platform} --core_selection_schemes as_many_as_possible --task_selection_schemes highest_bottom_level --first_scheduler_change_trigger 0 --periodic_scheduler_change_trigger 1.0 --reference_flops 3.21Gf --wrench-energy-simulation --simulation_noise_scheme micro-platform --speculative_work_fraction 1.0 --workflow {workflow}"
        ave_makespan = 0
        ave_rss = 0
        ave_simtime = 0
        ave_ratio = 0
        for trial in range(0,num_trials):
            xp = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            rss = 0
            for line in xp.stderr.decode("utf-8").split('\n'):
                if "MAKESPAN" in line:
                    makespan = float(line.split(" ")[-1])
                elif "Maximum resident set size" in line:
                    rss = 1000 * float(line.split(" ")[-1])

            json_output = json.loads(xp.stdout.decode("utf-8"))
            simtime = json_output["simulation_time"]


            ave_makespan += makespan
            ave_rss += rss
            ave_simtime += simtime
            ave_ratio += makespan / simtime

        ave_makespan /= num_trials
        ave_rss /= num_trials
        ave_simtime /= num_trials
        ave_ratio /= num_trials

        ave_rss /= (1000*1000)

        workflow_name = workflow.split("/")[-1].split("-")[0]
        print(f"{workflow_name} {ave_makespan:.2f} & {ave_simtime:.2f} &   {ave_ratio:.2f} & {ave_rss:.2f}")


    # Running things in parallel
    task_selection_schemes = [
        "most_flops",
        "most_children",
        "most_data",
        "highest_bottom_level"
    ]
    cluster_selection_schemes = [
        "fastest_cores",
        "most_local_data",
        "most_idle_cores",
        "most_idle_cpu_resources"
    ]
    core_selection_schemes = [
        "as_many_as_possible",
        "parallel_efficiency_ninety_percent",
        "parallel_efficiency_fifty_percent"
    ]

    picked_workflow = ""
    for workflow in workflows:
        if "bwa" in workflow:
            picked_workflow = workflow
            break

    max_individual_time = 0
    for task_selection_scheme in task_selection_schemes:
        for cluster_selection_scheme in cluster_selection_schemes:
            for core_selection_scheme in core_selection_schemes:
                command = f"/usr/bin/time -v scheduling_using_simulation_simulator --algorithm_selection_scheme makespan  --cluster_selection_schemes {cluster_selection_scheme} --clusters {platform} --core_selection_schemes {core_selection_scheme} --task_selection_schemes {task_selection_scheme} --first_scheduler_change_trigger 0 --periodic_scheduler_change_trigger 1.0 --reference_flops 3.21Gf --wrench-energy-simulation --simulation_noise_scheme micro-platform --speculative_work_fraction 1.0 --workflow {workflow}"
                t0 = time.time()
                child = subprocess.Popen(command.split(" "))
                child.wait()
                t1 = time.time()
                total = t1-t0
                max_individual_time = max(max_individual_time, total)
    print(f"MAX INDIVIFUAL TIME: {max_individual_time:.2f}")

    children = []
    t0 = time.time()
    for task_selection_scheme in task_selection_schemes:
        for cluster_selection_scheme in cluster_selection_schemes:
            for core_selection_scheme in core_selection_schemes:
                command = f"/usr/bin/time -v scheduling_using_simulation_simulator --algorithm_selection_scheme makespan  --cluster_selection_schemes {cluster_selection_scheme} --clusters {platform} --core_selection_schemes {core_selection_scheme} --task_selection_schemes {task_selection_scheme} --first_scheduler_change_trigger 0 --periodic_scheduler_change_trigger 1.0 --reference_flops 3.21Gf --wrench-energy-simulation --simulation_noise_scheme micro-platform --speculative_work_fraction 1.0 --workflow {workflow}"
                children.append(subprocess.Popen(command.split(" ")))

    for child in children:
        child.wait()

    t1 = time.time()
    total = t1-t0
    print(f"PARALLEL TIME: {total:.2f}")


if __name__ == "__main__":
    main()
