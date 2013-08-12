#siafu

Command-line tool that uses Fabric to manage remote hosts and services

##Run
You need to have [Fabric](https://github.com/fabric/fabric) installed.

    fab -f siafu

##Summary

siafu allows you to:
- start / stop services
- shutdown / reboot machines
- run scenarios
- run remote shell commands based on service or machine
- dry-run commands

##Configuration

See the example configuration file at `siafu.yaml`. 

###Section: machines
Allows you to create aliases for the machines that you would like to use from within siafu. 

###Section: services
Specify what services are running on which machines. Give each service a unique name in order to run siafu commands relative to the service and the machines the service is running on.

###Section: scenarios
You can define a sequence of simple actions that comprise a scenario. You can then run a scenario from the command-line or from within the siafu console by writing `do <scenario-name>`. The console uses auto-complete when possible.

##Usage patterns

Check if all machines running the proxy service have a running java process

    siafu ☷  ^proxy pgrep java

Stop / start all core services on all machines running core service

    siafu ☷  stop core
    siafu ☷  start core

Dry-run a scenario

	siafu ☷  d
	dry-run = True
	siafu ☷  do restart_with_delay

Change ownership of a file on machines m01 and m02

	siafu ☷  $m01,m02 chown tomcat:tomcat /example.com/config.dat


##Note!

Fabric will exit, and thus siafu, if it encounters any errors. To stop this behaviour, set `warn-only` to True by typing `w <enter>` at the siafu console.
