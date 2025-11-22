# Shot Clock

Sistema di gestione automatica del timer di gioco per biliardo con rilevamento del movimento delle biglie tramite computer vision.

## Indice

1. [Descrizione](#descrizione)
2. [Requisiti](#requisiti)
3. [Installazione](#installazione)
4. [Esecuzione del Progetto](#esecuzione-del-progetto)
5. [Architettura](#architettura)
6. [API Endpoints](#api-endpoints)
7. [Testing](#testing)
8. [Configurazione](#configurazione)
9. [Documentazione Aggiuntiva](#documentazione-aggiuntiva)

## Descrizione

ShotClock è un sistema completo per la gestione automatica dei tempi di gioco nel biliardo. Il sistema:

- **Rileva automaticamente** il movimento delle biglie tramite computer vision (OpenCV)
- **Gestisce i turni** dei giocatori con timer automatici
- **Notifica** tramite suoni e WebSocket gli eventi di gioco
- **Supporta regolamenti personalizzabili** (durata turni, incrementi tempo, allarmi)
- **Configurabile** per diversi tavoli da gioco

Il progetto è stato refactored secondo i principi della **Clean Architecture** per garantire:
- ✅ Testabilità (logica business isolata)
- ✅ Manutenibilità (separazione delle responsabilità)
- ✅ Flessibilità (facile cambiare implementazioni)

## Requisiti

### Software

- **Python 3.12+**
- **Node.js** e **pnpm** (per il frontend web)
- **Webcam o PiCamera** (per il rilevamento movimento)

### Dipendenze Python

Le dipendenze sono elencate in `device/requirements.txt`:

- Flask 3.1.0 (API REST)
- Flask-SocketIO 5.5.1 (comunicazione real-time)
- Flask-SQLAlchemy 3.1.1 (database)
- OpenCV (computer vision)
- gpiozero 2.0.1 (per GPIO su Raspberry Pi)
- numpy 2.2.3

### Hardware (Opzionale)

- **Raspberry Pi** con GPIO per buzzer hardware
- **Webcam** o **PiCamera** per acquisizione video

## Installazione

### 1. Clona il Repository

```bash
git clone https://github.com/giopalma/ShotClock.git
cd ShotClock
```

### 2. Installa le Dipendenze Python

```bash
cd device
pip install -r requirements.txt
```

**Nota:** Su sistemi non-Raspberry Pi, gpiozero potrebbe non essere necessario per lo sviluppo.

### 3. Installa le Dipendenze Frontend (Opzionale)

```bash
cd web
pnpm install
```

### 4. Configura il File di Ambiente

Crea un file `.env` nella root del progetto con le seguenti variabili:

```env
FLASK_SECRET_KEY=your-secret-key-here
```

## Esecuzione del Progetto

Il progetto è composto da due componenti che devono essere eseguiti separatamente:

### Opzione A: Versione Legacy (Originale)

#### Backend (Device) - Legacy

```bash
# Dalla root del progetto
python -m device

# Con modalità debug
python -m device --debug

# Modalità test (con frame video fisso)
python -m device --test --static
```

**Endpoint API Legacy:** `http://localhost:5000`

#### Frontend (Web Interface)

```bash
cd web
pnpm run dev
```

**URL Frontend:** `http://localhost:3000` (o porta indicata da pnpm)

### Opzione B: Versione Clean Architecture (Nuova)

#### Backend - Clean Architecture

```bash
# Dalla root del progetto
python -m src.main

# Con modalità debug
python -m src.main --debug
```

**Nuovi Endpoint API:** `http://localhost:5000/api/v2/*`

**Nota:** La versione Clean Architecture può coesistere con quella legacy. Entrambe le API sono disponibili contemporaneamente.

### Verifica del Funzionamento

1. **Verifica Backend:**
   ```bash
   curl http://localhost:5000/check-auth
   ```

2. **Verifica Frontend:**
   Apri il browser su `http://localhost:3000`

## Architettura

### Architettura Legacy (`device/`)

Struttura monolitica tradizionale:

```
device/
├── api/              # API Flask e risorse REST
├── game/             # Logica di gioco e gestione timer
├── video_producer.py # Acquisizione video
└── config.py         # Configurazione
```

### Architettura Clean (`src/`)

Architettura a strati con inversione delle dipendenze:

```
src/
├── domain/              # Logica business pura (zero dipendenze)
│   ├── entities/       # Entità (Game, Ruleset, TablePreset)
│   ├── repositories/   # Interfacce repository
│   └── services/       # Interfacce servizi
├── application/        # Casi d'uso
│   └── use_cases/     # CreateGame, ManageGame
├── infrastructure/     # Implementazioni tecniche
│   ├── persistence/   # Repository SQLAlchemy
│   ├── api/          # Controller Flask
│   ├── video/        # Adapter OpenCV
│   └── hardware/     # Adapter GPIO/Timer
└── main.py           # Entry point
```

**Principio della Dipendenza:**
```
Infrastructure → Application → Domain
```

## API Endpoints

### API Legacy (`/`)

#### Gioco
- `POST /game` - Crea una nuova partita
- `GET /game` - Ottieni stato partita corrente
- `POST /game/actions` - Azioni di gioco (start, pause, resume, increment)
- `DELETE /game` - Termina partita

#### Regolamenti
- `GET /ruleset` - Lista tutti i regolamenti
- `POST /ruleset` - Crea nuovo regolamento
- `GET /ruleset/<id>` - Ottieni regolamento specifico
- `DELETE /ruleset/<id>` - Elimina regolamento

#### Tavoli
- `GET /table` - Lista tutti i preset tavoli
- `POST /table` - Crea nuovo preset
- `GET /table/<id>` - Ottieni preset specifico
- `DELETE /table/<id>` - Elimina preset

#### Video
- `GET /video/frame` - Ottieni frame corrente
- `POST /video/frame` - Frame con maschera applicata
- `GET /video/record` - Avvia registrazione video
- `GET /video/stream` - Stream video
- `POST /video/stream/control` - Controlla stream

#### Autenticazione
- `POST /login` - Login
- `POST /logout` - Logout
- `GET /check-auth` - Verifica autenticazione
- `POST /password` - Cambia password

### API Clean Architecture (`/api/v2/`)

#### Gioco
- `POST /api/v2/game` - Crea partita
  ```json
  {
    "ruleset_id": 1,
    "table_preset_id": 1,
    "player1_name": "Giocatore 1",
    "player2_name": "Giocatore 2"
  }
  ```

- `GET /api/v2/game` - Stato partita
- `DELETE /api/v2/game` - Termina partita

- `POST /api/v2/game/actions` - Azioni
  ```json
  {
    "action": "start|pause|resume|increment",
    "player": 0  // Solo per increment (0 o 1)
  }
  ```

### WebSocket Events

Il sistema emette eventi WebSocket per aggiornamenti real-time:

- `game` - Eventi di gioco ("created", "started", "ended")
- `timer` - Aggiornamenti timer
  ```json
  {
    "timestamp": 1234567890,
    "remaining_time": 30.5,
    "status": "running|paused"
  }
  ```

**Connessione WebSocket:**
```javascript
const socket = io('http://localhost:5000');
socket.on('timer', (data) => {
  console.log('Tempo rimanente:', data.remaining_time);
});
```

## Testing

### Test Unitari

```bash
# Esegui tutti i test
python -m unittest discover tests

# Test specifici
python -m unittest tests.domain.test_entities
python -m unittest tests.application.test_create_game_use_case
```

**Risultato atteso:** `8/8 tests passing ✅`

### Test Manuali

1. **Test Creazione Partita:**
   ```bash
   curl -X POST http://localhost:5000/api/v2/game \
     -H "Content-Type: application/json" \
     -d '{
       "ruleset_id": 1,
       "table_preset_id": 1,
       "player1_name": "Alice",
       "player2_name": "Bob"
     }'
   ```

2. **Test Avvio Partita:**
   ```bash
   curl -X POST http://localhost:5000/api/v2/game/actions \
     -H "Content-Type: application/json" \
     -d '{"action": "start"}'
   ```

## Configurazione

### File `config.ini`

Configurazione del sistema (esempio):

```ini
[DEFAULT]
# Configurazioni generali
```

### Variabili d'Ambiente

Crea un file `.env`:

```env
# Chiave segreta Flask (OBBLIGATORIA)
FLASK_SECRET_KEY=your-super-secret-key-change-this

# Ambiente Flask
FLASK_ENV=api
```

### Database

Il database SQLite viene creato automaticamente in `device/shotclock.db` al primo avvio.

**Tabelle:**
- `ruleset` - Regolamenti di gioco
- `table_preset` - Configurazioni tavoli

## Utilizzo da Codice

### Versione Clean Architecture

```python
from src.infrastructure.di_container import DIContainer
from device.api import db, socketio
from device.video_producer import VideoProducer

# Inizializza il container DI
container = DIContainer(
    db=db,
    video_producer=VideoProducer.get_instance(),
    socketio=socketio
)

# Ottieni i use case
create_game = container.get_create_game_use_case()
manage_game = container.get_manage_game_use_case()

# Crea una partita
game = create_game.execute(
    ruleset_id=1,
    table_preset_id=1,
    player1_name="Alice",
    player2_name="Bob"
)

# Avvia la partita
error = manage_game.start_game(game)
if not error:
    print("Partita avviata con successo!")

# Pausa
manage_game.pause_game(game)

# Riprendi
manage_game.resume_game(game)

# Termina
manage_game.end_game(game)
```

## Documentazione Aggiuntiva

Per maggiori dettagli sull'architettura e l'implementazione:

- **[CLEAN_ARCHITECTURE.md](CLEAN_ARCHITECTURE.md)** - Guida completa all'architettura Clean
- **[INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)** - Come integrare vecchio e nuovo codice
- **[REFACTORING_PLAN.md](REFACTORING_PLAN.md)** - Piano di refactoring e prossimi passi
- **[IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)** - Riepilogo dell'implementazione
- **[src/README.md](src/README.md)** - Documentazione architettura Clean

## Troubleshooting

### Problema: ModuleNotFoundError

**Soluzione:** Assicurati di aver installato tutte le dipendenze:
```bash
cd device
pip install -r requirements.txt
```

### Problema: Database locked

**Soluzione:** Chiudi tutte le istanze del server e riprova.

### Problema: Webcam non rilevata

**Soluzione:** 
1. Verifica che la webcam sia collegata
2. Su Linux, verifica i permessi: `sudo usermod -a -G video $USER`
3. Prova con modalità test: `python -m device --test --static`

### Problema: GPIO non disponibile

**Soluzione:** Il GPIO è disponibile solo su Raspberry Pi. Su altri sistemi, il buzzer viene simulato con winsound (Windows) o disabilitato.

## Licenza

[Specificare la licenza del progetto]

## Autori

- Giovanni Palma (@giopalma)

## Contribuire

1. Fork del progetto
2. Crea un branch per la feature (`git checkout -b feature/AmazingFeature`)
3. Commit delle modifiche (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Apri una Pull Request

## Contatti

Per domande o supporto, apri una issue su GitHub.
