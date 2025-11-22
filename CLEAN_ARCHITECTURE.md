# Clean Architecture - ShotClock Project

## Introduzione

Questo documento descrive la nuova architettura del progetto ShotClock, refactored secondo i principi della Clean Architecture.

## Struttura del Progetto

```
shotclock/
├── domain/                     # Livello Domain - Nessuna dipendenza esterna
│   ├── entities/              # Entità di dominio
│   │   ├── game.py
│   │   ├── ruleset.py
│   │   └── table_preset.py
│   ├── repositories/          # Interfacce Repository (Ports)
│   │   ├── ruleset_repository.py
│   │   └── table_preset_repository.py
│   └── services/              # Interfacce Service (Ports)
│       ├── timer_service.py
│       ├── video_service.py
│       └── notification_service.py
│
├── application/               # Livello Application
│   └── use_cases/            # Casi d'uso dell'applicazione
│       ├── create_game.py
│       └── manage_game.py
│
└── infrastructure/           # Livello Infrastructure - Dettagli di implementazione
    ├── persistence/         # Implementazioni Repository (Adapters)
    │   ├── sqlalchemy_ruleset_repository.py
    │   └── sqlalchemy_table_preset_repository.py
    ├── api/                # Controller API Flask
    ├── video/              # Adapters per video processing
    │   └── video_adapter.py
    ├── hardware/           # Adapters per hardware (GPIO, timer)
    │   ├── timer_adapter.py
    │   └── notification_adapter.py
    └── di_container.py     # Dependency Injection Container
```

## Principi della Clean Architecture

### 1. Regola delle Dipendenze

Le dipendenze puntano sempre verso l'interno:
- **Infrastructure** → **Application** → **Domain**
- Il **Domain** non ha dipendenze esterne
- L'**Application** dipende solo dal **Domain**
- L'**Infrastructure** implementa le interfacce definite nei livelli interni

### 2. Inversione delle Dipendenze (Dependency Inversion Principle)

Gli strati interni definiscono le interfacce (Ports), gli strati esterni forniscono le implementazioni (Adapters).

Esempio:
```python
# Domain layer (Port)
class RulesetRepository(ABC):
    @abstractmethod
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        pass

# Infrastructure layer (Adapter)
class SQLAlchemyRulesetRepository(RulesetRepository):
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        # Implementazione con SQLAlchemy
```

## Esempio di Implementazione Completa

### 1. Entità di Dominio (Domain Entity)

```python
# shotclock/domain/entities/ruleset.py
from dataclasses import dataclass

@dataclass
class Ruleset:
    """Entità di dominio pura - nessuna dipendenza esterna"""
    id: int
    name: str
    initial_duration: int
    turn_duration: int
    allarm_time: int
    increment_duration: int
    max_increment_for_match: int
```

### 2. Repository Interface (Port)

```python
# shotclock/domain/repositories/ruleset_repository.py
from abc import ABC, abstractmethod
from typing import Optional
from shotclock.domain.entities.ruleset import Ruleset

class RulesetRepository(ABC):
    """Port - definisce il contratto, non l'implementazione"""
    
    @abstractmethod
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        pass
    
    @abstractmethod
    def create(self, name: str, ...) -> Ruleset:
        pass
```

### 3. Use Case (Application Layer)

```python
# shotclock/application/use_cases/create_game.py
from shotclock.domain.repositories.ruleset_repository import RulesetRepository
from shotclock.domain.entities.game import Game

class CreateGameUseCase:
    """Use Case - logica applicativa"""
    
    def __init__(self, ruleset_repository: RulesetRepository):
        self.ruleset_repository = ruleset_repository
    
    def execute(self, ruleset_id: int, ...) -> Optional[Game]:
        # Valida che il ruleset esista
        ruleset = self.ruleset_repository.get(ruleset_id)
        if not ruleset:
            return None
        
        # Crea l'entità Game
        game = Game(ruleset_id=ruleset_id, ...)
        return game
```

### 4. Repository Adapter (Infrastructure Layer)

```python
# shotclock/infrastructure/persistence/sqlalchemy_ruleset_repository.py
from flask_sqlalchemy import SQLAlchemy
from shotclock.domain.repositories.ruleset_repository import RulesetRepository
from shotclock.domain.entities.ruleset import Ruleset

class SQLAlchemyRulesetRepository(RulesetRepository):
    """Adapter - implementa il Port usando SQLAlchemy"""
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
    
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        model = self.db.session.get(RulesetModel, ruleset_id)
        return self._to_entity(model) if model else None
    
    def _to_entity(self, model) -> Ruleset:
        """Converte il modello SQLAlchemy in entità di dominio"""
        return Ruleset(
            id=model.id,
            name=model.name,
            # ...
        )
```

## Dependency Injection

### Container DI

Il `DIContainer` è responsabile della creazione e gestione delle dipendenze:

```python
# shotclock/infrastructure/di_container.py
class DIContainer:
    def __init__(self, db: SQLAlchemy, video_producer, socketio=None):
        self.db = db
        self.video_producer = video_producer
        self.socketio = socketio
    
    def get_ruleset_repository(self) -> RulesetRepository:
        return SQLAlchemyRulesetRepository(self.db)
    
    def get_create_game_use_case(self) -> CreateGameUseCase:
        return CreateGameUseCase(
            ruleset_repository=self.get_ruleset_repository(),
            table_preset_repository=self.get_table_preset_repository(),
        )
```

### Utilizzo

```python
# Inizializzazione
container = DIContainer(db=db, video_producer=video_producer, socketio=socketio)

# Ottieni il use case
create_game_use_case = container.get_create_game_use_case()

# Esegui il use case
game = create_game_use_case.execute(
    ruleset_id=1,
    table_preset_id=1,
    player1_name="Player 1",
    player2_name="Player 2",
)
```

## Testabilità

### Test Unitari per il Domain

I test del domain layer sono completamente isolati:

```python
import unittest
from shotclock.domain.entities.ruleset import Ruleset

class TestRuleset(unittest.TestCase):
    def test_create_ruleset(self):
        ruleset = Ruleset(
            id=1,
            name="Standard",
            initial_duration=600,
            turn_duration=30,
            allarm_time=5,
            increment_duration=10,
            max_increment_for_match=3,
        )
        self.assertEqual(ruleset.name, "Standard")
```

### Test Unitari per Application Layer

I test dell'application layer usano mock per le dipendenze:

```python
import unittest
from unittest.mock import Mock
from shotclock.application.use_cases.create_game import CreateGameUseCase
from shotclock.domain.entities.ruleset import Ruleset

class TestCreateGameUseCase(unittest.TestCase):
    def test_execute_success(self):
        # Mock del repository
        mock_repo = Mock()
        mock_repo.get.return_value = Ruleset(
            id=1, name="Standard", initial_duration=600,
            turn_duration=30, allarm_time=5,
            increment_duration=10, max_increment_for_match=3
        )
        
        # Mock del table preset repository
        mock_table_repo = Mock()
        mock_table_repo.get.return_value = Mock()
        
        # Crea il use case con i mock
        use_case = CreateGameUseCase(mock_repo, mock_table_repo)
        
        # Esegui il test
        game = use_case.execute(
            ruleset_id=1,
            table_preset_id=1,
            player1_name="Player 1",
            player2_name="Player 2",
        )
        
        self.assertIsNotNone(game)
        self.assertEqual(game.ruleset_id, 1)
```

## Vantaggi della Clean Architecture

1. **Testabilità**: I livelli domain e application possono essere testati in isolamento
2. **Manutenibilità**: La logica di business è separata dai dettagli di implementazione
3. **Flessibilità**: Facile sostituire implementazioni (es. cambiare database)
4. **Indipendenza dai Framework**: Il core business non dipende da Flask, SQLAlchemy, ecc.
5. **Chiarezza**: La struttura del codice riflette l'architettura dell'applicazione

## Mappatura dei Componenti Esistenti

### Prima del Refactoring
- `device/game/ruleset.py` - Entità + logica DB mescolate
- `device/api/models_dao.py` - Modelli SQLAlchemy + DAO
- `device/game/game_manager.py` - Stato globale + logica
- `device/game/timer.py` - Implementazione timer
- `device/video_producer.py` - Gestione video

### Dopo il Refactoring
- **Domain**: Entità pure senza dipendenze
- **Application**: Use cases con logica applicativa
- **Infrastructure**: 
  - `persistence/` - Repository SQLAlchemy
  - `api/` - Controller Flask
  - `video/` - Adapters video
  - `hardware/` - Adapters timer/buzzer

## Framework e Librerie Esterne

Tutte le librerie esterne sono confinate nello strato **Infrastructure**:

- **Flask, Flask-SocketIO, Flask-RESTful** → `infrastructure/api/`
- **SQLAlchemy** → `infrastructure/persistence/`
- **OpenCV** → `infrastructure/video/`
- **gpiozero** → `infrastructure/hardware/`
- **numpy, argon2, jwt** → Usati solo nell'infrastructure

## Prossimi Passi

1. Migrare gradualmente i controller API Flask per usare i use cases
2. Aggiungere test unitari per tutti i livelli
3. Documentare ogni use case con esempi
4. Creare factory pattern per casi complessi
5. Implementare pattern Observer per eventi
