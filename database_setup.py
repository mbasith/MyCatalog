#! /usr/bin/python3
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'id': self.id,
            'name': self.name,
            'email': self.id,
            'picture': self.id,
        }


class Genre(Base):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    # Foreign Key
    user_id = Column(Integer, ForeignKey('user.id'))

    # Relationship to User Table
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializable format"""
        return {
            'name': self.name,
            'id': self.id,
            'user_id': self.user_id
        }


class Game(Base):
    __tablename__ = 'videogame'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    price = Column(String(8))
    rating = Column(String(250))
    platform = Column(String(100))

    # Foreign Keys
    genre_id = Column(Integer, ForeignKey('genre.id'))
    user_id = Column(Integer, ForeignKey('user.id'))

    # Relationship to genre Table
    genre = relationship(Genre)

    # Relationship to User Table
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'price': self.price,
            'rating': self.price,
            'platform': self.platform,
            'user_id': self.user_id
        }


engine = create_engine('sqlite:///videogamecatalog.db')
Base.metadata.create_all(engine)
