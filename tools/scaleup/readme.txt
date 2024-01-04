[readme]

This set of scripts is to automatically create RSpec for any type of topologies crossing XenVMs on InstaGENI aggregates using geni-lib, which is a python library written by Nick Bastin from Barnstormer Softworks. 

These scripts are authored by Xuan Liu, University of Missouri, Kansas City.

[Overview]
----------
To use this scripts, please be aware following assumptions:
1. All nodes in the automatically generated RSpec file are VMs of type 'emulab-xen' only. In current verstion, neither 'raw-pc' nor 'emulab-openvz' type is supported. 
2. All nodes are with following common hardware source reservation by default:
	<ns0:xen xmlns:ns0="http://www.protogeni.net/resources/rspec/ext/emulab/1" cores="1" ram="256" disk="8"/>
3. Each subnet is set as 192.168.x.0/24, where x is from 1 to 254. If you need to create more than 255 subnets, you will have to modify the topo_gen.py. 
4. All stitched link capacity is set as 20000 kbps. If you need to set a different link capacity for stitched links, you will need to modify the value by yourself in the generated RSpec. 

This source code folder is organized as below:
./topo_gen.py
./rspec_gen.py
./site_info.py
./sample_configuration/
./sample_output_rspec/
./readme.txt

Note that: 
You can find sample configuration files under sample_configuration folder, and the corresponding generated RSpec, and topopology pictures can be found under sample_output_rspec folder

To ran an example, use following command:
$ python rspec_gen.py -r ./sample_configuration/ring_config.txt
or
$ ./rspec_gen.py -r ./sample_configuration/ring_config.txt



[Goal]
------

The goal of the scripts to automatically create an RSpec file for a large topology that contains one or more node categories, and each node category has specific postboot install scritps and execute commands. This set of scripts provides three main features:

1. Arbitrary Topology Creation

	a. Currently three types of standard topologies are supported, which are ring, m-by-n grid, and full mesh topologies. 

	b. You can also create a random topology, by specifying the number of nodes, and the probabilty that a node can have a link to other nodes.

	c. You can create a single multi-node LAN topology.

	d. If none of the topology types are the one you need, you can create customized topology by providing the link information. There is a variation for the "custom" type, where you are able to attach multi-node LANs to the core topology defined in the [custom] section.


2. Cross-Aggregate Connectivity

You are able to create stitched links or egre links between XenVMs crossing multiple aggregates, and you will need to specify particular information in the configuration file, respectively. 


3. Easy to configure multiple node categories

You can specify particular install services and post-boot execute commands to each node category in the configuration file, and the script will create the RSpec accordingly. 



[Running Environment]
---------------------

The scripts have been tested on MacOS 10.9.3 with python version is python 2.7.8



[Setup Instruction]
-------------------

1. Install and Configure geni-lib

To use this set of scripts, you will need to install and configure geni-lib on your local system. You can follow the instructions from the link below to install and configure geni-lib on your local system. Meanwhile, you can go to the example page (see below)for some examples. 

Setup geni-lib: http://groups.geni.net/geni/wiki/HowTo/SetupGENILIB

Examples of Using geni-lib: http://groups.geni.net/geni/wiki/HowTo/GenerateRSpecUsingGENILIB


2. Install Dependencies
The script relies on a python library called "NetworkX" to create complex network topologies, so you have to install this software to your local system as well. You can find documentation about NetworkX at its official website: http://networkx.lanl.gov/index.html

For Ubuntu users, you can run "sudo apt-get install networkx" to install it; for Mac users, you can get networkx from MacPort. 




[Edit Configuration File]
-------------------------

A sample configuration file (sample_config.txt) is provided along with the scripts. Now we briefly introduce the different sections in the configuration file. 

1. [general] section

In this section, you will provide the general configuration information for your desired topology. 

	a. topo_type
	
		You will need to specify the type of network that you would like to create. There are three standard topology supported: ring, star, line, m-by-n grid and full mesh. You can also create a random network by specifying a probability of having a link from a node. Any other type of topology goes to "custom" category. Once the topology type is determined, you will need to configure the detail information for the specific topology in a different section of the configuration file.

		The script can also create a simple LAN topology, that is, you can create a single LAN that connects multiple nodes, and every node is in the same subnet. 

		For example, if you want to create a 2-by-3 grid topology, then you will need to enter:

			topo_type = grid

		Then you will next configure [grid] section in the configuration file.

	b. node_type
		Sometimes you may need to have more than one type of nodes in the network, where each type has different software packages, so you will need to specify the node types in this field. 

		For example, your network has both routers and end hosts, and your will enter:

			node_type=router, host
	
		Then, you will need to congiure both [router] and [host] sections in the configuration file.

	c. single_am
		This field specify whether you are using one single aggregate or multiple aggregates to build topology. If you are using a single aggregate:

			single_am = yes
		
		If you put a "no" value for single_am, you must configure "use_stitching" field in the [general] section

	d. use_stitching

		This field is used only for cross-aggregate networks. If you would like to create stitched links between two stitching sites, then you will need to specify:

			use_stitching = yes

		If you don't need to create stitched links, you will need to put "no" value for "use_stitching" field. 
		Note that, by default, the links between a stitching site and a non-stitching site is defined as an egre link.

	e. output_rspec

		This field specify the name of the output RSpec file.

	f. subnet (optional)

	    The first two octets of the IP subnet for the nodes in this topology.
	    For example, if you set "subnet=192.168", link X will have addresses on the network
	    192.168.X.0/24 and each host on that link will have an address something like 192.168.X.1, etc.
	    If the field is missing it defaults to 192.168.

	    For example, to set addresses to be on the 10.2.X.0/24 network use:
            subnet=10.2


2. Sections for topology types

	a. [ring] section
		If you choose ring topology in the [general] section, you should specify the value for the "num_nodes" field in this section, By default, the number of nodes for a ring topology is set as "3". You can find a sample configuration file for ring topology in ring_config.txt

	b. [grid] section
		If you choose grid topology in the [general] section, you will need to specify two values, the number of nodes in a row, and the number of nodes in a column. By default, it's a 2-by-2 grid network configuration. You can find a sample configuration file for grid topology in grid_config.txt.
		If it’s an m-by-n grid topology, the nodes will be numbered as below:
		1,2,3,…,n
		n+1,n+2,…,2n
		…
		(m-1)*n+1,(m-1)*n+2,…,m*n
		

	c. [mesh] section
		If you choose mesh topology in the [general] section, you will need to provide information about how many nodes in the fully mesh topology. By default, it's a 4-node fully mesh. You can find a sample configuration file for mesh topology in mesh_config.txt

	d. [linear] section
		If you choose line topology in the [general] section, you will need to provide information about how many nodes in the linear topology. You can find a sample configuration file for the linear topology in linear_config.txt

	e. [star] section
		If you choose star topology in the [general] section, you will need to provide information about how many nodes in the star topology. You can find a sample configuration file for mesh topology in star_config.txt

	f. [random] section
		If you choose random topology in the [general] section, in addition to the "num_nodes" field, you also need to specify the probabilty that a node can have a link to another node, which is defined by "edge_prob" field.

	g. [custom] section
		If you choose to create your own customized topology, you should configure [custom] section. In this section, you will need to provide the link information (the "edge" field) in the format of "[(1,2),(2,3),(3,4), ...]". You can find a sample configuration file for custom topology in custom_config.txt

	h. [lan] section
		If you choose to create a simple n-node LAN topology, you should configure [lan] section. You will specify the number of nodes connected to the LAN. When creating a LAN, it is set single aggregate by default. You can find a sample configuration file for LAN topology in LAN_config.txt.  To make the LAN a Shared VLAN, set the `shared_vlan` field to be the name of the shared VLAN (e.g. shared_vlan=my_shared_vlan).

	i. [add-lan] section (optional)
	    This section is associated with the [custom] section. You will only need to configure this section when you are creating a customized topology with multi-node LANs.
	   
	    For example:
		If your existing topology without LAN is [(1,2),(2,3),(3,1)], and you want to attach a three-node
		LAN to each node:
		You will need to define: 
							lans = [(1,4,5),(2,6,7),(3,8,9)] 
		in this [add-lan] section.

	j. [add-shared-vlan] section (optional)
	    You will only need to configure this section when you are adding a shared VLAN to one of the above topologies.

	    For example:
		If your existing topology without LAN is [(1,2),(2,3),(3,1)], and you want to attach a two
		shared VLAN to this topology:

		[add-shared-vlan]
        shared_vlans=my_shared_vlan,my_other_vlan

        my_shared_vlan and my_other_vlan should be the name of existing Shared VLANs.  You then need to define a section
        for each shared VLAN.  Each section will contain a lans field specifying which nodes will be connected to the
        shared VLAN:

        [my_shared_vlan]
        lans=[(1,2)]

        [my_other_vlan]
        lans=[(2,3)]

        See also the `shared_vlan` tag in the [lan] section above.


3. Configure Node Categories

	The configuration for specific node categories depends on the "node_type" values configured in [general] section. Assuming "node_type=router, host", you will need to create two sections for this part, each section represent a type of node, and it has seven fields: 

		a. node_prefix

			The value of node_prefix will become part of the node name in your output RSpec file. For example, if the node type is "router", the prefix can be configured as "router", so that the node name will be "router-#". 


		b. disk_image

			You can leave this field as blank, and a default disk image will be loaded to the node when you request the resources from the aggregate(s). However, if you have created a custom image, and would like the node to load it, you should give the URL of the custom image to this field.   


		c. install_script 

			The "install_script" field is blank by default. If you need the node to load post-boot services (tarball of the install scripts), you can put the URL of the tarball and the path where the tarball file should be downloaded. Note that, if you have multiple install scripts, you need to put each install script in a new line. 

			For example:
			correct:	install_script=url1, path1
									   url2, path2
									   url3, path3
			wrong: 		install_script=url1, path1; url2, path2;
									   url3, path3
		

		d. execute_cmd 

			The "execute_cmd" and "shell" fields are blank by default. If you would like to run some executable services or command in the post-boot stage of a node, you need to specify both information accordingly. Again, each command should be put in different line, similar to how to specify install_script. 

			For example:
				execute_cmd = ls, sh
							  myScript.sh, sh
				
			This indicates that at the post-boot stage, you will execute two commands. 


		e. node_list

			This field defines the set of node ids that belongs to the particular node type. If there is only one node type, you can simply define "node_list=ALL"
                f. routable_control_ip
			This field says the node should be given a publicly routable IP address.  For example, this is useful for nodes that need to run publicly accessible webservers.
		        To use, add this command to the description of the node:
			    routable_control_ip=yes

		A full configuration example for node_type "router":

		[router]
		node_prefix=rt
		disk_image=https://www.instageni.clemson.edu/image_metadata.php?uuid=21a48773-f7cc-11e3-aa57-000000000000
		install_script=http://geni-myvini.umkc.gpeni.net/resources/experiments/xorp_autostart.tar.gz,/local
		 		http://geni-myvini.umkc.gpeni.net/resources/experiments/xorp_run.tar.gz, /local
				http://emmy9.casa.umass.edu/GEC-20/gimidev.tar.gz, /
				http://geni-myvini.umkc.gpeni.net/resources/experiments/labwiki.tar.gz, /local
				http://geni-myvini.umkc.gpeni.net/resources/experiments/install_script.tar.gz, /local
		execute_cmd=/bin/bash /local/xorp_autostart/start-xorp.sh, sh
				    /bin/bash /local/install_script/initial_install.sh, sh
				    sudo sh /gimidev/gimibot.sh, sh
		routable_control_ip=yes
		node_list=ALL

4. Aggregate Assignment 

	Based on the configuration for "single_am" in the [general] section, you should specify the aggregates for particular sets of nodes in [am_nodes] section. The syntax is <AM> = <Node List>

		a. single_am=yes

			We will create unbounded RSpec, so you can choose any aggregate when you reqeust the resources by giving the RSpec file. In this case, you can put "any=ALL", where "any" means "any aggregate" and "ALL" means all nodes in the network are from the same aggregate. If you would like to select one of the aggregate from the list, i.e. select ig-gpo, then, you enter 0=ALL under [am_nodes]
				
				[am_nodes]
				# If single_am = yes, and you would like to have unbounded RSpec
				any=ALL

				# If single_am = yes, and you would like to select one of the aggregate from the list, i.e. select ig-gpo, 
				# then, you enter ig-gpo=ALL
				# ig-gpo=ALL 


		b. single_am=no

			The configuration file gives a list of available InstaGENI aggregates for you to select. When "single_am=no", the RSpec has to be bounded. In other words, you have to select aggregates, and assgin each node to a proper aggregate. 
			
			For example, if there are four nodes (0,1,2,3), and node 0 and 1 are from aggregate 1, and node 2 and 3 are from aggregate 2, the [am_nodes] will look like:
				
				[am_nodes]
				ig-nysernet = 0,1
				ig-illinois = 2,3


