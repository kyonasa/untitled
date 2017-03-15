#***************************************************************************
#@author:liwj mak huangxt wangxh
#***************************************************************************
import abc
import collections
import os
import sys
import eventlet

from oslo_config import cfg
from oslo_log import log as logging
import oslo_messaging

import  warnings
warnings.simplefilter("ignore", DeprecationWarning)

from ncclient import manager
from xml.dom.minidom import parse
import xml.dom.minidom

LOG = logging.getLogger(__name__)

from neutron.agent.wocloudvtep.drivers import abstract_driver 

class H3CNetconfUtil(object):
    
    def __init__(self,server_ip,server_port,username,password):
        self._server_ip = server_ip
        self._server_port = server_port
        self._username = username
        self._password = password
    
    def _my_unknown_host_cb(self, host, figerprint):
        return True
        
    def get_iface_index(self, interface_name):  
        ifindex = -1
        xmldata = """
        <top xmlns="http://www.h3c.com/netconf/data:1.0">
            <Ifmgr>
                <Interfaces>
                    <Interface>
                        <IfIndex/>
                        <Name>"""+interface_name+"""</Name>
                        <AbbreviatedName/>
                    </Interface>
                </Interfaces>
            </Ifmgr>
        </top>
        """
        try:
	    with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    c = m.get(('subtree',xmldata)).data_xml
		    dom = xml.dom.minidom.parseString(str(c))
		    root = dom.documentElement        
		    ifIndex = root.getElementsByTagName("IfIndex")
		    if len(ifIndex)!= 0:
		    	ifindex = int(ifIndex[0].firstChild.data)
        except Exception as e:
            LOG.error(e)
        return ifindex
    
    def delete_vxlan(self,vxlanid):
        xmldata = """
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <VXLAN xc:operation="delete">
                    <VXLANs>
                        <Vxlan>
                            <VxlanID>"""+str(vxlanid)+"""</VxlanID>                            
                        </Vxlan>
                    </VXLANs>
                </VXLAN>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target = 'running', config = xmldata)
        except Exception as e:
            LOG.error(e)
            
    def delete_vsi(self, vsiname):
        xmldata = """
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <L2VPN xc:operation="delete">
                    <VSIs>
                        <VSI>
                            <VsiName>"""+str(vsiname)+"""</VsiName>
                        </VSI>
                    </VSIs>
                </L2VPN>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target = 'running', config = xmldata)
        except Exception as e:
            LOG.error(e) 
            
    def delete_srv(self, ifIndex, sVlanRange):
        srvID = self.get_srv_id(ifIndex = ifIndex, sVlanRange = sVlanRange)
        if srvID == -1:
            return
        xmldata = """
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">               
                <L2VPN xc:operation="delete">
                    <ACs>
                        <AC>
                            <IfIndex>"""+str(ifIndex)+"""</IfIndex>
                            <SrvID>"""+str(srvID)+"""</SrvID>
                        </AC>
                    </ACs>
                    <SRVs>
                        <SRV>
                            <IfIndex>"""+str(ifIndex)+"""</IfIndex>
                            <SrvID>"""+str(srvID)+"""</SrvID>
                        </SRV>
                    </SRVs>
                </L2VPN>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target = 'running', config = xmldata)
        except Exception as e:
            LOG.error(e)
    
    def get_srv_id(self,ifIndex,sVlanRange):
        ifindex = -1
        xmldata = """
        <filter type="subtree">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <L2VPN>              
                    <SRVs>
                        <SRV>
                            <IfIndex>"""+str(ifIndex)+"""</IfIndex>                        
                            <SVlanRange>"""+str(sVlanRange)+"""</SVlanRange>
                        </SRV>
                    </SRVs>
                </L2VPN>
             </top>
        </filter>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    c = m.get_config(source = 'running',filter = xmldata).data_xml
		    dom = xml.dom.minidom.parseString(str(c))
		    root = dom.documentElement        
		    ifIndex = root.getElementsByTagName("SrvID")
		    if len(ifIndex)!= 0:
		    	ifindex = int(ifIndex[0].firstChild.data)
        except Exception as e:
            LOG.error(e)
        return ifindex
    
    def delete_tunnel(self, tunnelid):
        if tunnelid == -1:
            return
        xmldata = """
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <TUNNEL xc:operation="delete">
                    <Tunnels>
                        <Tunnel>
                            <ID>"""+str(tunnelid)+"""</ID>
                        </Tunnel>
                    </Tunnels>
                </TUNNEL>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target='running', config=xmldata)
        except Exception as e:
            LOG.error(e)
            
    def unbond_tunnel_vxlan(self, srcip, dstip, tunnelid, vxlanid):
        if tunnelid == -1:
            return
        xmldata = """
        <config xmlns:xc="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <VXLAN xc:operation="delete">
                    <Tunnels>
                        <Tunnel>
                            <VxlanID>"""+str(vxlanid)+"""</VxlanID>
                            <TunnelID>"""+str(tunnelid)+"""</TunnelID>
                        </Tunnel>
                    </Tunnels>
                </VXLAN>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target = 'running', config = xmldata)
        except Exception as e:
            LOG.error(e)
            
    def get_tunnel_id(self,srcip,dstip):
        tunnel_id = -1
        xmldata = """
        <filter type="subtree">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <TUNNEL>
                    <Tunnels>
                        <Tunnel>
                            <IPv4Addr>
                                <SrcAddr>"""+str(srcip)+"""</SrcAddr>
                                <DstAddr>"""+str(dstip)+"""</DstAddr>
                            </IPv4Addr>
                        </Tunnel>
                    </Tunnels>
                </TUNNEL>
            </top>
        </filter>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    c = m.get_config(source = 'running',filter = xmldata).data_xml
		    dom = xml.dom.minidom.parseString(str(c))
		    root = dom.documentElement        
		    tunnels = root.getElementsByTagName("Tunnel")
		    for tunnel in tunnels:
		    	srcaddr = tunnel.getElementsByTagName("SrcAddr")
			dstaddr = tunnel.getElementsByTagName("DstAddr")
			tunnelid = tunnel.getElementsByTagName("ID")
			if ((len(srcaddr)!= 0) & (len(dstaddr)!= 0)):
				tunnel_id = int(tunnelid[0].firstChild.data)
        except Exception as e:
            LOG.error(e)
        return tunnel_id
    
    def find_max_srv_id(self,ifidex):     
        data = self.get_srv_config(ifidex)
        root = xml.dom.minidom.parseString(data).documentElement
        srvs = root.getElementsByTagName("SRV")
        maxSrvID = 0
        for srv in srvs:
            if((int(srv.getElementsByTagName("IfIndex")[0].firstChild.data) == ifidex)&
               ((int(srv.getElementsByTagName("SrvID")[0].firstChild.data) >= maxSrvID)&
                len(srv.getElementsByTagName("SrvID")[0].firstChild.data) != 0)):
                maxSrvID = int(srv.getElementsByTagName("SrvID")[0].firstChild.data)
        return maxSrvID
    
    def get_srv_config(self,ifIndex):
        c = ""    
        xmldata = """
        <filter type="subtree">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <L2VPN>
                    <SRVs>
                        <SRV>
                            <IfIndex>"""+str(ifIndex)+"""</IfIndex>
                        </SRV>
                    </SRVs>
                </L2VPN>                          
            </top>
        </filter>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    c = m.get_config(source = 'running',filter = xmldata).data_xml
        except Exception as e:
            LOG.error(e)
        return c
    
    def create_srv(self,ifIndex,srvID,sVlanRange,vsiName):
        xmldata = """
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <L2VPN>
                    <SRVs>
                        <SRV>
                            <IfIndex>"""+str(ifIndex)+"""</IfIndex>
                            <SrvID>"""+str(srvID)+"""</SrvID>
                            <Encap>4</Encap>
                            <SVlanRange>"""+str(sVlanRange)+"""</SVlanRange>
                        </SRV>
                    </SRVs>
                    <ACs>
                        <AC>
                            <IfIndex>"""+str(ifIndex)+"""</IfIndex>
                            <SrvID>"""+str(srvID)+"""</SrvID>
                            <VsiName>"""+str(vsiName)+"""</VsiName>
                        </AC>
                    </ACs>
                </L2VPN>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target = 'running', config = xmldata)
        except Exception as e:
            LOG.error(e)
            
    def check_tunnel(self,srcip, dstip):
        data = self.get_tunnel_config()
        dom = xml.dom.minidom.parseString(data)
        root = dom.documentElement
        tunnels = root.getElementsByTagName("Tunnel")
        ids = root.getElementsByTagName("ID")
        for tunnel in tunnels:
            srcaddr = tunnel.getElementsByTagName("SrcAddr")
            dstaddr = tunnel.getElementsByTagName("DstAddr")
            tunnelid = tunnel.getElementsByTagName("ID")
            if ((len(srcaddr) != 0) & (len(dstaddr) != 0)):
                if ((srcaddr[0].firstChild.data == srcip) & (dstaddr[0].firstChild.data == dstip)):
                    return int(tunnelid[0].firstChild.data)
        maxid = -1
        for tunnelid in ids:
            if int(tunnelid.childNodes[0].data) > maxid:
                maxid = int(tunnelid.childNodes[0].data)
        self.create_tunnel(srcip = srcip,dstip = dstip,tunnelid = int(maxid)+1)
        return int(maxid)+1 
    
    def get_tunnel_config(self):
        c = ''
        xmldata = """
        <filter type="subtree">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <TUNNEL>
                    <Tunnels>
                    </Tunnels>
                </TUNNEL>
            </top>
        </filter>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    c = m.get_config(source = 'running',filter = xmldata).data_xml
        except Exception as e:
            LOG.error(e)
        return c
    
    def bond_tunnel_vxlan(self,vxlanid, tunnelid):
        xmldata = """
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <VXLAN>
                    <Tunnels>
                        <Tunnel>
                            <VxlanID>"""+str(vxlanid)+"""</VxlanID>
                            <TunnelID>"""+str(tunnelid)+"""</TunnelID>
                        </Tunnel>
                    </Tunnels>
                </VXLAN>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target = 'running', config = xmldata)
        except Exception as e:
            LOG.error(e)
            
    def create_tunnel(self,srcip,dstip,tunnelid):
        xmldata = """
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <TUNNEL>
                    <Tunnels>
                        <Tunnel>
                            <ID>"""+str(tunnelid)+"""</ID>
                            <Mode>24</Mode>
                            <IPv4Addr>
                                <SrcAddr>"""+str(srcip)+"""</SrcAddr>
                                <DstAddr>"""+str(dstip)+"""</DstAddr>
                            </IPv4Addr>
                        </Tunnel>
                    </Tunnels>
                </TUNNEL>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target = 'running', config = xmldata)
        except Exception as e:
            LOG.error(e)
            
    def create_vxlan(self,vsiname,vxlanid):
        xmldata = """
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <VXLAN>
                    <VXLANs>
                        <Vxlan>
                            <VxlanID>"""+str(vxlanid)+"""</VxlanID>
                            <VsiName>"""+str(vsiname)+"""</VsiName>
                        </Vxlan>
                    </VXLANs>
                </VXLAN>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target = 'running', config = xmldata)
        except Exception as e:
            LOG.error(e)
            
    def create_vsi(self,vsiname):
        xmldata = """
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
            <top xmlns="http://www.h3c.com/netconf/config:1.0">
                <L2VPN>
                    <VSIs>
                        <VSI>
                            <VsiName>"""+str(vsiname)+"""</VsiName>
                        </VSI>
                    </VSIs>
                </L2VPN>
            </top>
        </config>
        """
        try:
            with manager.connect_ssh(host = self._server_ip, 
                    port = self._server_port, 
                    username = self._username, 
                    password = self._password, 
                    unknown_host_cb = self._my_unknown_host_cb, 
                    device_params = {'name':'h3c'}) as m:
		    m.edit_config(target = 'running', config = xmldata)
        except Exception as e:
            LOG.error(e)

class H3CVtepDriver(abstract_driver.WocloudVtepAbstractDriver):
    
    OPTS = [
        cfg.StrOpt('wocloudvtep_h3c_netconf_server_ip',
                   help=_("The netconf server ip for wocloudvtep")), 
        cfg.IntOpt('wocloudvtep_h3c_netconf_server_port',
                   help=_("The netconf server ip for wocloudvtep")),
        cfg.StrOpt('wocloudvtep_h3c_netconf_server_username',
                   default=[],
                   help=_("The netconf server username for wocloudvtep")),
        cfg.StrOpt('wocloudvtep_h3c_netconf_server_password',
                   help=_("The netconf server password for wocloudvtep")),
    ]
    
    def __init__(self,conf,endpoint):
        super(H3CVtepDriver,self).__init__(conf,endpoint)
        
    def wocloudvtep_created(self,endpoint):
        LOG.info("begin wocloudvtep_created")
        LOG.info(endpoint)
        LOG.info("end wocloudvtep_created")
    
    def port_bond_to_wocloudvtep(self,endpoint,port):
        LOG.info("begin port_bond_to_wocloudvtep")
        if self._check_vlan_need_config(port['network_id'], port['host']):
            self.ports[port['id']] = port
            host = port['host']
            portname = self.hosts[host]['portname']
            netconf_util = H3CNetconfUtil(self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_ip,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_port,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_username,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_password
                                          )
            ifIndex = netconf_util.get_iface_index(str(portname))
            srvID = netconf_util.find_max_srv_id(ifIndex)+1
            sVlanRange = self.networks[port['network_id']]['vlan']
            vsiName = self._get_vsi_name(port['network_id'])
            LOG.info('create srv')
            netconf_util.create_srv(ifIndex,srvID,sVlanRange,vsiName)
        else:
            self.ports[port['id']] = port
        LOG.info("end port_bond_to_wocloudvtep")
    
    def network_bond_to_wocloudvtep(self,endpoint,network):
        LOG.info("begin network_bond_to_wocloudvtep")
        if endpoint == self.endpoint:
            self.networks[network['id']] = network
            netconf_util = H3CNetconfUtil(self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_ip,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_port,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_username,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_password
                                          )
            LOG.info('create vsi for %s' % network['id'])
            netconf_util.create_vsi(self._get_vsi_name(network['id']))
            LOG.info('add vni %d vsi for %s' % (network['vxlan'],network['id']))
            netconf_util.create_vxlan(self._get_vsi_name(network['id']),network['vxlan'])
            for endpoint in network['endpoints']:
                if endpoint != self.endpoint:
                    LOG.info('ensure tunnel from %s to %s' % (self.endpoint,endpoint))
                    tunnelid = netconf_util.check_tunnel(self.endpoint,endpoint)
                    LOG.info('connnect vni %s with tunnel  %s <-> %s' % (network['vxlan'],self.endpoint,endpoint))
                    netconf_util.bond_tunnel_vxlan(network['vxlan'], tunnelid)
        else:
            if self.networks.has_key(network['id']):
                self.networks[network['id']]['endpoints'].append(endpoint)
                netconf_util = H3CNetconfUtil(self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_ip,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_port,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_username,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_password
                                          )
                LOG.info('ensure tunnel from %s to %s' % (self.endpoint,endpoint))
                tunnelid = netconf_util.check_tunnel(self.endpoint,endpoint)
                LOG.info('connnect vni %s with tunnel  %s <-> %s' % (network['vxlan'],self.endpoint,endpoint))
                netconf_util.bond_tunnel_vxlan(network['vxlan'], tunnelid)
        LOG.info("end network_bond_to_wocloudvtep")
    
    def port_unbond_from_wocloudvtep(self,endpoint,port):
        LOG.info("begin port_unbond_from_wocloudvtep")
        if self.ports.has_key(port['id']):
            port = self.ports.pop(port['id'])
            if self._check_vlan_need_remove(port['network_id'], port['host']):
                network = self.networks[port['network_id']]
                host = port['host']
                portname = self.hosts[host]['portname']
                netconf_util = H3CNetconfUtil(self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_ip,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_port,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_username,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_password
                                          )
                ifIndex = netconf_util.get_iface_index(str(portname))
                LOG.info("delete srv %s from host %s" % (network['vlan'],port['host']))
                netconf_util.delete_srv(ifIndex = ifIndex, sVlanRange = network['vlan'])
        LOG.info("end port_unbond_from_wocloudvtep")
    
    def network_unbond_from_wocloudvtep(self,endpoint,network):
        if not self.networks.has_key(network['id']):
            return
        LOG.info("begin network_unbond_from_wocloudvtep")
        netconf_util = H3CNetconfUtil(self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_ip,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_port,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_username,
                                          self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_password
                                          )
        if endpoint == self.endpoint:
            network = self.networks.pop(network['id'])
            for endpoint in network['endpoints']:
                if endpoint != self.endpoint: 
                    LOG.info("disconnect vni %s from tunnel %s-%s" % (network['vxlan'],self.endpoint,endpoint))
                    tunnelid = netconf_util.get_tunnel_id(srcip = self.endpoint, dstip = endpoint)
                    netconf_util.unbond_tunnel_vxlan(srcip = self.endpoint, dstip = endpoint, tunnelid = tunnelid, vxlanid = network['vxlan'])
                    if self._check_tunnel_need_remove(endpoint):
                        LOG.info("tunnel %s <-> %s will be removed" %(self.endpoint,endpoint))
                        netconf_util.delete_tunnel(tunnelid)
            LOG.info("remove vxlan %s" % network['vxlan'])
            netconf_util.delete_vxlan(network['vxlan'])
            LOG.info("remove vsi %s" % network['id'])
            netconf_util.delete_vsi(self._get_vsi_name(network['id'][0:30]))
        else:
            network_id = network['id']
            self.networks[network_id]['endpoints'].remove(endpoint)
            LOG.info('disconnnect vni %s with tunnel  %s <-> %s' % (self.networks[network_id]['vxlan'],self.endpoint,endpoint))
            tunnelid = netconf_util.get_tunnel_id(srcip = self.endpoint, dstip = endpoint)
            netconf_util.unbond_tunnel_vxlan(srcip = self.endpoint, dstip = endpoint, tunnelid = tunnelid, vxlanid = self.networks[network_id]['vxlan'])
            if self._check_tunnel_need_remove(endpoint):
                LOG.info('remove tunnel from %s to %s' % (self.endpoint,endpoint))
                netconf_util.delete_tunnel(tunnelid)
        LOG.info("end network_unbond_from_wocloudvtep")
        
    def _get_vsi_name(self,network_id):
        return network_id[0:30]
    
    def _check_vlan_need_config(self,network_id,host):
        for port_id in self.ports:
            if self.ports[port_id]['network_id'] == network_id and self.ports[port_id]['host'] == host:
                return False
        return True
    
    def _check_tunnel_need_remove(self,endpoint):
        for network_id in self.networks:
            if self.networks[network_id]['endpoints'].count(endpoint):
                return False
        return True
    
    def _check_vlan_need_remove(self,network_id,host):
        for port_id in self.ports:
            if self.ports[port_id]['network_id'] == network_id and self.ports[port_id]['host'] == host:
                return False
        return True
    
    @staticmethod
    def get_driver_type_name():
        return 'h3c'
    
    def get_wocloudvtep_configurations(self):
        return {'ip':self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_ip,
                'port':self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_port,
                'username':self.conf.WOCLOUDVTEP.wocloudvtep_h3c_netconf_server_username,
                'password':'******'
                }

