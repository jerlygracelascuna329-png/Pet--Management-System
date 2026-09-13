from flask import Flask, render_template, request, redirect, session, flash

app = Flask(__name__)
app.secret_key = "pet-secret-key"


# =========================
# USER CLASSES - POLYMORPHISM
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
# PET CLASS - ENCAPSULATION
# =========================

class Pet:
    def __init__(self, name, species, age, owner):
        self.__name = name
        self.__species = species
        self.__age = age
        self.__owner = owner

    # GETTERS
    def get_name(self):
        return self.__name

    def get_species(self):
        return self.__species

    def get_age(self):
        return self.__age

    def get_owner(self):
        return self.__owner

    # SETTERS
    def set_name(self, name):
        self.__name = name

    def set_species(self, species):
        self.__species = species

    def set_age(self, age):
        self.__age = age

    def set_owner(self, owner):
        self.__owner = owner


# =========================
# PET LIST
# =========================

pets = []


# =========================
# USERS
# =========================

users = [
    Admin("admin", "1234", "Admin"),
    Veterinarian("vet", "1234", "Veterinarian"),
    Receptionist("reception", "1234", "Receptionist")
]


# =========================
# LOGIN
# =========================

@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        for user in users:

            if user.username == username and user.password == password:

                session["username"] = user.username
                session["role"] = user.role
                session["dashboard_message"] = user.dashboard()

                return redirect("/dashboard")

        flash("Invalid username or password!")

    return render_template("login.html")


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
        dashboard_message=session["dashboard_message"]
    )


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    session.clear()
    flash("Logged out successfully!")

    return redirect("/")


# =========================
# PET RECORDS / ADD PET
# =========================

@app.route("/pets", methods=["GET", "POST"])
def pet_records():

    # Check if user is logged in
    if "username" not in session:
        return redirect("/")

    # ADD PET
    if request.method == "POST":

        # Only Admin and Receptionist can add
        if session["role"] not in ["Admin", "Receptionist"]:
            flash("You are not allowed to add pets.")
            return redirect("/pets")

        name = request.form["name"].strip()
        species = request.form["species"].strip()
        age = request.form["age"].strip()
        owner = request.form["owner"].strip()

        # Check empty fields
        if not name or not species or not age or not owner:
            flash("Please fill in all fields.")
            return redirect("/pets")

        # Check if age is a number
        if not age.isdigit():
            flash("Age must be a number.")
            return redirect("/pets")

        # Check if age is greater than 0
        if int(age) <= 0:
            flash("Age must be greater than 0.")
            return redirect("/pets")

        # Create Pet
        new_pet = Pet(name, species, age, owner)

        # Add to list
        pets.append(new_pet)

        flash("Pet added successfully!")

        return redirect("/pets")

    # DISPLAY PETS
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

    # Only Admin can delete
    if session["role"] != "Admin":
        flash("Only Admin can delete pets.")
        return redirect("/pets")

    # Check if pet exists
    if index < 0 or index >= len(pets):
        flash("Pet not found.")
        return redirect("/pets")

    # Delete pet
    pets.pop(index)

    flash("Pet deleted successfully!")

    return redirect("/pets")


# =========================
# UPDATE PET
# =========================

@app.route("/update/<int:index>", methods=["GET", "POST"])
def update_pet(index):

    if "username" not in session:
        return redirect("/")

    # All three roles can update
    if session["role"] not in ["Admin", "Veterinarian", "Receptionist"]:
        flash("Access Denied!")
        return redirect("/pets")

    # Check if pet exists
    if index < 0 or index >= len(pets):
        flash("Pet not found.")
        return redirect("/pets")

    pet = pets[index]

    # UPDATE PET
    if request.method == "POST":

        name = request.form["name"].strip()
        species = request.form["species"].strip()
        age = request.form["age"].strip()
        owner = request.form["owner"].strip()

        # Check empty fields
        if not name or not species or not age or not owner:
            flash("Please fill in all fields.")
            return redirect(f"/update/{index}")

        # Check if age is a number
        if not age.isdigit():
            flash("Age must be a number.")
            return redirect(f"/update/{index}")

        # Check if age is greater than 0
        if int(age) <= 0:
            flash("Age must be greater than 0.")
            return redirect(f"/update/{index}")

        # Update using setters
        pet.set_name(name)
        pet.set_species(species)
        pet.set_age(age)
        pet.set_owner(owner)

        flash("Pet updated successfully!")

        return redirect("/pets")

    # Show update page
    return render_template(
        "update_pet.html",
        pet=pet,
        index=index
    )


# =========================
# SEARCH PET
# =========================

@app.route("/search", methods=["GET", "POST"])
def search_pet():

    if "username" not in session:
        return redirect("/")

    search_result = []

    if request.method == "POST":

        search_name = request.form["search_name"].strip().lower()

        for pet in pets:

            if search_name in pet.get_name().lower():
                search_result.append(pet)

    return render_template(
        "search.html",
        pets=search_result,
        role=session["role"]
    )


# =========================
# RUN APP
# =========================

if __name__ == "__main__":
    app.run(debug=True)