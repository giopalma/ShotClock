from device.api import db
from sqlalchemy.orm import Mapped, mapped_column
from typing import List, Tuple
import json
from dataclasses import dataclass
import logging


@dataclass
class Ruleset(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    initial_duration: Mapped[int] = mapped_column()
    turn_duration: Mapped[int] = mapped_column()
    allarm_time: Mapped[int] = mapped_column()
    increment_duration: Mapped[int] = mapped_column()
    max_increment_for_match: Mapped[int] = mapped_column()


class RulesetDao:
    @staticmethod
    def get_all():
        return Ruleset.query.all()

    @staticmethod
    def delete(id):
        ruleset = Ruleset.query.get(id)
        if ruleset is None:
            return False
        db.session.delete(ruleset)
        db.session.commit()
        return True

    @staticmethod
    def create(
        name: str,
        initial_duration: int,
        turn_duration: int,
        allarm_time: int,
        increment_duration: int,
        max_increment_for_match: int,
    ):
        new_ruleset = Ruleset(
            name=name,
            initial_duration=initial_duration,
            turn_duration=turn_duration,
            allarm_time=allarm_time,
            increment_duration=increment_duration,
            max_increment_for_match=max_increment_for_match,
        )
        db.session.add(new_ruleset)
        db.session.commit()
        return new_ruleset


@dataclass
class TablePreset(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True)
    points: Mapped[str] = mapped_column()
    colors: Mapped[str] = mapped_column()


class TablePresetDao:
    @staticmethod
    def get_all():
        return TablePreset.query.all()

    @staticmethod
    def delete(id):
        ruleset = TablePreset.query.get(id)
        if ruleset is None:
            return False
        db.session.delete(ruleset)
        db.session.commit()
        return True

    @staticmethod
    def create(name: str, points: List[Tuple[int, int]], colors: List[Tuple[int, int]]):
        new_tablepreset = TablePreset(
            name=name,
            points=json.dumps(points),
            colors=json.dumps(colors),
        )
        db.session.add(new_tablepreset)
        db.session.commit()
        return new_tablepreset
