from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail, Message
from models import db, Hero, Power, HeroPower

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'your_email@gmail.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'


db.init_app(app)
migrate = Migrate(app, db)
mail = Mail(app)

# Routes

@app.route('/')
def index():
    return jsonify({"message": "Welcome to the Superheroes API!"})

# GET /heroes
@app.route('/heroes')
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([{
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name
    } for hero in heroes])


@app.route('/heroes/<int:id>')
def get_hero_by_id(id):
    hero = Hero.query.get(id)
    if not hero:
        return jsonify({"error": "Hero not found"}), 404

    return jsonify({
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": [{
            "id": hp.id,
            "hero_id": hp.hero_id,
            "power_id": hp.power_id,
            "strength": hp.strength,
            "power": {
                "id": hp.power.id,
                "name": hp.power.name
            }
        } for hp in hero.hero_powers]
    })


@app.route('/powers')
def get_powers():
    powers = Power.query.all()
    return jsonify([{
        "id": power.id,
        "name": power.name
    } for power in powers])


@app.route('/powers/<int:id>', methods=['GET', 'PATCH'])
def power_by_id(id):
    power = Power.query.get(id)
    if not power:
        return jsonify({"error": "Power not found"}), 404

    if request.method == 'GET':
        return jsonify({
            "id": power.id,
            "name": power.name
        })

    try:
        data = request.get_json()
        power.description = data['description']
        db.session.commit()
        return jsonify({
            "id": power.id,
            "name": power.name
        }), 200
    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400


@app.route('/hero_powers', methods=['POST'])
def create_hero_power():
    try:
        data = request.get_json()

        new_hero_power = HeroPower(
            strength=data['strength'],
            power_id=data['power_id'],
            hero_id=data['hero_id']
        )

        db.session.add(new_hero_power)
        db.session.commit()

        hero = Hero.query.get(data['hero_id'])
        power = Power.query.get(data['power_id'])

        return jsonify({
            "id": new_hero_power.id,
            "hero_id": hero.id,
            "power_id": power.id,
            "strength": new_hero_power.strength,
            "hero": {
                "id": hero.id,
                "name": hero.name,
                "super_name": hero.super_name
            },
            "power": {
                "id": power.id,
                "name": power.name
            }
        }), 201

    except Exception as e:
        return jsonify({"errors": [str(e)]}), 400


@app.route('/send_mail', methods=['POST'])
def send_email():
    data = request.get_json()
    try:
        msg = Message(
            subject=data.get('subject', 'Hello from Superheroes App'),
            sender=app.config['MAIL_USERNAME'],
            recipients=[data['recipient']],
            body=data.get('body', 'Welcome to the Superheroes app!')
        )
        mail.send(msg)
        return jsonify({"message": "Email sent successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
