# Wes Floyd April 2015

import sys
import requests
import json
import argparse
import pprint
import time

pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser(description='Check for operation of a Storm process')
parser.add_argument('--nimbus', help='host running Nimbus server')
parser.set_defaults(nimbus='sandbox224')
parser.add_argument('--interval', help='time to wait between checks for complete topologies')
parser.set_defaults(interval=5)
args = parser.parse_args()

# Check tuples every X seconds
tupleCheckInterval = args.interval
nimbusServer = args.nimbus
nimbusPort = "8744"
url = "http://" + nimbusServer + ":" + nimbusPort + "/api/v1/topology/summary"

resp = requests.get(url)
resp.encoding = 'utf-8'
topologySummary = resp.json()

#Get most recent number of emitted tuples for that topology or 0 on error
def getTopoTuples(topoID):
    url = "http://" + nimbusServer + ":" + nimbusPort + "/api/v1/topology/"+topoID
    resp = requests.get(url)
    resp.encoding = 'utf-8'
    data = resp.json()
    
    #If the topology ID does not exist, return 0
    if 'error' in data:
        print 'Topology "'+topoID+'" returned error'
        return 0
    
    #Return number of emitted tuples for "all time"
    #Doc - https://github.com/apache/storm/blob/0.9.3-branch/STORM-UI-REST-API.md#apiv1topologyid-get
    return data['topologyStats'][3]['emitted']

#Returns a dictionary of tuple id and the number of its current emitted tuples
def updateTupleCounts(data):
    tuplesEmitted = {}
    for topology in data['topologies']:
        topologyID = topology['id']
        tuplesEmitted[topologyID] = getTopoTuples(topologyID)
    return tuplesEmitted

# Send some alert on the topology
def alertTopo(id):
    print 'Topology with id:\'' + id + 'has stopped processing tuples\''

# Prime the loop by getting the current list of tuple ids and emitted count, then wait for interval time
oldTupleCountDict = updateTupleCounts(topologySummary)
# Prime the loop by waiting the interval for the tuples to increase
time.sleep(tupleCheckInterval)
# Constantly check to see if topologies have stopped receiving tuples
while True:
    newTupleCountDict = updateTupleCounts(topologySummary)

    #iterate through oldTuple list, alert if same number of all time tuples were emitted
    for key in oldTupleCountDict:
        oldTupleID = key
        oldTupleCount = oldTupleCountDict[key]
        newTupleCount = newTupleCountDict[oldTupleID]

        # If tuple count has not increased
        if newTupleCount <= oldTupleCount:
            print "old",oldTupleCount
            print "new",newTupleCount
            alertTopo(oldTupleID)
        else:
            print 'DEBUG: "'+oldTupleID+'" continues to run properly'

    #TODO Consider removing topologies from oldTupleCountDict when alert is triggered?

    # Update oldTupleCountDict to reflect the most recent count data
    oldTupleCountDict = updateTupleCounts(topologySummary)
    # Delay loop for interval time period
    time.sleep(tupleCheckInterval)





'''
for topo in data['topologies']:
    idList.append(topo['id'])
    nameList.append(topo['name'])
    

Get topology id: 
data['topologies'][0]['id']

Get number of tuples processed by bolt
/api/v1/topology/:id -> bolts.acked
https://github.com/apache/storm/blob/0.9.3-branch/STORM-UI-REST-API.md
'''


'''
while True:
    r = requests.get(url)
    print r.text
    time.sleep(5)  # Delay for 5 seconds

'''


'''
#---------------Junk below --------------#
Sandbox 224 command:
storm jar /usr/hdp/current/storm-client/contrib/storm-starter/storm-starter-0.9.3.2.2.4.2-2-jar-with-dependencies.jar storm.starter.RollingTopWords production-topology remote

SeRegion-Prod command:
storm jar /usr/hdp/current/storm-client/contrib/storm-starter/storm-starter-0.9.3.2.2.4.0-2633-jar-with-dependencies.jar storm.starter.RollingTopWords production-topology remote
python topology-check.py --nimbus seregion-prod-ma01.cloud.hortonworks.com



https://github.com/apache/storm/blob/0.9.3-branch/STORM-UI-REST-API.md
Ambari alerts - https://github.com/apache/ambari/blob/trunk/ambari-server/src/main/resources/common-services/YARN/2.1.0.2.0/package/alerts/alert_nodemanager_health.py



#curl -X GET http://wftestw01.cloud.hortonworks.com:8744/api/v1/
#curl -u admin:admin -X GET  http://wftestm01:8080/api/v1/clusters/wftest/host_components
#http://wftestw01.cloud.hortonworks.com:8744/api/v1/cluster/configuration

#print r.text.split('\n')[0]
'''