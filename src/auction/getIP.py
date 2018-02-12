import sys
import subprocess

if sys.platform == "darwin":
	subprocess.call("ipconfig getifaddr en1 > serverIP.LazyCat", shell=True)
else:
	subprocess.call("ip addr | grep 'state UP' -A2 | tail -n1 | awk '{print $2}' | cut -f1  -d'/' > serverIP.LazyCat", shell=True)