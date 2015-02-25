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

> ./trace.py --help
>
> ./trace.py 8.8.8.8
>
> ./trace.py '8.8.8.8' '59.106.161.11' '130.102.131.70' '200.89.76.16'
>
> ./trace.py --ttl 80 -v 'google.com' 'github.com'

**IPS used in example and that are good for testing :**
 - 8.8.8.8 : Google DNS Server (USA)
 - 59.106.161.11 : University of Tokyo (JPN)
 - 130.102.131.70 : University of Queensland (AUS)
 - 200.89.76.16 : University of Chile (CHL)
 - 188.44.50.103 : Moscow University (RUS)
 - 163.200.81.116 : University of South Africa (ZAF)

## Working Test Environments
- Python
  - 2.7.8
  - 3.4.0
- Linux
  - Mint (3.13.0)
  - Ubuntu (3.16.0)
  - Arch (3.18.6)
- Windows
  - Windows 7 (SP1)

# Bugs and Fixes
- More Debugging and Error Checking Needed
- Make the code a little more robust and user friend
