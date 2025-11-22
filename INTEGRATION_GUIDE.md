# Guida di Integrazione - Clean Architecture

Questa guida spiega come integrare gradualmente il codice esistente con la nuova architettura Clean Architecture.

## Strategia di Migrazione

### Approccio Graduale (Raccomandato)

1. **Fase 1**: Mantenere il codice esistente funzionante
2. **Fase 2**: Creare nuove funzionalità usando Clean Architecture
3. **Fase 3**: Migrare gradualmente le funzionalità esistenti

### Opzione 1: Co-esistenza (Minimal Changes)

Il vecchio codice in `device/` continua a funzionare. Il nuovo codice in `src/` può essere usato per nuove funzionalità o refactoring progressivo.

```python
# device/__main__.py (rimane invariato)
# Il vecchio codice continua a funzionare normalmente

# Nuovo entrypoint per Clean Architecture
# src/main.py
from src.infrastructure.di_container import DIContainer
from device.api import db, socketio
from device.video_producer import VideoProducer

# Inizializza il container
container = DIContainer(
    db=db,
    video_producer=VideoProducer.get_instance(),
    socketio=socketio
)

# Usa i use cases
create_game = container.get_create_game_use_case()
manage_game = container.get_manage_game_use_case()
```

### Opzione 2: Integrazione Completa

Modificare `device/api/__init__.py` per usare i nuovi controller:

```python
# device/api/__init__.py
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os

# Importa il DI Container
from src.infrastructure.di_container import DIContainer
from src.infrastructure.api.game_controller import GameController, GameActionsController

load_dotenv()

# ... setup esistente di db, app, etc ...

# Inizializza il DI Container
container = DIContainer(
    db=db,
    video_producer=VideoProducer.get_instance(),
    socketio=socketio
)

# Crea i controller con dipendenze iniettate
game_controller = GameController(container)
game_actions_controller = GameActionsController(container, game_controller)

# Registra i controller (nuova architettura)
api.add_resource(
    game_controller,
    "/api/v2/game",
    resource_class_kwargs={'container': container}
)
api.add_resource(
    game_actions_controller,
    "/api/v2/game/actions",
    resource_class_kwargs={'container': container, 'game_controller': game_controller}
)

# ... mantieni gli endpoint esistenti per compatibilità ...
```

## Esempio di Migrazione: GameResource

### Prima (device/api/resources.py)

```python
class GameResource(Resource):
    def post(self):
        data = request.json
        ruleset = models_dao.RulesetDao.get(data['ruleset_id'])
        table = models_dao.TablePresetDao.get(data['table_id'])
        
        game = game_manager.new_game(
            ruleset=ruleset,
            table=table,
            player1_name=data['player1_name'],
            player2_name=data['player2_name'],
            socketio=socketio
        )
        return {"status": "created"}, 201
```

### Dopo (Clean Architecture)

```python
# src/infrastructure/api/game_controller.py
class GameController(Resource):
    def __init__(self, container: DIContainer):
        self.create_game_use_case = container.get_create_game_use_case()
        self.manage_game_use_case = container.get_manage_game_use_case()
    
    def post(self):
        data = request.get_json()
        
        # Usa il use case
        game = self.create_game_use_case.execute(
            ruleset_id=data["ruleset_id"],
            table_preset_id=data["table_id"],
            player1_name=data["player1_name"],
            player2_name=data["player2_name"],
        )
        
        if not game:
            return {"error": "Invalid parameters"}, 400
        
        # Salva il game corrente
        self.current_game = game
        
        # Avvia il game
        error = self.manage_game_use_case.start_game(game)
        if error:
            return {"error": error}, 400
        
        return {"status": "created"}, 201
```

## Vantaggi della Nuova Architettura

### 1. Testabilità

**Prima:**
```python
# Difficile da testare - dipendenze hard-coded
def test_create_game():
    # Richiede database reale, socketio, video producer, ecc.
    game = game_manager.new_game(...)
```

**Dopo:**
```python
# Facile da testare - mock delle dipendenze
def test_create_game_use_case():
    mock_repo = Mock()
    mock_repo.get.return_value = Ruleset(...)
    
    use_case = CreateGameUseCase(mock_repo, mock_table_repo)
    game = use_case.execute(...)
    
    assert game.status == "ready"
```

### 2. Riusabilità

```python
# Il use case può essere usato da:
# - API REST endpoint
# - GraphQL resolver
# - CLI command
# - Background job
# - Test unitari

create_game = container.get_create_game_use_case()
game = create_game.execute(1, 1, "Player1", "Player2")
```

### 3. Manutenibilità

```python
# Cambiare il database da SQLAlchemy a MongoDB:
# - Crea nuovo MongoDBRulesetRepository
# - Implementa RulesetRepository interface
# - Modifica solo DIContainer
# - Use cases e domain rimangono invariati!

class MongoDBRulesetRepository(RulesetRepository):
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        doc = self.collection.find_one({"_id": ruleset_id})
        return Ruleset(**doc) if doc else None
```

## Migrazione dei DAO

### Prima (device/api/models_dao.py)

```python
class RulesetDao:
    @staticmethod
    def get(id):
        return Ruleset.query.get(id)
    
    @staticmethod
    def create(name, initial_duration, ...):
        new_ruleset = Ruleset(name=name, ...)
        db.session.add(new_ruleset)
        db.session.commit()
        return new_ruleset
```

### Dopo (Clean Architecture)

```python
# Domain: Definisce l'interfaccia
class RulesetRepository(ABC):
    @abstractmethod
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        pass

# Infrastructure: Implementa con SQLAlchemy
class SQLAlchemyRulesetRepository(RulesetRepository):
    def __init__(self, db: SQLAlchemy):
        self.db = db
    
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        model = self.db.session.get(RulesetModel, ruleset_id)
        return self._to_entity(model) if model else None
```

## Pattern di Test

### Test Unitari (Domain/Application)

```python
import unittest
from unittest.mock import Mock

class TestCreateGameUseCase(unittest.TestCase):
    def setUp(self):
        # Mock repositories
        self.mock_ruleset_repo = Mock()
        self.mock_table_repo = Mock()
        
        # Create use case
        self.use_case = CreateGameUseCase(
            self.mock_ruleset_repo,
            self.mock_table_repo
        )
    
    def test_execute_success(self):
        # Arrange
        self.mock_ruleset_repo.get.return_value = Ruleset(...)
        self.mock_table_repo.get.return_value = TablePreset(...)
        
        # Act
        game = self.use_case.execute(1, 1, "P1", "P2")
        
        # Assert
        self.assertIsNotNone(game)
        self.assertEqual(game.status, "ready")
```

### Test di Integrazione (Infrastructure)

```python
import unittest
from src.infrastructure.persistence.sqlalchemy_ruleset_repository import SQLAlchemyRulesetRepository

class TestSQLAlchemyRulesetRepository(unittest.TestCase):
    def setUp(self):
        # Setup test database
        self.app = create_test_app()
        self.db = create_test_db()
        self.repo = SQLAlchemyRulesetRepository(self.db)
    
    def test_get_existing_ruleset(self):
        # Arrange - Insert test data
        # Act
        ruleset = self.repo.get(1)
        # Assert
        self.assertIsNotNone(ruleset)
```

## Best Practices

### 1. Dependency Injection

```python
# ❌ Bad - Hard-coded dependencies
class GameService:
    def __init__(self):
        self.repo = SQLAlchemyRulesetRepository(db)  # Hard-coded!

# ✅ Good - Injected dependencies
class GameService:
    def __init__(self, repo: RulesetRepository):
        self.repo = repo  # Interface, not implementation
```

### 2. Separazione delle Preoccupazioni

```python
# ❌ Bad - Logica business nel controller
class GameController:
    def post(self):
        # Validazione
        # Logica business
        # Accesso al database
        # Notifiche
        return response

# ✅ Good - Controller sottile
class GameController:
    def post(self):
        data = request.get_json()
        game = self.create_game_use_case.execute(**data)
        return {"game": game}, 201
```

### 3. Entities Pure

```python
# ❌ Bad - Entity con dipendenze
@dataclass
class Game:
    def save(self):
        db.session.add(self)  # Dipendenza da SQLAlchemy!

# ✅ Good - Entity pura
@dataclass
class Game:
    ruleset_id: int
    player_names: List[str]
    # Solo dati, nessuna logica di persistence
```

## Domande Frequenti

### Q: Devo riscrivere tutto il codice?

**R:** No! Puoi:
1. Mantenere il codice esistente in `device/`
2. Usare la nuova architettura in `src/` per nuove funzionalità
3. Migrare gradualmente le funzionalità più importanti

### Q: Come testo il codice esistente che usa il database?

**R:** Hai due opzioni:
1. **Test di integrazione**: Usa un database di test
2. **Refactoring**: Migra alla Clean Architecture e usa mock

### Q: Posso usare entrambe le architetture?

**R:** Sì! Durante la transizione:
- Vecchi endpoint: `/game` (vecchia architettura)
- Nuovi endpoint: `/api/v2/game` (Clean Architecture)

### Q: Come gestisco le transazioni?

**R:** Nel use case o tramite decorator:

```python
class CreateGameUseCase:
    def execute(self, ...):
        # Inizia transazione
        try:
            ruleset = self.repo.get(...)
            # ... logica ...
            self.repo.commit()
        except:
            self.repo.rollback()
            raise
```

## Prossimi Passi

1. ✅ Struttura creata
2. ✅ Test unitari funzionanti
3. ✅ Documentazione completa
4. ⏳ Integrazione con API Flask esistente
5. ⏳ Migrazione graduale funzionalità
6. ⏳ Test di integrazione end-to-end

## Risorse

- [Clean Architecture - Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Dependency Inversion Principle](https://en.wikipedia.org/wiki/Dependency_inversion_principle)
