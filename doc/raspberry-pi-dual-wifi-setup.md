# Configurazione Dual Wi-Fi su Raspberry Pi

Questa guida spiega come configurare un Raspberry Pi con due interfacce Wi-Fi in modo che:
- wlan0 (integrata) funzioni sempre come hotspot
- wlan1 (esterna/USB) si connetta a internet

## Prerequisiti
- Raspberry Pi con OS Lite
- Adattatore Wi-Fi USB per la seconda interfaccia
- NetworkManager installato

## 1. Verifica delle interfacce disponibili

```bash
ip a
```

Conferma che entrambe le interfacce (wlan0 e wlan1) siano riconosciute dal sistema.

## 2. Installa NetworkManager (se non già presente)

```bash
sudo apt update
sudo apt install network-manager
```

## 3. Crea l'hotspot su wlan0

```bash
sudo nmcli device wifi hotspot ifname wlan0 ssid "NomeDelTuoHotspot" password "LaPassword"
```

## 4. Connetti wlan1 alla rete Wi-Fi

```bash
sudo nmcli device wifi connect "NomeDellaReteWiFi" password "PasswordDellaRete" ifname wlan1
```

## 5. Configura wlan0 per usare sempre l'hotspot

```bash
# Assicurati che l'hotspot si avvii automaticamente
sudo nmcli connection modify Hotspot connection.autoconnect yes
sudo nmcli connection modify Hotspot connection.autoconnect-priority 100
sudo nmcli connection modify Hotspot connection.interface-name wlan0

# Impedisci a wlan0 di connettersi ad altre reti
sudo nano /etc/udev/rules.d/70-wifi-wlan0.rules
```

Aggiungi questo contenuto al file:
```
ACTION=="add", SUBSYSTEM=="net", KERNEL=="wlan0", RUN+="/usr/bin/nmcli radio wifi on", RUN+="/usr/bin/nmcli connection up Hotspot"
```

## 6. Configura wlan1 per connettersi automaticamente alla rete Wi-Fi

```bash
# Ottieni il nome della connessione per wlan1
nmcli connection show

# Imposta l'autoconnect e l'interfaccia specifica
sudo nmcli connection modify "NomeDellaConnessione" connection.autoconnect yes
sudo nmcli connection modify "NomeDellaConnessione" connection.interface-name wlan1
```

## 7. Riavvia i servizi

```bash
sudo systemctl restart udev
sudo systemctl restart NetworkManager
```

## 8. Riavvia il sistema e verifica

```bash
sudo reboot
```

Dopo il riavvio, verifica che:
```bash
nmcli connection show --active
```

Dovresti vedere:
- L'hotspot attivo su wlan0
- La connessione Wi-Fi attiva su wlan1 (se l'adattatore è collegato)

## Note aggiuntive
- Se wlan1 viene rimosso, il dispositivo rimarrà offline ma l'hotspot su wlan0 continuerà a funzionare
- Se hai problemi con l'autoconnect di wlan1, puoi creare una regola udev come fatto per wlan0
