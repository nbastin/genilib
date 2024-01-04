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
This script is to generate topology, determine the IP addresses for the
interfaces, etc. Then, we can create RSpec based on the network information
using geni-lib written by Nick Bastin of Barnstormer Softworks

Code by Xuan Liu

July 8, 2014
"""

import networkx as nx
import re

LINE = 'linear'
RING = 'ring'
STAR = 'star'
GRID = 'grid'
MESH = 'mesh'
RANDOM = 'random'
CUSTOM = 'custom'
LAN = 'lan'

TOPO_TYPES = [LINE, RING, STAR, GRID, MESH, RANDOM, CUSTOM, LAN]

class Interface(object):
    ''' virtual interface class '''
    def __init__(self, hostname='node', id=0, addr=None):
        '''initialize the object'''
        #self.id = "%s:if%d" % (hostname, id)
        self.id = "if%d" % id
        self.component_id = "eth%d" % id
        self.addr = addr
        self.prefix = '255.255.255.0'
        self.capacity = '10000'
        self.link_id = 0
    
    def set_address(self, subnet, hostid, subnet_prefix="192.168"):
        ''' set ip address to the interface '''
        self.addr = '.'.join([str(subnet_prefix), str(subnet), str(hostid)])
        
    def set_linkid(self, subnet):
        ''' set the link id so this interface is binded to a particular link'''
        self.link_id = subnet
        
        
class Node(object):
    '''Node class'''
    def __init__(self, id=0, node_type='node'):
        ''' initialize the object'''
        # initialize the node type as "node"
        self.node_type = node_type
        # initialize the index for a particular node type that starts from 0
        self.node_index = 0
        # the syntax of node's hostname is <node_prefix>-<node_index>
        self.hostname = ''
        # initalize the node's disk image as None
        self.disk_image = None
        # initilize the number of virtual interfaces on a node
        self.num_iface = 0
        # the id for the nodes, it's independent on the node_type
        self.id = id
        # initialize node's geographical information in form of (latitude, longitude)
        self.geoinfo = None
        # initilzie the node's cpu usage
        self.cpu = None
        # initilize the node's memory usage
        self.bw = None
        # initilize the node's prefix, which is part of the node's hostname
        # the prefix could be defined the same as the node_type
        self.prefix=''
        # initialize the list of the node's virtual interfaces
        self.iface_list = []
    
    def set_prefix(self, prefix):
        '''set prefix for a node '''
        self.prefix = prefix
        
        
    def update_type(self, node_type):
        ''' update node type '''
        self.node_type = node_type
    
    def set_name(self, name):
        ''' set hostname for the node '''
        self.hostname = name
    
    def set_disk_image(self, config_info):
        '''Set the custom image for nodes'''
        self.disk_image = config_info[self.node_type]['disk_image']
    
    def set_cpu(self, cpu):
        ''' set the cpu setting '''
        self.cpu = cpu
    
    def set_bw(self, bw):
        ''' set the bw '''
        self.bw = bw
        
    def set_geoinfo(self, lat, lon):
        ''' set the latitude and longitude info'''
        self.geoinfo = (lat, lon)
        
    def add_iface(self, subnet_id, hostid, subnet_prefix="192.168"):
        ''' Add interface to a node '''
        # let the interface id starts from 1
        if self.iface_list == []:
            new_iface_id = 1
        else:
            new_iface_id = self.num_iface + 1
        # create a new interface
        new_iface = Interface(self.hostname, new_iface_id)
        # set IP address to the new interface
        new_iface.set_address(subnet_id, hostid, subnet_prefix)
        # bind the new interface to the subnet of the link
        new_iface.set_linkid(subnet_id)
        # update the interface list at the node
        self.iface_list.append(new_iface)
        self.num_iface += 1
 
        
 
        
class Link(object):
    """
    In this class, we define the link to be an edge connecting two interfaces 
    from two different nodes, repsectively.
    
    There are two possible types of links:
    1. Regular link between two nodes: 1 ---- 2
    2. LAN links, where each link connect a node to the center switch
        For example: A LAN is like:
                                          1
                                          |
                                  2 --- sw(0) --- 3
        Assuming the center switch is node 0, so the links are (0,1), (0,2)
        and (0,3)
    """
    def __init__(self, id=1, link_type='link'):
        """
        initilize a link object
        """
        # Link Id will be the subnet number 
        self.id = id
        # initilize the list of nodes that are attached to this link. 
        self.nodes = []
        # initialize the subnet, starts from 192.168.1.0
        self.network = '192.168.%d.0' % id
        # initilize the link type as 'link' type, which means the link type has 
        # not been decided
        self.link_type = link_type
        # link member is a pari of nodes, in form of (a, b), where a and b are node id
        self.member = None
        # The interfaces that the link connects to
        self.ifaces = None
    
    def add_nodes(self, node):
        '''add node that the link connects to'''
        self.nodes.append(node)
        
    def set_member(self, edge):
        ''' set the member node ids of the link '''
        self.member = edge
        
    def set_ifaces(self, iface_pair):
        ''' set the associated interfaces '''
        self.ifaces = iface_pair
        
    def update_type(self, link_type):
        ''' update link type from origin type "link" '''
        self.link_type = link_type
        
        
class Network(object):
    """
    Create a model that has one or more virtual networks, and the detailed
    information of the model will be used to generate RSpec    
    """
 
    def __init__(self, topo_type='ring'):
        ''' initialize the model '''
        # a dictionary containing node objects
        self.node_dict = {}
        # a list of link objects
        self.link_list = []
        # topology
        self.topo = None
        # report on this virtual network
        self.summary = {}
        # number of routers
        self.num_nodes = 0
        # network type
        self.topo_type = topo_type

    def create_lan(self, topo_info):
        ''' create single multi-node LAN '''
        if 'num_nodes' in topo_info:     
            if topo_info['num_nodes'].isdigit():
                self.num_nodes = int(topo_info['num_nodes'])
                if self.num_nodes > 254:
                    raise ValueError("Cannot have more than 254 nodes in a single LAN. " \
                                     "You have %d nodes!" % self.num_nodes)
                else:
                    # A LAN is actually a "star" topology where the center node is an 
                    # invisiable node that does not appear in the RSpec file
                    self.topo = nx.star_graph(self.num_nodes)
                    sub_link_list = self.topo.edges()
                    link_id = 1
                    # If there is LAN type, self.link_list is a nested list type
                    # The inner list represents the LAN has multiple links
                    self.link_list.append([])
                    for edge in sub_link_list:
                        link = Link(link_id)
                        link.member = edge
                        self.link_list[0].append(link)
            else:
                raise ValueError("Invalid configuration: 'num_nodes = %s' "\
                            "in [%s] section, where it should be digit "\
                            "numbers only" % (topo_info['num_nodes'], self.topo_type))
        else:
            raise KeyError("Configuration for 'num_nodes' value is missing" \
                        " in the [%s] section, please check!" % self.topo_type)
       
    def add_lan(self, topo_info):
        """
        Add LANs to current topology 
        Assume there is an existing non-LAN topology defined, and this script
        will add one or more LANs to this topology, where the LANs are 
        pre-configured in the configuration file
        """
        # the number of LANs to be added
        num_lans = len(topo_info)
        # the number of exsiting non-LAN links
        num_nonlan_links = len(self.link_list)
        # checking if the total number of links exceeds 255
        if len(topo_info) + len(self.link_list) > 254:
            raise ValueError("Total number of subnets cannot exceed 255!" \
                             "You have %d LANs plus %d links" % \
                             (num_lans, num_nonlan_links))
        else:
            # less than 255 links, continue
            for lan in topo_info:
                #new_lan_nodes = eval(topo_info[lan])
                new_lan_nodes = topo_info[lan]
                # checking if the LAN has more than 254 nodes
                if len(new_lan_nodes) > 254:
                    raise ValueError("Cannot have more than 254 nodes in " \
                                     "a single LAN. You have %d nodes!" \
                                     % self.num_nodes)
                else:
                    # add a LAN to existing topology
                    self.topo.add_star(new_lan_nodes)
                    #lan_links = []
                    self.link_list.append([])
                    for node in new_lan_nodes[1:]:
                        new_edge = (new_lan_nodes[0], node)
                        #lan_links.append(new_edge)
                        link_id = len(self.link_list)
                        link = Link(link_id)
                        link.member = new_edge
                        self.link_list[-1].append(link)
        return link

    def relabel_nodes(self):
        ''' relabel node index from 1 '''
        mapping = {}
        new_index = 1
        for node_id in self.topo.nodes():
            mapping[node_id] = new_index
            new_index += 1
        self.topo = nx.relabel_nodes(self.topo, mapping)
        
        
    def create_ring(self, topo_info):
        ''' create ring topology '''
        if 'num_nodes' in topo_info:
            if topo_info['num_nodes'].isdigit():
                self.num_nodes = int(topo_info['num_nodes'])

                self.topo = nx.cycle_graph(self.num_nodes)
                self.relabel_nodes()
            else:
                raise ValueError("Invalid configuration: 'num_nodes = %s' "\
                            "in [%s] section, where it should be digit "\
                            "numbers only" % (topo_info['num_nodes'], self.topo_type))
        else:
            raise KeyError("Configuration for 'num_nodes' value is missing" \
                        " in the [%s] section, please check!" % self.topo_type)
           

    def create_line(self, topo_info):
        ''' create linear topology '''
        if 'num_nodes' in topo_info:
            if topo_info['num_nodes'].isdigit():
                self.num_nodes = int(topo_info['num_nodes'])
                temp = nx.grid_2d_graph( 1, self.num_nodes)
                mapping = {}
                for i in xrange(0, self.num_nodes):
                    mapping[(0,i)] = i+1
                self.topo = nx.relabel_nodes( temp, mapping)

            else:
                raise ValueError("Invalid configuration: 'num_nodes = %s' "\
                            "in [%s] section, where it should be digit "\
                            "numbers only" % (topo_info['num_nodes'], self.topo_type))
        else:
            raise KeyError("Configuration for 'num_nodes' value is missing" \
                        " in the [%s] section, please check!" % self.topo_type)

    def create_grid(self, topo_info):
        ''' create m-by-n grid topology '''             
        if 'num_row' in topo_info and 'num_col' in topo_info:  
            if topo_info['num_row'].isdigit() and topo_info['num_col'].isdigit():
                node_row = int(topo_info['num_row'])
                node_col = int(topo_info['num_col'])
                self.num_nodes = node_row * node_col
                temp = nx.grid_2d_graph(node_row, node_col)
                mapping = {}
                node_id = 1
                for index_row in range(0,node_row):
                    for index_col in range(0, node_col):
                        mapping[(index_row, index_col)] = node_id
                        node_id += 1
                self.topo = nx.relabel_nodes(temp, mapping)
            else:
                raise ValueError("Invalid configuration for 'num_row = %s' or "\
                            "'num_col = %s' in [%s] section, where both"\
                            " should be integer "\
                            "numbers only" % (topo_info['num_row'], topo_info['num_col'], self.topo_type))                
        else:
            raise KeyError("Configuration for 'num_row' or 'num_col' or both is missing" \
                        " in the [%s] section, please check!" % self.topo_type)

    def create_star(self, topo_info):
        ''' create star topology '''
        if 'num_nodes' in topo_info:
            if topo_info['num_nodes'].isdigit():
                self.num_nodes = int(topo_info['num_nodes'])
                self.topo = nx.star_graph(self.num_nodes)
                self.relabel_nodes()
            else:
                raise ValueError("Invalid configuration for 'num_nodes = %s' "\
                            "in [%s] section, where it should be digit "\
                            "numbers only" % (topo_info['num_nodes'], self.topo_type))
        else:
            raise KeyError("Configuration for 'num_nodes' value is missing" \
                        " in the [%s] section, please check!" % self.topo_type)

    def create_mesh(self, topo_info):
        ''' create full mesh topology '''
        if 'num_nodes' in topo_info:
            if topo_info['num_nodes'].isdigit():
                self.num_nodes = int(topo_info['num_nodes'])
                self.topo = nx.complete_graph(self.num_nodes)
                self.relabel_nodes()
            else:
                raise ValueError("Invalid configuration for 'num_nodes = %s' "\
                            "in [%s] section, where it should be digit "\
                            "numbers only" % (topo_info['num_nodes'], self.topo_type))
        else:
            raise KeyError("Configuration for 'num_nodes' value is missing" \
                        " in the [%s] section, please check!" % self.topo_type)

                        
    def create_rand_topo(self, topo_info):
        ''' create random topology '''
        if 'num_nodes' in topo_info and 'edge_prob' in topo_info:  
            if topo_info['num_nodes'].isdigit() and re.match("^\d+?\.\d+?$", topo_info['edge_prob']):
                self.num_nodes = int(topo_info['num_nodes'])
                prob = eval(topo_info['edge_prob'])
                self.topo = nx.gnp_random_graph(self.num_nodes, prob)
                self.relabel_nodes()
            else:
                raise ValueError("Invalid configuration for 'node_row = %s' or "\
                            "'node_col = %s' in [%s] section, where 'num_nodes'"\
                            " should be integer and 'edge_prob' should be floating "\
                            "number between 0 and 1" % (topo_info['num_nodes'], topo_info['edge_prob'], self.topo_type))                
        else:
            raise KeyError("Configuration for 'num_nodes' or 'edge_prob' or both is missing" \
                        " in the [%s] section, please check!" % self.topo_type)
                        
                        
    def create_custom(self, topo_info):
        ''' create custom topology '''
        if 'edges' in topo_info:
            self.topo = nx.Graph()            
            links = eval(topo_info['edges'])
            self.topo.add_edges_from(links)
        else:
            raise KeyError("Configuration for 'edges' is missing" \
                        " in the [%s] section, please check!" % self.topo_type)
                        
    def create_network(self, topo_info):
        """ 
        Create networks
        net_type:
        1: linear
        2: ring
        3: start
        4: grid
        5: fully mesh
        6: random
        7: custom: self defined topology
        The input topo_info is the dictionary of topology information
        """
        
        if self.topo_type == LINE:
            # linear topology
            self.create_line(topo_info)

        if self.topo_type == RING:
            # ring topology
            self.create_ring(topo_info)

        if self.topo_type == STAR:
            # star topology
            self.create_star(topo_info)
         
        if self.topo_type == GRID:
            # grid topology
            self.create_grid(topo_info)
            
        if self.topo_type == MESH:
            # fully mesh topology
            self.create_mesh(topo_info)
            
            
        if self.topo_type == RANDOM:
            # random topology
            self.create_rand_topo(topo_info)
            
            
        if self.topo_type == CUSTOM:
            # self defined topology
            self.create_custom(topo_info)
                
            
    def create_links(self):
        """
        create non-LAN links in the network, this function is called first if
        there are LANs to be added later. In other words, when creating 
        networks, first call this function to add non-LAN links. 
        """
        for idx, edge in enumerate(self.topo.edges()):         
            # link id starts from 1
            link = Link(idx+1)
            link.member = edge
            # update link list
            self.link_list.append(link)
    
    def get_node_summary(self):
        ''' get summary information about nodes '''
        self.summary['node'] = {}
        for node_id in self.node_dict:
            node = self.node_dict[node_id]
            self.summary['node'][node.id] = {}
            self.summary['node'][node.id]['hostname'] = node.hostname
            self.summary['node'][node.id]['type'] = node.node_type
            self.summary['node'][node.id]['cpu'] = node.cpu
            self.summary['node'][node.id]['bw'] = node.bw
            self.summary['node'][node.id]['disk_image'] = node.disk_image
            self.summary['node'][node.id]['num_iface'] = node.num_iface
            self.summary['node'][node.id]['geo_info'] = node.geoinfo
            self.summary['node'][node.id]['interface'] = {}
            self.summary['node'][node.id]['node-index'] = node.node_index
            for iface in node.iface_list:
                self.summary['node'][node.id]['interface'][iface.id] = {}
                self.summary['node'][node.id]['interface'][iface.id]['addr'] = iface.addr
                self.summary['node'][node.id]['interface'][iface.id]['prefix'] = iface.prefix
                self.summary['node'][node.id]['interface'][iface.id]['capacity'] = iface.capacity
                self.summary['node'][node.id]['interface'][iface.id]['name'] = iface.component_id
                self.summary['node'][node.id]['interface'][iface.id]['link_id'] = iface.link_id
    
    def get_link_summary(self):
        ''' get summary information about links '''
        self.summary['link'] = {}
        for link in self.link_list:
            # checking whether the link represents a multi-node LAN or not
            if isinstance(link, list):
                # the link is a list, and it represents a multi-node LAN, and 
                # all edges in this list share the same subnet
                link_id = link[0].id
                self.summary['link'][link_id] = {}
                self.summary['link'][link_id]['type'] = []
                self.summary['link'][link_id]['network'] = []
                self.summary['link'][link_id]['nodes'] = []
                self.summary['link'][link_id]['iface_pair'] = []
                for sub_link in link:
                    self.summary['link'][link_id]['type'].append(sub_link.link_type)
                    self.summary['link'][link_id]['network'].append(sub_link.network)
                    self.summary['link'][link_id]['nodes'].append(sub_link.member)
                    self.summary['link'][link_id]['iface_pair'].append(sub_link.ifaces)
            else:
                # non-LAN links summary
                self.summary['link'][link.id] = {}
                self.summary['link'][link.id]['type'] = link.link_type
                self.summary['link'][link.id]['network'] = link.network
                self.summary['link'][link.id]['nodes'] = link.member
                self.summary['link'][link.id]['iface_pair'] = link.ifaces


    def get_summary(self):
        ''' Print summary information about the network '''
        self.get_node_summary()
        self.get_link_summary()
        
        

def update_lan_format(lan_info, vn):
    """
    Assume from the configuration file, experimenters enter the information
    for additional LANs are lan=[(1,2,3),(4,5,6)], this function is to convert
    the format of LANs to the format that the script can add the LAN-links to 
    existing topology. 
    
    The function returns the new format of the lans as: 
    {sw1: [sw1, 1,2,3],
     sw2: [sw2, 4,5,6]
    }
    
    """
    # get a list of nodes in the exsiting topology
    node_list = vn.topo.nodes()
    # adding nodes attaching to a LAN to the existing node list
    for lan in lan_info:
        for node in lan:
            if node not in node_list:
                node_list.append(node)
    node_list.sort()
    # create a new lan dictionray
    new_lan_list = {}
    # Assign the initial id to the center switch node of the lAN
    sw_node = len(node_list) + 1
    for lan in lan_info:
        new_lan = list(lan)
        # insert the center switch node to the first element in the list
        # this is because the function add_star from networkx requirs the center node to be the first element
        new_lan.insert(0, sw_node)
        # update the new lan dictionary
        new_lan_list[sw_node] = new_lan
        # get the id for the next center switch
        sw_node += 1
    return new_lan_list, node_list


def config_links(vn, subnet_prefix):
    ''' configure the link information '''
    for link in vn.link_list:
        if isinstance(link, list):
            # for multi-node LAN case, the IP addresses for each node is like
            # 192.168.x.1, 192.168.x.2, ..., and start_ip represents the digit 
            # at the fourth chunk in the IPv4 address format.
            start_ip = 1
            for sub_link in link:
                nodeA_id, nodeB_id = sub_link.member
                # create Node object that connects to a LAN link
                if nodeA_id not in vn.node_dict:
                    nodeA = Node(nodeA_id, 'node')
                    vn.node_dict[nodeA_id] = nodeA
                if nodeB_id not in vn.node_dict:
                    nodeB = Node(nodeB_id, 'node')
                    vn.node_dict[nodeB_id] = nodeB
                # add new interface to the new nodes
                # NodeA is the invisible node type "sw", so we assign a fake IP (192.168.x.0) to it.
                vn.node_dict[nodeA_id].add_iface(sub_link.id, 0, subnet_prefix)
                # NodeB is the real node we need to include in the RSpec, assigning the real valid IP
                vn.node_dict[nodeB_id].add_iface(sub_link.id, start_ip, subnet_prefix)
                # get the ID for the new added interface, which is the last element in the node's interface list, represented by index "-1"
                nodeA_new_iface = vn.node_dict[nodeA_id].iface_list[-1].id
                nodeB_new_iface = vn.node_dict[nodeB_id].iface_list[-1].id
                # bind the link to corresponding interfaces
                sub_link.set_ifaces((nodeA_new_iface, nodeB_new_iface))
                # update the valid IP address for next node attaching to the LAN
                start_ip += 1
        else:
            # Non-LAN Links
            nodeA_id, nodeB_id = link.member
            if nodeA_id not in vn.node_dict:
                nodeA = Node(nodeA_id, 'node')
                vn.node_dict[nodeA_id] = nodeA
            if nodeB_id not in vn.node_dict:
                nodeB = Node(nodeB_id, 'node')
                vn.node_dict[nodeB_id] = nodeB 
            # Assuming the subnet is 192.168.x.0, so one node has IP 192.168.x.1, and the other is 192.168.x.2
            vn.node_dict[nodeA_id].add_iface(link.id, 1, subnet_prefix)
            vn.node_dict[nodeB_id].add_iface(link.id, 2, subnet_prefix)
            # get the ID for the new added interface, which is the last element in the node's interface list, represented by index "-1"
            nodeA_new_iface = vn.node_dict[nodeA_id].iface_list[-1].id
            nodeB_new_iface = vn.node_dict[nodeB_id].iface_list[-1].id
            # bind the link to corresponding interfaces
            link.set_ifaces((nodeA_new_iface, nodeB_new_iface)) 
    



def config_nodes(vn, config_info):
    ''' configure the node information '''
    
    # For random topology only, excluding the nodes not used
    for node_id in vn.topo.nodes():
        if node_id not in vn.node_dict:
            spare_node = Node(node_id, 'node')
            vn.node_dict[node_id] = spare_node
  
    # multiple node types defined in the configuration file must separated by ","
    node_type_list = config_info['general']['node_type'].split(',')
    # Create a dictionary to track nodes belonging to different types
    node_track = {}
    
    # initial the node list for each node type
    for node_type in node_type_list:
        node_type = node_type.strip()
        node_track[node_type]= []
    
    # configure nodes
    for node_id in vn.node_dict:
        node = vn.node_dict[node_id]           
        for node_type in node_type_list:
            node_type = node_type.strip()
            if config_info[node_type]['node_list'].upper() == 'ALL':
                # if all nodes belong to <node_type>
                sublist = vn.topo.nodes()
            else:
                # otherwise, get the list of nodes belonging to this particular <node_type>
                sublist = map(int, config_info[node_type]['node_list'].split(','))
            if node.id in sublist:
                # configure the node, if find the node id from the list
                node.set_prefix(config_info[node_type]['node_prefix'])
                node.update_type(node_type)
                # update the node list for the particular node type
                node_track[node_type].append(node.id)
                # for each node type, the index starts from 1
                node.node_index = len(node_track[node_type])
                node.set_name('%s-%d' % (node.prefix, node.node_index))
                #if node.node_type != 'lan-sw':
                node.disk_image = config_info[node_type]['disk_image']
                break
            if 'add-lan' in config_info:
                # the keys of the lan information dictionary are the center switches of the additional LANs
                if node.id in config_info['add-lan'].keys():
                    node.update_type('lan-sw')
                    break;
            if 'lan' in config_info:
                # 'lan' is a single-LAN type, node with id 0 is the center switch
                if node.id == 0:
                    node.update_type('lan-sw')
                    break;
        if node.node_type == 'node':
            raise ValueError("Node %s is not configured, please check the node" \
                            " list for each node category" % node.id)


def create_topo(config_info):
    ''' create networks including LAN topology '''
    # Get topopology type information, and make it to lower case
    topo_type = config_info['general']['topo_type'].lower()
    if topo_type not in TOPO_TYPES:
        type_list =  '["' + '", "'.join(TOPO_TYPES) + '"]'
        raise ValueError("Wrong topology type was provided! It should be" \
                         " one type from %s. You have \"%s\" " \
                         "in the configuration file" % (type_list,topo_type))
    else:
        if topo_type not in config_info:
            raise KeyError("There is no [%s] section in the configuration " \
                           "file, you need to add a section for topology " \
                           "type %s" % (topo_type, topo_type))
        else:
            topo_info = config_info[topo_type]
    # get LAN information from the configuration file, if it exists
    if 'add-lan' in config_info:
        print "Adding additional LANs to your topology"
        if 'lans' in config_info['add-lan']:
            lan_info = eval(config_info['add-lan']['lans'])
        else:
            raise KeyError("Configuration for 'lans' value is missing" \
                        " in the [add-lan] section, please check!")
    else:
        lan_info = None
        #print "There are no additional multi-point LANs."

    # get Shared LAN information from the configuration file, if it exists
    shared_lan_info ={}
    if 'add-shared-vlan' in config_info:
        print "Adding additional Shared LANs to your topology"

        if 'shared_vlans' in config_info['add-shared-vlan']:
            shared_vlans = config_info['add-shared-vlan']['shared_vlans']
            shared_vlans = [vlan.strip() for vlan in shared_vlans.split(",")]
            for sharedlan in shared_vlans:
                if sharedlan in config_info:
                    if 'lans' in config_info[sharedlan]:
                        shared_lan_info[sharedlan] = eval(config_info[sharedlan]['lans'])
        else:
            raise KeyError("Configuration for 'lans' value is missing" \
                        " in the [add-lan] section, please check!")
    else:
        shared_lan_info = None
        #print "There are no additional multi-point LANs."

    subnet_prefix = "192.168"
    if "subnet" in config_info['general']:
        subnet_prefix = config_info['general']['subnet']
        if len(subnet_prefix.split(".")) != 2:
            raise ValueError("WARNING: the value of the 'subnet' field is '%s'.  It should be two octets long (e.g 192.168 or 10.0) but was not." % str(subnet))

        try:
            sec_octet = int(subnet_prefix.split(".")[-1].strip())
        except:
            raise ValueError("subnet is not of form #.# where # is an integer in the range [0,255]. " \
            "Instead subnet = '%s'." % \
            (subnet_prefix))
        if sec_octet > 255:
            raise ValueError("Second octet of subnet cannot exceed 255! " \
            "Instead subnet = '%s'." % \
            (subnet_prefix))

        if sec_octet < 0:
            raise ValueError("Second octet of subnet cannot be less than 0! " \
            "Instead subnet = '%s'." % \
            (subnet_prefix))

    # create a virtual network object
    vn = Network(topo_type)

    sharedlan2 = None
    # if there are shared LANs to be added to an existing topology
    shared = {}
    # Two scenarios: single-LAN topology or other types of topologies
    if vn.topo_type == LAN:
        vn.create_lan(topo_info)

        if len(config_info['general']['node_type'].split(',')) == 1:
            # If there are only one type of nodes
            node_type = config_info['general']['node_type'].strip()
            if config_info[node_type]['node_list'].upper() == 'ALL':
                # if all nodes of the LANs are from this type
                config_info[node_type]['node_list'] = str(vn.topo.nodes()[1:])[1:-1]

        if "shared_vlan" in config_info[topo_type]:
            sharedlan2 = config_info[topo_type]['shared_vlan']
            #shared_vlans[sharedlan2] = config_info[node_type]['node_list']
            # The value here doesn't matter. It's just important that the entry exist.
            shared[sharedlan2] = True
                
    else:
        vn.create_network(topo_info)
        if len(vn.topo.edges()) > 254:
            raise ValueError("Can't have more than 254 links in the topology!" \
                             " Your topology has %d links!" % len(vn.topo.edges()))
        vn.create_links()


        if lan_info:
            vn, config_info, newlan = add_lan_to_vn( vn, lan_info, config_info)

        if shared_lan_info:
            for key, value in shared_lan_info.items():
                vn, config_info, newlan = add_lan_to_vn( vn, value, config_info)
                shared[key] = newlan

    # Configure new links
    config_links(vn, subnet_prefix)

    # Configure new nodes
    config_nodes(vn, config_info)

    vn.get_summary()

    return vn, shared
    
def add_lan_to_vn( vn, info, config_info):

            # if there are additional LANs, update the LAN information by adding the center switches transparently
            new_lan_list, node_list = update_lan_format(info, vn)
            # update the 'add-lan' information with add-on center switch node
            if not ("add-lan" in config_info):
                config_info['add-lan'] = {}
            config_info['add-lan'] = dict(config_info['add-lan'].items() + new_lan_list.items())
            if len(config_info['general']['node_type'].split(',')) == 1:
                node_type = config_info['general']['node_type'].strip()
                if config_info[node_type]['node_list'].upper() == 'ALL':
                    # update the list of nodes without the center switches
                    config_info[node_type]['node_list'] = str(node_list)[1:-1]
            newlan = vn.add_lan(new_lan_list)
            return vn, config_info, newlan
