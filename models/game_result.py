from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from config.database import Base

class GameResult(Base):
    __tablename__ = "game_results"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    wpm = Column(Float)
    accuracy = Column(Float)
    real_accuracy = Column(Float)
    text = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def to_dict(self):
        # Ensure created_at is timezone-aware before formatting
        created_at_iso = self.created_at.isoformat() if self.created_at is not None else None
        return {
            "id": self.id,
            "username": self.username,
            "wpm": self.wpm,
            "accuracy": self.accuracy,
            "real_accuracy": self.real_accuracy,
            "text": self.text,
            "created_at": created_at_iso
        }
