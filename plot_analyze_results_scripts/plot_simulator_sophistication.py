#!/usr/bin/env python3
#import warnings
#warnings.filterwarnings("error")
from plot_utils import *
from mappings import workflow_indices
from mappings import platform_configs

import sys
sys.path.append('../')
from extract_scripts.pretty_dict import pretty_dict

def plot_simulator_sophistication(plot_path, results_dict, noise_dicts,workflows, platforms_to_use):
	
	
	#algs = noNoise[workflow][platform]

	#safeRemove(algs, "us")
	##print("WORKFLOW: " + workflow + "; PLAT=" + platform + "; ALGS:" + str(algs))
	#best = min(algs.values())


if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)

	#sys.stdout.write("\n# NO CONTENTION (IDEAL) RESULTS \n")
	#sys.stdout.write("#######################\n")
	#plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1], 1)
	#plot_no_contention_ideal(plot_path, result_dicts, best_algorithm_on_average)
	sys.stdout.write("\n# NO CONTENTION (NOISE) PLOT \n")
	sys.stdout.write("#######################\n")
	# file_factors=[1,10,100,1000]
	file_factors=[1]
	platforms=[0,1,2]

	for factor in file_factors:
		win=0
		loss=0
		tie=0
		plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1], factor, 1)
		for i in platforms:
			ret=plot_no_contention_noise(plot_path, result_dicts,"no_contention_noise", factor, best_algorithm_on_average,["1000genome-chameleon-8ch-250k-001.json","epigenomics-chameleon-ilmn-4seq-50k-001.json","srasearch-chameleon-10a-003.json"],i)
			win+=ret[0]
			loss+=ret[1]
			tie+=ret[2]
	
		print(f"Agergated | Wins: {win} | Losses: {loss} | Ties: {tie}\n")
		
	for factor in file_factors:
		win=0
		loss=0
		tie=0
		plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1], factor, 1)
		for i in platforms:
			ret=plot_no_contention_noise(plot_path, result_dicts,"no_contention_amdahl_noise", factor, best_algorithm_on_average,["1000genome-chameleon-8ch-250k-001.json","epigenomics-chameleon-ilmn-4seq-50k-001.json","srasearch-chameleon-10a-003.json"],i)
			win+=ret[0]
			loss+=ret[1]
			tie+=ret[2]
	
		print(f"Agergated | Wins: {win} | Losses: {loss} | Ties: {tie}\n")

