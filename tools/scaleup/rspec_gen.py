#!/usr/bin/env python 

#--------------------------------------------------------------------
# Copyright (c) 2014 Raytheon BBN Technologies
# Copyright (c) 2017  Barnstormer Softworks, Ltd.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and/or hardware specification (the "Work") to
# deal in the Work without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Work, and to permit persons to whom the Work
# is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Work.
#
# THE WORK IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE WORK OR THE USE OR OTHER DEALINGS
# IN THE WORK.
# ----------------------------------------------------------------------

"""
This script is to generate RSpec for a particular slice based on the network
configuration

by Xuan Liu

July 8, 2014

"""

# Safe things to import while our environment is broken
import sys
import os.path

script_dir = os.path.dirname(os.path.realpath(__file__))
if os.path.exists(os.path.normpath("%s/../../.hg" % (script_dir))):
  # We're inside the repository, set up some more path nonsense
  sys.path.append(os.path.normpath("%s/../.." % (script_dir)))


import topo_gen
import geni.gcf.geni.config as config
import site_info
#import geni.aggregate.exogeni as eg
import geni.rspec.pg as pg
import geni.rspec.igext as ig
from optparse import OptionParser

# Global Variable
BOOL = ['yes', 'no', 'y', 'n']
NO = ['n', 'no']
YES = ['y', 'yes']
NODE_PROPERTY = ['node_prefix', 'disk_image', 'install_script', 'execute_cmd', 'node_list']
OPTIONAL_NODE_PROPERTY = ['routable_control_ip']


def check_general_sec(config_info):
    ''' check general section '''
    if 'general' not in config_info:
        raise KeyError("You must configure [general] section in "\
                "your configuration file first!")


def check_node_type(config_info):
    ''' check if node_type is correctly configured '''
    if 'node_type' in config_info['general']:
        node_type_list = config_info['general']['node_type'].split(',')
        for node_type in node_type_list:
            if node_type.strip() not in config_info:
                raise KeyError("Cannot find [%s] section in the configuration file.  " \
                               "The [general] section lists a node type of '%s', so there should be a " \
                               "section called [%s]! Please check your " \
                               "configuration file" % (node_type, node_type, node_type))
            else:
                node_property = config_info[node_type.strip()].keys()
                if not( set(node_property) >= set(NODE_PROPERTY) ):
                    node_property.sort()
                    NODE_PROPERTY.sort()
                    raise ValueError("Please check the configuration section for node type [%s]. " \
                                     "The node properties should be %s, but your "
                                     "configuration is %s. " % (node_type, 
                                                               str(NODE_PROPERTY), 
                                                               str(node_property)))
                    
                elif not( set(node_property) <= (set(OPTIONAL_NODE_PROPERTY) | set(NODE_PROPERTY)) ):
                    node_property.sort()
                    NODE_PROPERTY.sort()
                    raise ValueError("Please check the configuration section for node type [%s]. " \
                                     "The optional node properties are %s, but your "
                                     "configuration is %s. " % (node_type, 
                                                               str(OPTIONAL_NODE_PROPERTY), 
                                                               str(set(node_property)-set(NODE_PROPERTY))))                  

    else:
        raise KeyError("You MUST configure \"node_type\" field in the [general] "\
                       "section!")
        
def check_output_rspec(config_info):
    ''' check if output_rspec is correctly configured '''
    if 'output_rspec' not in config_info['general']:
        raise KeyError("You must configure 'output_rspec' field in [general] section of "\
                "the configuration file!")

def check_topo_type(config_info):
    ''' check if topo_type is correctly configured '''
    if 'topo_type' in config_info['general']:
        topo_type = config_info['general']['topo_type'].lower()
        if topo_type not in topo_gen.TOPO_TYPES:
            raise ValueError("Invalid 'topo_type' of '%s' defined in the configuration file. You "\
                        "should choose one from the list %s" % (topo_type, str(topo_gen.TOPO_TYPES)))
        else:
            if topo_type not in config_info:
                raise KeyError("You defined 'topo_type' as '%s', but there is no " \
                "[%s] section configured for this topology type. Please check your configuration file." % (topo_type, topo_type))
    else:
        raise KeyError("You must configure \"topo_type\" value in the [general] section of your configuration file!")

def check_am_usage(config_info):
    ''' Check the value for single_am '''
    if 'single_am' in config_info['general']:
        if config_info['general']['single_am'].lower() not in BOOL:
            raise ValueError("Incorrect value configured for 'single_am'! "\
                             "The possible values for 'single_am' are %s" % str(BOOL))
        elif config_info['general']['single_am'].lower() in NO:
            if 'use_stitching' not in config_info['general']:
                raise KeyError("You chose to use multiple InstaGENI aggregates, " \
                              "but you haven't configure the 'use_stitching' value " \
                              "in the [general] section. The syntax is " \
                              "'use_stitching=yes/y/no/n'!")
            elif config_info['general']['use_stitching'].lower() not in BOOL:
                raise ValueError("Incorrect value configured for 'use_stitching'! "\
                        "The possible values for 'use_stitching' are %s" % str(BOOL))
    else:
        raise KeyError("You must configure \"single_am\" value in the [general] "\
                       "section of the configuration file!")
        


def check_am_assignment(config_info):
    ''' check [am_nodes] section in the configuration file '''
    ig_sites = site_info.ig_site.values()
    ig_name = ['any']
    for site in ig_sites:
        ig_name.append(site.name)

    if 'am_nodes' in config_info:
        if config_info['am_nodes']:
            if config_info['general']['single_am'] in YES:
                if len(config_info['am_nodes'].keys()) > 1:
                    raise ValueError("'single_am = yes', but nodes are assigned to more than one aggregate. Please check [am_nodes] section.")
            if config_info['general']['single_am'] in NO:
                if len(config_info['am_nodes'].keys()) <= 1:
                    raise ValueError("'single_am = no', but nodes are assigned to less than two aggregates. Please check [am_nodes] section")
                
            if not set(config_info['am_nodes'].keys()).issubset(set(ig_name)):
                raise KeyError("Check [am_nodes] section in the " \
                "configuration file, there are errors in the aggregate's "
                "name. The current assigned aggregates are %s.  Possible values are %s" % (str(config_info['am_nodes'].keys()) ,str(ig_name) ))
        else:
            raise KeyError("You should configure [am_nodes] section, it cannot be empty!")
    else:
        raise KeyError("[am_nodes] section is missing in the configuration file, please add it!")
                
        
def check_config(config_info):
    ''' check errors in the configuration file '''
    check_general_sec(config_info)
    check_output_rspec(config_info)
    check_topo_type(config_info)
    check_node_type(config_info)
    check_am_usage(config_info)
    check_am_assignment(config_info)


def find_site_id(site_name):
    ''' given an InstaGENI site name, find the corresponding site id '''
    for item in site_info.ig_site:
        if site_info.ig_site[item].name == site_name.lower():
            return item
        else:
            continue


def check_link_type(link, site_dict, stitching=None):
    """
    determine the link type 
    The third variable indicates that if don't need stitching link 
    (stitching='n'), which means all links between different aggregates 
    are egre tunnels, otherwise we use stitching links as long as 
    it's supported by the aggregates. 
    """
    nodeA, nodeB = link
    nodeA_site = 0
    nodeB_site = 0
    # Get site id for each node
    for site_id in site_dict:
        if nodeA in site_dict[site_id]:
            nodeA_site = site_id
        if nodeB in site_dict[site_id]:
            nodeB_site = site_id
    #print nodeA_site, nodeB_site
    if nodeA_site == nodeB_site or stitching == None:
        # Both nodes are from the same site
        link_type = 'lan'
    elif nodeA_site not in site_info.stitch_site or nodeB_site not in site_info.stitch_site:
        # One of the node is from the non-stitched site
        link_type =  'egre'
    elif nodeA_site in site_info.stitch_site and nodeB_site in site_info.stitch_site:
        # Both nodes are from different non-stitched sites
        if stitching == 'no':
            # Do not intend to use stitched link type between the nodes
            link_type = 'egre'
        else:
            link_type = 'stitched'
    
    return link_type
        
        
def get_link_types(site_dict, link_list, use_stitching):
    """
    Create a dictionary of links, 
    where the key is the link type: lan, egre, stitched.
    For example:
    link_dict = {'lan':(1,2), 'egre': (2,3), 'stitched': (3,4)}, indicating
    that link between node 1 and node 2 is 'lan' type, 
         link between node 2 and node 3 is 'egre' type,
         and link between node 3 and node 4 is 'stitched' type
    """
    link_dict = {}
    link_dict['lan'] = []
    link_dict['egre'] = []
    link_dict['stitched'] = []
    for item in link_list:
        if isinstance(item, list):
            # If the links belongs to a multi-node LAN
            link_type = 'lan'
            sublist = []
            for edge in item:
                sublist.append(edge.member)
            link_dict[link_type].append(sublist)           
        else:
            # non-LAN type links
            link = item.member
            link_type = check_link_type(link, site_dict, use_stitching)
            link_dict[link_type].append(link)
    return link_dict        
        

def add_node_to_rspec(config_info, site_dict, link_ifaces, vn, rspec):
    ''' add node resource to RSpec '''
    for site_id in site_dict:
        node_in_site = site_dict[site_id]
        for node_id in node_in_site:           
            node = vn.node_dict[node_id]
            vm = ig.XenVM(node.hostname)
            # Nodes are bounded to particular InstaGENI Sites, add component_manager_id to RSpec
            if site_id != 'any':
                vm.component_manager_id = site_info.ig_site[int(site_id)].component_manager_id
                
            for iface in node.iface_list:
                vm_iface = vm.addInterface(iface.id)
                vm_iface.addAddress(pg.IPv4Address(iface.addr, iface.prefix))
                link_ifaces[iface.link_id].append(vm_iface)
             
                    
            if node.node_type == 'lan-sw':
                # invisible node for LAN topology, no need to add service, etc.
                pass
            else:     
                # add node properties to non-"sw" type nodes
                vm.disk_image = node.disk_image
                service_list = config_info[node.node_type]['install_script'].split('\n')
                cmd_list = config_info[node.node_type]['execute_cmd'].split('\n')
                if "routable_control_ip" in config_info[node.node_type]:
                    vm.routable_control_ip = config_info[node.node_type]['routable_control_ip'] in YES
                for service in service_list:
                    if service != '':
                        service_url = service.split(',')[0].strip()
                        service_path = service.split(',')[1].strip()
                        vm.addService(pg.Install(url=service_url, path=service_path))
                for cmd in cmd_list:
                    if cmd != '':
                        cmd_exe = cmd.split(',')[0].strip()
                        cmd_shell = cmd.split(',')[1].strip()
                        vm.addService(pg.Execute(shell=cmd_shell, command=cmd_exe))
                rspec.addResource(vm)
    return rspec


def adding_iface_to_lan(lan_link_list, link, link_ifaces, shared_vlan=None):
    ''' add interfaces to a multi-node LAN '''
    for sub_link in lan_link_list:
        sub_link.update_type('lan')
        id = lan_link_list.index(sub_link)
        link.addInterface(link_ifaces[sub_link.id][id])
        if shared_vlan:
            link.connectSharedVlan( shared_vlan )

def add_link_to_rspec(config_info, site_dict, link_ifaces, vn, rspec, shared_vlan_info):
    ''' add link resource to RSpec '''
    if 'use_stitching' in config_info['general']:
        use_stitching = config_info['general']['use_stitching']
    else:
        use_stitching = None
        
    link_dict = get_link_types(site_dict, vn.link_list, use_stitching) 

    
    if vn.topo_type == 'lan':
        # single multi-node LAN topology
        for item in vn.link_list:
            link_name = 'lan' + str(vn.link_list.index(item))
            link = pg.LAN(link_name)
            if isinstance(item, list):
                # multi-node LAN links, adding relevant interfaces to the same LAN
                if not shared_vlan_info:
                    adding_iface_to_lan(item, link, link_ifaces)
                else:
                    sharedvlan = shared_vlan_info.keys()[0]
                    adding_iface_to_lan(item, link, link_ifaces, shared_vlan=sharedvlan)
            rspec.addResource(link)            
    else:
        # Mixed Topology or Typical non-LAN topolgoy
        for item in vn.link_list:         
            if isinstance(item, list):
                # Multi-node LAN part
                link_name = 'lan' + str(vn.link_list.index(item))
                link = pg.LAN(link_name)
                # get LAN information from the configuration file, if it exists
                sharedvlan = None
                for key, value in shared_vlan_info.items():
                    if value in item:
                        sharedvlan = key
                        break
                adding_iface_to_lan(item, link, link_ifaces, shared_vlan=sharedvlan)
            else:  
                # Non-LAN Part
                if item.member in link_dict['egre']:
                    item.update_type('egre')
                    index = link_dict['egre'].index(item.member)
                    link_name = item.link_type + str(index)
                    link = pg.L2GRE(link_name)
                elif item.member in link_dict['lan']:
                    item.update_type('lan')
                    index = link_dict['lan'].index(item.member)
                    link_name = item.link_type + str(index)
                    link = pg.LAN(link_name)
                elif item.member in link_dict['stitched']:
                    item.update_type('stitched')
                    index = link_dict['stitched'].index(item.member)
                    link_name = item.link_type + str(index)
                    link = pg.StitchedLink(link_name)
                else:
                    pass
                link.addInterface(link_ifaces[item.id][0])
                link.addInterface(link_ifaces[item.id][1])
            rspec.addResource(link)      
    return rspec

def dryrun():
    ''' test for new configuration file '''
    config_file = 'custom_config.txt'
    config_info = config.read_config(config_file)

    rspec_file = config_info['general']['output_rspec']
    
    # create network 
    vn, shared_vlan_info = topo_gen.create_topo(config_info)
    
    # Check whether using single InstaGENI site or multiple InstaGENI sites
    if config_info['general']['single_am'] in BOOL:
        site_id = config_info['am_nodes'].keys()[0]
        config_info['am_nodes'][site_id]= vn.topo.nodes()
        site_dict = config_info['am_nodes']
    else:
        site_dict = {}
        for site_id in config_info['am_nodes']:
            temp_list = config_info['am_nodes'][site_id].split(',')
            site_dict[int(site_id)] = map(int, temp_list)
 
    rspec = pg.Request()
    
    link_ifaces = {}
    for link_id in range(1, len(vn.link_list)+1):
        link_ifaces[link_id] = []
    # add node resources
    rspec = add_node_to_rspec(config_info, site_dict, link_ifaces, vn, rspec)
    # add link resources
    rspec = add_link_to_rspec(config_info, site_dict, link_ifaces, vn, rspec)
    # write rspec
    rspec.writeXML(rspec_file)
    return link_ifaces


      
def create_option(parser):
    """
    add the options to the parser
    takes the arguments from commandline
    """
    parser.add_option("-v", action="store_true", 
                      dest="verbose",
                      help="Print output to screen")
    parser.add_option("-r", dest="config_file".lower(),
                      type="str",
                      default="config.txt",
                      help="Specify the configuration file, "\
                           "and the default file name is %default.")
    




def main(argv=None):
    """
    program warpper 

    Create RSpec for a specific topology type. 
    
    Inputs are:
        -r config_file: Specify the configuration file
    """
    # get arguments
    if not argv:
        argv = sys.argv[1:]
    
    usage = ("%prog [-r config_file] ")

    parser = OptionParser(usage=usage)
    create_option(parser)
    (options, _) = parser.parse_args(argv)
    config_file = options.config_file
    config_info = config.read_config(config_file)
    # Error Checking for the configuration file 
    check_config(config_info)
    rspec_file = config_info['general']['output_rspec']
    
  
        
    
    # Create and configure the topology
    vn, shared_vlan_info = topo_gen.create_topo(config_info)
    
    # Check whether using single InstaGENI site or multiple InstaGENI sites
    if config_info['general']['single_am'] in YES:
        # Single InstaGENI site is used
        site_dict = {}
        site_name = config_info['am_nodes'].keys()[0].lower()
        site_nodes = config_info['am_nodes'][site_name]
        if config_info['am_nodes'][site_name] != 'all':
            print("INFO: 'single_am=yes' so ALL nodes " \
                      "belong to a single InstaGENI aggregate.")
            if ("any" in config_info['am_nodes']) and config_info['am_nodes']['any'].strip().lower() == "all":
                print("INFO: The RSpec will be unbound "\
                "(because nodes are listed as %s)." % config_info['am_nodes'])
            else:
                print("The RSpec will be bound "\
                "(because nodes are listed as %s)." % config_info['am_nodes'])
        if vn.topo_type == 'lan':
            # excluding the first node, which is the lan-sw type
            config_info['am_nodes'][site_name]= vn.topo.nodes()[1:]
        else:
            config_info['am_nodes'][site_name]= vn.topo.nodes()
        
           
        if site_name != 'any':            
            # RSpec is bounded, find the corresponding InstaGENI site id
            site_id = find_site_id(site_name)
            site_dict[site_id] = config_info['am_nodes'][site_name]
        else:
            # Unbounded RSpec
            site_dict = config_info['am_nodes']
            
    else:
        # Use multiple InstaGENI sites
        site_dict = {}
        for site_name in config_info['am_nodes']:
            temp_list = config_info['am_nodes'][site_name].split(',')
            if site_name.lower() == 'any':
                ''' Partially Unbound '''
                raise KeyError("WARNING: You are assigning node %s as unbound. " \
                        "Please select one of the InstaGENI aggregates. "\
                        "Currently partially unbound RSpecs for multi-aggregate topologies" \
                        " are not supported" % str(temp_list))
            else:
                site_id = find_site_id(site_name)
                site_dict[int(site_id)] = map(int, temp_list)
 
    rspec = pg.Request()
    
    link_ifaces = {}
    for link_id in range(1, len(vn.link_list)+1):
        link_ifaces[link_id] = []
    
    # add node resources
    rspec = add_node_to_rspec(config_info, site_dict, link_ifaces, vn, rspec)
    # add link resources
    rspec = add_link_to_rspec(config_info, site_dict, link_ifaces, vn, rspec, shared_vlan_info)
    # write rspec
    rspec.writeXML(rspec_file)    
    print("\nThe generated RSpec has been written to:\n\t %s " % rspec_file)
    

    
    
if __name__ == '__main__':
    sys.exit(main())
