SUMMARY

We've had a team going through everything found at the safehouse and have
uncovered a USB drive with keys and configuration to connect to a Wireguard
VPN.  (See attached file(s))

We've also extracted files from the damaged drone into a tar archive:
drone.tar.gz This is available within the bundle.tar file which includes other
files we've created to help simulate the drone network using Docker and Docker
Compose.

DRONE DETAILS

We've included within drone.tar.gz all of the drone files we think are helpful,
but unfortunately one of the "flightmonitor" files was corrupt.  We included a
placeholder file filled with 0 bytes to the expected size, but that's the best
we could do.  It doesn't seem neccessary to get the simulation running.  The
placeholder/all-zero file is at:
/var/opt/updater/modules/flightmonitor/1.1/flightmonitor

NETWORK DETAILS

We've been able to connect to the VPN and reach the IP address listed in the
configuration. The only open port was TCP/9000. Combining this knowledge with
our reverse engineering efforts against the damaged drone, we've recreated a
small test network we think matches the network running at the compound.  You
can run `docker-compose up --build` after extracting bundle.tar If you try this
on an architecture other than arm64, you should make use of
multarch/qemu-user-static.  You can read the Dockerfile and docker-compose.yml
for more details.  It's also easy to add more drones by duplicating the
relevent section of the compose file.

UNKNOWNS...

The test network includes a 'controller' which is a standin for the device
accessible from the VPN. It seems to respond in a similar way to the drone
"router" so we think the same software is running on this device.
Learning how this works seems like a requirement for communicating with drones
on the network, but we don't think it's worth the time to search for bugs in
the router software.  Trying to probe or exploit bugs in the router could lead
to detection before we're ready to free the hostage.

BONUS

We tested and reverse engineered a small amount of the router so we can successfully send
"HELLO" messages (see "hello.py") and have the router (controller or drone) respond with it's hostname and some
other unknown information.  This works great in the lab, but over the VPN we don't know how to
communicate with the drones directly.  There must be way for the controller to route messages....
