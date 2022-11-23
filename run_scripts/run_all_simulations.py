#!/usr/bin/env python3
import random
import time
import subprocess
import glob
from multiprocessing import Pool
import sys
import json
import os
from pymongo import MongoClient

global collection


def run_simulation(arg):

    (command_to_run, docker_container_id, mongo_url, version) = arg

    docker_prefix = "docker exec -it " + docker_container_id + " bash -c "
    print_json_command_to_run = docker_prefix + "\"" + command_to_run + " --print_JSON " + " 2> /dev/null\""
    real_command_to_run = docker_prefix + "\"" + command_to_run + " 2> /dev/null\""

    # Get the input JSON to check on whether we really need to run this
    attempt = 0
    while attempt < 10:
        if attempt > 0:
            sys.stderr.write("!")
        attempt += 1
        try:
            # Check if already done
            json_output = subprocess.check_output(print_json_command_to_run, shell=True)
            config = json.loads(json_output)

            mongo_client = MongoClient(host=mongo_url, serverSelectionTimeoutMS=1000)
            mydb = mongo_client["scheduling_with_simulation"]
            collection = mydb["results_" + version]

            if collection.find_one(config):
                sys.stderr.write(".")
                sys.stderr.flush()
                mongo_client.close()
                return

            # Run the simulator
            json_output = subprocess.check_output(real_command_to_run, shell=True, stderr=subprocess.DEVNULL)
            result = json.loads(json_output)

            # Update the DB
            collection.insert_one(result)
            sys.stderr.write("X")
            sys.stderr.flush()
            mongo_client.close()
            break

        except BaseException:
            time.sleep(1)
            continue

    if attempt == 10:
        sys.stderr.write(command_to_run)
        sys.stderr.write("TO MANY ATTEMPTS, SOMETHING'S WRONG")
        return


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

        mongo_url = sys.argv[2]
        root_dir = os.path.abspath(sys.argv[3])
        workflow_dir = "workflows/"
        workflow_json_files = sorted(glob.glob(root_dir + "/" + workflow_dir + "/*.json", recursive=True))
        workflow_json_files = [x.split("/")[-1] for x in workflow_json_files]
        num_threads = int(sys.argv[4])
        platform_configs = [int(x) for x in sys.argv[5].split(",")]
        workflow_configs = [int(x) for x in sys.argv[6].split(",")]

        run_ideal = "--run-ideal" in sys.argv

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
                         " <version> <mongourl> <path to root directory> <num threads>"
                         "<platform configuration list> <workflow configuration list> "
                         "[--run-ideal] "
                         "[--run-ideal-multi-adaptation] "
                         "[--run-noise <start seed> <end seed (inclusive)>] "
                         "\n\n")
        sys.stderr.write("Example: " + sys.argv[0] + " v3 mongodb://128.171.140.102:443 .. 8 0,1,2 0,1 --run-ideal "
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

    #
    # Setup Mongo
    ####################
    try:
        mongo_client = MongoClient(host=mongo_url, serverSelectionTimeoutMS=1000)
        mongo_client.server_info()
    except:
        sys.stderr.write("Cannot connect to Mongo... aborting\n")
        sys.exit(1)

    #
    # Start Docker container
    ##############################
    docker_command = "docker run -it -d -v " + root_dir + ":/home/me jsspp_journal"
    docker_container_id = subprocess.check_output(docker_command, shell=True).decode("utf-8").rstrip()

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

    commands_to_run = []

    # Loop over all platforms
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
                            commands_to_run.append((command, docker_container_id, mongo_url, version))

            if run_ideal_multi_adaptation:
                # RUN ADAPTATION STUFF
                command = base_command + platform_spec + workflow_spec
                command += " --simulation_noise 0.0 "
                command += " --periodic_scheduler_change_trigger 0.1 "
                command += " --task_selection_scheme " + ",".join(task_selection_schemes) + " "
                command += " --cluster_selection_scheme " + ",".join(cluster_selection_schemes) + " "
                command += " --core_selection_scheme " + ",".join(core_selection_schemes) + " "
                commands_to_run.append((command, docker_container_id, mongo_url, version))

                command = base_command + platform_spec + workflow_spec
                command += " --simulation_noise 0.0 "
                command += " --periodic_scheduler_change_trigger 0.1 "
                command += " --simulation_noise_reduction 0.0 "
                command += " --adapt-only-if-noise-has-changed "
                command += " --task_selection_scheme " + ",".join(task_selection_schemes) + " "
                command += " --cluster_selection_scheme " + ",".join(cluster_selection_schemes) + " "
                command += " --core_selection_scheme " + ",".join(core_selection_schemes) + " "
                commands_to_run.append((command, docker_container_id, mongo_url, version))


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
                            commands_to_run.append((command, docker_container_id, mongo_url, version))

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
                            #command += " --adapt-only-if-noise-has-changed "
                            command += " --at-most-one-adaptation "
                            command += " --at-most-one-noise-reduction "
                            command += " --task_selection_scheme " + ",".join(task_selection_schemes) + " "
                            command += " --cluster_selection_scheme " + ",".join(cluster_selection_schemes) + " "
                            command += " --core_selection_scheme " + ",".join(core_selection_schemes) + " "
                            commands_to_run.append((command, docker_container_id, mongo_url, version))


    ###################################
    # RUN STUFF
    ###################################

    # REMOVE DUPLICATES
    xps = sorted(list(set(commands_to_run)))

    sys.stderr.write("Running (up to) " + str(len(xps)) + " experiments\n")

    with Pool(num_threads) as p:
        p.map(run_simulation, xps)

    #############################
    # CLEAN UP
    #############################
    docker_command = "docker kill " + docker_container_id
    os.system(docker_command)
    sys.stderr.write("\n") # avoid weird terminal stuff?


if __name__ == "__main__":
    main()
