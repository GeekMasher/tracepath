#!/usr/bin/python
#######################################################################################
#       
#   Trace route script that allows the user to create a path to any IP
#       and plot it in kml file for viewing on Google Maps
#
#               GeekMasher | @geekmasher
#
#######################################################################################

try:
# Standard import
    import sys, os, socket, json, time, argparse
# Third-party imports (use Python-pip to insyall them)
    import requests
    import simplekml
except:
    print("[...] Error when Importing")
    print("\nPlease Install :\n\t- requests\n\t- simplekml")
    exit(2)

kml = simplekml.Kml()           # Create simple KML var
verbose=False                   # Displays more data
setTTL=30                       # Time-To-Live var
fileOutput=None                 # User file output var

#######################################################################################
#   > Trace function
#       trace(DestIP)
#######################################################################################
def trace(ip):
    global setTTL
    errorCount = 0
    nodesCounter = 0
    ips=[]                                      # list of new ips found along the path
    t=[0]                                       # message in sent packet (bytearray form)
    counter=0                                   # counts the number of hops until the end
    addrPos=''                                  # Current IP
    port = 33434                                # port thats use
    dest_addr = socket.gethostbyname(ip)        # Last DestIP

    print("[...] Tracing IP : " + dest_addr + " ("+ip+")")

    for ttl in range(1,setTTL+1):               # loops a possible 30 times (max time-to-live var)
        counter += 1

        # setup socket type for recv.
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.getprotobyname('icmp'))
        # setup socket type for send
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.getprotobyname('udp'))
        # setup time-to-live var 
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)

        recv_socket.bind(('', port))                                # Bind local socket to resivce packet
        recv_socket.settimeout(0.1)                                 # Must be set to program doesn't freez
        send_socket.sendto(bytearray(t), (dest_addr, port))         # Send packets

        try:
            _, curr_addr = recv_socket.recvfrom(512)                # Wait for reponce
            addrPos = str(curr_addr[0])

            if addrPos is not None:
                nodesCounter += 1
                ips.append((addrPos, ttl))                          # get the current address and save into the list
                if verbose: print("[+++]\t"+str(ttl)+"\t"+str(addrPos))

        except socket.error:                    # Error handling
            if verbose: print("[---]\t"+str(ttl)+"\t................")
            ips.append((None, ttl))
            errorCount += 1
        finally:        
            send_socket.close()
            recv_socket.close()                 # Close sockets

        if str(addrPos) == str(dest_addr):
            break                               # break loop when hit target
        else:
            addrPos = None
    print("")                                   # Spacing
   
    if errorCount < setTTL:                                            # Make sure that there are an amount of IPs
        if str(dest_addr) != str(ips[len(ips)-1][0]):                     # Check last hops to see if 
            print("[***] IP is never Reached")              # Show that finally IP is not reached
        else:
            print("[...] Total Hops : " + str(nodesCounter))     # hops until target

        geo(ip, ips)                                        # sends to next step
    else:
        error(2)                                            # Show error if no IPs in list

#######################################################################################
#   > Geolocation function;
#       geo(DestIP, ips[ip,ttl])
#######################################################################################
def geo(ip, ips):
    global setTTL
    print("\n[...] Finding Geolocations...")

    checkList = []          # Format : [(Name, lat, lon, [(ip, ttl))]
    nullNodes = []          # Format : [(ip, ttl)]
    checkBool = False

    url="http://ip-api.com/json/"                       # API link

    # Format of i : (ip, ttl)
    for i in ips:
        if i[0] is None:
            nullNodes.append(("Node Not Found", i[1]))

        else:
            u=requests.get(url + i[0])                      # request json string from API

            if int(u.status_code) == 200:                   # check if the request was a success

                j=json.loads(str(u.text))                   # load json string

                if j["status"] == "success":                # check in the json file that 
                    name = j["org"] +", "+ j["country"]
                    if verbose: print("[+++] > " + str(i[0]))

                    if len(checkList) > 0:
                        for check in checkList:
                            if j["lon"] == check[1] and j["lat"] == check[2]:
                                check[3].append((i[0], i[1]))
                                checkBool = True
                                break

                        if checkBool == False:
                            checkList.append((name, j["lon"], j["lat"], [(i[0], i[1])]))
                        checkBool = False

                    else:
                        checkList.append((name, j["lon"], j["lat"], [(i[0], i[1])]))
                            
                else:
                    nullNodes.append((i[0] + " (no data)", i[1]))
            else:
                if verbose: print("[---] > " + str(i[0]))

#######################################################################################
#       > Sorting system
#######################################################################################

    newCheckList = []           # Format : [(Name, lat, lon, description)]
    ttlMarker = 1

    for location in checkList:
        nodes = location[3]
        description = ""

        for i in xrange(ttlMarker, setTTL):
            try:
                knownNodes = [y[1] for y in nodes].index(ttlMarker)
                description += str((nodes[knownNodes])[1]) + " : " + str((nodes[knownNodes])[0]) + "\n"
                nodes.remove(nodes[knownNodes])
            except:
                try:
                    unknownNodes = [y[1] for y in nullNodes].index(ttlMarker)
                    description += str((nullNodes[unknownNodes])[1]) + " : " + str((nullNodes[unknownNodes])[0]) + "\n"
                    nullNodes.remove(nullNodes[unknownNodes])
                except:
                    description += str(ttlMarker)+" : Error with Node Finder\n"
                
            ttlMarker += 1

            if len(nodes) < 1:
                break

        newCheckList.append((location[0], location[1], location[2], description))

    if len(newCheckList) > 0:                      # make sure that there is more than one location before continuing
        exportToKML(ip, newCheckList, nullNodes)              # sends to last step
    else:
        error(3)                                # display error 3

#######################################################################################
#   > Generate KML 
#       exportToKML(DestIP, locations[[ip, ttl, lat, lon, details]])
#######################################################################################
def exportToKML(ip, locations, nullNodes):    
    listOfPoints=[]

    print("\n[...] Point Count : " + str(len(locations)))

    for loc in locations:                               # loops thought locations
        pnt = kml.newpoint()                            # creates new point
        pnt.name = str(loc[0])    # add name for point
        pnt.description = str(loc[3])                   # add description
        pnt.coords = [(loc[1], loc[2])]                 # add coords
        listOfPoints.append((loc[1], loc[2]))                        # appends geo location to list

    line = kml.newlinestring()                          # set vars for the lines
    line.name = str(ip)
    line.coords = listOfPoints                          # add the list of points as the lines
    line.extrude = 1                                    # sends line around the planet
    line.tessellate = 1
    line.style.linestyle.width = 5                      # set line width
    line.style.linestyle.color = simplekml.Color.blue   # set color of lines
    # SimpleKML library supports lines
    # http://simplekml.readthedocs.org/en/latest/gettingstarted.html#creating-a-linestring

    saveFile(ip=ip)                  # save file for IP

#######################################################################################
#   > Save the KML file to a file, timestamped
#       saveFile()
#######################################################################################
def saveFile(ip=None):
    print("[...] Export to kml...")
    if fileOutput == None and ip == None:                          # checks if the user has added custom file
        file= os.getcwd() + "/" + str(time.time()).split('.')[0] + ".kml"  # time stamped file
    elif fileOutput == None:
        file= os.getcwd() + "/" + str(ip) + ".kml"  # time stamped file
    else:
        file=fileOutput                             # user file

    kml.save(file)                      # Save to a file

    print("[...] Find KML at: "+file)

#######################################################################################
#   > Checks the IP to make sure its a real IP or 
#       checker(ip)
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
#   > Error messages
#       error(id)
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
    # Prameters
    parser = argparse.ArgumentParser(description="GeekMasher's Trace Script")
    # Adds the Time-To-Life pram
    #parser.add_argument("--ttl", help="Time-To-Live variable", action='count', type=int)
    # Adds the verbose option
    parser.add_argument("-v", "--verbose", help="Displays extra data", action="store_true")
    # Adds output file path
    parser.add_argument("-o", "--output", help="Output File location", type=argparse.FileType('w'))
    # Adds all of the other prams
    parser.add_argument("ipaddress", help="List of IP addresses", nargs=argparse.REMAINDER)
    opts = parser.parse_args()          # gets argv

    if opts.verbose:                    # if verbose is set
        global verbose
        verbose = True                  # set to true
    if opts.ttl is not None:            # If ttl is set
        global setTTL
        setTTL = opts.ttl               # set ttl
    if opts.output:                     # if output is set
        global fileOutput
        fileOutput = opts.output        # set output file

    if sys.platform == "linux2":
        if not os.geteuid() == 0:           # check if the user is running as root
            sys.exit('[***] Script must be run as Root or Admin\n')
    
    for i in opts.ipaddress:            # Loop around each IP
        if checker(i):                  # Check argv to make sure its a IP / Domain Name
            trace(str(i))               # start the trace
            print("\n[...] Finished with IP.")

            kml = None
            kml = simplekml.Kml()

            print(" ----------------------------------------")
        else:
            print("[***} "+str(i)+" is no a valid IP address")
    print("[...] Ending process...")

if __name__ == "__main__":              # Starting point
    sys.exit(main())                    # Goto main
