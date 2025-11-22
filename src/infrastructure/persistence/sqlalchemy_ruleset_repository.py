"""
SQLAlchemy implementation of RulesetRepository.
This is an adapter that implements the repository port using SQLAlchemy.
"""
from typing import List, Optional
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy
from src.domain.entities.ruleset import Ruleset
from src.domain.repositories.ruleset_repository import RulesetRepository


class RulesetModel(DeclarativeBase):
    """SQLAlchemy model for Ruleset."""
    __tablename__ = "ruleset"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    initial_duration: Mapped[int] = mapped_column()
    turn_duration: Mapped[int] = mapped_column()
    allarm_time: Mapped[int] = mapped_column()
    increment_duration: Mapped[int] = mapped_column()
    max_increment_for_match: Mapped[int] = mapped_column()


class SQLAlchemyRulesetRepository(RulesetRepository):
    """
    SQLAlchemy adapter for RulesetRepository.
    
    This implements the repository interface using SQLAlchemy,
    keeping the database details in the infrastructure layer.
    """
    
    def __init__(self, db: SQLAlchemy):
        self.db = db
        self.model = RulesetModel
    
    def _to_entity(self, model: RulesetModel) -> Ruleset:
        """Convert SQLAlchemy model to domain entity."""
        return Ruleset(
            id=model.id,
            name=model.name,
            initial_duration=model.initial_duration,
            turn_duration=model.turn_duration,
            allarm_time=model.allarm_time,
            increment_duration=model.increment_duration,
            max_increment_for_match=model.max_increment_for_match,
        )
    
    def get(self, ruleset_id: int) -> Optional[Ruleset]:
        """Retrieve a ruleset by its ID."""
        model = self.db.session.get(self.model, ruleset_id)
        return self._to_entity(model) if model else None
    
    def get_all(self) -> List[Ruleset]:
        """Retrieve all rulesets."""
        models = self.db.session.query(self.model).all()
        return [self._to_entity(model) for model in models]
    
    def create(
        self,
        name: str,
        initial_duration: int,
        turn_duration: int,
        allarm_time: int,
        increment_duration: int,
        max_increment_for_match: int,
    ) -> Ruleset:
        """Create a new ruleset."""
        new_model = self.model(
            name=name,
            initial_duration=initial_duration,
            turn_duration=turn_duration,
            allarm_time=allarm_time,
            increment_duration=increment_duration,
            max_increment_for_match=max_increment_for_match,
        )
        self.db.session.add(new_model)
        self.db.session.commit()
        return self._to_entity(new_model)
    
    def delete(self, ruleset_id: int) -> bool:
        """Delete a ruleset by its ID."""
        model = self.db.session.get(self.model, ruleset_id)
        if model is None:
            return False
        self.db.session.delete(model)
        self.db.session.commit()
        return True
