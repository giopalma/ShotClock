# Lo script permette di utilizzare l'interfaccia wlan0 del RaspberryPi 4
# come Host AP ed utilizza un sistema Captive Portal per far accedere
# l'utente direttamente alla dashboard

#!/bin/bash

# Aggiorna i pacchetti e installa i pacchetti necessari per creare l'Host AP
sudo apt update
sudo apt install -y hostapd dnsmasq dhcpcd

# Disabilita i servizi
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Configura hostapd
cat <<EOF | sudo tee /etc/hostapd/hostapd.conf > /dev/null
interface=wlan0
driver=nl80211
ssid="Billiard Timer"
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
EOF

# Imposta hostapd per usare la configurazione appena creata
sudo sed -i 's|#DAEMON_CONF=""|DAEMON_CONF="/etc/hostapd/hostapd.conf"|' /etc/default/hostapd


# Configura dnsmasq
cat <<EOF | sudo tee /etc/dnsmasq.conf > /dev/null
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
EOF

# Configura l'interfaccia di rete per wlan0
cat <<EOF | sudo tee /etc/dhcpcd.conf > /dev/null
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF
sudo systemctl restart dhcpcd

# Configura iptables per il portale captive
sudo iptables -t nat -A PREROUTING -i wlan0 -p tcp --dport 80 -j DNAT --to-destination 192.168.4.1:80
sudo sh -c "iptables-save > /etc/iptables.ipv4.nat"


# Rendi iptables persistente al riavvio
sudo sed -i '/^exit 0/i sudo iptables-restore < /etc/iptables.ipv4.nat' /etc/rc.local

# Configura il server web e la pagina captive
sudo bash -c 'echo "<html><body><h1>Benvenuto nel portale captive!</h1></body></html>" > /var/www/html/index.html'

# Abilita e avvia i servizi
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
sudo systemctl start hostapd
sudo systemctl start dnsmasq
sudo systemctl restart lighttpd

echo "Configurazione completata. L'hotspot Wi-Fi è attivo."