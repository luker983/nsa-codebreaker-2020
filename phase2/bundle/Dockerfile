################################################################################
# Dockerfile to simulate a drone
#
# requires "./drone.tar.gz" - extracted from the broken drone
# requires "./supervisord.conf - created in lab to mimic the broken drone
# expects a "router" running at the controller IP
#
# To run on a non-arm64 CPU, you can use:
# https://github.com/multiarch/qemu-user-static
################################################################################
FROM multiarch/qemu-user-static:x86_64-aarch64 as qemu
FROM arm64v8/alpine:3.12.0
COPY --from=qemu /usr/bin/qemu-aarch64-static /usr/bin/
USER root
RUN apk add --no-cache libgcc libltdl libstdc++
RUN apk add --no-cache supervisor

# setup a non-root user to match the files
RUN addgroup -S -g 400 drone && adduser -D -S --no-create-home --uid 400 -G drone drone

# extract drone files to image
COPY drone.tar.gz /tmp/drone.tar.gz
RUN tar zxvpf /tmp/drone.tar.gz && rm /tmp/drone.tar.gz

# overwrite controller IP address to match the docker-compose setup
ARG CONTROLLER_ENDPOINT
RUN echo ${CONTROLLER_ENDPOINT} > /etc/controller

# use our supervisord configuration that runs the services based on analysis of the broken drone
COPY supervisord.conf /etc/supervisor.d/supervisord.conf
RUN mkdir -p /var/log/supervisord
RUN chmod 775 /var/log/supervisord
RUN chown -R root:drone /var/log/supervisord

# overwrite broken flightmonitor with our version which simulates a drone in flight
COPY flightmonitor.sh /opt/flightmonitor/flightmonitor
RUN chmod 755 /opt/flightmonitor/flightmonitor
# setup the /var/run/... directory
RUN mkdir -p /var/run/flightmonitor && chown -R drone:drone /var/run/flightmonitor

# run the simulated drone
USER root
WORKDIR /var/log/supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor.d/supervisord.conf"]


