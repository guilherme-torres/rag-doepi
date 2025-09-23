from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Text
from app.database.db import Base


class History(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"))
    ai_response: Mapped[str] = mapped_column(Text)
    ai_model: Mapped[str]

    document: Mapped["Document"] = relationship(back_populates="histories")

    def __repr__(self):
        return f"History(id={self.id}, document_id={self.document_id}, ai_model={self.ai_model})"
