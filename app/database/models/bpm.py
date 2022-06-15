from .database import db


class Bpm(db.Model):
    __tablename__ = 'bpm'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    lvl = db.Column(db.Integer, nullable=False)
    id_company = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    id_owner = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    id_parent = db.Column(db.Integer, db.ForeignKey('bpm.id'), nullable=True)

    def __repr__(self):
        return f"""Бизнес процесс [Название: {self.code} {self.name},
        Уровень: {self.lvl}, ID компании: {self.id_company},
        ID владельца: {self.id_owner}]"""
