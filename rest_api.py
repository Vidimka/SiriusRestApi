import uuid

from flask import Flask, jsonify, request, redirect, make_response
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

LinksBase = declarative_base()
engine = create_engine('sqlite:///links.db')


class Link(LinksBase):
    __tablename__ = 'link'
    id = Column(Integer, primary_key=True)
    ran_id = Column(Integer)
    recieved_link = Column(String(250), nullable=False)
    shorten_link = Column(String(250), nullable=False)
    views = Column(Integer, nullable=False, default=0)


LinksBase.metadata.create_all(engine)
LinksBase.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)


def write_link(spam, eggs, foo, bar):
    session.add(Link(ran_id=spam, recieved_link=eggs, shorten_link=foo, views=bar))
    session.commit()


@app.post("/shorten")
def short_link():
    if not request.json or 'urlToShorten' not in request.json:
        return make_response("Bad request", 400)
    link = request.json['urlToShorten']
    random_id = str(uuid.uuid1())[0:8]
    new_link = "http:/localhost:5000/" + random_id
    write_link(random_id, link, new_link, 0)
    return make_response(jsonify({"status": "Created", "shortenedURL": new_link}), 201)


@app.get("/<link_id>")
def get_full_link(link_id):
    link_data = session.query(Link).filter_by(ran_id=link_id).first()
    if link_data is None:
        return make_response("Not Found", 404)
    link_data.views += 1
    session.commit()
    resp = make_response(link_data.recieved_link, 301)
    resp.headers["Location"] = link_data.recieved_link
    return resp



@app.get("/<link_id>/views")
def get_views(link_id):
    link_data = session.query(Link).filter_by(ran_id=link_id).first()
    if link_data is None:
        return make_response("Not Found", 404)
    return make_response(jsonify({"viewCount": link_data.views}), 200)


if __name__ == '__main__':
    app.run(debug=True)
