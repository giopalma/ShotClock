"""
SQLAlchemy implementation of TablePresetRepository.
This is an adapter that implements the repository port using SQLAlchemy.
"""
from typing import List, Optional, Tuple
import json
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from shotclock.domain.entities.table_preset import TablePreset
from shotclock.domain.repositories.table_preset_repository import TablePresetRepository


class TablePresetModel(DeclarativeBase):
    """SQLAlchemy model for TablePreset."""
    __tablename__ = "table_preset"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    points: Mapped[str] = mapped_column()
    colors: Mapped[str] = mapped_column()
    min_area_threshold: Mapped[int] = mapped_column(default=100)


class SQLAlchemyTablePresetRepository(TablePresetRepository):
    """
    SQLAlchemy adapter for TablePresetRepository.
    
    This implements the repository interface using SQLAlchemy,
    keeping the database details in the infrastructure layer.
    """
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.model = TablePresetModel
    
    def _to_entity(self, model: TablePresetModel) -> TablePreset:
        """Convert SQLAlchemy model to domain entity."""
        return TablePreset(
            id=model.id,
            name=model.name,
            points=json.loads(model.points),
            colors=json.loads(model.colors),
            min_area_threshold=model.min_area_threshold,
        )
    
    def get(self, preset_id: int) -> Optional[TablePreset]:
        """Retrieve a table preset by its ID."""
        model = self.db.session.get(self.model, preset_id)
        return self._to_entity(model) if model else None
    
    def get_all(self) -> List[TablePreset]:
        """Retrieve all table presets."""
        models = self.db.session.query(self.model).all()
        return [self._to_entity(model) for model in models]
    
    def create(
        self,
        name: str,
        points: List[Tuple[int, int]],
        colors: List[Tuple[int, int, int]],
        min_area_threshold: int,
    ) -> TablePreset:
        """Create a new table preset."""
        new_model = self.model(
            name=name,
            points=json.dumps(points),
            colors=json.dumps(colors),
            min_area_threshold=min_area_threshold,
        )
        self.db.session.add(new_model)
        self.db.session.commit()
        return self._to_entity(new_model)
    
    def delete(self, preset_id: int) -> bool:
        """Delete a table preset by its ID."""
        model = self.db.session.get(self.model, preset_id)
        if model is None:
            return False
        self.db.session.delete(model)
        self.db.session.commit()
        return True
