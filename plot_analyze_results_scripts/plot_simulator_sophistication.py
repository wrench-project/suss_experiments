#!/usr/bin/env python3
# import warnings
# warnings.filterwarnings("error")
from plot_utils import *
from mappings import workflow_indices
from mappings import platform_configs

import sys

sys.path.append('../')
from extract_scripts.pretty_dict import pretty_dict


def plot_simulator_sophistication_dfbs(plot_path, plot_name, result_dicts, workflows, clusters):

    sophistication_levels = ["no_contention_no_amdahl_noise", "no_contention_yes_amdahl_noise",
                             "yes_contention_no_amdahl_noise", "noise"]
    noise_levels = result_dicts[sophistication_levels[0]].keys()
    # pretty_dict(results_dict)
    data_points = {}
    for noise_level in noise_levels:
        data_points[noise_level] = {}
        for sophistication_level in sophistication_levels:
            data_points[noise_level][sophistication_level] = []

    for noise_level in data_points:
        for sophistication_level in sophistication_levels:
            for workflow in workflows:
                for cluster in clusters:
                    # print(f"{noise_level} {sophistication_level} {workflow} {cluster}")
                    makespans = result_dicts[sophistication_level][noise_level][noise_level][workflow][cluster]["us"]
                    best_makespan = float(min(result_dicts["basic_algorithms"][workflow][cluster].values()))
                    for makespan in makespans:
                        dfb = dgfb(best_makespan, makespan)
                        data_points[noise_level][sophistication_level].append(dfb)

    for noise_level in noise_levels:
        output_filename = plot_path + "sophistication_noise_" + str(noise_level) + "_" + plot_name + ".pdf"
        f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(12, 6))
        ax1.yaxis.grid()

        colors = {
            "no_contention_no_amdahl_noise": "r",
            "no_contention_yes_amdahl_noise": "b",
            "yes_contention_no_amdahl_noise": "g",
            "noise": "k"}

        labels = {
            "no_contention_no_amdahl_noise": "no-contention / no-amdahl",
            "no_contention_yes_amdahl_noise": "no-contention / amdahl",
            "yes_contention_no_amdahl_noise": "contention / no-amdahl",
            "noise": "contention / amdahl"}

        for sophistication_level in sophistication_levels:
            cdf_values = []
            dfb_values = [x/10.0 for x in range(0, 1000, 1)]
            for dfb_value in dfb_values:
                cdf_values.append(100 * sum([x <= dfb_value for x in data_points[noise_level][sophistication_level]]) /
                                  len(data_points[noise_level][sophistication_level]))

            ax1.plot(dfb_values, cdf_values, colors[sophistication_level] + "-",
                     linewidth=2, label=labels[sophistication_level])

        plt.xticks(range(0,101,10))
        plt.grid(which='both', linestyle=':')
        plt.xlabel("% degradation from best (dfb)")
        plt.ylabel("Fraction of experimental scenarios (%)")

        plt.legend()
        plt.savefig(output_filename)
        plt.close()
        sys.stdout.write("Generated plot '" + output_filename + "'\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
        sys.exit(1)

    plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = \
        importData(sys.argv[1], file_factor=1, verbosity=1)

    # platforms = clusters
    platforms = clusters[0:3]
    plot_simulator_sophistication_dfbs(plot_path, "ALL", result_dicts, workflows, platforms)

    for workflow in workflows:
        plot_simulator_sophistication_dfbs(plot_path, workflow.split("-")[0], result_dicts, [workflow], platforms)
