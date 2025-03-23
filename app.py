from flask import Flask, request, redirect, url_for, render_template, session
from flask_sqlalchemy import SQLAlchemy  
from dotenv import load_dotenv
from models import db, User  
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import os
from dash import Dash, html, dcc, callback, Input, Output, page_container, page_registry, register_page
import dash_bootstrap_components as dbc
from flask_login import LoginManager, login_user, current_user





# load the environmnet varibales
load_dotenv()

app = Flask(__name__, static_folder="static")
app.secret_key = os.getenv("APP_SECRET_KEY")  # Required for flash messages



# MySQL Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Enable CORS for all routes
CORS(app, origins=["http://127.0.0.1:5000"])


db.init_app(app)  # Bind SQLAlchemy with the app
bcrypt = Bcrypt(app)

# Initialize the login manager
login_manager = LoginManager()
login_manager.init_app(app)



@app.route("/",  methods=["GET", "POST"])  
def default():
    return render_template("login.html")  



@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = None  
    if request.method == "POST":
        username_or_email = request.form.get("email")
        password = request.form.get("password")
        # Check if the username/email exists in the database
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()

        if user:
            if bcrypt.check_password_hash(user.password, password):
                # Successful login
                session['user_id'] = user.id  
                session['username'] = user.username  
                login_user(user)
                return redirect(url_for('home'))  
            else:
                error_message = "Incorrect password. Please try again."  
        else:
            error_message = "Username or email not found. Please try again."  

    return render_template("login.html", error_message=error_message)




@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        fname = request.form["first_name"]
        lname = request.form["last_name"]


        # Check if user already exists
        existing_user = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return redirect(url_for("register"))

        # Create new user and hash password
        new_user = User(username=username, email=email, first_name=fname, last_name=lname)
        new_user.set_password(password)  # Hash password before saving

        # Save to database
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))

    return render_template("register.html")  # Show registration form


@login_manager.user_loader
def load_user(user_id):
    # print("user id is : " , User.query.get(user_id))
    return User.query.get(user_id)  

@app.route('/home')
def home():
    print("Current user:", current_user)
    # print("current user is " , current_user.username)
    return redirect('/home/dashboard')  # Redirect to a specific Dash page


# Initialize Dash app
dash_app = Dash(
    __name__,
    server=app,
    external_stylesheets=[dbc.themes.BOOTSTRAP, "/assets/custom.css"],
    url_base_pathname="/home/",
    use_pages=True,
)

# Define the vertical navbar
navbar = dbc.Nav(
    [
        # App Name
        dbc.NavLink(
            "Budget Buddy",
            href="/home/dashboard",
            className="navbar-brand",
            style={
                "font-size": "1.5rem",
                "font-weight": "bold",
                "color": "#007BFF",
                "margin-bottom": "20px",
                "text-align": "center",
            },
        ),
        # Navigation Links
        dbc.NavLink(
            "Dashboard",
            href="/home/dashboard",
            active="exact",
            className="nav-link",
            style={"font-size": "1.1rem", "margin": "5px 0", "color": "black"},
        ),
        dbc.NavLink(
            "Generate Grants",
            href="/home/generate-grants",
            active="exact",
            className="nav-link",
            style={"font-size": "1.1rem", "margin": "5px 0", "color": "black"},
        ),
        dbc.NavLink(
            "Manage Grants",
            href="/home/manage-grants",
            active="exact",
            className="nav-link",
            style={"font-size": "1.1rem", "margin": "5px 0", "color": "black"},
        ),
        dbc.NavLink(
            "Settings",
            href="/home/settings",
            active="exact",
            className="nav-link",
            style={"font-size": "1.1rem", "margin": "5px 0", "color": "black"},
        ),
        dbc.NavLink(
            "Profile",
            href="/home/profile",
            active="exact",
            className="nav-link",
            style={"font-size": "1.1rem", "margin": "5px 0", "color": "black"},
        ),
        dbc.NavLink(
            "Logout",
            href="/home/logout",
            active="exact",
            className="nav-link",
            style={"font-size": "1.1rem", "margin": "5px 0", "color": "red"},
        ),
    ],
    vertical=True,
    pills=True,
    style={
        "background-color": "#f8f9fa",
        "padding": "0px 20px",
        "font-size" : "34px", 
        # "border-radius": "10px",
        # "box-shadow": "2px 2px 10px rgba(0, 0, 0, 0.1)",
    },
)

# Main layout
dash_app.layout = dbc.Container(
    children=[
        dcc.Location(id="url", refresh=True),
        dbc.Row(
            [
                # Sidebar Column
                dbc.Col(
                    [
                        navbar,
                    ],
                    width=2,
                    style={
                        "background-color": "#f8f9fa",
                        "height": "100vh",
                        "padding": "20px",
                        "color" : "red",
                        # f8f9fa
                    },
                ),
                # Main Content Column
                dbc.Col(
                    [
                        dbc.Alert(
                            [
                                html.Div(
                                    children=[
                                        html.H4("Dashboard", id="dash_app_heading")
                                    ],
                                    className="dash_app_heading",
                                )
                            ],
                            color="primary",
                            style={
                                "text-align": "left",
                                "font-size": "1.5rem",
                                "margin-bottom": "10px",
                                # "border-left": "2px solid black",
                                # "border-radius" : "8px",
                                "background-color" : "#f8f9fa",
                                "border" : "none",
                            },
                        ),
                        html.Div(
                            children=[page_container],
                            style={
                                "padding": "0px 10px 10px 10px",  # top, right, bottom, left
                            },
                        ),
                    ],
                    width=10,
                    style={"padding": "0px"},
                ),
            ]
        ),
    ],
    style={"min-width": "1400px"},
    fluid=True,
    className="main_body",
)

# Callback to update the heading based on the URL
@dash_app.callback(
    Output("dash_app_heading", "children"),  # Correct property to update
    Input("url", "pathname"),  # Correct input property
)
def change_dash_app_heading(url):
    if url == "/home/dashboard":
        return "Dashboard"
    elif url == "/home/generate-grants":
        return "Generate Grants"
    elif url == "/home/manage-grants":
        return "Manage Grants"
    elif url == "/home/settings":
        return "Settings"
    elif url == "/home/profile":
        return f"Hello {current_user.username.upper()}!"
    elif url == "/home/logout":
        return "Logout"
    return "Welcome!"  # Default message


if __name__ == "__main__":
    app.run(debug=True)
    with app.app_context():
        db.create_all()
