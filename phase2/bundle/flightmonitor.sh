#!/usr/bin/env sh
# simulate a flight monitor
# simulate drone in-flight based on our analysis of the 1.0 flight monitor software
touch /var/run/flightmonitor/inflight && chown drone:drone /var/run/flightmonitor/inflight
echo $$ > /var/run/flightmonitor.pid
sleep infinity
