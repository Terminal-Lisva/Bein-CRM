from .database import db


class CodeDoc(db.Model):
    __tablename__ = 'code_documents'
    __table_args__ = {
        'autoload': True,
        'autoload_with': db.engine
    }
    bpm = db.relationship("Bpm")
    type_doc = db.relationship("TypeDoc")
