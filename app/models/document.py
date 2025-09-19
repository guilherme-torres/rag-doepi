from typing import List
from datetime import date
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    tipo: Mapped[str]
    ref: Mapped[str]
    dia: Mapped[date]
    number: Mapped[int]
    year: Mapped[int]
    text: Mapped[str] = mapped_column(Text)
    filename: Mapped[str]
    link: Mapped[str]

    histories: Mapped[List["History"]] = relationship(back_populates="document")

    def __repr__(self):
        return f"Document(id={self.id}, filename={self.filename})"
