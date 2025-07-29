from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass


class Base(MappedAsDataclass, DeclarativeBase):
    pass


class BaseMV(MappedAsDataclass, DeclarativeBase):
    pass
