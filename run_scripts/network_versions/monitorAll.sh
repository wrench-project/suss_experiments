parallel-ssh -h servers.list -i './suss_experiments/run_scripts/network_versions/theEvenLessHackyMonitor.sh' | grep -v cc@
parallel-ssh -h servers.list -i './suss_experiments/run_scripts/network_versions/theEvenLessHackyMonitor.sh' | grep -v cc@ | cut -d' ' -f 3 | awk '{sum += $1} END {print sum}'
