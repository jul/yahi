from archery import mdict
from datetime import datetime as dt

from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from json import dump

Base = automap_base()
engine = create_engine("postgresql://jul@/trollo")
Base.prepare(autoload_with=engine)
Posts = Base.classes.posts
session = Session(engine)

hr = lambda ts: "%02d-%02d" % (ts.hour, ts.minute - ts.minute % 10)
date = lambda ts: ts.strftime("%Y-%m-%d")

dump(
    sum(
        mdict(
            by_type=mdict({ post.maybe_spam and "spam" or "ham" : 1 }),
            date_all = mdict({date(post.created_at) : 1}),
            hour_all = mdict({hr(post.created_at) : 1}),
            date_spam = mdict({date(post.created_at):
                0 if post.maybe_spam is None else post.maybe_spam}),
            hour_spam = mdict({hr(post.created_at):
                0 if post.maybe_spam is None else post.maybe_spam}),
            date_ham = mdict({date(post.created_at):
                0 if post.maybe_spam is None else not post.maybe_spam}),
            hour_ham = mdict({hr(post.created_at):
                0 if post.maybe_spam is None else not post.maybe_spam}),
            date_score = mdict({date(post.created_at) : post.score}),
            hour_score = mdict({hr(post.created_at) : post.score}),
        )
        for post in session.query(Posts).all()
    ),
    open("data.js", "w"),
    indent=4
)


