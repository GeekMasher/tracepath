#!/usr/bin/python

import sys, os, socket, json, time      # Standard import
import requests, simplekml              # Third-party imports (use Python-pip to insyall them)

kml = simplekml.Kml()       # Create simple KML var
verbose=False

def trace(ip):
	print("[...] Tracing IP : " + ip)

	ips=[]      # list of new ips found along the path
	t=[0]       # message in sent packet (bytearray form)
	
	ports = [53, 123]
	dest_addr = socket.gethostbyname(ip)
	max_hops = 30
	icmp = socket.getprotobyname('icmp')

	for ttl in range(1,30):     # loops a possible 30 times (max time-to-live var)
		for port in ports:
			sock_type = socket.getprotobyname('udp')

			recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)              # setup socket type for recv.
			send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, sock_type)       # setup socket type for send
			send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)                       # setup time-to-live var

			recv_socket.bind(('', port))        # Bind local socket to resivce packet
			recv_socket.settimeout(0.1)         # Must be set to program doesn't freez
			send_socket.sendto(bytearray(t), (ip, port))        # Send packets

			curr_addr = None        # setup var
			try:
				_, curr_addr = recv_socket.recvfrom(512)        # Wait for reponce
				curr_addr = curr_addr[0]        # Get the address
			except socket.error:        # Error handling
				pass
			finally:
				send_socket.close()
				recv_socket.close()     # Close sockets

			if curr_addr is not None:
				ips.append(curr_addr)       # get the current address and save into the list
				if verbose == True: print("[...] Found IP : " + str(curr_addr))
				break
			else:
				if verbose == True: print("[...] Lost IP : " + str(curr_addr))

		if curr_addr == dest_addr:
			break               # break loop when hit target

	if str(ip) != str(ips[len(ips)-1]):
		print("[***] IP is never Reached")
		print("[...] Last IP : " + str(ips[len(ips)-1]))

	if len(ips) > 1:            #checks that there are IP's in the array
		print("[...] IP's found: " + str(len(ips)))
		geo(ip, ips)            # sends to next step

def geo(ip, ips):
	print("[...] Finding Geolocations...")
	gl = []                 # Store locations
	first="null"
	last = "null"
	counter = 1
	url="http://ip-api.com/json/"       # API link/url
	for i in ips:       # for each ip in trace
		if verbose == True: print("[...] > Requesting : " + url + i)
		u=requests.get(url + i) # request json string from API
		if int(u.status_code) == 200:       # check if the request was a success
			j=json.loads(str(u.text))       # load json string
			if j["status"] == "success":
				gl.append((j["lon"],j["lat"]))  # add 'lat,lon' to locations

				if first == "null":
					first=str(j["org"]+", "+j["city"]+", "+j["country"])        # Format first location
					first_b=True        # set to true
				if len(ips) == counter:
					last=str(j["org"]+", "+j["city"]+", "+j["country"])         # Format first location
		else:
			error(3)
		counter=counter+1
	if len(gl) > 0:     # make sure that there is more than one location before continuing
		exportToKML(ip,first,last,gl)       # sends to last step
	else:
		error(3)

def exportToKML(ip, src, des, gl):
	file = ip.replace('.','') + ".kml"      # File string
	titl = ip           # Title = ip
	desc = "Trace from " + src + " to " + des       # Description
	
	line = kml.newlinestring(name=titl, description=desc, coords=gl)    # set vars for the lines
	line.extrude = 1        # sends line around the planet (for Google Earth, no difference on maps)
	line.tessellate = 1
	line.style.linestyle.width = 5              # set line width
	line.style.linestyle.color = simplekml.Color.blue   # set color of lines
	# SimpleKML library supports lines
	# http://simplekml.readthedocs.org/en/latest/gettingstarted.html#creating-a-linestring

def saveFile():
	print("[...] Export to kml...")
	dir=str(os.getcwd()+"/kml")         # Get current dir
	file=str(time.time()).split('.')[0]+".kml"
	if not os.path.exists(dir):         # Create folder 'kml' if it doesn't exist
		os.makedirs(dir)
	if not os.path.exists(dir+"/"+file):    # Create file if it doesn't exist
		f=open(dir+"/"+file,'w+')   

	kml.save(dir+"/"+file)          # Save to a file

	print("[...] Find KML at: "+dir+"/"+file)

def checker(ip):
	v=False
	try:
		socket.inet_aton(ip)    # test if the given IP is valide
		v=True        
	except socket.error:            # when it hits an error
		v=False
	if not v == True:
		try:
			i=socket.gethostbyname(ip)  # check if its a url not IP
			v=True
		except socket.gaierror:
			v=False
	return v

def error(id):      # error list
	if id == 0:
		print("[...] Error with agrv, IP address invalide")
	elif id == 1:
		print("[...] Error with step 1 (main)")
		print("[...] Please check your argvs")
	elif id == 2:
		print("[...] Error with step 2 (trace)")
	elif id == 3:
		print("[...] Error with step 3 (geo location API)")
	elif id == 4:
		print("[...] Error with step 4 (file/kml)")
	else:
		print("[...] Error has occured, ID = " + str(id))
	sys.exit(1)
	
def main(argv):
	os.system('clear')
	print("[...] Starting process...")
	g=[]

	if len(argv) > 1:       # Makes sure that there is more than 2 vars
		for i in range(1, len(argv)):       # Loop around each IP
			trace(str(argv[i]))      # start the trace
			print("[...] Finished with IP.")
			print(" ----------------------------------------")
		saveFile()
	else:
		error(1)    
	print("[...] Ending process...")

if __name__ == "__main__":
	sys.exit(main(sys.argv))            # Get argvs
