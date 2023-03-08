#!/usr/bin/env python3
import socket
import sys
import time
import ast
import socket
import sys
import time
import ast
import random
import subprocess
import glob
import json
import os


def foo(data):
    print(data)
    return data


def main():
    # Argument parsing
    ######################
    try:
        version = sys.argv[1]

        if version == "v3":
            file_factor = " --file_size_factor 1.0 "
            platform_configurations = [
                "48:10:3.21Gf:1:100Gbps:10Gbps",
                "48:10:3.21Gf:1:100Gbps:10Gbps,32:16:4.0125Gf:1:100Gbps:7Gbps",
                "48:10:3.21Gf:1:100Gbps:10Gbps,32:16:4.0125Gf:1:100Gbps:7Gbps,10:48:6.4842Gf:1:100Gbps:8Gbps"
            ]
        else:
            sys.stderr.write("Invalid version argument")
            raise BaseException()

        server = sys.argv[2].split(":")

        root_dir = os.path.abspath(sys.argv[3])
        workflow_dir = "workflows/"
        workflow_json_files = sorted(glob.glob(root_dir + "/" + workflow_dir + "/*.json", recursive=True))
        workflow_json_files = [x.split("/")[-1] for x in workflow_json_files]

        platform_configs = [int(x) for x in sys.argv[4].split(",")]
        workflow_configs = [int(x) for x in sys.argv[5].split(",")]

        run_ideal = "--run-ideal" in sys.argv
        
        no_contention = "--no-contention" in sys.argv


        run_ideal_multi_adaptation = "--run-ideal-multi-adaptation" in sys.argv

        run_noise = "--run-noise" in sys.argv
        if run_noise:
            idx = sys.argv.index("--run-noise")
            start_seed = int(sys.argv[idx + 1])
            end_seed = int(sys.argv[idx + 2])

        if "--help" in sys.argv:
            raise BaseException()

    except BaseException:
        sys.stderr.write("Usage: " + sys.argv[0] +
                         " <version> <server url> <path to root directory> "
                         "<platform configuration list> <workflow configuration list> "
                         "[--no-contention] "
                         "[--run-ideal] "
                         "[--run-ideal-multi-adaptation] "
                         "[--run-noise <start seed> <end seed (inclusive)>] "
                         "\n\n")
        sys.stderr.write("Example: " + sys.argv[0] + " v3 128.171.140.102:443 ../.. 0,1,2 0,1 --run-ideal "
                                                     "--run-ideal-multi-adaptation --run-noise 1000 1005\n\n")
        sys.stderr.write("Platform configs:\n")
        try:
            for i in range(0, len(platform_configurations)):
                sys.stderr.write("\t" + str(i) + ": " + platform_configurations[i] + "\n")
        except BaseException:
            sys.stderr.write("  None found\n")

        sys.stderr.write("Workflow configs:\n")
        try:
            for i in range(0, len(workflow_json_files)):
                sys.stderr.write("\t" + str(i) + ": " + workflow_json_files[i] + "\n")
        except BaseException:
            sys.stderr.write("  None found\n")

        sys.exit(1)

    s = socket.socket()

    s.connect((server[0], int(server[1])))
    #
    # Set a few variables common to all experiments below
    #####################################################
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

    ###############################
    # CREATE EXPERIMENTS
    ###############################
    xps = []

    base_command = "scheduling_using_simulation_simulator "
    base_command += file_factor
    base_command += " --reference_flops 3.21Gf --wrench-energy-simulation "
    base_command += " --first_scheduler_change_trigger 0.00 "
    base_command += " --simulation_noise_scheme micro-platform "
    base_command += " --speculative_work_fraction 1.0 "
    base_command += " --algorithm_selection_scheme makespan "
    base_command += " --wrench-mailbox-pool-size=50000"
    if no_contention:
        base_command += " --no-contention "

    commands_to_run = []
    for platform_config_index in platform_configs:
        platform = platform_configurations[platform_config_index]
        platform_spec = " --clusters " + platform + " "

        # Loop over all workflows
        for workflow_config in workflow_configs:
            workflow_spec = " --workflow " + workflow_dir + workflow_json_files[workflow_config] + " "

            if run_ideal:
                # RUN INDIVIDUAL ALGORITHMS
                for task_selection_scheme in task_selection_schemes:
                    for cluster_selection_scheme in cluster_selection_schemes:
                        for core_selection_scheme in core_selection_schemes:
                            command = base_command + platform_spec + workflow_spec
                            command += " --periodic_scheduler_change_trigger 0.1 "  # useless here of course
                            command += " --task_selection_scheme " + str(task_selection_scheme)
                            command += " --cluster_selection_scheme " + str(cluster_selection_scheme)
                            command += " --core_selection_scheme " + str(core_selection_scheme)
                            commands_to_run.append((command, version))

            if run_ideal_multi_adaptation:
                # RUN ADAPTATION STUFF
                command = base_command + platform_spec + workflow_spec
                command += " --simulation_noise 0.0 "
                command += " --periodic_scheduler_change_trigger 0.1 "
                command += " --task_selection_scheme " + ",".join(task_selection_schemes) + " "
                command += " --cluster_selection_scheme " + ",".join(cluster_selection_schemes) + " "
                command += " --core_selection_scheme " + ",".join(core_selection_schemes) + " "
                commands_to_run.append((command, version))

                command = base_command + platform_spec + workflow_spec
                command += " --simulation_noise 0.0 "
                command += " --periodic_scheduler_change_trigger 0.1 "
                command += " --simulation_noise_reduction 0.0 "
                command += " --adapt-only-if-noise-has-changed "
                command += " --task_selection_scheme " + ",".join(task_selection_schemes) + " "
                command += " --cluster_selection_scheme " + ",".join(cluster_selection_schemes) + " "
                command += " --core_selection_scheme " + ",".join(core_selection_schemes) + " "
                commands_to_run.append((command, version))

            if run_noise:
                # RUN ONE ADAPTATION WITH NOISE, BUT NOT ADAPTING IF NOISE HAS NOT CHANGED
                noises = ["1.0", "0.9", "0.8", "0.7", "0.6", "0.5", "0.4", "0.3", "0.2", "0.1", "0.0"]
                noise_reductions = ["1.0", "0.9", "0.8", "0.7", "0.6", "0.5", "0.4", "0.3", "0.2", "0.1", "0.0"]
                for start_noise_index in range(0, len(noises)):
                    for noise_reduction_index in range(start_noise_index, len(noises)):
                        start_noise = noises[start_noise_index]
                        noise_reduction = noise_reductions[noise_reduction_index]

                        if start_noise == "0.0":
                            seed_range = [42]
                        else:
                            seed_range = range(start_seed, end_seed + 1)

                        for seed in seed_range:
                            command = base_command + platform_spec + workflow_spec
                            command += " --periodic_scheduler_change_trigger 0.1 "
                            command += " --simulation_noise " + str(start_noise) + " "
                            command += " --simulation_noise_seed " + str(seed) + " "
                            command += " --simulation_noise_reduction " + str(noise_reduction) + " "
                            command += " --adapt-only-if-noise-has-changed "
                            command += " --at-most-one-noise-reduction "
                            command += " --at-most-one-adaptation "
                            command += " --task_selection_scheme " + ",".join(task_selection_schemes) + " "
                            command += " --cluster_selection_scheme " + ",".join(cluster_selection_schemes) + " "
                            command += " --core_selection_scheme " + ",".join(core_selection_schemes) + " "
                            commands_to_run.append((command, version))

                # RUN ONE ADAPTATION FOR CASES IN WHICH NOISE HAS NOT CHANGED!
                for start_noise_index in range(0, len(noises)):
                    start_noise = noises[start_noise_index]
                    noise_reduction = "0.0"

                    if start_noise == "0.0":
                        seed_range = [42]
                    else:
                        seed_range = range(start_seed, end_seed + 1)

                    for seed in seed_range:
                        command = base_command + platform_spec + workflow_spec
                        command += " --periodic_scheduler_change_trigger 0.1 "
                        command += " --simulation_noise " + str(start_noise) + " "
                        command += " --simulation_noise_seed " + str(seed) + " "
                        command += " --simulation_noise_reduction " + str(noise_reduction) + " "
                        # command += " --adapt-only-if-noise-has-changed "
                        command += " --at-most-one-adaptation "
                        command += " --at-most-one-noise-reduction "
                        command += " --task_selection_scheme " + ",".join(task_selection_schemes) + " "
                        command += " --cluster_selection_scheme " + ",".join(cluster_selection_schemes) + " "
                        command += " --core_selection_scheme " + ",".join(core_selection_schemes) + " "
                        commands_to_run.append((command, version))

    ###################################
    # RUN STUFF
    ###################################

    # REMOVE DUPLICATES
    xps = sorted(list(set(commands_to_run)))

    sys.stderr.write("Dispaching (up to) " + str(len(xps)) + " experiments\n")

    s.send(str({"cmd": "ADD", "data": xps}).replace("\\","/").encode('utf-8'))
    print(str({"cmd": "ADD", "data": xps}).replace("\\","/"))
    s.close()


if __name__ == "__main__":
    main()
