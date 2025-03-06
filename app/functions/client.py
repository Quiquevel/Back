import os
from shuttlelib.openshift.client import OpenshiftClient

entity_id=(os.getenv("ENTITY_ID")).lower()
client = OpenshiftClient(entity_id=entity_id)


def getclustersdata(environment):    
    clusterdatalistall = []    
    clusterdatalistsimplified = []
    clusternames = set()
    
    clusters = list(client.clusters[environment])
    for cluster in clusters:
        clusterdata = client.clusters[environment][cluster]
        regions = list(clusterdata)
        for region in regions:
            clusterdata = client.clusters[environment][cluster][region]
            url = clusterdata['url']            
            clusterdata = {'environment': environment,
                    'cluster': cluster,
                    'region': region,
                    'url': url
            }                                                
            if clusterdata:
                clusterdatalistall.append(clusterdata)
    
    for cluster in clusterdatalistall:
        if (cluster['cluster']).lower() == "azure":            
            clusterdatalistsimplified.append(cluster)
        elif cluster['cluster'] not in clusternames:
            clusterdatalistsimplified.append(cluster)
            clusternames.add(cluster['cluster'])           
    
    return clusterdatalistall, clusterdatalistsimplified


def getenvironmentsclusterslist():
    environmentlist = []
    clusterlist = []

    environmentlist = list(client.clusters.keys())
    for environment in environmentlist:
        clusterlist.extend(client.clusters[environment])
    
    environmentlist.extend([x.upper() for x in environmentlist])
    
    clusterlist.extend([x.upper() for x in clusterlist])
    clusterlist = list(set(clusterlist))
    clusterlist.sort()
    
    return environmentlist, clusterlist
