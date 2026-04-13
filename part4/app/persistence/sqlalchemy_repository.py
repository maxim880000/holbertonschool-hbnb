from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from app.persistence.repository import Repository

class SQLAlchemyRepository(Repository):
    def __init__(self, session: Session, model):
        self.session = session
        self.model = model

    def add(self, obj):
        self.session.add(obj)
        self.session.commit()
        return obj

    def get(self, obj_id):
        return self.session.query(self.model).get(obj_id)

    def get_all(self):
        return self.session.query(self.model).all()

    def update(self, obj_id, data):
        obj = self.get(obj_id)
        if obj:
            for key, value in data.items():
                setattr(obj, key, value)
            self.session.commit()
        return obj

    def delete(self, obj_id):
        obj = self.get(obj_id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False

    def get_by_attribute(self, attr_name, attr_value):
        try:
            return self.session.query(self.model).filter(getattr(self.model, attr_name) == attr_value).one()
        except NoResultFound:
            return None

    def get_all_by_attribute(self, attr_name, attr_value):
        return self.session.query(self.model).filter(getattr(self.model, attr_name) == attr_value).all()
