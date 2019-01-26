apt-get update -yq && apt-get upgrade -yq && \
apt-get install -yq curl

curl -sL https://deb.nodesource.com/setup_10.x | bash - && \
apt-get install -yq nodejs build-essential

npm install -g npm