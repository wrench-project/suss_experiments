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
def plot_no_contention_noise(plot_path, results_dict, best_algorithm_on_average,workflows):
	# (Re) Compute the dfb of the best_algorithm_on_average
	noNoise = results_dict["basic_algorithms"]


	# Compute our dfb for all noises
	averages = {}
	flats = {}
	errors = {}
	noiseV=results_dict["noise"]
	contentionV=results_dict["no_contention_noise"]
	for base_noise in noiseV:
		if not base_noise in contentionV or not base_noise in contentionV[base_noise] :
			continue
		transMap = {}

		noReduction = noiseV[base_noise][base_noise]
		noContention= contentionV[base_noise][base_noise]
		
		for workflow in workflows:
			if not workflow in noReduction or not workflow in noContention:
				continue
			for platform in noNoise[workflow]:
				if not platform in noReduction[workflow] or not platform in noContention[workflow]:
					continue
				# print(workform)
				try:
					# print(noise)
					# print(noNoise[workflow][platform])
					algs = noNoise[workflow][platform]
					
					safeRemove(algs, "us")
					best = min(algs.values())
					if not workflow in transMap:
						transMap[workflow]={}
					transMap[workflow][platform] = {"noise":[],"noContention":[]}
					points = noReduction[workflow][platform]["us"].copy()
					for i in range(len(points)):
						points[i] = dgfb(best, points[i])
					transMap[workflow][platform]["noise"] = points

					points = noContention[workflow][platform]["us"].copy()
					for i in range(len(points)):
						points[i] = dgfb(best, points[i])
					transMap[workflow][platform]["noContention"] = points
				except KeyError:
					break
				except ZeroDivisionError:
					break
		for workflow in transMap:
			if not workflow in flats:
				flats[workflow]={}
				averages[workflow]={}
				errors[workflow]={}
			if not base_noise in flats[workflow]:
				flats[workflow][base_noise] = {"noise":[],"noContention":[]}
				averages[workflow][base_noise]={}
				errors[workflow][base_noise]={}
			for platform in transMap[workflow]:
				for point in transMap[workflow][platform]["noise"]:
					flats[workflow][base_noise]["noise"].append(point)
				for point in transMap[workflow][platform]["noContention"]:
					flats[workflow][base_noise]["noContention"].append(point)
			#print(flats[workflow][base_noise])
			std_error = np.std(flats[workflow][base_noise]["noise"], ddof=1) / np.sqrt(len(flats[workflow][base_noise]["noise"]))
			average = sum(flats[workflow][base_noise]["noise"]) / len(flats[workflow][base_noise]["noise"])
			averages[workflow][base_noise]["noise"]=average
			errors[workflow][base_noise]["noise"]=std_error
			std_error = np.std(flats[workflow][base_noise]["noContention"], ddof=1) / np.sqrt(len(flats[workflow][base_noise]["noContention"]))
			average = sum(flats[workflow][base_noise]["noContention"]) / len(flats[workflow][base_noise]["noContention"])
			averages[workflow][base_noise]["noContention"]=average
			errors[workflow][base_noise]["noContention"]=std_error
	finalAverages={}
	finalErrors={}	
	for workflow in averages:
		finalAverages[workflow]={}
		finalErrors[workflow]={}
		finalAverages[workflow]["noise"]=[None] * 11
		finalErrors[workflow]["noise"]=[None] * 11
		finalAverages[workflow]["noContention"]=[None] * 11
		finalErrors[workflow]["noContention"]=[None] * 11
		for i in range(0,11):
			key=i/10
			
			finalAverages[workflow]["noise"][i]=averages[workflow][key]["noise"]
			finalErrors[workflow]["noise"][i]=	errors[workflow][key]["noise"]
			finalAverages[workflow]["noContention"][i]=averages[workflow][key]["noContention"]
			finalErrors[workflow]["noContention"][i]=	errors[workflow][key]["noContention"]
	for workflow in finalAverages:
		print(workflow)
		for sub in finalAverages[workflow]:
			print("\t",sub,finalAverages[workflow][sub])
			
	for workflow in finalAverages:
		print(workflow)
		for sub in finalAverages[workflow]:
			print("\t",sub,finalErrors[workflow][sub])
def _plot_no_mitigation(plot_path, results_dict, best_algorithm_on_average):
	# (Re) Compute the dfb of the best_algorithm_on_average
	noNoise = results_dict["basic_algorithms"]
	best_algorithm_on_average_ave_dfb = 0
	best_algorithm_on_average_ave_dfb_count = 0

	for workflow in noNoise:
		for platform in noNoise[workflow]:
			algs = noNoise[workflow][platform]
			best = min(algs.values())
			best_algorithm_on_average_ave_dfb += dgfb(best, noNoise[workflow][platform][best_algorithm_on_average])
			best_algorithm_on_average_ave_dfb_count += 1

	best_algorithm_on_average_ave_dfb /= best_algorithm_on_average_ave_dfb_count

	# Compute our dfb for all noises
	averages = []
	flats = {}
	maxima = []
	minima = []
	errors = []
	for base_noise in results_dict["noise"]:
		if base_noise == 0.0:
			continue
		# todo rework for point distributions
		transMap = {}

		noReduction = results_dict["noise"][base_noise][base_noise]

		for workflow in noNoise:
			for platform in noNoise[workflow]:
				workform = "W" + str(workflow_index_map[workflow]) + ":P" + str(cluster_index_map[platform])
				# print(workform)
				try:
					# print(noise)
					# print(noNoise[workflow][platform])
					algs = noNoise[workflow][platform]

					safeRemove(algs, "us")
					best = min(algs.values())

					transMap[workform] = []
					points = noReduction[workflow][platform]["us"].copy()
					for i in range(len(points)):
						points[i] = dgfb(best, points[i])
					# print(points)
					transMap[workform] = points
				except KeyError:
					break
				except ZeroDivisionError:
					break

		flats[base_noise] = []
		for workform in transMap:
			for point in transMap[workform]:
				flats[base_noise].append(point)
		std_error = np.std(flats[base_noise], ddof=1) / np.sqrt(len(flats[base_noise]))
		average = sum(flats[base_noise]) / len(flats[base_noise])
		averages.append(average)
		maxima.append(max(flats[base_noise]))
		minima.append(min(flats[base_noise]))
		errors.append(std_error)

	fontsize = 18
	f, ax1 = plt.subplots(1, 1, sharey=True, figsize=(12, 6))
	ax1.yaxis.grid()
	display_width = 0.027

	handles = []
	x_value = 0.1
	x_ticks = range(0, 10)
	x_ticklabels = [.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]

	ax1.set_xticks(x_ticks)
	ax1.set_xticklabels(x_ticklabels, rotation=45, fontsize=fontsize - 2)

	ax1.set_ylabel("% degradation from best (dfb)", fontsize=fontsize)
	ax1.set_xlabel("Simulation error magnitude ($e$)", fontsize=fontsize)
	ax1.invert_xaxis()
	ax1.plot([x_ticks[0]-0.5, x_ticks[-1]+0.5], [best_algorithm_on_average_ave_dfb, best_algorithm_on_average_ave_dfb], 'r-')
	ax1.plot(range(0, len(averages)), averages, 'b-', linewidth=2)

	pos = x_ticks[0]
	for base_noise in flats:
		plot_violin(ax1, pos, 0.6, flats[base_noise], "yellow", 0.5)
		percentage_above = 100.0 * len([x for x in flats[base_noise] if x > best_algorithm_on_average_ave_dfb]) / len(flats[base_noise])
		plt.text(pos -0.05, best_algorithm_on_average_ave_dfb + 0.3, "{:.2f}".format(round(percentage_above, 2)) + "%", fontsize=fontsize-3)
		plt.text(pos -0.05, best_algorithm_on_average_ave_dfb - 0.9, "{:.2f}".format(round(100 - percentage_above, 2)) + "%", fontsize=fontsize-3)
		pos += 1

	#	ax1.errorbar(range(0, len(averages)), averages, yerr=errors, capsize=10)
	# Create the figure

	plt.ylim([0,20])

	plt.yticks(fontsize=fontsize)
	f.tight_layout()

	output_filename = plot_path + "dfb_vs_error_full.pdf"
	plt.savefig(output_filename)
	plt.close()
	sys.stdout.write("Generated plot '" + output_filename + "'\n")
	
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
	plot_no_contention_noise(plot_path, result_dicts, best_algorithm_on_average,["srasearch-chameleon-10a-003.json","bwa-chameleon-large-003.json"])
	
