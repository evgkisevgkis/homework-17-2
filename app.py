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
director_ns = api.namespace('directors')


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


class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


movie_schema = MovieSchema()
director_schema = DirectorSchema()

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

    def post(self):
        try:
            movie_data = request.json
            new_movie = Movie(**movie_data)
            with db.session.begin():
                db.session.add(new_movie)
            return 'Фильм добавлен в базу данных', 201
        except Exception as e:
            return e, 400


@movie_ns.route('/<int:mid>')
class OneMovieView(Resource):
    def get(self, mid: int):
        one_movie = Movie.query.get(mid)
        if not one_movie:
            return 'Извините, фильм с таким ID не найден.', 404
        return movie_schema.dump(one_movie), 200

    def put(self, mid: int):
        movie = Movie.query.get(mid)
        if not movie:
            return 'Извините, фильм с таким ID не найден.', 404
        try:
            movie_data = request.json
            movie.title = movie_data.get('title')
            movie.description = movie_data.get('description')
            movie.trailer = movie_data.get('trailer')
            movie.year = movie_data.get('year')
            movie.rating = movie_data.get('rating')
            movie.genre_id = movie_data.get('genre_id')
            movie.director_id = movie_data.get('director_id')
            db.session.add(movie)
            db.session.commit()
            return 'Фильм обновлён', 200
        except Exception as e:
            return e, 400

    def delete(self, mid: int):
        movie = Movie.query.get(mid)
        if not movie:
            return 'Извините, фильм с таким ID не найден.', 404
        db.session.delete(movie)
        db.session.commit()
        return 'Фильм успешно удалён', 204


if __name__ == '__main__':
    app.run()
