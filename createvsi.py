import  warnings
warnings.simplefilter("ignore", DeprecationWarning)
from ncclient import manager
import time

def my_unknown_host_cb(host, figerprint):
    return True


def demo(host, port, user, pwd):
    with manager.connect_ssh(host=host, 
        port=port, 
        username=user, 
        password=pwd, 
        unknown_host_cb=my_unknown_host_cb, 
        device_params = {'name':'h3c'}) as m:
        xml = """
        <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
          <top xmlns="http://www.h3c.com/netconf/config:1.0">
            <L2VPN>
                     <VSIs>
                        <VSI>
                           <VsiName>vpnb</VsiName>
                        </VSI>
                     </VSIs>
            </L2VPN>
          </top>
        </config>
        """
        print m.edit_config(target='running', config=xml)

if __name__ == '__main__':
    demo("10.3.214.197", 830, "admin", "admin")
    print "closed"
    time.sleep(1)
