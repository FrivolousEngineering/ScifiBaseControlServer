# ScifiBaseControlServer
![UnitTest](https://github.com/nallath/ScifiBaseControlServer/workflows/UnitTest/badge.svg)

This project strives to provide a way to simulate SCIFI bases for LARP projects. It does this by providing a "Node" based system, where each node simulates a single device in the larger network (eg; A generator, a resource storage, etc). For simplicity sake, the system works with ticks (or turns). 

Each of these nodes will attempt to get the resources it requires and provide whatever it produces to systems it is connected with. While doing this, it's possible for heat to be generated, which is automatically dispersed by convection / radiation, as well as by passing it on to other connected systems (For example: a generator that is connected with a water storage will transfer it's heat to the water storage). Systems will be damaged over time and will receive more damage if they become overheated

For stability sake, the system is subdivided into two processes, the Server and the simulation engine.

## Server
The server is the system which provides the connection to the outside world. The most notable clients of this data are the Engineering consoles, these are places where engineers (the players) can view the state of the larger system and influence it. The level of influence they have depends on the rights that they have. A better / higher level  / clearance engineer will be able to do and control more.

## Simulation Engine
The simulation enigne keeps track of the nodes and ensures that all calculations are done per tick. 

![ContainerOverview](https://github.com/nallath/ScifiBaseControlServer/blob/master/documentation/SciFiBaseControl%20Container.png)
