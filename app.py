from flask import Flask, render_template, request, redirect, session, jsonify
from models import db, User, Expense, Budget, Venue
from chatbot import final_answer
from dotenv import load_dotenv
import os, requests, random
from models import Review
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

# ================= HOME =================
@app.route("/")
def home():

    return redirect("/login")
# ================= LOGIN =================
@app.route("/login", methods=["GET","POST"])

def login():

    if request.method == "POST":

        username = request.form["username"]

        password = request.form["password"]

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session["user"] = user.username

            session["role"] = user.role

            # 🔥 REDIRECT BASED ON ROLE
            if user.role == "owner":

                return redirect("/owner_dashboard")

            else:

                return redirect("/dashboard")

        else:

            return "Invalid Username or Password"

    return render_template("login.html")

# ================= REGISTER =================
@app.route("/register", methods=["GET","POST"])

def register():

    if request.method == "POST":

        new_user = User(

            username=request.form["username"],

            password=request.form["password"],

            role=request.form["role"]

        )

        db.session.add(new_user)

        db.session.commit()

        return redirect("/login")

    return render_template("register.html")


# ================= DASHBOARD =================
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/login")

    user = session.get("user")

    expenses = Expense.query.filter_by(user=user).all()

    budget_obj = Budget.query.filter_by(user=user).first()
    budget = budget_obj.total_budget if budget_obj else 0

    # 🔥 FIXED (safe values)
    planned = [e.planned_amount or 0 for e in expenses]
    actual = [e.actual_amount or 0 for e in expenses]
    categories = [e.category for e in expenses]

    return render_template(
        "dashboard.html",
        expenses=expenses,
        categories=categories,
        planned=planned,
        actual=actual,
        budget=budget
    )
    

# ================= owner DASHBOARD =================
@app.route("/owner_dashboard")
def owner_dashboard():

    user = session.get("user")

    venues = Venue.query.filter_by(owner=user).all()

    reviews = Review.query.all()

    return render_template(
        "owner_dashboard.html",
        venues=venues,
        reviews=reviews
    )
    
# ================= ADD EXPENSE =================
@app.route("/add_expense", methods=["POST"])
def add_expense():

    user = session.get("user")

    db.session.add(Expense(
        user=user,
        category=request.form.get("category"),
        planned_amount=float(request.form.get("planned")),
        actual_amount=float(request.form.get("actual"))
    ))

    db.session.commit()
    return redirect("/dashboard")


# ================= DELETE EXPENSE =================
@app.route("/delete_expense/<int:id>")
def delete_expense(id):

    exp = Expense.query.get(id)

    if exp:
        db.session.delete(exp)
        db.session.commit()

    return redirect("/dashboard")


# ================= UPDATE EXPENSE (FIXED) =================
@app.route("/update_expense", methods=["POST"])
def update_expense():

    exp = Expense.query.get(request.form.get("id"))

    if exp:
        exp.category = request.form.get("category")
        exp.planned_amount = float(request.form.get("planned"))
        exp.actual_amount = float(request.form.get("actual"))

        db.session.commit()

    return redirect("/dashboard")


# ================= CHATBOT (FIXED) =================
@app.route("/chatbot", methods=["POST"])
def chatbot():

    data = request.get_json()

    user = session.get("user")

    expenses = Expense.query.filter_by(user=user).all()

    # ✅ FIX
    budget_obj = Budget.query.filter_by(user=user).first()

    budget = budget_obj.total_budget if budget_obj else 0

    total = sum(e.actual_amount or 0 for e in expenses)

    details = "\n".join([
        f"{e.category}: Planned ₹{e.planned_amount}, Actual ₹{e.actual_amount}"
        for e in expenses
    ])
    venues = Venue.query.all()

    venue_text = "\n".join([

    f"""
       Venue Name: {v.name}
       Location: {v.location}
       Type: {v.type}
       Price: ₹{v.price}
       Price Type: {v.price_type}
       Rating: Available
       Google Maps:
       https://www.google.com/maps/search/?api=1&query={v.name}
    """

    for v in venues
])
    reply = final_answer(

    user_input=data.get("message"),

    budget=budget,

    details=details,

    venue_data=venue_text,

    lat=data.get("lat"),

    lng=data.get("lng")
)

    return jsonify({"reply": reply})



# ================= HAVERSINE =================
def haversine(lat1, lon1, lat2, lon2):

    R = 6371

    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)

    a = (
        math.sin(dLat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dLon / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return R * c


import math
import random
import requests
from flask import request, jsonify

@app.route("/venues", methods=["POST"])
def venues():

    data = request.get_json(silent=True) or {}

    search_place = data.get("search_place", "")

    selected_type = data.get("type")

    max_budget = data.get("budget")

    user_lat = data.get("user_lat")
    user_lng = data.get("user_lng")

    venue_lat = data.get("venue_lat")
    venue_lng = data.get("venue_lng")

    result = []

    # ================= GET OWNER VENUES =================

    all_venues = Venue.query.all()

    # ================= TYPE MAPPING =================

    type_mapping = {

        "hall": [
            "hall",
            "marriage hall",
            "wedding hall"
        ],

        "banquet": [
            "banquet",
            "banquet hall"
        ],

        "resort": [
            "resort",
            "wedding resort"
        ],

        "lawn": [
            "lawn",
            "event lawn"
        ]
    }

    # ================= FILTER OWNER VENUES =================

    if selected_type:

        filtered = []

        for v in all_venues:

            if not v.type:
                continue

            db_type = v.type.lower().strip()

            valid_types = type_mapping.get(
                selected_type.lower(),
                []
            )

            for t in valid_types:

                if t in db_type:

                    filtered.append(v)

                    break

        all_venues = filtered

    print("FILTERED OWNER VENUES:")

    for v in all_venues:

        print(
            v.name,
            v.type,
            v.lat,
            v.lng
        )

    # ================= OWNER VENUE LOOP =================

    for v in all_venues:

        # skip invalid coordinates
        if not v.lat or not v.lng:
            continue

        try:

            # distance from searched location
            search_distance = haversine(

                float(venue_lat),

                float(venue_lng),

                float(v.lat),

                float(v.lng)
            )

        except:
            continue

        print("OWNER:", v.name)
        print("SEARCH DISTANCE:", search_distance)

        # only nearby owner venues
        if search_distance > 15:
            continue

        # ================= BUDGET FILTER =================

        if max_budget:

            try:

                if float(v.price) > float(max_budget):
                    continue

            except:
                pass

        # ================= USER DISTANCE =================

        distance = 0

        if user_lat and user_lng:

            try:

                distance = haversine(

                    float(user_lat),

                    float(user_lng),

                    float(v.lat),

                    float(v.lng)
                )

            except:
                distance = 0

        # ================= REVIEWS =================

        reviews = Review.query.filter_by(
        venue_id=v.id
        ).all()

        avg_rating = 0
        latest_comment = "No reviews yet"

        if reviews:

             avg_rating = (
               sum(r.rating for r in reviews)
               / len(reviews)
        )

             latest_comment = reviews[-1].comment

        # ================= ADD OWNER VENUE =================

        result.append({

            "id": v.id,

            "name": v.name,

            "lat": v.lat,

            "lng": v.lng,

            "phone": v.phone,

            "email": v.email,

            "type": v.type,

            "price": v.price,

            "price_type": v.price_type,

            "rating": round(avg_rating, 1),

            "distance": round(distance, 2),
            
            "comment": latest_comment,

            "image": v.image,

            "link":
            f"https://www.google.com/maps/search/?api=1&query={v.lat},{v.lng}"
        })

    # ================= PUBLIC VENUES =================

    venue_types = [

        "wedding hall",

        "banquet hall",

        "marriage hall",

        "wedding resort",

        "event lawn"
    ]

    # ================= FILTER PUBLIC VENUES =================

    if selected_type:

        if selected_type == "resort":

            venue_types = ["wedding resort"]

        elif selected_type == "hall":

            venue_types = ["wedding hall"]

        elif selected_type == "banquet":

            venue_types = ["banquet hall"]

        elif selected_type == "lawn":

            venue_types = ["event lawn"]

    # ================= ADD PUBLIC VENUES =================

    for vtype in venue_types:

        search_query = f"{vtype} in {search_place}"

        link = (
            "https://www.google.com/maps/search/?api=1&query="
            + search_query.replace(" ", "+")
        )

        # nearby random markers
        marker_lat = float(venue_lat) + random.uniform(-0.02, 0.02)

        marker_lng = float(venue_lng) + random.uniform(-0.02, 0.02)

        distance = 0

        if user_lat and user_lng:

            distance = haversine(

                float(user_lat),

                float(user_lng),

                marker_lat,

                marker_lng
            )

        result.append({

            "id": random.randint(1000, 999999),

            "name":
            f"{vtype.title()} - {search_place.title()}",

            "lat": marker_lat,

            "lng": marker_lng,

            "type": vtype.title(),

            "price": "Not Available",

            "price_type": "Public Venue",

            "phone": "",

            "email": "",

            "rating": 0,

            "distance": round(distance, 2),

            "link": link
        })

    # ================= SORT =================

    result.sort(

        key=lambda x: (

            -x["rating"],

            x["distance"]
        )
    )

    print("FINAL RESULT:", result)

    return jsonify(result)

# ================= SET BUDGET =================
@app.route("/set_budget", methods=["POST"])
def set_budget():

    user = session.get("user")
    amount = float(request.form.get("budget"))

    existing = Budget.query.filter_by(user=user).first()

    if existing:
        existing.total_budget = amount
    else:
        db.session.add(Budget(user=user, total_budget=amount))

    db.session.commit()
    return redirect("/dashboard")


# ================= DELETE BUDGET =================
@app.route("/delete_budget")
def delete_budget():

    user = session.get("user")

    budget = Budget.query.filter_by(user=user).first()

    if budget:
        db.session.delete(budget)
        db.session.commit()

    return redirect("/dashboard")

# ================= add venue =================
@app.route("/add_venue", methods=["POST"])
def add_venue():
    import requests
    user = session.get("user")
    location_name = request.form["location"]
    

    location_name = request.form["location"]

    lat = None
    lng = None

    try:

        url = f"https://nominatim.openstreetmap.org/search?q={location_name}&format=json"

        response = requests.get(url).json()

        if response:

               lat = float(response[0]["lat"])
               lng = float(response[0]["lon"])

    except Exception as e:

        print("LOCATION ERROR:", e)

    

    # ===== SERVICES =====
    services = request.form.getlist("service_name")
    prices = request.form.getlist("service_price")

    service_data = []
    for s, p in zip(services, prices):
        if s and p:
            service_data.append(f"{s}:{p}")

    services_string = ",".join(service_data)

    # ===== IMAGE =====
    image = request.files.get("image")
    filename = ""

    if image and image.filename != "":
        filename = image.filename
        image.save("static/uploads/" + filename)
    id = request.form.get("id")
    if id:
        # ===== EDIT MODE =====
        v = Venue.query.get(id)

        v.name = request.form["name"]
        v.location = request.form["location"]
        v.type = request.form["type"]
        v.phone = request.form.get("phone")
        v.email = request.form.get("email")
        v.price_type = request.form["price_type"]
        v.price = float(request.form["price"])
        v.capacity = int(request.form["capacity"])
        v.services = services_string
        v.lat = lat
        v.lng = lng
        if filename:
            v.image = filename

    else:
        # ===== ADD MODE =====
        v = Venue(
            owner=user,
            name=request.form["name"],
            location=request.form["location"],
            type=request.form["type"],
            phone=request.form.get("phone"),
            email=request.form.get("email"),
            price=float(request.form["price"]),
            price_type=request.form["price_type"],
            capacity=int(request.form["capacity"]),
            services=services_string,
            image=filename,
            
            lat=lat,
            lng=lng
        )

        db.session.add(v)
    print("SAVED LAT:", lat)
    print("SAVED LNG:", lng)
    db.session.commit()

    return redirect("/owner_dashboard")


# ================= DELETE VENUE =================
@app.route("/delete_venue/<int:id>")
def delete_venue(id):

    v = Venue.query.get(id)

    if v:
        db.session.delete(v)
        db.session.commit()

    return redirect("/owner_dashboard")

# ================= logout  =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ================= review  =================

@app.route("/submit_review", methods=["POST"])
def submit_review():

    data = request.get_json()

    user = session.get("user")

    review = Review(

        user=user,

        venue_id=int(data["venue_id"]),

        rating=int(data["rating"]),

        comment=data["comment"]
    )

    db.session.add(review)

    db.session.commit()

    return jsonify({

        "message":"Review Added Successfully"
    })
# ================= Review =================
@app.route("/add_review", methods=["POST"])
def add_review():

    user = session.get("user")

    venue_id = request.form.get("venue_id")
    rating = int(request.form.get("rating"))
    comment = request.form.get("comment")

    db.session.add(Review(
        user=user,
        venue_id=venue_id,
        rating=rating,
        comment=comment
    ))

    db.session.commit()

    return redirect("/dashboard")

# ================= RUN =================
if __name__ == "__main__":
    app.run(debug=True)
