#!/usr/bin/env python3
from plot_utils import *

# the following code roughly translates
# from *.py in ./ import *
import os

for module in os.listdir(os.path.dirname(os.path.abspath(__file__))):
	if module == __file__ or module[-3:] != '.py' or ' ' in module:
		continue
	exec("from " + module[:-3] + " import *")
del module


def main():
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)
	file_factors=[1,10,100,1000]
	file_factor=1
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1],file_factor, 2)

	# Generate basic algorithms plot
	sys.stdout.write("\n# BASIC ALGORITHMS PLOT\n")
	sys.stdout.write("#######################\n")
	generate_basic_algorithms_plot(plot_path, result_dicts["basic_algorithms"], best_algorithm_on_average)

	# Compute multi-adaptation statistics
	#sys.stdout.write("\n# ZERO-ERROR, MULTI-ADAPTATION STATISTICS\n")
	#sys.stdout.write("#########################################\n")
	#compute_multi_adaptation_statistics(result_dicts["multi_adaptation"])
	# broken by current data
	
	# Generate the noise violin plots for all cases
	sys.stdout.write("\n# ERROR PLOTS\n")
	sys.stdout.write("#############\n")
	start_noises = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
	for start_noise_index in range(0, len(start_noises)):
		start_noise = start_noises[start_noise_index]
		for end_noise_index in range(0, start_noise_index + 1):
			end_noise = start_noises[end_noise_index]
			plot_single_noise_line(result_dicts, start_noise, end_noise, best_algorithm_on_average,
								   plot_path + "dfb_vs_scenario_noise_" + str(start_noise) + "_mitigated_noise_" + str(end_noise) + ".pdf")


	# Plot adfb line results per workflow / platform
	sys.stdout.write("\n# AVE. DFB PLOTS PER WORKFLOW / PLATFORM\n")
	sys.stdout.write("########################################\n")
	for workflow in workflows:
		for cluster in clusters:
			noise_lines = {}
			for start_noise_index in range(0, len(start_noises)):
				start_noise = start_noises[start_noise_index]
				if start_noise <= 0.0:
					continue
				line = []
				for end_noise_index in range(0, start_noise_index + 1):
					end_noise = start_noises[end_noise_index]
					adfb = compute_adfb(result_dicts, workflow, cluster, start_noise, end_noise)
					line.append(adfb)
				noise_lines[start_noise] = line
			plot_adfb_lines(plot_path, workflow, cluster, noise_lines)

	# No mitigation results
	sys.stdout.write("\n# NO MITIGATION PLOT \n")
	sys.stdout.write("#######################\n")
	plot_no_mitigation(plot_path, result_dicts, best_algorithm_on_average)

	# Rank histogram plot
	sys.stdout.write("\n# RANK HISTOGRAM PLOTS\n")
	sys.stdout.write("########################\n")
	start_noises = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
	plot_cumulative_rank_histograms(plot_path, result_dicts, start_noises)

	# no Contention ideal
	#sys.stdout.write("\n# NO CONTENTION (IDEAL) PLOTS\n")
	#sys.stdout.write("########################\n")
	#start_noises = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
#	
#	plot_no_contention_ideal(plot_path, result_dicts, best_algorithm_on_average)
	sys.stdout.write("\n# IMPORTING FILEFACTOR RESULTS\n")
	sys.stdout.write("########################\n")
	allResults={}
	for factor in file_factors:
	
		result = importData(sys.argv[1],factor,0)[1]
		allResults[factor]=result
	# no Contention noise
	sys.stdout.write("\n# NO CONTENTION (NOISE) PLOTS\n")
	sys.stdout.write("########################\n")
	start_noises = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
	#plot_no_contention_noise(plot_path, result_dicts, best_algorithm_on_average,["srasearch-chameleon-10a-003.json","bwa-chameleon-large-003.json","epigenomics-chameleon-ilmn-4seq-50k-001.json"])
	for factor in file_factors:
		plot_no_contention_noise(plot_path, allResults, factor, best_algorithm_on_average,["1000genome-chameleon-8ch-250k-001.json","epigenomics-chameleon-ilmn-4seq-50k-001.json","srasearch-chameleon-10a-003.json"])
	
# MAIN
if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		pass #dont throw massive error on ctrl+c
