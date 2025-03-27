import uvicorn
from fastapi import FastAPI
from routes import openshift

DESCRIPTION = """
FASTAPI BASE model de pruebas

### SUMMARY
With the help of this microservice, pod stack dumps can be pulled and downloaded.
Use:
The parameters and possible values are:

  "functionalEnvironment": “dev, pre, pro”
  "cluster": "ohe (only for dev & pre), bks (only for dev & pre), probks, dmzbbks, azure, prodarwin, dmzbdarwin, confluent, proohe, dmzbohe, dmzbazure, ocp05azure”
  "region": "bo1, bo2",
  "namespace": "pod's namespace",
  "pod": ["pod's name"],
  "action": "1, 2, 3, 4"

### ENDPOINTS

* **almastatus:** Get status info of soul POD.

### PARAMETERS
* **project**: namespaces's name
* **env**: ohe (only for dev & pre), bks (only for dev & pre), probks, dmzbbks, azure, prodarwin, dmzbdarwin, confluent, proohe, dmzbohe, dmzbazure, ocp05azure
* **namespace**: Pod's namespace
* **pod**: pod's name
* **action**: Action to perform (1 - HeapDump, 2 - ThreadDump, 3 - HeapDump DataGrid, 4 - ThreadDump DataGrid)
"""

CONTACT = {
    "name": "SRE CoE DevSecOps",
    "email": "SRECoEDevSecOps@gruposantander.com"
}

tags_healthcheck = [
    {
        "name": "POD's DUMPS",
        "description": "Use to get Heap Dumps/Thread Dumps from pods."
    },
    {
        "name": "healthcheck",
        "description": "Use for service status in POD"
    }
]

app = FastAPI(
    docs_url="/api/v1/dumps",
    title="shuttle-openshift-heapdump",
    description=DESCRIPTION,
    version="1.0.6",
    openapi_url="/api/v1/openapi.json",
    contact=CONTACT,
)

app.include_router(openshift.pod_exec, prefix="/dumps", tags=["v1"])

@app.get("/health", tags=["healthcheck"])
async def healthcheck():
    return "SERVER OK"

# COMENTAR PARA DESPLEGAR EN OPENSHIFT
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True, workers=2, timeout_keep_alive=600)