from typing import Any, Tuple, List
from pydantic import BaseModel
from sqlite3 import connect, Connection

class Omr(BaseModel):

    @staticmethod
    def tablename():
        return ""

    @classmethod
    def from_tuple(cls, data : Tuple):
        assert len(data) == len(cls.__fields__)
        values = {}
        index = 0
        for field in cls.__fields__:
            values[field] = data[index]
            index += 1
        return cls(**values)

    @classmethod
    def all(cls, conn: Connection, field : str | None = None, value : Any = None):
        cursor = conn.cursor()
        if field is None:
            elements = cursor.execute(f"Select * from {cls.tablename()};").fetchall()
        else:
            assert field in cls.__fields__
            elements = cursor.execute(f"Select * from {cls.tablename()} where {field} = ?;", [value]).fetchall()
        cursor.close()
        return [cls.from_tuple(element) for element in elements]

    def create(self, conn: Connection):
        cursor = conn.cursor()
        cursor.execute(
            f'Insert into {self.tablename()} Values ({("?,"*len(self.__dict__))[:-1]});',
            list(self.__dict__.values()),
        )
        cursor.close()
        conn.commit()

    def save(self, conn: Connection):
        keys = [key+"=?" for key in self.__dict__.keys()]
        values = list(self.__dict__.values())
        values.append(values[0])
        cursor = conn.cursor()
        cursor.execute(
            f'Update {self.tablename()} Set {",".join(keys)} where {keys[0]};',
            values
        )
        cursor.close()
        conn.commit()

    @classmethod
    def load(cls, conn: Connection, pk: Any):
        cursor = conn.cursor()
        print(f"Select * from {cls.tablename()} where {list(cls.__fields__.keys())[0]} = ?;")
        elem = cursor.execute(f"Select * from {cls.tablename()} where {list(cls.__fields__.keys())[0]} = ?;", [pk]).fetchone()
        cursor.close()
        if elem is None:
            return None
        return cls.from_tuple(elem)

    def delete(self, conn: Connection):
        cursor = conn.cursor()
        pk = list(self.__dict__.items())[0]
        print(pk)
        cursor.execute(f"Delete from {self.tablename()} where {pk[0]}=?;",[pk[1]])
        cursor.close()
        conn.commit()
