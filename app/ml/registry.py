"""In-process model registry with explicit activation."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RegisteredModel:
    name: str
    version: str
    model: Any
    active: bool = False


class ModelRegistry:
    """Register immutable versions and activate one version per model name."""

    def __init__(self) -> None:
        self._models: dict[tuple[str, str], RegisteredModel] = {}
        self._active: dict[str, str] = {}

    def register(self, model: Any, *, name: str, version: str) -> RegisteredModel:
        key = (name, version)
        if key in self._models:
            return self._models[key]
        record = RegisteredModel(name=name, version=version, model=model)
        self._models[key] = record
        return record

    def activate(self, *, name: str, version: str) -> RegisteredModel:
        key = (name, version)
        if key not in self._models:
            raise KeyError("model version is not registered")
        self._active[name] = version
        record = self._models[key]
        active = RegisteredModel(record.name, record.version, record.model, True)
        self._models[key] = active
        return active

    def active(self, name: str) -> RegisteredModel:
        version = self._active.get(name)
        if version is None:
            raise KeyError("no active model for name")
        return self._models[(name, version)]
