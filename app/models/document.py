from typing import List
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.db import Base


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(Text)
    filename: Mapped[str]

    histories: Mapped[List["History"]] = relationship(back_populates="document")

    def __repr__(self):
        return f"Document(id={self.id}, filename={self.filename})"
