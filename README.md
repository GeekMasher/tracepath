# Tracepath

For one of my University projects, I was asked to create an application/script that could map the path from your local host to a server and plot the ip addresses it on a map (kml)

# Install and Run

Simply run the install.sh, this will install:
 * python - To run the code (you most likely have this installed already)
 * traceroute - To the traceroute section of the code
 * python-pip - To install 3rd party python libs 

Python-pip will install library's
 * requests - pulls urls (simular to curl)
 * simplekml - Generates and provides kml functionality

**Note:** If you haven't got the 'apt-get' package manager, then this will not work.

# Examples of commands:

./trace.py 8.8.8.8
python trace.py "8.8.8.8" "59.106.161.11" "130.102.131.70" "200.89.76.16"


IPS used in example:
 - 8.8.8.8 : Google DNS Server (US)
 - 59.106.161.11 : University of Tokyo (JP)
 - 130.102.131.70 : University of Queensland (AUS)
 - 200.89.76.16 : University of Chile (CH)


# Bugs

- Some server don't have the port used (80, udp) open so won't map correctly
