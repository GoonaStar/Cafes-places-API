from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
import random
app = Flask(__name__)

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

TopSecretApiKey = "1234f"

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/random")
def get_random_cafes():
    cafes = db.session.query(Cafe).all()
    chosen_cafe = random.choice(cafes)
    return jsonify(cafe=chosen_cafe.to_dict())

@app.route("/all")
def get_all():
    cafes = db.session.query(Cafe).all()
    all_cafes = [cafe.to_dict() for cafe in cafes]
    return jsonify(cafes=all_cafes)

@app.route("/search")
def get_cafe_at_location():
    loc_query = request.args.get("loc")
    cafe = Cafe.query.filter_by(location=loc_query).first()
    if cafe:
        return jsonify(cafe=cafe.to_dict())
    else:
        return jsonify(error="Sorry no cafe found at this location")

@app.route("/add", methods=["POST"])
def post_new_cafe():
    if request.args.get("api-key")==TopSecretApiKey:
        new_cafe = Cafe(
            name=request.form.get("name"),
            map_url=request.form.get("map_url"),
            img_url=request.form.get("img_url"),
            location=request.form.get("loc"),
            has_sockets=bool(request.form.get("sockets")),
            has_toilet=bool(request.form.get("toilet")),
            has_wifi=bool(request.form.get("wifi")),
            can_take_calls=bool(request.form.get("calls")),
            seats=request.form.get("seats"),
            coffee_price=request.form.get("coffee_price"),
        )
        db.session.add(new_cafe)
        db.session.commit()
        return jsonify(response="Successfully added to the database")
    else:
        return jsonify(response={"Forbidden": "unauthorized"}), 401

@app.route("/update-price/<int:cafe_id>", methods=["PATCH"])
def update_coffe_price(cafe_id):
    cafe_selected_db = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_selected_db:
        cafe_price = request.args.get("coffee_price")
        cafe_selected_db.coffee_price = cafe_price
        db.session.commit()
        return jsonify(response="Sucessfully updated")
    else:
        return jsonify(response="No cafe matching with this id")

@app.route("/report-closed/<cafe_id>", methods=["DELETE"])
def delete_cafe(cafe_id):
    cafe_to_delete = Cafe.query.filter_by(id=cafe_id).first()
    if cafe_to_delete:
        if request.args.get("api-key") == TopSecretApiKey:
            db.session.delete(cafe_to_delete)
            db.session.commit()
            return jsonify(response={"success": "Cafe successfully deleted"}), 200
        else:
            return jsonify(response={"Forbidden": "Unauthorized"}), 401
    else:
        return jsonify(response={"Not Found": "No cafe found with this id"}), 403




## HTTP GET - Read Record

## HTTP POST - Create Record


## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
