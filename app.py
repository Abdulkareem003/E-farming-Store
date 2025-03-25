from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import qrcode
import os
import joblib
import cv2
import base64
import numpy as np
import pandas as pd
from flask_mysqldb import MySQL
from flask_mail import Mail, Message  
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta  # For session expiration
from database import init_db, get_user_by_email, insert_user, store_order  # Import DB functions

app = Flask(__name__)
app.secret_key = "your_secret_key"

# ✅ Configure Flask Session
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.permanent_session_lifetime = timedelta(days=7)

# ✅ Initialize MySQL Database
init_db(app)

# ✅ Load Machine Learning Model & Vectorizer
model = joblib.load("model/medicinal_plant_model.pkl")
vectorizer = joblib.load("model/vectorizer.pkl")

# ✅ Load Plant Dataset
df = pd.read_csv("C:/Users/abdul/OneDrive/Desktop/medical plant/archive/Medicinal plant dataset.csv")

# ✅ Function to Get Plant Info
def get_plant_info(plant_name):
    plant_vectorized = vectorizer.transform([plant_name])
    prediction = model.predict(plant_vectorized)[0]

    plant_data = df[df["plant_name"].str.lower() == plant_name.lower()]
    image_path = plant_data.iloc[0]["image_path"] if not plant_data.empty else None

    img_base64 = None
    if image_path and os.path.exists(image_path):
        img = cv2.imread(image_path)
        _, buffer = cv2.imencode(".jpg", img)
        img_base64 = base64.b64encode(buffer).decode("utf-8")

    return {"plant_name": plant_name, "info": prediction, "image": img_base64}

# 🏠 Home Route
@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))

@app.route("/products")
def products():
    return render_template("products.html")

@app.route("/categories")
def categories():
    return render_template("categories.html")

@app.route("/feature")
def feature():
    return render_template("feature.html")

@app.route("/medical")
def medical():
    return render_template("medical.html")


# 📝 Signup Route
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if get_user_by_email(email):
            return "User already exists!"

        hashed_password = generate_password_hash(password)
        insert_user(email, hashed_password)

        return redirect(url_for("signin"))

    return render_template("signup.html")

# 🔑 Signin Route
@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = get_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            session.permanent = True  # ✅ Keeps user logged in
            session["user"] = user["email"]
            return redirect(url_for("profile"))  # ✅ Redirect to profile
        return "Invalid email or password"

    return render_template("signin.html")

# 👤 Profile Route
@app.route("/profile")
def profile():
    if "user" in session:
        return render_template("profile.html", user=session["user"])
    return redirect(url_for("signin"))

# 🚪 Logout Route
@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("signin"))

# ✅ Predict Route
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    plant_name = data.get("plant_name", "").strip()

    if not plant_name:
        return jsonify({"error": "No plant name provided"}), 400

    result = get_plant_info(plant_name)
    return jsonify(result)

@app.route("/add_to_cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()
    item = {
        "name": data["name"], 
        "price": data["price"], 
        "image": "images/" + data["image"]  # ✅ Store relative image path
    }

    if "cart" not in session:
        session["cart"] = []

    session["cart"].append(item)  # Append new product properly
    session.modified = True
    return jsonify({"message": f"{item['name']} added to cart!"})


@app.route("/remove_from_cart", methods=["POST"])
def remove_from_cart():
    data = request.get_json()
    product_name = data.get("name")

    if "cart" in session:
        for item in session["cart"]:
            if item["name"] == product_name:
                session["cart"].remove(item)
                break  # Remove only one occurrence
        session.modified = True

    return jsonify({"message": f"{product_name} removed from cart!"})


# ✅ Cart Route
@app.route("/cart")
def cart():
    print(session.get("cart"))  # Debugging: Print cart contents in the console
    return render_template("cart.html")

# ✅ MySQL Configuration
app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"  
app.config["MYSQL_PASSWORD"] = ""  
app.config["MYSQL_DB"] = "e_farming"
app.config["MYSQL_CURSORCLASS"] = "DictCursor"
mysql = MySQL(app)

# ✅ Email Configuration (Using Gmail SMTP)
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "theaktn1234@gmail.com"  # 🔹 Replace with your email
app.config["MAIL_PASSWORD"] = "nlentiiemoedrnnj"  # 🔹 Replace with your app password
mail = Mail(app)

# ✅ Checkout Route with Email Confirmation
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        email = request.form["email"]
        total = 500  # Example amount, you can calculate cart total

        # ✅ Store Order in Database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO orders (email, total_amount) VALUES (%s, %s)", (email, total))
        mysql.connection.commit()
        cursor.close()

        # ✅ Send Order Confirmation Email
        msg = Message("Order Confirmation - E-Farming Store", sender="your_email@gmail.com", recipients=[email])
        msg.body = f"Hello,\n\nYour order has been successfully placed! 🎉\nTotal Amount: ₹{total}\n\nThank you for shopping with us!\n\n- E-Farming Store"
        mail.send(msg)

        return "Order placed successfully! Confirmation email sent."

    return render_template("checkout.html", qr_path="static/images/upiQR.jpg")

if __name__ == "__main__":
    app.run(debug=True)
