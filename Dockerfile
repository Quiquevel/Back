FROM registry.global.ccc.srvb.bo.paas.cloudcenter.corp/shuttle-san/python:3.11.1
# Create app directory as working directory
WORKDIR /app

ENV TZ=Europe/Madrid

RUN set -x && \
    export GIT_SSL_NO_VERIFY="true" && \
    export http_proxy=http://proxyapp.cloudcenter.corp:8080 && \
    export https_proxy=http://proxyapp.cloudcenter.corp:8080 && \
    export no_proxy=.cloudcenter.corp && \
    apt-get update && \
    apt-get install -y python3-dev build-essential && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt /

RUN export GIT_SSL_NO_VERIFY="true" && \
    export http_proxy=http://proxyapp.cloudcenter.corp:8080 && \
    export https_proxy=http://proxyapp.cloudcenter.corp:8080 && \
    export no_proxy=.cloudcenter.corp && \
    pip install --proxy ${https_proxy} --no-cache-dir --trusted-host files.pythonhosted.org \
    --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host github.alm.europe.cloudcenter.corp \
    -r /requirements.txt && \
    apt-get update && \
    apt-get install -y curl rsync && \
    apt-get install -y jq && \
    apt-get install -y vim && \
    rm -rf /var/lib/apt/lists/*

# Use ADD instruction to download and extract oc.tar.gz
ADD https://mirror.openshift.com/pub/openshift-v4/clients/oc/latest/linux/oc.tar.gz /usr/local/bin/
RUN tar -xf /usr/local/bin/oc.tar.gz -C /usr/local/bin && \
    rm /usr/local/bin/oc.tar.gz

WORKDIR /app

# Copy code from root repo to the working directory
COPY /app/ /app/

RUN groupadd -g 1000060000 userpython && \
    useradd -u 1000 -g userpython -d /home/userpython -s /bin/bash userpython && \
    mkdir -p /home/userpython && \
    mkdir -p /app/downloads && \
    chown -R userpython:userpython /app && \
    chown -R userpython:userpython /home/userpython

COPY delete_pods_bo1.py /home/app/
COPY delete_pods_bo2.py /home/app/
COPY run_both_scripts.sh /home/app/

RUN chown userpython:userpython /home/app/ && \
    chmod 777 /home/app/delete_pods_bo1.py && \
    chmod 777 /home/app/delete_pods_bo2.py && \
    chmod 777 /home/app/run_both_scripts.sh

# Switch to non-root user
USER userpython

# Giving executable permission
USER 1000
EXPOSE 8080
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]