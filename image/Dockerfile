FROM    nginx
RUN     apt-get update \
        && apt-get install -y man \
        && apt-get install -y vim \
        && apt-get install -y curl \
        && apt-get install -y wget \
        && apt-get install -y tcpdump \
        && apt-get install -y iptables \
        && apt-get install -y ebtables \
        && apt-get install -y conntrack \
        && apt-get install -y dnsutils \
        && apt-get install -y iperf3 \
        && apt-get install -y netcat \
        && apt-get install -y net-tools
# Setup and source bashrc and color schema
ADD     bashrc /root/.bashrc
ENV     HOME /root