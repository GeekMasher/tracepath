#!/usr/bin/python3
#######################################################################################
#		
#	Trace route script that allows the user to create a path to any IP
#		and plot it in kml file for viewing on Google Maps
#
#				GeekMasher | @geekmasher
#
#######################################################################################

# Standard import
import sys, os, socket, json, time, getopt
# Third-party imports (use Python-pip to insyall them)
import requests
import simplekml
import argparse


kml = simplekml.Kml()		# Create simple KML var
verbose=False			# Displays more data
setTTL=30
fileOutput=None

#######################################################################################
#	> Trace function
#		trace(DestIP)
#######################################################################################
def trace(ip):
    ips=[]      # list of new ips found along the path
    t=[0]       # message in sent packet (bytearray form)
    counter=0
    ports = [33434, 53, 123]	# Ports
    curr_addr = None
    dest_addr = socket.gethostbyname(ip)	# Last DestIP
    icmp = socket.getprotobyname('icmp')	# Return protocol
    sock_type = socket.getprotobyname('udp')        # Sending protocol

    print("[...] Tracing IP : " + dest_addr + " ("+ip+")")

    for ttl in range(1,setTTL+1):     # loops a possible 30 times (max time-to-live var)
        for port in ports:	# loops thought each port
            counter += 1

            recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)              # setup socket type for recv.
            send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, sock_type)       # setup socket type for send
            send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)                       # setup time-to-live var
            recv_socket.bind(('', port))        # Bind local socket to resivce packet
            recv_socket.settimeout(0.1)         # Must be set to program doesn't freez
            send_socket.sendto(bytearray(t), (ip, port))        # Send packets

            try:
                _, curr_addr = recv_socket.recvfrom(512)        # Wait for reponce
                curr_addr = curr_addr[0]        # Get the address
                break
            except socket.error:        # Error handling
                pass

            send_socket.close()
            recv_socket.close()     # Close sockets

        if curr_addr is not None:
            ips.append((curr_addr, ttl))       # get the current address and save into the list
            if verbose: print("[+++]\t"+str(ttl)+"\t"+str(curr_addr))	
        else:
            if verbose: print("[---]\t"+str(ttl)+"\t................")
        if str(curr_addr) == str(dest_addr):
            break               # break loop when hit target
        curr_addr = None

    print("")
    lnt = int(sum(len(x) for x in ips) / 2) - 1
    rate = (counter / 100 * lnt)
    if lnt >= 1:
        if str(ip) != str(ips[lnt][0]):
            print("[***] IP is never Reached")
            print("[...] Last IP : " + str(ips[lnt][0]))
        else:
            print("[...] Total Hops : " + str(counter))
            print("[...] IP's found : " + str(ips[lnt][0]))

        print("[...] Success Rate: "+str(rate)+"%")
        geo(ip, ips)            # sends to next step
    else:
        error(2)

#######################################################################################
#	> Geolocation function;
#		geo(DestIP, ips[ip,ttl])
#######################################################################################
def geo(ip, ips):
    print("[...] Finding Geolocations...")
    gl = []                 # Store locations

    url="http://ip-api.com/json/"       	# API link/url

    for i in ips:       	# for each ip in trace
        if verbose: print("[...] > Requesting : " + url + i)

        u=requests.get(url + i[0]) 			# request json string from API

        if int(u.status_code) == 200:			# check if the request was a success
            j=json.loads(str(u.text))       	# load json string
            if j["status"] == "success":
                details=(j["org"], j["city"], j["country"])
                
                gl.append((i[0], i[1], j["lon"], j["lat"], details))  # add 'ip, ttl, lat, lon, details'
		
            else:
                error(3)

        if len(gl) > 0:     		# make sure that there is more than one location before continuing
            exportToKML(ip, gl)     # sends to last step
        else:
            error(3)		# display error 3

#######################################################################################
#	> Generate KML 
#		exportToKML(DestIP, locations[[ip, ttl, lat, lon, details]])
#######################################################################################
def exportToKML(ip, locations):
    file = ip.replace('.','') + ".kml"      # File string
    listOfPoints=[]

    for loc in locations:		# loops thought locations
        pnt = kml.newpoint()	# creates new point
        pnt.name = str(loc[1]) + " : " + str(loc[2])	# add name for point
        pnt.description = str(loc[4])		# add description
        pnt.coords = [(loc[2], loc[3])]		# add coords
        listOfPoints.append((loc[0], loc[1]))	# appends geo location to list

    line = kml.newlinestring()    # set vars for the lines
    line.coords = listOfPoints
    line.extrude = 1        # sends line around the planet (for Google Earth, no difference on maps)
    line.tessellate = 1
    line.style.linestyle.width = 5              # set line width
    line.style.linestyle.color = simplekml.Color.blue   # set color of lines
    # SimpleKML library supports lines
    # http://simplekml.readthedocs.org/en/latest/gettingstarted.html#creating-a-linestring

#######################################################################################
#	> Save the KML file to a file, timestamped
#		saveFile()
#######################################################################################
def saveFile():
    print("[...] Export to kml...")
    dir=str(os.getcwd()+"/kml")         # Get current dir
    if fileOutput == None:
        file=str(time.time()).split('.')[0]+".kml"
    else:
        file=fileOutput

        if not os.path.exists(dir):         # Create folder 'kml' if it doesn't exist
            os.makedirs(dir)
        if not os.path.exists(dir+"/"+file):    # Create file if it doesn't exist
            f=open(dir+"/"+file,'w+')   

        kml.save(dir+"/"+file)          # Save to a file

        print("[...] Find KML at: "+dir+"/"+file)

#######################################################################################
#	> Checks the IP to make sure its a real IP or 
#		checker(ip)
#######################################################################################
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

#######################################################################################
#	> Error messages
#		error(id)
#######################################################################################
def error(id):      # error list
    if id == 0:
        print("[***] Error with agrv, IP address invalide")
    elif id == 1:
        print("[***] Error with step 1 (main)")
    elif id == 2:
        print("[***] Error with step 2 (trace)")
    elif id == 3:
        print("[***] Error with step 3 (geo location API)")
    elif id == 4:
        print("[***] Error with step 4 (file/kml)")
    else:
        print("[***] Error has occured, ID = " + str(id))
        print("")
        sys.exit(1)

#######################################################################################
#       > Main section of code
#               main(arguments)
#######################################################################################
def main():
    print("")
    parser = argparse.ArgumentParser(description="GeekMasher's Trace Script")
    parser.add_argument("--ttl", help="Time-To-Live variable", action='count')
    parser.add_argument("-v", "--verbose", help="Displays extra data", action="store_true")
    parser.add_argument("-o", "--output", help="Output File location", type=argparse.FileType('w'))
    parser.add_argument("ipaddress", help="List of IP addresses", nargs=argparse.REMAINDER)
    opts = parser.parse_args()

    if opts.verbose:
        global verbose
        verbose = True
    if opts.ttl is not None:
        global setTTL
        setTTL = opts.ttl
    if opts.output:	
        global fileOutput
        fileOutput = opts.output

    if not os.geteuid() == 0:
        sys.exit('\n[***] Script must be run as Root or Admin\n')
	
    for i in opts.ipaddress:       # Loop around each IP
        if checker(i):
            trace(str(i))      # start the trace
            print("[...] Finished with IP.")
            print(" ----------------------------------------")
        else:
            print("[***} "+str(i)+" is no a valid IP address")
        saveFile()
        print("[...] Ending process...")

if __name__ == "__main__":
    sys.exit(main())

