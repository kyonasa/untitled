try:
    from ncclient import manager, xml_
    from ncclient.operations.rpc import RPCError
    from ncclient.transport.errors import AuthenticationError
    from ncclient.operations.errors import TimeoutExpiredError
    HAS_NCCLIENT = True
except ImportError:
    HAS_NCCLIENT = False

step1 = """
bridge-domain 10
 vxlan vni 5010
"""
CREATE_BD = """
    <config>
      <evc xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <bds>
          <bd operation="merge">
            <bdId>10</bdId>
          </bd>
        </bds>
      </evc>
    </config>
"""
CREATE_BD_VNI = """
    <config>
      <nvo3 xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <nvo3Vni2Bds>
          <nvo3Vni2Bd operation="merge">
            <vniId>5010</vniId>
            <bdId>10</bdId>
          </nvo3Vni2Bd>
        </nvo3Vni2Bds>
      </nvo3>
    </config>
"""
DELETE_BD_VNI = """
    <config>
      <nvo3 xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <nvo3Vni2Bds>
          <nvo3Vni2Bd operation="delete">
            <vniId>5010</vniId>
            <bdId>10</bdId>
          </nvo3Vni2Bd>
        </nvo3Vni2Bds>
      </nvo3>
    </config>
"""

step2 = """
interface 10GE2/0/2.1 mode l2
 encapsulation dot1q vid 10
 bridge-domain 10
"""
CREATE_L2_INTERFACE = """
    <config>
      <ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <interfaces>
          <interface operation="merge">
            <ifName>10GE2/0/2.1</ifName>
            <ifPhyType>10GE</ifPhyType>
            <ifParentIfName>10GE1/0/2</ifParentIfName>
            <ifNumber>1</ifNumber>
            <ifClass>subInterface</ifClass>
            <l2SubIfFlag>true</l2SubIfFlag>
          </interface>
        </interfaces>
      </ifm>
    </config>
"""
CREATE_L2_INTERFACE_DOT1Q_VID = """
    <config>
      <ethernet xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <servicePoints>
          <servicePoint>
            <ifName>10GE2/0/2.1</ifName>
            <flowDot1qs operation="create">
              <dot1qVids>0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000</dot1qVids>
            </flowDot1qs>
          </servicePoint>
        </servicePoints>
      </ethernet>
    </config>
"""
DELETE_L2_INTERFACE_DOT1Q_VID = """
    <config>
      <ethernet xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <servicePoints>
          <servicePoint>
            <ifName>10GE2/0/2.1</ifName>
            <flowDot1qs operation="delete">
              <dot1qVids>0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000</dot1qVids>
            </flowDot1qs>
          </servicePoint>
        </servicePoints>
      </ethernet>
    </config>
"""
BIND_BD_VLAN = """
    <config>
      <evc xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <bds>
          <bd>
            <bdId>10</bdId>
            <bdBindVlan operation="merge">
              <vlanList>0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000</vlanList>
            </bdBindVlan>
          </bd>
        </bds>
      </evc>
    </config>
"""

step3 = """
interface LoopBack1
 ip address 2.2.2.2 255.255.255.255
"""
CREATE_LOOPBACK_INTERFACE = """
    <config>
      <ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <interfaces>
          <interface operation="merge">
            <ifName>LoopBack1</ifName>
            <ifPhyType>LoopBack</ifPhyType>
            <ifParentIfName>LoopBack1</ifParentIfName>
            <ifNumber>1</ifNumber>
          </interface>
        </interfaces>
      </ifm>
    </config>
"""
CONFIG_INTERFACE_LOOPBACK = """
    <config>
      <ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <interfaces>
          <interface>
            <ifName>LoopBack1</ifName>
            <ifmAm4 operation="merge">
              <am4CfgAddrs>
                <am4CfgAddr operation="create">
                  <subnetMask>255.255.255.255</subnetMask>
                  <ifIpAddr>2.2.2.2</ifIpAddr>
                </am4CfgAddr>
            </ifmAm4>
          </interface>
        </interfaces>
      </ifm>
    </config>
"""

step4 = """
interface Nve1
 source 2.2.2.2
 vni 5010 head-end peer-list 3.3.3.3
 """
CREATE_NVE_INTERFACE = """
    <config>
      <ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <interfaces>
          <interface operation="merge">
            <ifName>Nve1</ifName>
            <ifPhyType>Nve</ifPhyType>
            <ifParentIfName>Nve1</ifParentIfName>
            <ifNumber>1</ifNumber>
          </interface>
        </interfaces>
      </ifm>
    </config>
"""
CREATE_NVE_INTERFACE_SOURCE = """
    <config>
      <nvo3 xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <nvo3Nves>
          <nvo3Nve operation="merge">
            <ifName>Nve1</ifName>
            <srcAddr>2.2.2.2</srcAddr>
          </nvo3Nve>
        </nvo3Nves>
      </nvo3>
    </config>
"""
CREATE_HEAD_END_PEER_LIST = """
    <config>
      <nvo3 xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <nvo3Nves>
          <nvo3Nve>
            <ifName>Nve1</ifName>
            <vniMembers>
              <vniMember>
                <vniId>5010</vniId>
                <nvo3VniPeers>
                  <nvo3VniPeer operation="merge">
                    <peerAddr>3.3.3.3</peerAddr>
                  </nvo3VniPeer>
                </nvo3VniPeers>
              </vniMember>
            </vniMembers>
          </nvo3Nve>
        </nvo3Nves>
      </nvo3>
    </config>
"""

step5 = """
interface Vbdif10
 ip address 192.168.10.10 255.255.255.0
 mac-address 0000-5e00-0101
"""
CREATE_VBDIF_INTERFACE = """
    <config>
      <ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <interfaces>
          <interface operation="merge">
            <ifName>Vbdif10</ifName>
            <ifPhyType>Vbdif</ifPhyType>
            <ifParentIfName>Vbdif10</ifParentIfName>
            <ifNumber>10</ifNumber>
            <ifMac>0000-5e00-0101</ifMac>
          </interface>
        </interfaces>
      </ifm>
    </config>
"""
CONFIG_INTERFACE_VBDIF = """
    <config>
      <ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <interfaces>
          <interface>
            <ifName>Vbdif10</ifName>
            <ifmAm4 operation="merge">
              <am4CfgAddrs>
                <am4CfgAddr operation="create">
                  <subnetMask>255.255.255.0</subnetMask>
                  <ifIpAddr>192.168.10.10</ifIpAddr>
                </am4CfgAddr>
            </ifmAm4>
          </interface>
        </interfaces>
      </ifm>
    </config>
"""

step6 = """
interface Eth-Trunk10.1 mode l2
 encapsulation dot1q vid 10
 bridge-domain 10
"""
CREATE_L2_INTERFACE_ETH_TRUNK = """
    <config>
      <ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <interfaces>
          <interface operation="merge">
            <ifName>Eth-Trunk10.1</ifName>
            <ifPhyType>Eth-Trunk</ifPhyType>
            <ifParentIfName>Eth-Trunk10</ifParentIfName>
            <ifNumber>1</ifNumber>
            <ifClass>subInterface</ifClass>
            <l2SubIfFlag>true</l2SubIfFlag>
          </interface>
        </interfaces>
      </ifm>
    </config>
"""
CREATE_L2_ETH_TRUNK_DOT1Q_VID = """
    <config>
      <ethernet xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <servicePoints>
          <servicePoint>
            <ifName>Eth-Trunk10.1</ifName>
            <flowDot1qs operation="create">
              <dot1qVids>0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000</dot1qVids>
            </flowDot1qs>
          </servicePoint>
        </servicePoints>
      </ethernet>
    </config>
"""
DELETE_L2_ETH_TRUNK_DOT1Q_VID = """
    <config>
      <ethernet xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <servicePoints>
          <servicePoint>
            <ifName>Eth-Trunk10.1</ifName>
            <flowDot1qs operation="delete">
              <dot1qVids>0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000</dot1qVids>
            </flowDot1qs>
          </servicePoint>
        </servicePoints>
      </ethernet>
    </config>
"""
BIND_BD_VLAN_ETH_TRUNK = """
    <config>
      <evc xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
        <bds>
          <bd>
            <bdId>10</bdId>
            <bdBindVlan operation="merge">
              <vlanList>0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000:0020000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000</vlanList>
            </bdBindVlan>
          </bd>
        </bds>
      </evc>
    </config>
"""

def main():

    if not HAS_NCCLIENT:
        print("the ncclient not installed")
        return

    try:
        mc = manager.connect(host="111.202.93.90", port="22", username="admin", password="admin",
                             allow_agent=False, look_for_keys=False, hostkey_verify=False,
                             device_params={'name': 'DC2_leaf3'}, timeout=30)
    except AuthenticationError:
        print("Error: Authentication failed while connecting to device.")
        raise
    except Exception:
        print("Error: Other error happen.")
        raise

    con_obj = None

    #step 1
    try:
        con_obj = mc.edit_config(target='running', config=CREATE_BD)
    except RPCError:
        print ("Error: step 1.1")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE_BD ok")

    try:
        con_obj = mc.edit_config(target='running', config=CREATE_BD_VNI)
    except RPCError:
        print ("Error: step 1.2")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE_BD_VNI ok")

    #step 2
    try:
        con_obj = mc.edit_config(target='running', config=CREATE_L2_INTERFACE)
    except RPCError:
        print ("Error: step 2.1")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE_L2_INTERFACE ok")

    try:
        con_obj = mc.edit_config(target='running', config=CREATE_L2_INTERFACE_DOT1Q_VID)
    except RPCError:
        print ("Error: step 2.2")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE_L2_INTERFACE_DOT1Q_VID ok")

    try:
        con_obj = mc.edit_config(target='running', config=BIND_BD_VLAN)
    except RPCError:
        print ("Error: step 2.3")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set BIND_BD_VLAN ok")



if __name__ == '__main__':
    main()
