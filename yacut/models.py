from datetime import datetime
from yacut import db


# Модель для хранения пар «длинная — короткая» ссылка
class URLMap(db.Model):
    __tablename__ = 'url_map'

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(2048), nullable=False)
    short = db.Column(db.String(64), unique=True, nullable=False, index=True)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'original': self.original,
            'short': self.short,
            'timestamp': (
                self.timestamp.isoformat() if self.timestamp else None
            ),
        }
