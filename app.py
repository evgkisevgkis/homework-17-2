from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')
genre_ns = api.namespace('genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")


class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()


movie_schema = MovieSchema()


@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        pre = Movie.query
        director_id = request.args.get('director_id')
        genre_id = request.args.get('genre_id')
        if director_id:
            pre = pre.filter(Movie.director_id == director_id)
        if genre_id:
            pre = pre.filter(Movie.genre_id == genre_id)
        all_movies = pre.all()
        if not all_movies:
            return 'Извините, по вашему запросу ничего не найдено', 404
        return movie_schema.dump(all_movies, many=True), 200


@movie_ns.route('/<int:mid>')
class OneMovieView(Resource):
    def get(self, mid: int):
        one_movie = Movie.query.get(mid)
        if not one_movie:
            return 'Извините, фильм с таким ID не найден.', 404
        return movie_schema.dump(one_movie), 200


if __name__ == '__main__':
    app.run()
