README - Additional Instructions
___________________

The jounalist was wearing a fitness tracker. Although this device does not capture GPS data, it does capture acceleration data. Perhaps we can use this data to locate and save our victim!

Security cameras show where the the journalist was kidnapped and it has been marked on the included city map. The kidnappers then headed directly East. After that, we lost track of them.

We have obtained the journalist's accelerometer data from their fitness tracker app thanks to your success in decrypting their password database. A list of lateral acceleration values (in m/s^2) for each second starting at the time of the kidnapping can be found in the 'stepinator.json' file.

Unfortunately, after about two and a half minutes, the tracker stopped collecting data.

We have provided a map of the city streets showing the kidnapping location. Each city block is about 100m long. This map is available as a shapefile as well as a .png image file.

Finally, we have obtained the traffic light information for the city. Each intersection has a light, and each light has a cycle of 30 seconds green, 30 seconds red. If a light is green for vehicles traveling through the intersection vertically, it will be red for those traveling horizontally (and vice versa). The victim was kidnapped just as the lights changed color. Maps showing the traffic lights at certain time intervals are attached.

We suspect that the kidnappers obeyed all traffic laws and stayed close to the speed limits. Right turns on red lights are not allowed. The speed limit in the city is 13 m/s. The kidnappers likely slow down when they take a right or left turn. We also believe that the kidnappers would not loop back when driving away--you may assume that once an intersection was traversed, that intersection was not revisited. 

Finally, since the journalist was kidnapped in the middle of the night, it is safe to assume that there were no other cars on the road.

Determine the closest intersection to where the journalist was located when their fitness tracker stopped recording data.
