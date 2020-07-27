FROM centos:7

LABEL maintainer="Sunil Samal <ssamal@redhat.com>"

RUN yum install -y epel-release &&\
    yum install -y gcc-c++ git python36-pip python36-requests httpd httpd-devel python36-devel &&\
    yum clean all


COPY ./requirements.txt /requirements.txt

RUN pip3 install --upgrade pip

RUN pip3 install git+https://github.com/fabric8-analytics/fabric8-analytics-auth.git@ad3dab5#egg=fabric8a_auth

RUN pip3 install git+https://github.com/fabric8-analytics/fabric8-analytics-rudra.git@e9a9239#egg=rudra

RUN pip3 install -r requirements.txt

COPY ./entrypoint.sh /bin/entrypoint.sh

COPY ./src /src

RUN chmod +x /bin/entrypoint.sh

ENTRYPOINT ["/bin/entrypoint.sh"]
