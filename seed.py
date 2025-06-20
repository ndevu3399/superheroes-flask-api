from app import app
from models import db, Hero, Power, HeroPower

with app.app_context():
    db.drop_all()
    db.create_all()

    hero1 = Hero(name="Kamala Khan", super_name="Ms. Marvel")
    hero2 = Hero(name="Gwen Stacy", super_name="Spider-Gwen")
    db.session.add_all([hero1, hero2])

    power1 = Power(name="super strength", description="gives the wielder super-human strengths")
    power2 = Power(name="flight", description="gives the wielder the ability to fly through the skies at supersonic speed")
    db.session.add_all([power1, power2])
    db.session.commit()

    hp = HeroPower(strength="Strong", hero_id=hero1.id, power_id=power2.id)
    db.session.add(hp)
    db.session.commit()
