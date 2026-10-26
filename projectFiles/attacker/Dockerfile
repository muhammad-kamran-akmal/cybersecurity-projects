FROM kalilinux/kali-rolling

RUN apt-get update && apt-get install -y --no-install-recommends \
        nmap \
        hydra \
        openssh-client \
        iputils-ping \
        net-tools \
        procps \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /root
CMD ["sleep", "infinity"]
