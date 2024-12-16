from pydantic import BaseModel


class Base1(BaseModel):
    class Config:
        table_name: str | None = None

    @classmethod
    def table_name(cls) -> str:
        return cls.Config.table_name or cls.__name__.lower() + "s"


class Base2(Base1):
    is_archived: bool = False
