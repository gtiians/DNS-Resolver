# DNS Resolver
> Note that the code here is not the complete version of the project. The complete code is maintained on GitLab and could be published after 2025 due to UNSW policy. <br/>
Please contact me to review the complete version of the code in person.

## Table of Contents
1 [Introduction](#introduction) </br>
2 [Demo](#demo)  
3 [Basic Version](#basic-version) </br>
&nbsp;&nbsp;&nbsp;&nbsp;3.1 [System Overview](#system-overview) <br/>
&nbsp;&nbsp;&nbsp;&nbsp;3.2 [Communications and the Client-Server Paradigm](#communications-and-the-client-server-paradigm) <br/>
&nbsp;&nbsp;&nbsp;&nbsp;3.3 [Client Operation](#client-operation) <br/>
&nbsp;&nbsp;&nbsp;&nbsp;3.4 [Resolver Operation](#resolver-operation) <br/>

## Introduction
A DNS (Domain Name System) resolver is a crucial component in computer networking that
translates human-readable domain names (like www.example.com) into corresponding IP addresses
(such as 192.0.2.1). The DNS resolver performs the task of querying DNS servers to obtain the IP
address associated with a given domain name. You are required to implement a DNS resolver that
can resolve domain names to their corresponding IP addresses.

## Demo


https://github.com/PhotKosee/dns/assets/114990364/503408dd-6fbf-4aaf-bbdc-03982596ab3c



## Basic Version
You will develop two network applications: <br/>
1. **Resolver**: Your resolver will extract information from name servers in response to client
requests. In the literature you may come across similar names which share common
functionality, such as recursive resolver, recursive server, recursive name server, and fullservice resolver. <br/>
2. **Client**: Your client will provide a command-line interface to allow users to generate queries,
wait for a response, and display the results. <br/>

### System Overview
A high-level overview and an example of DNS resolution is provided in the figure below. When the resolver
is first executed it reads in a “root hints file”, which contains the names and IP addresses of the
authoritative name servers for the root zone1
. This is necessary for the resolver to bootstrap the
resolution process. The resolver will listen for queries on a UDP port which is specified as a
command-line argument. Clients will send queries from a UDP port which is automatically allocated
by the operating system. Upon receiving a query, the resolver will repeatedly make non-recursive
queries, starting at the root and following referrals, to iteratively resolve the query on behalf of the
client. <br/>

![DNS Resolver](https://github.com/PhotKosee/dns/assets/114990364/96923c89-f723-4a10-85c0-0a22cb817524)

In the example of the figure above, the client is querying to find the domain name to IP address mapping for
“www.example.com”. That is, the type “A” resource record(s) associated with “www.example.com”. <br/><br/>
The first transaction involves the query (step 1) from the client to the resolver. The resolver will only
respond (step 8) once it has obtained the answer. This answer is a result of multiple queries to a
number of authoritative DNS servers. <br/><br/>
The resolver will typically resend the query (step 2) to one of the authoritative DNS servers for the
root zone (“.”), which will respond (step 3) with the list of authoritative DNS servers for the “.com”
zone. <br/><br/>
The resolver will then resend the query (step 4) to one of the authoritative DNS servers for the “.com”
zone, which will respond (step 5) with a list of authoritative DNS servers for the “example.com”
zone. <br/><br/>
Finally, the resolver will resend the query (step 6) to one of the authoritative DNS servers for the
“example.com” zone, which will respond (step 7) with the answer to the original query. That is, a
list of IP addresses (the single fictional “N” address in the figure) corresponding to the domain name
“www.example.com”. <br/><br/>
Note that in this example the resolver arrived at an authoritative answer. However, any of the queried
servers may have had the requested records cached, in which case the resolution process may have
terminated earlier with a non-authoritative answer. <br/>

### Communications and the Client-Server Paradigm
You may assume all communication is over UDP/IPv4 and all DNS servers will use port 53, as
highlighted in the figure above.<br/><br/>
You may also note from the figure that the client port is marked as “OS”. This is to indicate that it
should be allocated automatically by the operating system. Meanwhile the resolver port for
communicating with clients is marked as “CL”. This is to indicate that it should be specified as a
command-line argument. This is because the client will need to initiate communication with the
resolver, and therefore the resolver will need to be listening on a known port. The resolver in this
situation is the “server” in the “client-server paradigm”. The resolver however does not need to know
the client’s port in advance, as it will learn it upon receiving a query and store this information, along
with the client’s IP address, to correctly address the response.<br/><br/>
Conversely the resolver assumes the role of “client” for resolver-DNS communications. As such, the
resolver does not need a known port to perform the query resolution, so it should be allocated
automatically by the operating system. The name servers will learn the resolver port and IP address
upon receiving a query, and similarly store this information to correctly address the response.<br/>

### Client Operation
The client will be executed from the command-line. The client should minimally allow for the
following command-line arguments:<br/>
1. **resolver_ip**: the IP address of the host on which the resolver is running. If the client and
resolver are running on the same host then this should be the loopback address, 127.0.0.1.<br/>
2. **resolver_port**: the port on which the resolver is listening. This should match the port
argument given to the resolver at run-time.<br/>
3. **name**: the name of the resource record that is to be looked up.<br/>

Consider this example execution where the client is a C program: <br/><br/>
`$ ./client 127.0.0.1 5300 www.example.com`<br/><br/>
The client should initiate a query for the type A record(s) for www.example.com. The query should
be sent to the resolver at 127.0.0.1:5300.<br/><br/>
The client should implement some basic argument validation. For example, that the necessary
number of arguments are provided and that each has the correct domain. If the arguments are invalid
then the client should terminate with a usage message, for example:<br/><br/>
`$ ./client`<br/>
`Error: invalid arguments`<br/>
`Usage: client resolver_ip resolver_port name`<br/>

Once the arguments are validated the client should construct a DNS query for the given name. This
will require a more in-depth understanding of the DNS message format. As a starting point, you
should refer to “RFC-1034 Domain Names – Concepts and Facilities”
and “RFC-1035 Domain
Names – Implementation and Specification”

### Resolver Operation
The resolver will be executed from the command-line. The resolver should minimally allow for the
following command-line argument:<br/>
1. **port**: the port on which the resolver should listen for queries. This should match the port
argument given to the client at run-time. It should be a value in the range 1024 – 65535.<br/>

Consider this example execution where the resolver is a C program:<br/><br/>
`$ ./resolver 5300` <br/>

The resolver should bind to UDP port 5300 and listen for client queries. <br/>

Once the arguments are validated the resolver should first read in the root hints file, which contains
resource records for the root name servers. This file named.root will be located in the working
directory of the resolver. You do not need to account for the file being absent, having a different
name, or being in a different format. In parsing the file, you may ignore lines that start with a semicolon, which are comments, blank lines, and type AAAA records, which are for IPv6. A copy of the
file is available with this specification but may also be downloaded from InterNIC8
. <br/><br/>
Once the file has been loaded by the resolver it should bind to the UDP port specified as a commandline argument and listen for queries. During testing the resolver and all clients will be executed on
the same host. As such, it is only necessary for the resolver to bind to the loopback interface. You
may, however, choose to (also) bind to the network interface such that clients may issue queries from
other hosts on the local network. <br/><br/>
Once the resolver receives a request it should initiate the resolution process. As a starting point, you
should refer to the relevant sections of RFC-1034
and RFC-1035. Note that your resolver is a
simplification of the algorithm detailed in those sections. For example, in this basic version your
resolver only needs to deal with standard queries, of a single class (“IN”), and a single type (“A”).
Additionally, in this basic version your resolver does not need to cache records, multiplex multiple
requests, nor deal with a variety of error conditions.

