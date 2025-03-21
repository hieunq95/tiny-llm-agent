FROM jenkins/jenkins:lts

USER root

RUN apt-get update && \
    apt-get install -y docker.io && \
    apt-get install -y git sudo && \
    apt-get clean

RUN curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose && \
    chmod +x /usr/local/bin/docker-compose

# Allow Jenkins to use Docker
RUN groupadd docker || true && \
    usermod -aG docker jenkins

# Allow Jenkins user to run sudo without a password
RUN echo "jenkins ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/jenkins
RUN chmod 0440 /etc/sudoers.d/jenkins

# Copy entrypoint script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

USER jenkins

COPY . /var/jenkins_home/

EXPOSE 8080 50000

# Use entrypoint script to modify permissions at runtime
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

