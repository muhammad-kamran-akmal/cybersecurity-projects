FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
        openssh-server \
        iproute2 \
        iputils-ping \
        procps \
        nano \
    && rm -rf /var/lib/apt/lists/*

# --- Deliberate misconfigurations for educational auditing ---
RUN mkdir -p /run/sshd /home/kami/myfiles /home/kami/docs \
    && echo 'root:toor' | chpasswd \
    && printf 'This is a secret file with confidential data.\n' > /home/kami/myfiles/secret.txt \
    && printf 'This is important data that must not be lost.\n' > /home/kami/myfiles/important.txt \
    && printf 'financial records Q3\n' > /home/kami/myfiles/finance.txt \
    && printf 'private doc\n' > /home/kami/docs/report.txt \
    && sed -i 's/^#*PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config \
    && sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config \
    && ssh-keygen -A

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
CMD ["sleep", "infinity"]
