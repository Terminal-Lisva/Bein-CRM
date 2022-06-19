from .database import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    last_name = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    patronymic = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    company = db.relationship('Company', foreign_keys=company_id)

    def __repr__(self):
        return f"""Пользователь [ФИО: {self.last_name} {self.first_name}
        {self.patronymic}, Email: {self.email}, ID компании: {self.company}]"""
