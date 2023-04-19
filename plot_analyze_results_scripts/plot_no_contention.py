#!/usr/bin/env python3
#import warnings
#warnings.filterwarnings("error")
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


def plot_no_contention_noise(plot_path, results_dict, best_algorithm_on_average, workflows):
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
				if len(platform) < 80: #p3 only
					continue
				if not platform in noReduction[workflow] or not platform in noContention[workflow]:
					continue
				#print(platform)
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
			#print(workflow,base_noise)
			#print(flats[workflow][base_noise]["noise"])
			if len(flats[workflow][base_noise]["noise"])==1:
				std_error=0;
			else:
				std_error = np.std(flats[workflow][base_noise]["noise"], ddof=1) / np.sqrt(len(flats[workflow][base_noise]["noise"]))
			average = sum(flats[workflow][base_noise]["noise"]) / len(flats[workflow][base_noise]["noise"])
			averages[workflow][base_noise]["noise"]=average
			errors[workflow][base_noise]["noise"]=std_error
			if len(flats[workflow][base_noise]["noContention"]):
				std_error=0;
			else:
				std_error = np.std(flats[workflow][base_noise]["noContention"], ddof=1) / np.sqrt(len(flats[workflow][base_noise]["noContention"]))
			if len(flats[workflow][base_noise]["noContention"])>0:
				average = sum(flats[workflow][base_noise]["noContention"]) / len(flats[workflow][base_noise]["noContention"])
			else:
				average = sum(flats[workflow][base_noise]["noContention"]) / 1
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
	averages=finalAverages
	errors=finalErrors
	fontsize = 18

	# Create the figure and subplots
	f, (ax1, ax2) = plt.subplots(2, 1, sharex=True,sharey=False, figsize=(12, 6))
	#f.subplots_adjust(hspace=0.2)

	# Set grid and display width
	ax1.yaxis.grid()
	ax2.yaxis.grid()
	display_width = 0.027

	# Set x-ticks and labels
	x_ticks = range(0, 11)
	x_ticklabels = [0,.1, .2, .3, .4, .5, .6, .7, .8, .9, 1.0]
	ax2.set_xticks(x_ticks)
	ax1.tick_params(axis='y', labelsize=fontsize - 2)
	ax2.tick_params(axis='y', labelsize=fontsize - 2)
	ax1.set_yticks(range(0, 81, 10))
	ax2.set_yticks(range(0, 11, 2))
	ax2.set_xticklabels(x_ticklabels, rotation=45, fontsize=fontsize - 2)

	# Set y-axis labels
	#plt.set_ylabel("% degradation from best (dfb)", fontsize=fontsize)
	ax2.set_ylabel(" ", fontsize=fontsize)
	f.text(0.02, 0.5, '% degradation from best (dfb)', ha='center', va='center', rotation='vertical', fontsize=fontsize)

	ax2.set_xlabel("Simulation error magnitude ($e$)", fontsize=fontsize)


	# Set y-axis limits
	ax1.set_ylim([0,80])
	ax2.set_ylim([0,10])

	# Create handles for legend
	handles = []

	# Set colors for each workflow
	colors = {}
	n = 0
	cmap = plt.cm.get_cmap("hsv", len(averages) + 1)
	for workflow in averages:
		colors[workflow] = cmap(n)
		n += 1
	#print(averages.keys())
	#return
	# Plot first dataset on top subplot
	
	# Invert x-axis
	ax1.invert_xaxis()
	dataset1='srasearch-chameleon-10a-003.json'
	ax1.errorbar(range(0, len(averages[dataset1]["noise"])), 
				 averages[dataset1]["noise"], 
				 yerr=errors[dataset1]["noise"], 
				 capsize=5,
				 color=colors[dataset1], 
				 label=dataset1.split("-")[0]+" with contention",
				 ecolor='black',zorder=1)
	ax1.errorbar(range(0, len(averages[dataset1]["noContention"])), 
				 averages[dataset1]["noContention"], 
				 yerr=errors[dataset1]["noContention"], 
				 capsize=5,
				 color=colors[dataset1], 
				 linestyle='dashed', 
				 label=dataset1.split("-")[0]+" without contention",
					 ecolor='black',zorder=10)

	# Plot other two datasets on bottom subplot
	for workflow in [ 'bwa-chameleon-large-003.json', 'epigenomics-chameleon-ilmn-4seq-50k-001.json']:
		ax2.errorbar(range(0, len(averages[workflow]["noise"])), 
					 averages[workflow]["noise"], 
					 yerr=errors[workflow]["noise"], 
					 capsize=5,
					 color=colors[workflow], 
					 label=workflow.split("-")[0]+" with contention",
					 ecolor='black',zorder=10)
		ax2.errorbar(range(0, len(averages[workflow]["noContention"])), 
					 averages[workflow]["noContention"], 
					 yerr=errors[workflow]["noContention"], 
					 capsize=5,
					 color=colors[workflow], 
					 linestyle='dashed', 
					 label=workflow.split("-")[0]+" without contention",
					 ecolor='black',zorder=1)

	# Set legend
	f.legend(loc=7)

	#plt.ylim([0,70])

	plt.yticks(fontsize=fontsize-2)
	f.tight_layout()

	output_filename = plot_path + "no_contention_noise.pdf"
	plt.savefig(output_filename)
	plt.close()
	sys.stdout.write("Generated plot '" + output_filename + "'\n")
	#print(averages)



if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)

	sys.stdout.write("\n# NO CONTENTION (IDEAL) RESULTS \n")
	sys.stdout.write("#######################\n")
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1], 1)
	plot_no_contention_ideal(plot_path, result_dicts, best_algorithm_on_average)
	sys.stdout.write("\n# NO CONTENTION (NOISE) PLOT \n")
	sys.stdout.write("#######################\n")
	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1], 1)
	plot_no_contention_noise(plot_path, result_dicts, best_algorithm_on_average,["srasearch-chameleon-10a-003.json", "bwa-chameleon-large-003.json", "epigenomics-chameleon-ilmn-4seq-50k-001.json"])
	
