# Fastapi Base(HEAPDUMP in Python)

## Index
  - [Description](#description)
  - [Path/Functions](#pathfunctions)
  - [Structure](#structure)
    - [Directories](#directories)
    - [Files](#files)
  - [Local](#local)
  
<a name=description></a>
## Description:
Microservice to dump memory. 

<a name=functions></a>
## Path/Functions:
Outline of the published Paths
Functions it performs in more detail

get_my_pid(pod) -> get the pid of the java process.  
clean_old_files(directory, days=30) -> Delete files older than the one indicated in the "days" parameter.  
delete_pod(pod) -> If the box is checked, deletes the selected pod.  

<a name=functions></a>
## Structure:
<a name=directories></a>
### Directories:
Description of the folders used and what is stored in them 
<a name=files></a>
### Files:
Description of the files with the most important functions

App/functions/utils.py  
app/functions/heapdump.py  

<a name=local></a>
## Local:
Explanation of how to test it locally and develop (docker):

Example:
```bash
    docker build -t name-imge .
    docker run -d -p 8000:8000 --env-file local.env --name alma-status shuttle-alma:latest
```

Keep in mind that the application cannot run if it is not contained within a Docker
since there are libraries that are not available for Windows (ex. uvloop).
