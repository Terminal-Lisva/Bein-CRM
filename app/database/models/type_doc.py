from .database import db


class TypeDoc(db.Model):
    __tablename__ = 'types_documents'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }
