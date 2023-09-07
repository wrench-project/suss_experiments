#!/usr/bin/env python3
from plot_utils import *

if __name__ == "__main__":
	if len(sys.argv) != 2:
		sys.stderr.write("Usage: " + sys.argv[0] + " <version>\n")
		sys.exit(1)

	plot_path, result_dicts, workflows, clusters, best_algorithm_on_average = importData(sys.argv[1], 1)
