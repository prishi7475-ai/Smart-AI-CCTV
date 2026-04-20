import os
import sys
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import threading
from PIL import Image, ImageTk

from camera_worker import start_ai_surveillance
from motion import noise
from rect_noise import rect_noise
from record import record
from in_out import in_out

from database import init_db, login_user, register_user
from camera_worker import set_current_user


init_db()

# ==================================================
# GLOBAL USER VARIABLE
# ==================================================
current_user_email = None


# ==================================================
# THREAD SAFE AI START
# ==================================================
def start_ai_thread():
    threading.Thread(target=start_ai_surveillance).start()


# ==================================================
# PYINSTALLER RESOURCE PATH
# ==================================================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


# ==================================================
# ICON LOADER
# ==================================================
def load_icon(name, size=(40, 40)):
    icon_path = resource_path(os.path.join("icons", name))
    img = Image.open(icon_path)
    img = img.resize(size, Image.Resampling.LANCZOS)
    return ImageTk.PhotoImage(img)


# ==================================================
# MAIN WINDOW
# ==================================================
window = tk.Tk()
window.title("Smart AI CCTV Pro")
window.geometry("1000x700")
window.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")

# ==================================================
# LOGIN FRAME
# ==================================================
login_frame = tk.Frame(window, bg="#1e1e1e")
login_frame.pack(fill="both", expand=True)

tk.Label(
    login_frame,
    text="Smart AI CCTV Pro",
    font=("Arial", 28, "bold"),
    fg="white",
    bg="#1e1e1e"
).pack(pady=30)

email_entry = tk.Entry(login_frame, font=("Arial", 14), width=30)
email_entry.pack(pady=10)
email_entry.insert(0, "Email")

password_entry = tk.Entry(login_frame, font=("Arial", 14), show="*", width=30)
password_entry.pack(pady=10)
password_entry.insert(0, "Password")


def attempt_login():
    global current_user_email
    email = email_entry.get()
    password = password_entry.get()

    user = login_user(email, password)
    if user:
        set_current_user(email)
        show_dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")


def attempt_register():
    email = email_entry.get()
    password = password_entry.get()

    if register_user(email, "", password):
        messagebox.showinfo("Success", "Registration Successful")
    else:
        messagebox.showerror("Error", "User already exists")


tk.Button(
    login_frame,
    text="Login",
    font=("Arial", 14),
    width=20,
    command=attempt_login
).pack(pady=10)

tk.Button(
    login_frame,
    text="Register",
    font=("Arial", 14),
    width=20,
    command=attempt_register
).pack(pady=5)


# ==================================================
# DASHBOARD FRAME
# ==================================================
dashboard_frame = tk.Frame(window, bg="#1e1e1e")


def show_dashboard():
    login_frame.pack_forget()
    dashboard_frame.pack(fill="both", expand=True)


tk.Label(
    dashboard_frame,
    text="Dashboard",
    font=("Arial", 26, "bold"),
    fg="white",
    bg="#1e1e1e"
).pack(pady=20)

button_frame = tk.Frame(dashboard_frame, bg="#1e1e1e")
button_frame.pack(pady=20)

buttons = [
    ("AI Surveillance", "spy.png", start_ai_thread),
    ("Motion Detect", "security-camera.png", noise),
    ("Region Motion", "rectangle-of-cutted-line-geometrical-shape.png", rect_noise),
    ("Record Video", "mn.png", record),
    ("In-Out Detect", "incognito.png", in_out),
    ("Logout", "exit.png", lambda: logout()),
]


def logout():
    dashboard_frame.pack_forget()
    login_frame.pack(fill="both", expand=True)


for i, (text, icon, cmd) in enumerate(buttons):
    img = load_icon(icon)
    btn = tk.Button(
        button_frame,
        text=text,
        image=img,
        compound="left",
        font=("Arial", 14),
        width=250,
        height=60,
        command=cmd
    )
    btn.image = img
    btn.grid(row=i // 2, column=i % 2, padx=20, pady=20)


# ==================================================
# START APP
# ==================================================
if __name__ == "__main__":
    window.mainloop()