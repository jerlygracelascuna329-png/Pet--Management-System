from flask import Flask, render_template, request, redirect, session, flash

app = Flask(__name__)

app.secret_key = "pet-secret-key"


# =========================
# USER CLASSES
# =========================

class User:

    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    def dashboard(self):
        return "User Dashboard"


class Admin(User):

    def dashboard(self):
        return "Admin Dashboard"


class Veterinarian(User):

    def dashboard(self):
        return "Veterinarian Dashboard"


class Receptionist(User):

    def dashboard(self):
        return "Receptionist Dashboard"


# =========================
# PET CLASS
# =========================

class Pet:

    def __init__(self, name, species, age, owner):
        self.__name = name
        self.__species = species
        self.__age = age
        self.__owner = owner

    # Getters

    def get_name(self):
        return self.__name

    def get_species(self):
        return self.__species

    def get_age(self):
        return self.__age

    def get_owner(self):
        return self.__owner

    # Setters

    def set_name(self, name):
        self.__name = name

    def set_species(self, species):
        self.__species = species

    def set_age(self, age):
        self.__age = age

    def set_owner(self, owner):
        self.__owner = owner


# =========================
# USERS
# =========================

users = [

    Admin(
        "admin",
        "1234",
        "Admin"
    ),

    Veterinarian(
        "vet",
        "1234",
        "Veterinarian"
    ),

    Receptionist(
        "reception",
        "1234",
        "Receptionist"
    )

]


# =========================
# PET RECORDS
# =========================

pets = [

    Pet(
        "Bantay",
        "Dog",
        3,
        "Juan"
    ),

    Pet(
        "Brownie",
        "Dog",
        2,
        "Pedro"
    ),

    Pet(
        "Max",
        "Dog",
        5,
        "Ana"
    ),

    Pet(
        "Mingming",
        "Cat",
        2,
        "Maria"
    ),

    Pet(
        "Mimi",
        "Cat",
        1,
        "Carlo"
    ),

    Pet(
        "Luna",
        "Cat",
        4,
        "Rosa"
    )

]


# =========================
# LOGIN
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]

        for user in users:

            if (
                user.username.lower() == username.lower()
                and user.password == password
            ):

                session["username"] = user.username
                session["role"] = user.role
                session["dashboard_message"] = user.dashboard()

                return redirect("/dashboard")

        flash("Invalid username or password.")

        return redirect("/")

    return render_template("login.html")


# =========================
# SIGN UP
# =========================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form["username"].strip()
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]

        # Check empty fields

        if not username or not password or not confirm_password:

            flash("Please fill in all fields.")

            return redirect("/signup")


        # Check password

        if password != confirm_password:

            flash("Passwords do not match.")

            return redirect("/signup")


        # Check existing username

        for user in users:

            if user.username.lower() == username.lower():

                flash("Username already exists!")

                return redirect("/signup")


        # New accounts are Receptionists

        new_user = Receptionist(
            username,
            password,
            "Receptionist"
        )

        users.append(new_user)


        flash(
            "Account created successfully! You can now log in."
        )

        return redirect("/")


    return render_template("signup.html")


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    if "username" not in session:

        return redirect("/")

    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        message=session.get("dashboard_message", "")
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()

    flash("You have been logged out.")

    return redirect("/")


# =========================
# ADD PET
# =========================

@app.route("/add_pet", methods=["GET", "POST"])
def add_pet():

    if "username" not in session:

        return redirect("/")


    role = session["role"]


    # Only Admin and Receptionist

    if role not in ["Admin", "Receptionist"]:

        flash(
            "You do not have permission to add pets."
        )

        return redirect("/dashboard")


    if request.method == "POST":

        name = request.form["name"].strip()
        species = request.form["species"].strip()
        age = request.form["age"]
        owner = request.form["owner"].strip()


        if not name or not species or not age or not owner:

            flash("Please fill in all fields.")

            return redirect("/add_pet")


        new_pet = Pet(
            name,
            species,
            int(age),
            owner
        )

        pets.append(new_pet)


        flash("Pet added successfully!")

        return redirect("/pets")


    return render_template("add_pet.html")


# =========================
# VIEW PETS
# =========================

@app.route("/pets")
def view_pets():

    if "username" not in session:

        return redirect("/")


    return render_template(
        "pets.html",
        pets=pets,
        role=session["role"]
    )


# =========================
# DELETE PET
# =========================

@app.route("/delete/<int:index>")
def delete_pet(index):

    if "username" not in session:

        return redirect("/")


    # Only Admin

    if session["role"] != "Admin":

        flash(
            "You do not have permission to delete pets."
        )

        return redirect("/pets")


    if 0 <= index < len(pets):

        pets.pop(index)

        flash("Pet deleted successfully.")


    return redirect("/pets")


# =========================
# UPDATE PET
# =========================

@app.route("/update/<int:index>", methods=["GET", "POST"])
def update_pet(index):

    if "username" not in session:

        return redirect("/")


    if index < 0 or index >= len(pets):

        flash("Pet not found.")

        return redirect("/pets")


    pet = pets[index]


    if request.method == "POST":

        name = request.form["name"].strip()
        species = request.form["species"].strip()
        age = request.form["age"]
        owner = request.form["owner"].strip()


        if not name or not species or not age or not owner:

            flash("Please fill in all fields.")

            return redirect(
                f"/update/{index}"
            )


        pet.set_name(name)

        pet.set_species(species)

        pet.set_age(int(age))

        pet.set_owner(owner)


        flash("Pet updated successfully!")

        return redirect("/pets")


    return render_template(
        "update_pet.html",
        pet=pet,
        index=index
    )


# =========================
# SEARCH PET
# =========================

@app.route("/search", methods=["GET", "POST"])
def search():

    if "username" not in session:

        return redirect("/")


    search_results = pets


    if request.method == "POST":

        query = request.form["query"].strip().lower()


        search_results = []


        for pet in pets:

            if (
                query in pet.get_name().lower()
                or query in pet.get_species().lower()
                or query in pet.get_owner().lower()
            ):

                search_results.append(pet)


    return render_template(
        "pets.html",
        pets=search_results,
        role=session["role"],
        search=True
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(debug=True)