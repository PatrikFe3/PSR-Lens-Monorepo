from pathlib import Path
from typing import Generic, TypeVar

import yaml
from pydantic import BaseModel, ValidationError

T = TypeVar('T', bound=BaseModel)


class CatalogError(Exception):
    pass


class Registry(Generic[T]):

    def __init__(self, model: type[T], folder: Path):
        self._items: dict[str, T] = {}
        folder = Path(folder)
        if not folder.is_dir():
            raise CatalogError(f'Catalog folder not found: {folder}')
        for path in sorted(folder.glob('*.yaml')):
            try:
                data = yaml.safe_load(path.read_text(encoding='utf-8'))
            except yaml.YAMLError as err:
                raise CatalogError(f'{path}: {err}') from err
            if data is None:
                raise CatalogError(f'{path}: file is empty. Fill it in or delete it.')
            try:
                item = model.model_validate(data)
            except ValidationError as err:
                raise CatalogError(f'{path}: {err}') from err
            if item.id in self._items:
                raise CatalogError(f'{path}: duplicates id {item.id!r}')
            self._items[item.id] = item

    def get(self, item_id: str) -> T:
        try:
            return self._items[item_id]
        except KeyError:
            raise KeyError(f'Unknown id {item_id!r}. Known: {sorted(self._items)}') from None

    def __contains__(self, item_id: str) -> bool:
        return item_id in self._items

    def ids(self) -> list[str]:
        return sorted(self._items)

    def all(self) -> list[T]:
        return [self._items[i] for i in self.ids()]
