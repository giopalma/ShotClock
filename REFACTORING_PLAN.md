# Piano di Refactoring - Clean Architecture

Documento di pianificazione per il refactoring completo del progetto ShotClock secondo i principi della Clean Architecture.

## Stato Attuale

### ✅ Completato

1. **Analisi Iniziale**
   - ✅ Identificati framework e librerie: Flask, SQLAlchemy, OpenCV, gpiozero, numpy
   - ✅ Mappati componenti esistenti: API, Game logic, Video processing, Database
   - ✅ Identificate aree di tight coupling

2. **Struttura Base**
   - ✅ Creata struttura directory Clean Architecture
   - ✅ Implementati livelli: Domain, Application, Infrastructure
   - ✅ Configurato Dependency Injection Container

3. **Domain Layer**
   - ✅ Entità pure: Ruleset, TablePreset, Game
   - ✅ Repository interfaces (Ports)
   - ✅ Service interfaces (Ports): Timer, Video, Notification

4. **Application Layer**
   - ✅ Use Case: CreateGame
   - ✅ Use Case: ManageGame (start/pause/resume/end/increment)

5. **Infrastructure Layer**
   - ✅ Repository Adapters: SQLAlchemy implementations
   - ✅ Service Adapters: Timer, Video, Notification
   - ✅ API Controllers: Example Flask controllers

6. **Testing**
   - ✅ Test unitari per Domain entities (4 tests)
   - ✅ Test unitari per Application use cases (4 tests)
   - ✅ Struttura per test di integrazione

7. **Documentazione**
   - ✅ CLEAN_ARCHITECTURE.md - Guida completa
   - ✅ INTEGRATION_GUIDE.md - Guida di migrazione
   - ✅ shotclock/README.md - Quick start
   - ✅ Esempi di codice

## Mappatura Componenti

### Codice Esistente → Clean Architecture

| Componente Esistente | Nuovo Layer | Nuovo Componente |
|---------------------|-------------|------------------|
| `device/game/ruleset.py` | Domain | `shotclock/domain/entities/ruleset.py` |
| `device/table.py` | Domain | `shotclock/domain/entities/table_preset.py` |
| `device/api/models_dao.py` (Ruleset) | Infrastructure | `shotclock/infrastructure/persistence/sqlalchemy_ruleset_repository.py` |
| `device/api/models_dao.py` (TablePreset) | Infrastructure | `shotclock/infrastructure/persistence/sqlalchemy_table_preset_repository.py` |
| `device/game/timer.py` | Infrastructure | `shotclock/infrastructure/hardware/timer_adapter.py` |
| `device/game/game_manager.py` | Application | `shotclock/application/use_cases/manage_game.py` |
| `device/game/__init__.py` (Game) | Domain + Application | `shotclock/domain/entities/game.py` + Use Cases |
| `device/video_producer.py` | Infrastructure | `shotclock/infrastructure/video/video_adapter.py` |
| `device/game/video_consumer.py` | Infrastructure | `shotclock/infrastructure/video/video_adapter.py` |
| `device/api/resources.py` | Infrastructure | `shotclock/infrastructure/api/` controllers |

## Librerie Esterne - Confinamento nell'Infrastructure

| Libreria | Layer | Componente |
|----------|-------|------------|
| Flask, Flask-RESTful | Infrastructure | `shotclock/infrastructure/api/` |
| Flask-SocketIO | Infrastructure | `shotclock/infrastructure/hardware/notification_adapter.py` |
| SQLAlchemy | Infrastructure | `shotclock/infrastructure/persistence/` |
| OpenCV | Infrastructure | `shotclock/infrastructure/video/` |
| gpiozero | Infrastructure | `shotclock/infrastructure/hardware/` |
| numpy | Infrastructure | `shotclock/infrastructure/video/` |
| argon2, jwt | Infrastructure | `shotclock/infrastructure/api/auth/` |

## Prossimi Passi Dettagliati

### Fase 1: Completare Use Cases ⏳

1. **Use Cases Mancanti**
   - [ ] GetGameStatus use case
   - [ ] UpdateRuleset use case
   - [ ] UpdateTablePreset use case
   - [ ] ListRulesets use case
   - [ ] ListTablePresets use case

### Fase 2: Completare Infrastructure Adapters ⏳

1. **API Controllers**
   - [ ] RulesetController (CRUD operations)
   - [ ] TablePresetController (CRUD operations)
   - [ ] VideoController (frame retrieval, recording)
   - [ ] AuthController (login, logout, password)

2. **Video Adapters**
   - [x] VideoAdapter base (parzialmente completato)
   - [ ] VideoRecordingAdapter
   - [ ] VideoStreamAdapter
   - [ ] Frame processing utilities

3. **Hardware Adapters**
   - [x] TimerAdapter (completato)
   - [x] NotificationAdapter (completato)
   - [ ] GPIOAdapter (per buttons, se necessario)

### Fase 3: Migrazione API Endpoints ⏳

Migrare gradualmente gli endpoint esistenti per usare Clean Architecture:

**Priorità Alta:**
- [ ] `/game` → `/api/v2/game`
- [ ] `/game/actions` → `/api/v2/game/actions`
- [ ] `/ruleset` → `/api/v2/ruleset`
- [ ] `/table` → `/api/v2/table`

**Priorità Media:**
- [ ] `/video/frame` → `/api/v2/video/frame`
- [ ] `/video/stream` → `/api/v2/video/stream`
- [ ] `/video/record` → `/api/v2/video/record`

**Priorità Bassa:**
- [ ] `/login` → `/api/v2/auth/login`
- [ ] `/logout` → `/api/v2/auth/logout`
- [ ] `/password` → `/api/v2/auth/password`

### Fase 4: Testing Completo ⏳

1. **Unit Tests**
   - [x] Domain entities (completato)
   - [x] Application use cases (CreateGame completato)
   - [ ] Application use cases (ManageGame)
   - [ ] Application use cases (altri use cases)

2. **Integration Tests**
   - [ ] Repository adapters con database
   - [ ] API controllers con Flask test client
   - [ ] Video adapters con mock frames
   - [ ] End-to-end workflow tests

3. **Test Coverage**
   - [ ] Configurare coverage.py
   - [ ] Target: >80% coverage per domain e application
   - [ ] Target: >70% coverage per infrastructure

### Fase 5: Refactoring del WebSocket ⏳

1. **WebSocket Events**
   - [ ] Definire eventi di dominio (DomainEvents)
   - [ ] Implementare EventPublisher interface
   - [ ] Creare SocketIOEventPublisher adapter
   - [ ] Integrare con use cases

### Fase 6: Configurazione e Bootstrap ⏳

1. **Configuration**
   - [ ] Creare configuration interface
   - [ ] Implementare ConfigurationAdapter
   - [ ] Migrare da `device/config.py`

2. **Logging**
   - [ ] Creare logging interface
   - [ ] Implementare LoggingAdapter
   - [ ] Integrare con use cases

### Fase 7: Documentazione e Deploy ⏳

1. **Documentazione API**
   - [ ] OpenAPI/Swagger specification
   - [ ] API documentation with examples
   - [ ] Postman collection

2. **Deployment**
   - [ ] Docker support
   - [ ] Environment configuration
   - [ ] Production setup guide

## Strategia di Migrazione Consigliata

### Opzione A: Big Bang (Non Raccomandato)

- Riscrivere tutto il codice in una volta
- Alto rischio di breaking changes
- Difficile da testare incrementalmente

### Opzione B: Strangler Fig Pattern (Raccomandato) ✅

1. **Fase 1**: Coesistenza
   - Vecchio codice in `device/` continua a funzionare
   - Nuovo codice in `shotclock/` per nuove funzionalità
   - Entrambi condividono il database

2. **Fase 2**: Migrazione Graduale
   - Migrare endpoint uno alla volta
   - Mantenere backward compatibility
   - Test paralleli vecchio vs nuovo

3. **Fase 3**: Deprecazione
   - Deprecare vecchi endpoint
   - Grace period per i client
   - Rimuovere vecchio codice

### Timeline Suggerita

```
Settimana 1-2: ✅ Completata
- Setup struttura base
- Domain entities
- Core use cases
- Test iniziali

Settimana 3-4: ⏳ In corso
- Completare use cases
- Implementare adapters
- Test di integrazione

Settimana 5-6:
- Migrare API endpoints
- WebSocket refactoring
- Test end-to-end

Settimana 7-8:
- Documentazione completa
- Performance testing
- Deploy preparation
```

## Checklist di Qualità

Prima di considerare il refactoring completo:

### Domain Layer
- [x] Nessuna dipendenza esterna
- [x] Entities sono dataclasses pure
- [x] Interfaces ben definite
- [x] Test unitari passano

### Application Layer
- [x] Dipende solo da Domain
- [x] Use cases ben definiti
- [x] Single Responsibility per use case
- [x] Test con mock passano

### Infrastructure Layer
- [x] Implementa tutte le interfaces
- [x] Librerie esterne confinate
- [ ] Test di integrazione passano
- [ ] Error handling appropriato

### General
- [ ] Code coverage >80%
- [ ] Documentation completa
- [ ] No code smells critici
- [ ] Performance accettabile

## Metriche di Successo

1. **Testabilità**
   - ✅ Domain layer testabile in isolamento
   - ✅ Application layer testabile con mock
   - ⏳ Test coverage >80%

2. **Manutenibilità**
   - ✅ Chiara separazione delle responsabilità
   - ✅ Facile aggiungere nuove funzionalità
   - ⏳ Facile cambiare implementazioni

3. **Performance**
   - ⏳ Stesse performance del codice esistente
   - ⏳ No degradazione con DI

4. **Compatibilità**
   - ⏳ API backward compatible
   - ⏳ Database schema compatible

## Rischi e Mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione |
|---------|-------------|---------|-------------|
| Breaking changes API | Media | Alto | Versioning API, backward compatibility |
| Performance degradation | Bassa | Medio | Benchmarking, optimization |
| Complessità eccessiva | Media | Medio | Keep it simple, avoid over-engineering |
| Learning curve team | Alta | Basso | Documentation, code reviews, pair programming |

## Conclusioni

Il refactoring verso Clean Architecture è **ben avviato** con:
- ✅ Struttura completa implementata
- ✅ Core use cases funzionanti
- ✅ Test passanti
- ✅ Documentazione esaustiva

**Prossimo step immediato**: Completare i controller API e integrare con l'applicazione Flask esistente.
