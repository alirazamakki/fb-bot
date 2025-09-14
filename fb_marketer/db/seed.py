from __future__ import annotations

from sqlalchemy.orm import Session

from fb_marketer.db import SessionLocal, get_engine
from fb_marketer.db.init_db import init_db
from fb_marketer.db.models import Account, Group, Poster, Caption, Link
from fb_marketer.config import get_user_data_dir


def seed_demo() -> None:
    engine = get_engine()
    init_db(engine)
    with SessionLocal() as session:  # type: Session
        if session.query(Account).count() > 0:
            return
        default_profile_dir = (get_user_data_dir() / "profiles" / "demo_profile").as_posix()
        acc = Account(name="Demo Account", email_or_phone="demo@example.com", profile_path=default_profile_dir)
        session.add(acc)
        session.flush()

        g1 = Group(account_id=acc.id, fb_group_id="123", name="Demo Group 1", url="https://facebook.com/groups/demo1")
        g2 = Group(account_id=acc.id, fb_group_id="456", name="Demo Group 2", url="https://facebook.com/groups/demo2")
        session.add_all([g1, g2])

        p = Poster(filename="poster.png", filepath="/path/to/poster.png", category="default", tags=["demo"]) 
        c = Caption(text="Check this out: {LINK}", category="default", tags=["demo"]) 
        l1 = Link(url="https://example.com/a", category="default", weight=1)
        l2 = Link(url="https://example.com/b", category="default", weight=2)
        session.add_all([p, c, l1, l2])

        session.commit()


if __name__ == "__main__":
    seed_demo()

