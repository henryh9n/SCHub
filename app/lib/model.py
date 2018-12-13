from typing import Any
from app.lib.table_view import TableView


class Model(TableView):
    """ Base model class for module entities

    """
    def add(self, data: dict, **kwargs: dict) -> Any:
        return self.insert(data, **kwargs)

    def edit(self, id: int, data: dict, ret: str = 'id',
             **kwargs: dict) -> Any:
        return self.update_by_id(
            self.preprocess(self.before_edit(id, data, **kwargs), **kwargs),
            id, ret)

    def remove(self, id: int) -> int:
        self.before_remove(id)
        return self.delete_by_id(id)

    def preprocess(self, data: dict, **kwargs: dict) -> dict:
        return data

    def before_add(self, data: dict, **kwargs: dict) -> dict:
        return data

    def before_edit(self, id: int, data: dict, **kwargs) -> dict:

        return data

    def before_remove(self, id: int):
        pass
