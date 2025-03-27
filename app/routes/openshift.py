from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Optional
from pydantic import BaseModel, validator
from functions.commonfunctions import get_podnames, get_microservices, get_namespaces, get_clusters, do_get_problems
from functions.heapdump import getheapdump
from middleware.authorization import authorizationtreatment
from functions.historical import get_hist_dumps, get_download_dump
from functions.clientunique import getenvironmentsclusterslist
from functions.dyna import dynatracetreatment
from shuttlelib.utils.logger import logger

bearer = HTTPBearer()
UNAUTHORIZED_USER_ERROR = "User not authorized"

ENVIRONMENT_LIST, CLUSTER_DICT, REGION_DICT = getenvironmentsclusterslist()

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
        if v not in ENVIRONMENT_LIST:
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for functionalenvironment")
        return v

    @validator("cluster")
    def validate_cluster(cls, v, values):
        environment = values.get("functionalenvironment")
        if environment and v not in CLUSTER_DICT.get(environment, []):
            logger.info(f"El contenido de CLUSTER_DICT es: {CLUSTER_DICT}")
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for cluster in environment {environment}")
        return v

    @validator("region")
    def validate_region(cls, v, values):
        environment = values.get("functionalenvironment")
        cluster = values.get("cluster")
        if environment and cluster and v not in REGION_DICT.get(environment, {}).get(cluster, []):
            logger.info(f"El contenido de REGION_DICT es: {REGION_DICT}")
            raise HTTPException(status_code=400, detail=f"{v} value is not valid for region in cluster {cluster} and environment {environment}")
        return v

    @validator("namespace")
    def validate_namespace(cls,v):
        return v
    
@pod_exec.post("/heapdump")
async def execute_heapdump(target: heapdumpmodel, authorization: str = Depends(bearer)):
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if isdevops == False:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    return await getheapdump(functional_environment=target.functionalenvironment, cluster=target.cluster, region=target.region, namespace=target.namespace, pod=target.pod, action=target.action, delete=target.delete)

class env_list(BaseModel):
    ldap: str

@pod_exec.post("/environment_list")
async def get_environment_list(target: env_list, authorization: str = Depends(bearer)):  
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if not isdevops:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    return {"environments": ENVIRONMENT_LIST}

class cluster_list(BaseModel):
    functionalenvironment: str
    ldap: str

@pod_exec.post("/cluster_list")
async def get_cluster_list(target: cluster_list, authorization: str = Depends(bearer)):  
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if not isdevops:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    clusters = CLUSTER_DICT.get(target.functionalenvironment, [])
    return {"clusters": clusters}

class region_list(BaseModel):
    functionalenvironment: str
    cluster: str
    ldap: str

@pod_exec.post("/region_list")
async def get_region_list(target: region_list, authorization: str = Depends(bearer)):  
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if not isdevops:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    regions = REGION_DICT.get(target.functionalenvironment, {}).get(target.cluster, [])
    return {"regions": regions}

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

class ProblemList(BaseModel):
    ldap: str

@pod_exec.post("/problems_list")
async def get_problems_list(target: ProblemList, authorization: str = Depends(bearer)):
    isdevops = await authorizationtreatment(auth=authorization, ldap=target.ldap)
    if isdevops == False:
        raise HTTPException(status_code=403, detail=UNAUTHORIZED_USER_ERROR)
    return await do_get_problems()

class DynaModel(BaseModel):
    functional_environment: str
    timedyna: Optional[str] = None
 
    @validator("functional_environment")
    def validate_environment(cls, v):        
        if not any(x == v for x in ENVIRONMENT_LIST):
            raise HTTPException(status_code = 400, detail=f"{v} value is not valid for functionalEnvironment")
        return v
    
@pod_exec.post("/dynatrace", tags = ["v1"], description = "GET DYNATRACE ALERT", response_description = "JSON", status_code = 200)
async def get_dynatrace_alert(target: DynaModel):
    return await dynatracetreatment(functionalenvironment = target.functional_environment, timedyna = target.timedyna)