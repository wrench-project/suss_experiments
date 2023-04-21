#!/usr/bin/env python3
import glob
import subprocess
import shlex
import sys





def main():
    workflows = glob.glob("../workflows/*.json")
    platform = "48:10:3.21Gf:1:100Gbps:10Gbps,32:16:4.0125Gf:1:100Gbps:7Gbps,10:48:6.4842Gf:1:100Gbps:8Gbps"


    for workflow in workflows:
        command = f"/usr/bin/time -v scheduling_using_simulation_simulator --algorithm_selection_scheme makespan  --cluster_selection_schemes most_local_data --clusters {platform} --core_selection_schemes as_many_as_possible --task_selection_schemes highest_bottom_level --first_scheduler_change_trigger 0 --periodic_scheduler_change_trigger 1.0 --reference_flops 3.21Gf --wrench-energy-simulation --simulation_noise_scheme micro-platform --speculative_work_fraction 1.0 --workflow {workflow}"
        ave_makespan = 0
        ave_rss = 0
        ave_simtime = 0
        ave_ratio = 0
        for trial in range(0,10):
            xp = subprocess.run(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            for line in xp.stderr.decode("utf-8").split('\n'):
                if "MAKESPAN" in line:
                    makespan = float(line.split(" ")[-1])
                elif "Maximum resident set size" in line:
                    rss = 1000 * float(line.split(" ")[-1])
                elif "Elapsed" in line:
                    simtime = line.split(" ")[-1].split(":")[-1]
                    minutes = float(simtime.split(":")[0])
                    seconds = float(simtime.split(":")[1])
                    simetime = minutes*60 + seconds

            ave_makespan += makespan
            ave_rss += rss
            ave_simtime += simtime
            ave_ratio += makespan / simtime

        ave_makespan /= 10
        ave_rss /= 10
        ave_simtime /= 10
        ave_ratio /= 10

        ave_rss /= (1000*1000)

        print(f"{workflow}: f{ave_makespan} f{ave_simtime} f{ave_ratio} f{ave_rss}")
        

if __name__ == "__main__":
    main()
