from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

@app.route("/heroes")
def get_heroes():
    return jsonify([hero.to_dict() for hero in Hero.query.all()])

@app.route("/heroes/<int:id>")
def get_hero(id):
    hero = Hero.query.get(id)
    if hero:
        return jsonify(hero.to_dict())
    return jsonify({"error": "Hero not found"}), 404

@app.route("/powers")
def get_powers():
    return jsonify([power.to_dict() for power in Power.query.all()])

@app.route("/powers/<int:id>", methods=['GET', 'PATCH'])
def power_detail(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    if request.method == 'GET':
        return jsonify(power.to_dict())
    
    try:
        data = request.get_json()
        power.description = data.get("description", power.description)
        db.session.commit()
        return jsonify(power.to_dict())
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400

@app.route("/hero_powers", methods=["POST"])
def create_hero_power():
    try:
        data = request.get_json()
        hero_power = HeroPower(
            strength=data["strength"],
            hero_id=data["hero_id"],
            power_id=data["power_id"]
        )
        db.session.add(hero_power)
        db.session.commit()

        hero = Hero.query.get(hero_power.hero_id)
        power = Power.query.get(hero_power.power_id)
        return jsonify({
            "id": hero_power.id,
            "hero_id": hero.id,
            "power_id": power.id,
            "strength": hero_power.strength,
            "hero": {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name
            },
            "power": power.to_dict()
        })
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400
