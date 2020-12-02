ssh -f -M -S tuxweb -v -N  -L  localhost:20000:148.60.11.195:3306 -o ConnectTimeout=15 -o ServerAliveInterval=30 -o ServerAliveCountMax=3 -i ../keys/cle -p 22 zprojet@tuxmlweb.istic.univ-rennes1.fr

ssh -S tuxweb -O check tuxmlweb.istic.univ-rennes1.fr

touch tunnel

python3 server.py 8000

rm tunnel

ssh -S tuxweb -O exit tuxmlweb.istic.univ-rennes1.fr
 