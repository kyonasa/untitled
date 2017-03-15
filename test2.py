try:
    from ncclient import manager, xml_
    from ncclient.operations.rpc import RPCError
    from ncclient.transport.errors import AuthenticationError
    from ncclient.operations.errors import TimeoutExpiredError
    HAS_NCCLIENT = True
    import math
except ImportError:
    HAS_NCCLIENT = False

if not HAS_NCCLIENT:
    print("the ncclient not installed")

def svlanid(vlan):
    vlan=10
    svlanid=''
    vlanid=[0 for i in range(1024)]
    if vlan%4==0:
        vlanid[int(math.floor(vlan/4))]=8
    elif vlan%4==1:
        vlanid[int(math.floor(vlan / 4))] = 4
    elif vlan%4==2:
        vlanid[int(math.floor(vlan / 4))] = 2
    elif vlan%4==3:
        vlanid[int(math.floor(vlan / 4))] = 1
    for i in range(1024):
        svlanid=svlanid+str(vlanid[i])
    return svlanid

print (svlanid(10))

def create_BD(BD):
    CREATE_BD = """
        <config>
          <evc xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
            <bds>
              <bd operation="merge">
                <bdId>"""+str(BD)+"""</bdId>
              </bd>
            </bds>
          </evc>
        </config>
    """
    try:
        con_obj = mc.edit_config(target='running', config=CREATE_BD)
    except RPCError:
        print ("Error: step 1.1")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE_BD ok")

def BD_bind_VNI(BD,VNI):
    CREATE_BD_VNI = """
        <config>
          <nvo3 xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
            <nvo3Vni2Bds>
              <nvo3Vni2Bd operation="merge">
                <vniId>"""+str(VNI)+"""</vniId>
                <bdId>"""+str(BD)+"""</bdId>
              </nvo3Vni2Bd>
            </nvo3Vni2Bds>
          </nvo3>
        </config>
    """
    try:
        con_obj = mc.edit_config(target='running', config=CREATE_BD_VNI)
    except RPCError:
        print ("Error: step 1.2")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE_BD_VNI ok")

def create_l2_if(ifname,ifnumber,iftype):
    CREATE_L2_INTERFACE = """
        <config>
          <ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
            <interfaces>
              <interface operation="merge">
                <ifName>"""+str(ifname)+'.'+str(ifnumber)+"""</ifName>
                <ifPhyType>"""+str(iftype)+"""</ifPhyType>
                <ifParentIfName>"""+str(ifname)+"""</ifParentIfName>
                <ifNumber>"""+str(ifnumber)+"""</ifNumber>
                <ifClass>subInterface</ifClass>
                <l2SubIfFlag>true</l2SubIfFlag>
              </interface>
            </interfaces>
          </ifm>
        </config>
    """
    try:
        con_obj = mc.edit_config(target='running', config=CREATE_L2_INTERFACE)
    except RPCError:
        print ("Error: step 2.1")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE_L2_INTERFACE ok")

def create_l2_if_vlan(ifname,ifnumber,vlanid):
    CREATE_L2_INTERFACE_DOT1Q_VID = """
        <config>
          <ethernet xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
            <servicePoints>
              <servicePoint>
                <ifName>"""+str(ifname)+'.'+str(ifnumber)+"""</ifName>
                <flowDot1qs operation="create">
                  <dot1qVids>"""+str(svlanid(vlanid))+':'+str(svlanid(vlanid))+"""</dot1qVids>
                </flowDot1qs>
              </servicePoint>
            </servicePoints>
          </ethernet>
        </config>
    """
    try:
        con_obj = mc.edit_config(target='running', config=CREATE_L2_INTERFACE_DOT1Q_VID)
    except RPCError:
        print ("Error: step 2.2")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE_L2_INTERFACE_DOT1Q_VID ok")

def bind_BD_VLAN(BD,vlanid):
    BIND_BD_VLAN = """
        <config>
          <evc xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
            <bds>
              <bd>
                <bdId>"""+str(BD)+"""</bdId>
                <bdBindVlan operation="merge">
                  <vlanList>"""+str(svlanid(vlanid))+':'+str(svlanid(vlanid))+"""</vlanList>
                </bdBindVlan>
              </bd>
            </bds>
          </evc>
        </config>
    """
    try:
        con_obj = mc.edit_config(target='running', config=BIND_BD_VLAN)
    except RPCError:
        print ("Error: step 2.3")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set BIND_BD_VLAN ok")

def create_nve_if(NVEI_NAME,NVEI_ID):
    # e.g.
    # NVEI_NAME='Nve1'
    # NVEI_ID='1'
    CREATE_NVE_INTERFACE = """
        <config>
          <ifm xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
            <interfaces>
              <interface operation="merge">
                <ifName>"""+str(NVEI_NAME)+"""</ifName>
                <ifPhyType>Nve</ifPhyType>
                <ifParentIfName>"""+str(NVEI_NAME)+"""</ifParentIfName>
                <ifNumber>"""+str(NVEI_ID)+"""</ifNumber>
              </interface>
            </interfaces>
          </ifm>
        </config>
    """
    try:
        con_obj = mc.edit_config(target='running', config=CREATE_NVE_INTERFACE)
    except RPCError:
        print ("Error: step 4.1")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE NVEI ok")


def create_nvei_source(NVEI_NAME,source_ip):
    CREATE_NVE_INTERFACE_SOURCE = """
        <config>
          <nvo3 xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
            <nvo3Nves>
              <nvo3Nve operation="merge">
                <ifName>"""+str(NVEI_NAME)+"""</ifName>
                <srcAddr>"""+str(source_ip)+"""</srcAddr>
              </nvo3Nve>
            </nvo3Nves>
          </nvo3>
        </config>
    """
    try:
        con_obj = mc.edit_config(target='running', config=CREATE_NVE_INTERFACE_SOURCE)
    except RPCError:
        print ("Error: step 4.2")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE NVEI SOURCE ok")

def create_peer_list(NVEI_NAME,VNI,peer_ip):
    CREATE_HEAD_END_PEER_LIST = """
        <config>
          <nvo3 xmlns="http://www.huawei.com/netconf/vrp" content-version="1.0" format-version="1.0">
            <nvo3Nves>
              <nvo3Nve>
                <ifName>"""+str(NVEI_NAME)+"""</ifName>
                <vniMembers>
                  <vniMember>
                    <vniId>"""+str(VNI)+"""</vniId>
                    <nvo3VniPeers>
                      <nvo3VniPeer operation="merge">
                        <peerAddr>"""+str(peer_ip)+"""</peerAddr>
                      </nvo3VniPeer>
                    </nvo3VniPeers>
                  </vniMember>
                </vniMembers>
              </nvo3Nve>
            </nvo3Nves>
          </nvo3>
        </config>
    """
    try:
        con_obj = mc.edit_config(target='running', config=CREATE_HEAD_END_PEER_LIST)
    except RPCError:
        print ("Error: step 4.3")
        raise

    if "<ok/>" not in con_obj.xml:
        print ("Error: %s" % con_obj.xml)
    else:
        print ("set CREATE PEER LIST ok")


try:
    mc = manager.connect(host="111.202.93.90", port="22", username="admin", password="admin",
                         allow_agent=False, look_for_keys=False, hostkey_verify=False,
                         device_params={'name': 'huawei'}, timeout=30)
except AuthenticationError:
    print("Error: Authentication failed while connecting to device.")
    raise
except Exception:
    print("Error: Other error happen.")
    raise
ifname='10GE2/0/2'
ifnumber='1'
print (str(ifname)+'.'+str(ifnumber))