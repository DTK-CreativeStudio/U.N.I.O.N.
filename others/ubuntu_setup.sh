sudo apt -y --no-install-recommends upgrade
sudo apt -y --no-install-recommends dist-upgrade
sudo apt install -y --no-install-recommends python3-pip
sudo apt install -y --no-install-recommends curl
curl -L https://go.microsoft.com/fwlink/?LinkID=760868 -o vscode.deb
cd downloads
sudo apt install -y --no-install-recommends ./vscode.deb
sudo apt install -y --no-install-recommends apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
sudo apt update
apt-cache policy docker-ce
sudo apt install -y --no-install-recommends docker-ce
sudo usermod -aG docker ${USER}
sudo curl -L "https://github.com/docker/compose/releases/download/1.27.4/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo rm vscode.deb
sudo chmod -R 777 IO/
sudo chmod -R 777 /dev/bus/usb
sudo apt install -y --no-install-recommends mysql-client
sudo modprobe -r port100
sudo sh -c 'echo blacklist port100 >> /etc/modprobe.d/blacklist-nfc.conf'
sudo reboot
