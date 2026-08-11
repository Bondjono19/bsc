echo "timestamp,mem_available_mb,swap_used_mb,temp_c,throttled" > sysmon.csv
while true; do
  ts=$(date +%s)
  mem=$(free -m | awk '/^Mem:/ {print $7}')     
  swap=$(free -m | awk '/^Swap:/ {print $3}')    
  temp=$(vcgencmd measure_temp | grep -o '[0-9.]*')
  throttled=$(vcgencmd get_throttled)
  echo "$ts,$mem,$swap,$temp,$throttled" >> sysmon.csv
  sleep 1
done