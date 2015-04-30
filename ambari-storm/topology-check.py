# Wes Floyd April 2015

import requests
import json
import argparse
import pprint

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(description='Check for operation of a Storm process')
parser.add_argument('--nimbus', help='host running Nimbus server')
parser.set_defaults(nimbus='sandbox22')
args = parser.parse_args()

nimbusServer = args.nimbus
nimbusPort = "8744"
url = "http://" + nimbusServer + ":" + nimbusPort + "/api/v1/topology/summary"

resp = requests.get(url)
resp.encoding = 'utf-8'
data = resp.json()

'''
Get topology id: 
data['topologies'][0]['id']

Get number of tuples processed by bolt
/api/v1/topology/:id -> bolts.acked
https://github.com/apache/storm/blob/0.9.3-branch/STORM-UI-REST-API.md


test1
'''









'''
while True:
    r = requests.get(url)
    print r.text
    time.sleep(5)  # Delay for 1 minute (60 seconds)

'''


'''
#---------------Junk below --------------#
storm jar /usr/hdp/current/storm-client/contrib/storm-starter/storm-starter-0.9.3.2.2.0.0-2041-jar-with-dependencies.jar storm.starter.RollingTopWords production-topology remote
https://github.com/apache/storm/blob/0.9.3-branch/STORM-UI-REST-API.md
Ambari alerts - https://github.com/apache/ambari/blob/trunk/ambari-server/src/main/resources/common-services/YARN/2.1.0.2.0/package/alerts/alert_nodemanager_health.py



#curl -X GET http://wftestw01.cloud.hortonworks.com:8744/api/v1/
#curl -u admin:admin -X GET  http://wftestm01:8080/api/v1/clusters/wftest/host_components
#http://wftestw01.cloud.hortonworks.com:8744/api/v1/cluster/configuration

#print r.text.split('\n')[0]
'''