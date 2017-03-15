from pyhp.comware import HPCOM7
from pyhp.features.vlan import Vlan
from pyhp.features.vxlan import L2EthService
from pyhp.features.vxlan import Vxlan
from pyhp.features.vxlan import Tunnel
from pyhp.features.interface import Interface
from pyhp.features.ipinterface import IpInterface
from pyhp.features.ping import Ping
import django


from lxml import etree
from ncclient.xml_ import qualify
from pyhp.utils.xml.namespaces import HPDATA
from pyhp.utils.xml.namespaces import HPDATA_C
from pyhp.utils.xml.lib import append_subelement

args1=dict(host='10.3.214.197',username='admin',password='admin',port=830)
args2=dict(host='10.3.214.198',username='admin',password='admin',port=830)
device1=HPCOM7(**args1)
device2=HPCOM7(**args2)
device1.open()
device2.open()
# device.connected

# print (device)
#
ping=Ping(device1,'10.3.214.22')
vlan1=Vlan(device1, '15')
vlan2=Vlan(device2,'10')
vxlan1=Vxlan(device1,'12',vsi='vpnc')
vxlan2=Vxlan(device2,'12',vsi='vpnc')
L2EthService1=L2EthService(device1,'Ten-GigabitEthernet1/0/4','1001','vpnc')
L2EthService2=L2EthService(device2,'Ten-GigabitEthernet1/0/4','1001','vpnc')
tunnel1=Tunnel(device1,'2')
tunnel2=Tunnel(device2,'2')
interface1=Interface(device1,'Ten-GigabitEthernet1/0/2')
ipinterface1=IpInterface(device1,'Vlan-interface12')

# print (vxlan1.get_config())
print (vxlan1.remove_vsi(vsi='vpnc'))
device1.execute()
# print (vxlan1.get_config())

# print (L2EthService1.get_config())
# print (L2EthService1.remove())
# device1.execute()
# print (L2EthService1.get_config())
# # L=L2EthService()
# # print (vlan.vlanid)
# # print (etree.Element(qualify('top', HPDATA)))
# # print (HPDATA_C)
# #
# # top_level = .retree.Element(qualify('top', HPDATA))
# # append_subelement(top_level, vlan.tags, HPDATA)
# # last_child = top_level.find('.//{0}VLANID'.format(HPDATA_C))
# # print (top_level)
# # print (vlan.get_vlan_list())
# # print (vlan.build(vlanid='15'))
# # device.execute()
# # print (vlan2.get_vlan_list())
# print (ping.response)
# print (vxlan1.get_config())
# print (vxlan1.create())
# device1.execute()
# print (vxlan1.get_config())
#
# print (vxlan2.get_config())
# print (vxlan2.create())
# device2.execute()
# print (vxlan2.get_config())
# # print (tunnel.get_config())
#
# # print (vxlan.get_config())
# # print (vxlan.get_tunnels())
#
#
# print (L2EthService.get_config())
# print (tunnel1.get_config())
# print (tunnel1.build(src='1.1.1.1',dest='172.16.16.250'))
# device1.execute()
# print (tunnel1.get_config())
# print (tunnel2.get_config())
# print (tunnel2.build(src='172.16.16.250',dest='1.1.1.1'))
# device2.execute()
# print (tunnel2.get_config())
# print (vxlan2.build(tunnels_to_add=['2']))
# device2.execute()
# print (vxlan2.get_config())
# print (vxlan1.build(tunnels_to_add=['2']))
# device1.execute()
# print (vxlan1.get_config())
# # print (ipinterface2.get_config())
# # print (ipinterface2.build(addr='12.1.1.1',mask='24'))
# # print (ipinterface2.get_config())
# # device.execute()
# print (L2EthService1.get_config())
# print (L2EthService1.build(vsi='vpnc',instance='1002',encap='s-vid',vlanid='14',access_mode='vlan'))
# device1.execute()
# print (L2EthService1.get_config())
# print (L2EthService2.get_config())
# print (L2EthService2.build(vsi='vpnc',instance='1002',encap='s-vid',vlanid='14',access_mode='vlan'))
# device2.execute()
# print (L2EthService2.get_config())
# # interface=Interface(device,'Ten-GigabitEthernet1/0/14')
# # result = interface.get_config()
# # print result
# # import pdb;pdb.set_trace()
