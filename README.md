# Tracepath

For one of my University projects, I was asked to create an application/script that could map the path from your local host to a server and plot the ip addresses it on a map (kml)

# Installing
You do not need to run this script if you have these things installed already.

**Note:** If you haven't got the 'apt-get' package manager, then this will not work.

**Packages that will install :**
 * python - To run the code (you most likely have this installed already)
 * python-pip - To install 3rd party python libs 

**Python-pip will install library's :**
 * requests - pulls urls (simular to curl)
 * simplekml - Generates and provides kml functionality

# Examples of commands:

> ./trace.py 8.8.8.8
>> when changed the permissions on the file (sudo chmod +x trace.py)
>
> python trace.py "8.8.8.8" "59.106.161.11" "130.102.131.70" "200.89.76.16"
>> The script uses arguments to maps out paths between each path

**IPS used in example and that are good for testing :**
 - 8.8.8.8 : Google DNS Server (USA)
 - 59.106.161.11 : University of Tokyo (JPN)
 - 130.102.131.70 : University of Queensland (AUS)
 - 200.89.76.16 : University of Chile (CHL)

# Bugs
- Make the code a little more robust and user friendly
- Some server don't have the port (80, udp) open, so won't map correctly
