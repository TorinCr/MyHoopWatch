from app import db, create_app
from app.models import Player, Positions, PlayerRankings

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    pg = Positions(name="PG")
    sg = Positions(name="SG")
    sf = Positions(name="SF")
    pf = Positions(name="PF")
    c = Positions(name="C")

    db.session.add_all([pg, sg, sf, pf, c])
    db.session.commit()

    player1 = Player(
        name="John Smith",
        position="PG",
        graduation_year=2025,
        height="6'4",
        weight=190,
        state="TX",
        committed_to="Duke",
        highlights_url="https://www.youtube.com/watch?v=example1"
    )
    player1.positions.extend([pg, sg])

    player2 = Player(
        name="Malik Johnson",
        position="PF",
        graduation_year=2024,
        height="6'9",
        weight=220,
        state="CA",
        committed_to="Undecided",
        highlights_url="https://www.youtube.com/watch?v=example2"
    )

    player2.positions.append(pf)

    db.session.add_all([player1, player2])
    db.session.commit()

    ranking1 = PlayerRankings(player_id=player1.id, source="ESPN", rank=12)
    ranking2 = PlayerRankings(player_id=player1.id, source="247Sports", rank=10)
    ranking3 = PlayerRankings(player_id=player2.id, source="ESPN", rank=25)

    db.session.add_all([ranking1, ranking2, ranking3])
    db.session.commit()

    print("Seed data added.")