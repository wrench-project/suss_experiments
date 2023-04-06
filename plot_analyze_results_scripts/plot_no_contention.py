#!/usr/bin/env python3
from plot_utils import *
def plot_no_contention_ideal(plot_path, results_dict, best_algorithm_on_average):
	baseline = results_dict["basic_algorithms"]
	contention = results_dict["no_contention"]
	for workflow in contention:
		for platform in contention[workflow]:
			best=""
			bestv=100000000000000
			for alg in contention[workflow][platform]:
				if float(contention[workflow][platform][alg])<bestv:
					bestv=float(contention[workflow][platform][alg])
					best=alg
			realBest= min(baseline[workflow][platform].values())
			print(round(dgfb(realBest,baseline[workflow][platform][best]),2),workflow,platform)
def plot_no_contention_noise(plot_path, results_dict, best_algorithm_on_average):
	baseline = results_dict["basic_algorithms"]
	contention = results_dict["no_contention"]
	for workflow in contention:
		for platform in contention[workflow]:
			best=""
			bestv=100000000000000
			for alg in contention[workflow][platform]:
				if float(contention[workflow][platform][alg])<bestv:
					bestv=float(contention[workflow][platform][alg])
					best=alg
			realBest= min(baseline[workflow][platform].values())
			print(round(dgfb(realBest,baseline[workflow][platform][best]),2),workflow,platform)
if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)

	sys.stdout.write("\n# NO CONTENTION (IDEAL) PLOT \n")
	sys.stdout.write("#######################\n")
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1], 1)
	plot_no_contention_ideal(plot_path, result_dicts, best_algorithm_on_average)
	sys.stdout.write("\n# NO CONTENTION (NOISE) PLOT \n")
	sys.stdout.write("#######################\n")
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1], 1)
	plot_no_contention_ideal(plot_path, result_dicts, best_algorithm_on_average)
	
