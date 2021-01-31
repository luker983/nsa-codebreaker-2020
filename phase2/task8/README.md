<div align="center">
    <a href="/phase2/task7"><img src="/images/skip-back.svg" align="left"></a>
    <a href="/phase2/task9"><img src="/images/skip-forward.svg" align="right"></a>
</div>

<div align="center">

# Task 8 - Rescue & Escape (Part 1)

[![Categories Badge](/images/Categories-Reverse%20Engineering%2C%20Network%20Protocol%20Analysis-BrightGreen.svg)](https://shields.io/)
[![Points Badge](/images/Points-1700-blue.svg)](https://shields.io/)
</div>

## Prompt

> The team is ready to go in to rescue the hostage. With your help they will be able to escape safely. There is no doubt the team will be detected once they find the hostage, so they will need help reaching the evacuation site. We need you to destroy all of the drones. Physically crashing the drone(s) at just the right moment will both disable any surveillance and distract the guards. This should give the team just enough time for escape to the evacuation site.
>
> This will complicated...
>
> We've done some more analysis looking at the strings and symbols in the drone binaries, and our technical team thinks the best approach is to send a 'restart' or 'poweroff' command to the power module in each of the drones. If the command is executed, the drone will lose power and drop out of the sky (and likely be destroyed).
> 
> But, it looks like the commands may not be executed when the drone is in-flight. Solving that will be the next step, but for now, focus on figuring out how to send a command to the power module, even if the command is rejected because the drone is in flight.
> 
> In this case, it would be best if you can determine a single message which can be sent to the controller so it can be be broadcast to all of the drones at exactly the same time. We dont know what other monitoring or safety mechanisms are in place if a drone malfunction is detected, and we cannot affort to disable only some of the drones.
> 
> Once you've determined the buffer that needs to be sent, upload it here We will use the './hello.py send_packet ' functionality to attempt to send the message to verify it
> 
> Upload the packet (not frame) contents we should send when we're ready to disable the drones. (It should not have the 2 byte length prefix) 
> ```
> ```

## Files

* [README.txt](/phase2/README.txt) - Provided technical notes
* [wg3.conf](/phase2/wg3.conf) - Provided UDP VPN configuration (Redacted)
* [wg4.conf](/phase2/wg4.conf) - Provided TCP VPN configuration (Redacted)
* [bundle.tar](/phase2/bundle.tar) - Provided drone network simulator
    - [bundle/](/phase2/bundle/) - Untarred drone network simulator
* [hello.py](/phase2/hello.py) - Provided Connection script 
* [solve.py](/phase2/task8/solve.py) - Creates and writes the broadcast packet to `solution.txt`
* [solution.txt](/phase2/task8/solution.txt) - Task solution

## Solution

As hinted at in `README.txt`, this task involves figuring out how to route a single message to all of the nodes at once. Once we figure that out, we send whatever message forces a reboot when an update is available, although actually making an update available is task 9's job.

Rather than walking you through the whole reversing process, I'm going to leave that as an exercise to the reader and just show my results. Here is how a routable packet is formed:

| Field  | Size (bytes) | Description  |
| ------ | ------------ | ------------ |
| Flags | 1 | Must be less than zero (`1 << 7`) for routing |
| Message Type | 1 | 0=HELLO, 1=PEERS 2=HEARTBEAT 3=OPEN 4=DATA 5=CLOSE|
| Offset | 2 | Number of bytes taken up by the index, code, address count, and addresses (`6 + (2 * address count)`) |
| Index | 1 | This should be the index of the address that is processing the route (we set this to 1 because the router is the second value in the zero-indexed address list) |
| Code | 4 | Routing algorithm code. Shifted based on index, tells node which addresses to forward to |
| Address Count | 1 | Number of addresses in Addresses |
| Addresses | 2 each | 2 byte addresses gathered from PEERS requests |

The network is structured like a tree, where each node keeps track of the addresses of its peers. It looks something like this:

```
router
|
----node1
|   |
|   ----power
|   |
|   ----updater
|
----node2
|   |
|   ----power
|   |
|   ----updater
...
```

The first step is to get the address of each node, which we technically did in Task 7. The PEERS request returns the names as well as the addresses. Then, we can send a routed PEERS request to the controller with instructions to forward it to the nodes. That will return the addresses of the power and updater modules.

To make a routed PEERS request, we need to provide the information in the table above. Rather than broadcasting the PEERS request to all of the nodes, we're going to make one request for each node that looks like this:

```
flag    message offset  index   code    address count   addresses
-1      1       12      1       0x3     3               [0x0000, 0x0001, node address]
```

It is possible to broadcast the PEERS request, but I chose to do it this way because it's easier to tell which PEER is responding, and therefore module addresses can be associated with the appropriate node. 

We have three addresses: `0x0000` is our 'terminal'. In the simulation and the 'real' network it isn't actually this value, but the controller corrects it for us. `0x0001` is the router, and `node address` is the address for the node we got from PEERS. We have to supply the full path for packets and their responses to take. The index lets the router know that it needs to apply the routing code to the address list starting at the `0x0001` item. The `0x3` code tells it to forward the address after `index`, which is `node address`.

To be honest, I never fully reversed the routing code and just used trial-and-error to figure it out. I bumped up the logging level to `RT_LOG_LEVEL_DEBUG` in the simulation controller and node and then incremented the code until it worked. Once I found a successful value for a single hop/drone, I copied the bit pattern to make it work for broadcasts to multiple drones/modules as well. This is what happens when the router receives the routed PEERS request:

```
direct_pkt_from_hdr:47   | direct_pkt_from: route flag set
log_valid_treeroute_hdr:228  | thdr loc: 0x40008c8039
log_valid_treeroute_hdr:229  | thdr_const: code: 0x0003 count: 3 index: 1
log_valid_treeroute_hdr:231  | thdr_addrs:  0: *0x40008c803e = 0x0000
log_valid_treeroute_hdr:231  | thdr_addrs:  1: *0x40008c8040 = 0x0001 <-- index
log_valid_treeroute_hdr:231  | thdr_addrs:  2: *0x40008c8042 = 0x9803
  forward_or_drop_frame:65   | FD  5 - handle_routable - code:0003 index:1 src:0x0000
    treeroute_first_dst:164  | - handle_routable - first_dst: ctx: 0x40008c8140
    treeroute_first_dst:165  | - handle_routable - first_dst: ctx->index: 0x01
    treeroute_first_dst:166  | - handle_routable - first_dst: ctx->code: 0x0001
    treeroute_first_dst:167  | - handle_routable - first_dst: ctx->level: 1
    treeroute_first_dst:168  | - handle_routable - first_dst: ctx->search_level: 1
    treeroute_first_dst:169  | - handle_routable - first_dst: ctx->doen: 0
    treeroute_first_dst:187  | treeroute not reply, calling next_dst
    treeroute_first_dst:203  | - handle_routable - next_dst: ctx: 0x40008c8140
    treeroute_first_dst:204  | - handle_routable - next_dst: ctx->index: 0x02
    treeroute_first_dst:205  | - handle_routable - next_dst: ctx->code: 0x0000
    treeroute_first_dst:206  | - handle_routable - next_dst: ctx->level: 2
    treeroute_first_dst:207  | - handle_routable - next_dst: ctx->search_level: 1
    treeroute_first_dst:208  | - handle_routable - next_dst: ctx->doen: 0
  forward_or_drop_frame:74   | FD  5 - handle_routable - first_dst: ctx->index: 0x02
  forward_or_drop_frame:75   | FD  5 - handle_routable - first_dst: ctx->code: 0x0000
  forward_or_drop_frame:76   | FD  5 - handle_routable - first_dst: ctx->level: 2
  forward_or_drop_frame:77   | FD  5 - handle_routable - first_dst: ctx->search_level: 1
  forward_or_drop_frame:78   | FD  5 - handle_routable - first_dst: ctx->doen: 0
  forward_or_drop_frame:132  | FD  5 - handle_routable - multiple destinations decoded
     set_addr_from_peer:19   | ovewriting addr: 0x0000 -> 0x9801
  forward_or_drop_frame:149  | FD  5 - handle_routable - tctx->addrp: 0x40008c8042 -> 9803
  forward_or_drop_frame:150  | FD  5 - handle_routable - tctx->index: 0x02
  forward_or_drop_frame:151  | FD  5 - handle_routable - tctx->code: 0x0000
  forward_or_drop_frame:152  | FD  5 - handle_routable - tctx->level: 2
  forward_or_drop_frame:153  | FD  5 - handle_routable - tctx->search_level: 1
  forward_or_drop_frame:154  | FD  5 - handle_routable - tctx->doen: 0
  forward_or_drop_frame:183  | FD  5 - handle_routable - queued one of many to peer fd:  4
``` 

The reply to our routed PEERS messages looks something this:

```
RECVing Second PEERS...
8101000c01000000
0303980100019803
3dfe04706f776572
0000000000000000
0000000000000000
0000000000000000
0000003e00047570
6461746572000000
0000000000000000
0000000000000000
000000000000
PEER: address: 0x3dfe type: 4 name: b'power'
PEER: address: 0x3e00 type: 4 name: b'updater'
```

Now that we have the address of the power module, we can send a routed packet with a shutdown command. First we need to know how to route to a node's module. It's more difficult than it might seem at first because the controller has to broadcast the message to all of its nodes, and then each node needs to know which power module address to send the packet to. These are how I structured my addresses: `[terminal, controller, node1, power1, node2, power2, node3, power3, ...]`. The routing code that works for this is `0x66666667`. When the index is at the controller, it sends the packet to every other address starting at index 2: `node1`, `node1`, then `node3` and so on. Then, each node knows to forward to whatever address comes after its own.

Now we need to reverse the power module. After going through the `api` function in `libpower.so` and seeing how `netsvc` parses out packets meant for modules, it looks like we need to provide a message type of 4 to indicate data, a 32-byte value for proof-of-work, and then our command. The 32-byte proof-of-work can be anything in this task because the power module doesn't really care. I chose `b'\x00' * 32` and then appended `shutdown` to see what would happen:

```
Active Flight Monitor indicates drone is in-flight.  Will not issue power command. (try: forced-...)'
```

Great! It even helps us out by telling us to prepend `forced-` to our command. Trying that gives us:

```
Flight Monitor is up to date, and indicates drone is in-flight.  Cannot force power command
```

That's exactly what we're looking for to complete this task. Let's see if it works on the actual network: 

<div align="center">

![Solve GIF](images/solve.gif)
</div>

It does!

<div align="center">

![Proof](images/proof.png)
</div>

<div align="center">
    <a href="/phase2/task7"><img src="/images/skip-back.svg" align="left"></a>
    <a href="/phase2/task9"><img src="/images/skip-forward.svg" align="right"></a>
</div>

---
