from flask import Flask, render_template, request, redirect, session, flash
import os

app = Flask(__name__)
app.secret_key = "petcare_super_secret_key_2024"


# =========================================================
# OOP: USER CLASSES (INHERITANCE & POLYMORPHISM)
# =========================================================

class User:
    """Parent Class demonstrating Inheritance & Polymorphism"""
    def __init__(self, username, password, role):
        self.username = username
        self.password = password
        self.role = role

    # Polymorphic methods - overridden by child classes
    def get_role_badge(self):
        return "👤 Standard User"

    def get_permissions_description(self):
        return "General system access"

    def can_manage_users(self):
        return False

    def can_delete_pets(self):
        return False

    def can_process_requests(self):
        return False

    def dashboard_message(self):
        return "Welcome to your PetCare portal."


class Admin(User):
    """Child Class: Administrator"""
    def __init__(self, username, password, role="Administrator"):
        super().__init__(username, password, role)

    # Polymorphism: Method Overriding
    def get_role_badge(self):
        return "👨‍💼 Administrator (Full Access)"

    def get_permissions_description(self):
        return "Full control: Manage pets, users, appointments, and requests"

    def can_manage_users(self):
        return True

    def can_delete_pets(self):
        return True

    def can_process_requests(self):
        return True

    def dashboard_message(self):
        return "Manage pets, users, appointments, and overall system records."


class Veterinarian(User):
    """Child Class: Staff / Veterinarian"""
    def __init__(self, username, password, role="Veterinarian"):
        super().__init__(username, password, role)

    # Polymorphism: Method Overriding
    def get_role_badge(self):
        return "🧑‍⚕️ Veterinarian (Staff)"

    def get_permissions_description(self):
        return "Operational access: View/Add/Edit pets, approve appointments, and process requests"

    def can_manage_users(self):
        return False

    def can_delete_pets(self):
        return False

    def can_process_requests(self):
        return True

    def dashboard_message(self):
        return "Manage pet records, approve appointments, and process medical requests."


class PetOwner(User):
    """Child Class: Client / Customer"""
    def __init__(self, username, password, role="Pet Owner"):
        super().__init__(username, password, role)

    # Polymorphism: Method Overriding
    def get_role_badge(self):
        return "🐾 Pet Owner (Client)"

    def get_permissions_description(self):
        return "Client access: View pet information, schedule appointments, and submit requests"

    def can_manage_users(self):
        return False

    def can_delete_pets(self):
        return False

    def can_process_requests(self):
        return False

    def dashboard_message(self):
        return "View your pet records, book appointments, and track your service requests."


# =========================================================
# OOP: PET CLASS (ENCAPSULATION)
# =========================================================

class Pet:
    """Demonstrates Encapsulation with private attributes and getters/setters"""
    def __init__(self, name, species, age, owner):
        self.__name = name
        self.__species = species
        self.__age = int(age)
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

    # SETTERS (with validation logic)
    def set_name(self, name):
        if not name or not name.strip():
            raise ValueError("Pet name cannot be empty.")
        self.__name = name.strip()

    def set_species(self, species):
        if not species or not species.strip():
            raise ValueError("Species cannot be empty.")
        self.__species = species.strip()

    def set_age(self, age):
        val = int(age)
        if val < 0:
            raise ValueError("Age cannot be negative.")
        self.__age = val

    def set_owner(self, owner):
        if not owner or not owner.strip():
            raise ValueError("Owner cannot be empty.")
        self.__owner = owner.strip()


# =========================================================
# APPOINTMENT & REQUEST CLASSES
# =========================================================

class Appointment:
    def __init__(self, client, pet, appointment_date, appointment_time, service, veterinarian, status="Pending"):
        self.client = client
        self.pet = pet
        self.appointment_date = appointment_date
        self.appointment_time = appointment_time
        self.service = service
        self.veterinarian = veterinarian
        self.status = status


class PetRequest:
    def __init__(self, client, pet, request_type, description, status="Pending", response=""):
        self.client = client
        self.pet = pet
        self.request_type = request_type
        self.description = description
        self.status = status
        self.response = response

    # Backward compatibility for templates using .owner
    @property
    def owner(self):
        return self.client


# =========================================================
# TEMPORARY IN-MEMORY STORAGE (PYTHON LISTS ONLY)
# =========================================================

users = [
    Admin("admin", "admin123", "Administrator"),
    Veterinarian("vet", "vet123", "Veterinarian"),
    PetOwner("owner", "owner123", "Pet Owner")
]

pets = [
    Pet("Buddy", "Dog", 3, "owner"),
    Pet("Milo", "Cat", 2, "owner"),
    Pet("Coco", "Dog", 4, "owner"),
    Pet("Luna", "Cat", 1, "owner")
]

appointments = [
    Appointment("owner", "Buddy", "2026-10-15", "09:00 AM", "General Check-up", "Dr. Veterinarian", "Pending"),
    Appointment("owner", "Milo", "2026-10-16", "11:00 AM", "Vaccination", "Dr. Veterinarian", "Approved")
]

requests_list = [
    PetRequest("owner", "Buddy", "Check-up", "Buddy seems lethargic and has not been eating well.", "Pending", ""),
    PetRequest("owner", "Luna", "Vaccination", "Annual anti-rabies booster shot request.", "Approved", "Appointment slot has been reserved.")
]


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_current_user_object():
    """Helper to retrieve the current logged-in user object demonstrating Polymorphism"""
    if "username" not in session:
        return None
    for u in users:
        if u.username == session["username"]:
            return u
    return None


@app.context_processor
def inject_user():
    """Makes current user object and role available in all templates"""
    user_obj = get_current_user_object()
    return {
        "current_user_obj": user_obj,
        "session_role": session.get("role", "")
    }


# =========================================================
# AUTHENTICATION (LOGIN / LOGOUT)
# =========================================================

@app.route("/", methods=["GET", "POST"])
def login():
    if "username" in session:
        return redirect("/dashboard")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if not username or not password:
            flash("Please enter both username and password.")
            return render_template("login.html")

        # Find user
        for user in users:
            if user.username == username and user.password == password:
                session["username"] = user.username
                session["role"] = user.role
                flash(f"Welcome back, {user.username}! Login successful.")
                return redirect("/dashboard")

        flash("Invalid username or password.")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.")
    return redirect("/")


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():
    if "username" not in session:
        flash("Please log in to access the dashboard.")
        return redirect("/")

    current_user = get_current_user_object()
    return render_template(
        "dashboard.html",
        username=session["username"],
        role=session["role"],
        current_user=current_user
    )


# =========================================================
# PET RECORDS (CRUD)
# =========================================================

@app.route("/pets", methods=["GET", "POST"])
def pet_records():
    if "username" not in session:
        return redirect("/")

    if request.method == "POST":
        if session["role"] not in ["Administrator", "Veterinarian"]:
            flash("Unauthorized: Only Admin and Veterinarian can add pets.")
            return redirect("/pets")

        name = request.form.get("name", "").strip()
        species = request.form.get("species", "").strip()
        age_str = request.form.get("age", "").strip()
        owner = request.form.get("owner", "").strip()

        if not name or not species or not age_str or not owner:
            flash("Please complete all fields.")
            return redirect("/pets")

        try:
            age = int(age_str)
            new_pet = Pet(name, species, age, owner)
            pets.append(new_pet)
            flash(f"Pet '{name}' added successfully!")
        except ValueError as e:
            flash(f"Error adding pet: {str(e)}")
        except Exception as e:
            flash(f"Unexpected error: {str(e)}")

        return redirect("/pets")

    return render_template(
        "pets.html",
        pets=pets,
        role=session["role"]
    )


@app.route("/add_pet", methods=["GET", "POST"])
def add_pet():
    if "username" not in session:
        return redirect("/")

    if session["role"] not in ["Administrator", "Veterinarian"]:
        flash("Unauthorized: Only Admin and Veterinarian can add pets.")
        return redirect("/pets")

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        species = request.form.get("species", "").strip()
        age_str = request.form.get("age", "").strip()
        owner = request.form.get("owner", "").strip()

        if not name or not species or not age_str or not owner:
            flash("Please complete all fields.")
            return redirect("/add_pet")

        try:
            age = int(age_str)
            new_pet = Pet(name, species, age, owner)
            pets.append(new_pet)
            flash(f"Pet '{name}' added successfully!")
            return redirect("/pets")
        except ValueError as e:
            flash(f"Invalid input: {str(e)}")
            return redirect("/add_pet")

    return render_template("add_pet.html")


@app.route("/edit_pet/<int:index>", methods=["GET", "POST"])
def edit_pet(index):
    if "username" not in session:
        return redirect("/")

    if session["role"] not in ["Administrator", "Veterinarian"]:
        flash("Unauthorized: Only Administrator and Veterinarian can edit pet records.")
        return redirect("/pets")

    if index < 0 or index >= len(pets):
        flash("Pet record not found.")
        return redirect("/pets")

    pet = pets[index]

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        species = request.form.get("species", "").strip()
        age_str = request.form.get("age", "").strip()
        owner = request.form.get("owner", "").strip()

        if not name or not species or not age_str or not owner:
            flash("Please complete all fields.")
            return redirect(f"/edit_pet/{index}")

        try:
            pet.set_name(name)
            pet.set_species(species)
            pet.set_age(age_str)
            pet.set_owner(owner)
            flash(f"Pet '{name}' updated successfully!")
            return redirect("/pets")
        except ValueError as e:
            flash(f"Update failed: {str(e)}")
            return redirect(f"/edit_pet/{index}")

    return render_template("edit_pet.html", pet=pet, index=index)


@app.route("/delete/<int:index>")
@app.route("/delete_pet/<int:index>")
def delete_pet(index):
    if "username" not in session:
        return redirect("/")

    # Only Admin can delete (Polymorphism verification)
    user_obj = get_current_user_object()
    if not user_obj or not user_obj.can_delete_pets():
        flash("Unauthorized: Only Administrator has permission to delete pets.")
        return redirect("/pets")

    try:
        deleted = pets.pop(index)
        flash(f"Pet '{deleted.get_name()}' deleted successfully.")
    except IndexError:
        flash("Pet record not found.")

    return redirect("/pets")


@app.route("/search", methods=["GET", "POST"])
def search():
    if "username" not in session:
        return redirect("/")

    results = []
    if request.method == "POST":
        keyword = request.form.get("keyword", "").lower().strip()
        if keyword:
            for pet in pets:
                if (keyword in pet.get_name().lower() or
                    keyword in pet.get_species().lower() or
                    keyword in pet.get_owner().lower()):
                    results.append(pet)

    return render_template(
        "search.html",
        pets=results,
        role=session["role"]
    )


# =========================================================
# USER MANAGEMENT (ADMINISTRATOR ONLY)
# =========================================================

@app.route("/users")
def manage_users():
    if "username" not in session:
        return redirect("/")

    user_obj = get_current_user_object()
    if not user_obj or not user_obj.can_manage_users():
        flash("Access restricted to Administrators only.")
        return redirect("/dashboard")

    return render_template("users.html", users=users, role=session["role"])


@app.route("/add_user", methods=["GET", "POST"])
def add_user():
    if "username" not in session:
        return redirect("/")

    user_obj = get_current_user_object()
    if not user_obj or not user_obj.can_manage_users():
        flash("Access restricted to Administrators only.")
        return redirect("/dashboard")

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip()

        if not username or not password or not role:
            flash("Please complete all fields.")
            return redirect("/add_user")

        for u in users:
            if u.username.lower() == username.lower():
                flash(f"Username '{username}' already exists. Please pick another.")
                return redirect("/add_user")

        if role == "Administrator":
            new_user = Admin(username, password, role)
        elif role == "Veterinarian":
            new_user = Veterinarian(username, password, role)
        else:
            new_user = PetOwner(username, password, "Pet Owner")

        users.append(new_user)
        flash(f"User '{username}' created successfully!")
        return redirect("/users")

    return render_template("add_user.html")


@app.route("/edit_user/<int:index>", methods=["GET", "POST"])
def edit_user(index):
    if "username" not in session:
        return redirect("/")

    user_obj = get_current_user_object()
    if not user_obj or not user_obj.can_manage_users():
        flash("Access restricted to Administrators only.")
        return redirect("/dashboard")

    if index < 0 or index >= len(users):
        flash("User not found.")
        return redirect("/users")

    target_user = users[index]

    if request.method == "POST":
        password = request.form.get("password", "").strip()
        role = request.form.get("role", "").strip()

        if not password or not role:
            flash("Please complete all fields.")
            return redirect(f"/edit_user/{index}")

        # Re-instantiate with appropriate subclass to maintain polymorphism
        uname = target_user.username
        if role == "Administrator":
            users[index] = Admin(uname, password, role)
        elif role == "Veterinarian":
            users[index] = Veterinarian(uname, password, role)
        else:
            users[index] = PetOwner(uname, password, "Pet Owner")

        flash(f"User '{uname}' updated successfully!")
        return redirect("/users")

    return render_template("edit_user.html", target_user=target_user, index=index)


@app.route("/delete_user/<int:index>")
def delete_user(index):
    if "username" not in session:
        return redirect("/")

    user_obj = get_current_user_object()
    if not user_obj or not user_obj.can_manage_users():
        flash("Access restricted to Administrators only.")
        return redirect("/dashboard")

    if index < 0 or index >= len(users):
        flash("User not found.")
        return redirect("/users")

    if users[index].username == session["username"]:
        flash("You cannot delete your currently logged in account!")
        return redirect("/users")

    deleted = users.pop(index)
    flash(f"User '{deleted.username}' deleted successfully.")
    return redirect("/users")


# =========================================================
# APPOINTMENTS (PURE PYTHON LIST STORAGE)
# =========================================================

@app.route("/appointments")
def manage_appointments():
    if "username" not in session:
        return redirect("/")

    role = session["role"]
    # Pass pairs of (actual_index, appointment) so Pet Owner links don't break
    indexed_appointments = list(enumerate(appointments))

    if role == "Pet Owner":
        filtered = [
            (idx, appt) for idx, appt in indexed_appointments
            if appt.client.lower() == session["username"].lower()
        ]
        return render_template("appointments.html", appointments=filtered, role=role, is_filtered=True)

    return render_template("appointments.html", appointments=indexed_appointments, role=role, is_filtered=False)


@app.route("/add_appointment", methods=["GET", "POST"])
def add_appointment():
    if "username" not in session:
        return redirect("/")

    if session["role"] != "Pet Owner":
        flash("Only Pet Owners can book appointments.")
        return redirect("/appointments")

    if request.method == "POST":
        client = session["username"]
        pet = request.form.get("pet", "").strip()
        appointment_date = request.form.get("appointment_date", "").strip()
        appointment_time = request.form.get("appointment_time", "").strip()
        service = request.form.get("service", "").strip()
        veterinarian = request.form.get("veterinarian", "").strip()

        if not pet or not appointment_date or not appointment_time or not service or not veterinarian:
            flash("Please complete all required fields.")
            return redirect("/add_appointment")

        # Conflict checking
        for existing in appointments:
            if existing.appointment_date == appointment_date and existing.appointment_time == appointment_time:
                flash("That time slot is already booked. Please choose another date or time.")
                return redirect("/add_appointment")

        new_appt = Appointment(
            client, pet, appointment_date, appointment_time, service, veterinarian, "Pending"
        )
        appointments.append(new_appt)
        flash("Appointment booked successfully! Awaiting review.")
        return redirect("/appointments")

    return render_template("add_appointment.html")


@app.route("/appointments/available-times")
def available_times():
    if "username" not in session:
        return {"booked_times": []}

    selected_date = request.args.get("date")
    booked = [appt.appointment_time for appt in appointments if appt.appointment_date == selected_date]
    return {"booked_times": booked}


@app.route("/edit_appointment/<int:index>", methods=["GET", "POST"])
def edit_appointment(index):
    if "username" not in session:
        return redirect("/")

    if index < 0 or index >= len(appointments):
        flash("Appointment not found.")
        return redirect("/appointments")

    appt = appointments[index]

    if session["role"] != "Pet Owner":
        flash("Only Pet Owners can edit appointments.")
        return redirect("/appointments")

    if appt.client.lower() != session["username"].lower():
        flash("You can only edit your own appointments.")
        return redirect("/appointments")

    if appt.status != "Pending":
        flash("Only pending appointments can be edited.")
        return redirect("/appointments")

    if request.method == "POST":
        pet = request.form.get("pet", "").strip()
        new_date = request.form.get("appointment_date", "").strip()
        new_time = request.form.get("appointment_time", "").strip()
        service = request.form.get("service", "").strip()
        veterinarian = request.form.get("veterinarian", "").strip()

        if not pet or not new_date or not new_time or not service or not veterinarian:
            flash("Please complete all required fields.")
            return redirect(f"/edit_appointment/{index}")

        # Check conflicting slot on other appointments
        for i, other in enumerate(appointments):
            if i != index and other.appointment_date == new_date and other.appointment_time == new_time:
                flash("That time slot is already taken by another appointment.")
                return redirect(f"/edit_appointment/{index}")

        appt.pet = pet
        appt.appointment_date = new_date
        appt.appointment_time = new_time
        appt.service = service
        appt.veterinarian = veterinarian

        flash("Appointment updated successfully!")
        return redirect("/appointments")

    return render_template("edit_appointment.html", appointment=appt, index=index)


@app.route("/process_appointment/<int:index>")
def process_appointment(index):
    if "username" not in session:
        return redirect("/")

    if session["role"] not in ["Administrator", "Veterinarian"]:
        flash("Unauthorized: Only Admin or Veterinarian can approve appointments.")
        return redirect("/appointments")

    if index < 0 or index >= len(appointments):
        flash("Appointment not found.")
        return redirect("/appointments")

    appointments[index].status = "Approved"
    flash(f"Appointment for '{appointments[index].pet}' approved successfully!")
    return redirect("/appointments")


@app.route("/delete_appointment/<int:index>")
def delete_appointment(index):
    if "username" not in session:
        return redirect("/")

    if session["role"] != "Administrator":
        flash("Only Administrators can cancel/remove appointments.")
        return redirect("/appointments")

    if 0 <= index < len(appointments):
        removed = appointments.pop(index)
        flash(f"Appointment for '{removed.pet}' was removed.")
    else:
        flash("Appointment not found.")

    return redirect("/appointments")


# =========================================================
# REQUESTS (CLIENT REQUESTS & APPROVALS)
# =========================================================

@app.route("/requests")
def view_requests():
    if "username" not in session:
        return redirect("/")

    role = session["role"]
    indexed_requests = list(enumerate(requests_list))

    if role == "Pet Owner":
        filtered = [
            (idx, req) for idx, req in indexed_requests
            if req.client.lower() == session["username"].lower()
        ]
        return render_template("requests.html", requests=filtered, role=role, is_filtered=True)

    return render_template("requests.html", requests=indexed_requests, role=role, is_filtered=False)


@app.route("/add_request", methods=["GET", "POST"])
def add_request():
    if "username" not in session:
        return redirect("/")

    if session["role"] != "Pet Owner":
        flash("Only Pet Owners can submit requests.")
        return redirect("/requests")

    if request.method == "POST":
        pet = request.form.get("pet", "").strip()
        request_type = request.form.get("request_type", "").strip()
        description = request.form.get("description", "").strip()

        if not pet or not request_type or not description:
            flash("Please complete all required fields (Pet Name, Request Type, Description).")
            return redirect("/add_request")

        new_req = PetRequest(session["username"], pet, request_type, description, "Pending", "")
        requests_list.append(new_req)
        flash("Request submitted successfully!")
        return redirect("/requests")

    return render_template(
        "add_request.html",
        role=session["role"],
        username=session["username"]
    )


@app.route("/process_request/<int:index>", methods=["GET", "POST"])
def process_request(index):
    if "username" not in session:
        return redirect("/")

    user_obj = get_current_user_object()
    if not user_obj or not user_obj.can_process_requests():
        flash("Unauthorized: Only Administrator and Veterinarian can process requests.")
        return redirect("/requests")

    if index < 0 or index >= len(requests_list):
        flash("Request not found.")
        return redirect("/requests")

    pet_req = requests_list[index]

    if request.method == "POST":
        status = request.form.get("status", "").strip()
        response_msg = request.form.get("response", "").strip()

        if status not in ["Pending", "Approved", "Completed", "Rejected"]:
            flash("Invalid status choice.")
            return redirect(f"/process_request/{index}")

        pet_req.status = status
        pet_req.response = response_msg
        flash(f"Request status updated to '{status}'!")
        return redirect("/requests")

    return render_template("process_request.html", pet_request=pet_req, index=index)


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":
    app.run(debug=True)