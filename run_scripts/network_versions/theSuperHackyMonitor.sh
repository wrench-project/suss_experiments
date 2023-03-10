nproc;while true; do echo -n `ps -eo %cpu,pid --sort -%cpu | awk  '{if($1>90)print}' | wc -l` " "; sleep 1; echo -en "\033[2K\r"; done

