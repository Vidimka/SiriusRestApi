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
    views = Column(Integer, nullable=False)


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
    if not request.json or 'url_to_shorten' not in request.json:
        make_response(400, "Bad request")
    link = request.json['url_to_shorten']
    random_id = str(uuid.uuid1())[0:8]
    new_link = "http:/localhost:5000/" + random_id
    write_link(random_id, link, new_link, 0)
    return jsonify({"status": "Created", "shortenedURL": new_link})


@app.get("/<link_id>")
def get_full_link(link_id):
    if len(link_id) == 0:
        make_response(404, "Not Found")
    filt = session.query(Link).filter_by(ran_id=link_id).first()
    if filt is not None:
        filt.views += 1
        session.commit()
        return redirect(filt.recieved_link, 301)
    return jsonify({"redirectTo": filt.recieved_link})


@app.get("/<link_id>/views")
def get_views(link_id):
    if len(link_id) == 0:
        make_response(404, "Not Found")
    filt2 = session.query(Link).filter_by(ran_id=link_id).first()
    if filt2 is not None:
        return jsonify({"viewCount": filt2.views})


if __name__ == '__main__':
    app.run(debug=True)
