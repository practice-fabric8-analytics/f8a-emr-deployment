FROM centos:7

LABEL maintainer="Sunil Samal <ssamal@redhat.com>"

RUN yum install -y epel-release &&\
    yum install -y gcc-c++ git python34-pip python34-requests httpd httpd-devel python34-devel &&\
    yum clean all


COPY ./requirements.txt /requirements.txt

RUN pip3 install -r requirements.txt

COPY ./entrypoint.sh /bin/entrypoint.sh

COPY ./src /src

RUN chmod +x /bin/entrypoint.sh

ENTRYPOINT ["/bin/entrypoint.sh"]

