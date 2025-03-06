from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from pydantic import BaseModel, validator
from functions.utils import get_podnames, get_microservices, get_namespaces
from functions.heapdump import getheapdump
from middleware.authorization import authorizationtreatment
from functions.historical import get_hist_dumps, get_download_dump
from functions.client import getenvironmentsclusterslist

bearer = HTTPBearer()
UNAUTHORIZED_USER_ERROR = "User not authorized"

REGION_LIST = ["bo1","bo2","weu1","weu2"]
ENVIRONMENT_LIST, CLUSTER_LIST = getenvironmentsclusterslist()

pod_exec = APIRouter(tags=["v1"])
class heapdumpmodel(BaseModel):
    functionalenvironment: str
    cluster: str
    region: str
    namespace: str
    pod: list
    action: str
    ldap: str
    delete: bool=False

    @validator("functionalenvironment")
    def validate_environment(cls, v):
        if not any(x in v for x in ENVIRONMENT_LIST):
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for functionalenvironment")
        return v
    
    #To validate the cluster parameter.
    @validator("cluster")
    def validate_cluster(cls, v):
        if not any(x in v for x in CLUSTER_LIST):
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for cluster")
        return v
    
    @validator("namespace")
    def validate_namespace(cls,v):
        return v
    
    #to validate the region parameter
    @validator("region")
    def validate_region(cls, v):
        if not any(x in v for x in REGION_LIST):
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for region")
        return v
    
#Calling to the principal function
@pod_exec.post("/heapdump")
async def execute_heapdump(target: heapdumpmodel, authorization: str = Depends(bearer)):
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if isdevops == False:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    return await getheapdump(functional_environment=target.functionalenvironment, cluster=target.cluster, region=target.region, namespace=target.namespace, pod=target.pod, action=target.action, delete=target.delete)

class namespace_list(BaseModel):
    functionalenvironment: str
    cluster: str
    region: str
    ldap: str

@pod_exec.post("/namespace_list")
async def get_namespace_list(target: namespace_list, authorization: str = Depends(bearer)):  
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if isdevops == False:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    return await get_namespaces(functional_environment=target.functionalenvironment, cluster=target.cluster, region=target.region)

class MicroserviceList(BaseModel):
    functionalenvironment: str
    cluster: str
    region: str
    namespace: str
    ldap: str

@pod_exec.post("/microservices_list")
async def get_microservice_list(target: MicroserviceList, authorization: str = Depends(bearer)):
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if isdevops == False:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    return await get_microservices(functional_environment=target.functionalenvironment, cluster=target.cluster, region=target.region, namespace=target.namespace)

class PodList(BaseModel):
    functionalenvironment: str
    cluster: str
    region: str
    namespace: str
    microservices: str
    ldap: str

@pod_exec.post("/pod_list")
async def get_pod_list(target: PodList, authorization: str = Depends(bearer)):
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if isdevops == False:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    return await get_podnames(functional_environment=target.functionalenvironment, cluster=target.cluster, region=target.region, namespace=target.namespace, microservices=target.microservices)

class HistDump(BaseModel):
    namespace: str
    ldap: str

@pod_exec.post("/historical_dumps")
async def recover_hist_dumps(target: HistDump, authorization: str = Depends(bearer)):
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if isdevops == False:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    return await get_hist_dumps(namespace=target.namespace)

class DownloadDump(BaseModel):
    namespace: str
    file_name: str
    ldap: str

@pod_exec.post("/download_dump")
async def download_dump(target: DownloadDump, authorization: str = Depends(bearer)):
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if isdevops == False:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    return await get_download_dump(namespace=target.namespace, file_name=target.file_name)
