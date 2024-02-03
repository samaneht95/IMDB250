# =================================creating mysql tables===========================================
import sqlalchemy as db
from sqlalchemy.orm import declarative_base,Mapped,relationship
from sqlalchemy.orm import Session


engine=db.create_engine('mysql+pymysql://samaneh957:***@localhost/week2')
conn=engine.connect()

Base=declarative_base()

class Movie(Base):
    __tablename__="Movie"
    id=db.Column(db.VARCHAR(8),primary_key=True)
    title=db.Column(db.VARCHAR(128))
    year=db.Column(db.Integer)
    runtime=db.Column(db.Integer)
    parental_guide=db.Column(db.VARCHAR(16))
    gross_us_canada=db.Column(db.Integer)

    genre=relationship("Genre_movie",back_populates="movie")
    cast=relationship("Cast",back_populates="movie")
    crew=relationship("Crew",back_populates="movie")

    def __repr__(self):
        return (f"{self.id},{self.title},{self.year}")

class Person(Base):
    __tablename__="Person"
    id=db.Column(db.VARCHAR(8),primary_key=True)
    name=db.Column(db.VARCHAR(32))

    cast=relationship("Cast",back_populates="person")
    crew=relationship("Crew",back_populates="person")



class Cast(Base):
    __tablename__="Cast"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    movie_id=db.Column(db.VARCHAR(8),db.ForeignKey('Movie.id'))
    person_id=db.Column(db.VARCHAR(8),db.ForeignKey('Person.id'))

    movie=relationship("Movie",back_populates="cast")
    person=relationship("Person",back_populates="cast")


class Crew(Base):
    __tablename__="Crew"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    movie_id=db.Column(db.VARCHAR(8),db.ForeignKey('Movie.id'))
    person_id=db.Column(db.VARCHAR(8),db.ForeignKey('Person.id'))
    role=db.Column(db.VARCHAR(8))

    movie=relationship("Movie",back_populates="crew")
    person=relationship("Person",back_populates="crew")


class Genre_movie(Base):
    __tablename__="Genre_movie"
    id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    movie_id=db.Column(db.VARCHAR(8),db.ForeignKey('Movie.id'))
    genre=db.Column(db.VARCHAR(16))
    movie=relationship("Movie",back_populates="genre")



Base.metadata.create_all(engine)

# ===================================making pandas tables========================================
import pandas as pd
import ast

data=pd.read_excel("movies.xlsx")

# Movies------------------------------
movies=data[["film_ids","titles","years","runtimes","parental_guides","box_offices"]].copy()

movies["box_offices"]=movies["box_offices"].fillna(0)
movies["parental_guides"]=movies["parental_guides"].fillna("Unrated")
movies["parental_guides"].replace("Not Rated","Unrated",inplace=True)

movies=movies.rename(columns={"film_ids":"id","titles":"title","years":"year","runtimes":"runtime","parental_guides":"parental_guide","box_offices":"gross_us_canada"})

# Person------------------------------
person=pd.read_csv("person.csv")
person=person[["artist_id","artist_name"]].copy()

# Cast--------------------------------
data["stars"]=data["stars"].apply(ast.literal_eval)
c=data[["film_ids","stars"]].copy()
c=c.explode("stars").merge(person,left_on="stars",right_on="artist_name",how="inner")
cast=c[["film_ids","artist_id"]].rename(columns={"film_ids":"movie_id","artist_id":"person_id"})
# print(cast)

# crew---------------------------------
data["directors"]=data["directors"].apply(ast.literal_eval)
data["writers"]=data["writers"].apply(ast.literal_eval)
crew_d=data[["film_ids","directors"]].explode("directors")
crew_d["role"]=pd.Series(["director" for i in range(len(crew_d))])
crew_w=data[["film_ids","writers"]].explode("writers")
crew_w["role"]=pd.Series(["writer" for i in range(len(crew_w))])

crew_d = crew_d.rename(columns={'film_ids': 'movie_id', 'directors': 'name'})
crew_w = crew_w.rename(columns={'film_ids': 'movie_id', 'writers': 'name'})

crew=pd.concat([crew_d,crew_w],axis=0).reset_index()

crew=crew.merge(person,left_on="name",right_on="artist_name",how="inner")
crew=crew[["movie_id","artist_id","role"]]
crew=crew.rename(columns={"artist_id":"person_id"})


# genre_movie------------------------------------------------
data["genres"]=(data["genres"]).apply(ast.literal_eval)
genre=data[["film_ids","genres"]].explode("genres").explode("genres").reset_index()
genre=genre[["film_ids","genres"]].rename(columns={"film_ids":"movie_id","genres":"genre"})
# print(genre)

person=person.rename(columns={"artist_id":"id","artist_name":"name"})
# ============================================================================

session=Session(engine)

movies.to_sql(Movie.__tablename__,con=engine,if_exists="append",index=False)
person.to_sql(Person.__tablename__,con=engine,if_exists="append",index=False)
cast.to_sql(Cast.__tablename__,con=engine,if_exists="append",index=False)
crew.to_sql(Crew.__tablename__,con=engine,if_exists="append",index=False)
genre.to_sql(Genre_movie.__tablename__,con=engine,if_exists="append",index=False)
