echo -n $(echo -n `nproc` " ";echo -n `ps -eo %cpu,pid --sort -%cpu | awk  '{if($1>90)print}' | wc -l` " ") " "
