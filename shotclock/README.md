# Clean Architecture Implementation

This directory contains the Clean Architecture refactoring of the ShotClock project.

## Quick Start

### Running the Clean Architecture Version

```bash
# From the project root
python -m shotclock.main

# With debug mode
python -m shotclock.main --debug
```

### Running Tests

```bash
# Run all tests
python -m unittest discover tests

# Run specific test modules
python -m unittest tests.domain.test_entities
python -m unittest tests.application.test_create_game_use_case
```

## Architecture Overview

```
shotclock/
├── domain/              # Core business logic (no external dependencies)
│   ├── entities/       # Business entities (Game, Ruleset, TablePreset)
│   ├── repositories/   # Repository interfaces (Ports)
│   └── services/       # Service interfaces (Ports)
│
├── application/        # Application-specific business rules
│   └── use_cases/     # Use cases (CreateGame, ManageGame)
│
├── infrastructure/     # External concerns and implementations
│   ├── persistence/   # Database implementations (Adapters)
│   ├── api/          # API controllers (Flask)
│   ├── video/        # Video processing adapters
│   ├── hardware/     # Hardware adapters (Timer, Buzzer)
│   └── di_container.py  # Dependency Injection Container
│
└── main.py           # Application entry point
```

## Dependency Flow

```
Infrastructure → Application → Domain

Infrastructure implements interfaces defined in Domain
Application uses Domain interfaces
Domain has NO dependencies on outer layers
```

## Usage Examples

### Creating a Game

```python
from shotclock.infrastructure.di_container import DIContainer

# Initialize container with dependencies
container = DIContainer(db=db, video_producer=vp, socketio=socketio)

# Get use case
create_game = container.get_create_game_use_case()

# Execute
game = create_game.execute(
    ruleset_id=1,
    table_preset_id=1,
    player1_name="Player 1",
    player2_name="Player 2",
)
```

### Managing a Game

```python
# Get manage game use case
manage_game = container.get_manage_game_use_case()

# Start the game
error = manage_game.start_game(game)
if error:
    print(f"Error: {error}")

# Pause the game
manage_game.pause_game(game)

# Resume the game
manage_game.resume_game(game)

# Increment time for player
manage_game.increment_time(game, player=0)

# End the game
manage_game.end_game(game)
```

### API Endpoints (Clean Architecture)

```
POST   /api/v2/game           - Create a new game
GET    /api/v2/game           - Get current game status
DELETE /api/v2/game           - End the current game
POST   /api/v2/game/actions   - Execute game action
```

#### Create Game

```bash
curl -X POST http://localhost:5000/api/v2/game \
  -H "Content-Type: application/json" \
  -d '{
    "ruleset_id": 1,
    "table_preset_id": 1,
    "player1_name": "Player 1",
    "player2_name": "Player 2"
  }'
```

#### Game Actions

```bash
# Start game
curl -X POST http://localhost:5000/api/v2/game/actions \
  -H "Content-Type: application/json" \
  -d '{"action": "start"}'

# Pause game
curl -X POST http://localhost:5000/api/v2/game/actions \
  -H "Content-Type: application/json" \
  -d '{"action": "pause"}'

# Resume game
curl -X POST http://localhost:5000/api/v2/game/actions \
  -H "Content-Type: application/json" \
  -d '{"action": "resume"}'

# Increment time for player 0
curl -X POST http://localhost:5000/api/v2/game/actions \
  -H "Content-Type: application/json" \
  -d '{"action": "increment", "player": 0}'
```

## Testing

### Unit Testing (No External Dependencies)

```python
import unittest
from unittest.mock import Mock
from shotclock.application.use_cases.create_game import CreateGameUseCase

class TestCreateGameUseCase(unittest.TestCase):
    def test_execute_success(self):
        # Mock repositories
        mock_ruleset_repo = Mock()
        mock_table_repo = Mock()
        
        # Setup mocks
        mock_ruleset_repo.get.return_value = Ruleset(...)
        mock_table_repo.get.return_value = TablePreset(...)
        
        # Create use case with mocks
        use_case = CreateGameUseCase(mock_ruleset_repo, mock_table_repo)
        
        # Execute and assert
        game = use_case.execute(1, 1, "P1", "P2")
        self.assertIsNotNone(game)
```

### Integration Testing

```python
import unittest
from shotclock.infrastructure.di_container import DIContainer

class TestGameIntegration(unittest.TestCase):
    def setUp(self):
        # Setup test app and database
        self.container = DIContainer(db=test_db, ...)
    
    def test_create_and_start_game(self):
        # Test full flow
        create_game = self.container.get_create_game_use_case()
        manage_game = self.container.get_manage_game_use_case()
        
        game = create_game.execute(1, 1, "P1", "P2")
        error = manage_game.start_game(game)
        
        self.assertIsNone(error)
        self.assertEqual(game.status, "running")
```

## Key Concepts

### Entities (Domain)

Pure data structures representing core business concepts:

```python
@dataclass
class Game:
    ruleset_id: int
    table_preset_id: int
    player_names: List[str]
    increments: List[int]
    status: str
```

### Repository Ports (Domain)

Interfaces defining data access contracts:

```python
class RulesetRepository(ABC):
    @abstractmethod
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        pass
```

### Repository Adapters (Infrastructure)

Concrete implementations using specific technologies:

```python
class SQLAlchemyRulesetRepository(RulesetRepository):
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        # SQLAlchemy implementation
        pass
```

### Use Cases (Application)

Application-specific business logic:

```python
class CreateGameUseCase:
    def execute(self, ...):
        # Validate inputs
        # Create game entity
        # Return result
        pass
```

### Dependency Injection Container

Central configuration for all dependencies:

```python
class DIContainer:
    def get_create_game_use_case(self):
        return CreateGameUseCase(
            ruleset_repository=self.get_ruleset_repository(),
            table_preset_repository=self.get_table_preset_repository(),
        )
```

## Benefits

1. **Testability**: Test business logic without external dependencies
2. **Flexibility**: Easy to swap implementations (e.g., change database)
3. **Maintainability**: Clear separation of concerns
4. **Independence**: Core business logic doesn't depend on frameworks
5. **Clarity**: Architecture is explicit in the code structure

## Migration from Legacy Code

See [INTEGRATION_GUIDE.md](../INTEGRATION_GUIDE.md) for detailed migration strategies.

### Backward Compatibility

The Clean Architecture implementation can coexist with the legacy code:

- Legacy endpoints: `/game`, `/ruleset`, etc.
- New endpoints: `/api/v2/game`, `/api/v2/ruleset`, etc.

This allows gradual migration without breaking existing clients.

## Documentation

- [CLEAN_ARCHITECTURE.md](../CLEAN_ARCHITECTURE.md) - Complete architecture documentation
- [INTEGRATION_GUIDE.md](../INTEGRATION_GUIDE.md) - Migration guide
- See inline code documentation in each module

## Contributing

When adding new features:

1. Start with domain entities and interfaces
2. Implement use cases in application layer
3. Create adapters in infrastructure layer
4. Wire dependencies in DI container
5. Add unit tests for domain and application
6. Add integration tests for infrastructure

## Examples

See the `examples/` directory (to be created) for:
- Complete CRUD operations
- Complex business workflows
- Testing patterns
- Custom adapters
