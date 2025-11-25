import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
import subprocess
import hashlib
import sys, os

# -----------------------------------------
# RESOURCE PATH (Fix for PyInstaller)
# -----------------------------------------
def resource_path(filename):
    """Get absolute path to resource for PyInstaller."""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)


# -----------------------------------------
# DATABASE CONNECTION (Safe)
# -----------------------------------------
try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="System123@",
        database="phishguard_db"
    )
    cursor = conn.cursor()
except Exception as e:
    cursor = None
    print("Database connection failed:", e)


# -----------------------------------------
# PASSWORD HASHER
# -----------------------------------------
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# -----------------------------------------
# LOGIN FUNCTION
# -----------------------------------------
def login():
    if cursor is None:
        messagebox.showerror("Database Error", "Cannot connect to database.")
        return

    username = entry_username.get().strip()
    password = entry_password.get().strip()
    hashed_password = hash_password(password)

    query = "SELECT password FROM admin WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    if result and result[0] == hashed_password:
        messagebox.showinfo("Login Success", "Welcome, Admin!")
        root.destroy()

        # Open admin panel EXE (not .py)
        exe_name = "admin_panel.exe"

        if hasattr(sys, "_MEIPASS"):
            exe_path = os.path.join(os.path.dirname(sys.executable), exe_name)
        else:
            exe_path = os.path.join(os.getcwd(), exe_name)

        if os.path.exists(exe_path):
            subprocess.Popen([exe_path])
        else:
            messagebox.showerror("Error", f"{exe_name} not found!")

    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")


# -----------------------------------------
# TKINTER GUI
# -----------------------------------------
root = tk.Tk()
root.title("Admin Login")
root.attributes('-fullscreen', True)

# Background Image
bg_path = resource_path("bg_admin.jpg")

if not os.path.exists(bg_path):
    messagebox.showerror("Error", "Background image not found!")

bg_image = Image.open(bg_path)
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Login Frame
frame = tk.Frame(root, bg="black", padx=50, pady=50, bd=5)
frame.place(relx=0.5, rely=0.5, anchor="center")

tk.Label(frame, text="Admin Login", font=("Arial", 30, "bold"), bg="white").pack(pady=20)

tk.Label(frame, text="Username:", font=("Arial", 20), bg="white").pack()
entry_username = tk.Entry(frame, font=("Arial", 18), width=30)
entry_username.pack(pady=10)

tk.Label(frame, text="Password:", font=("Arial", 20), bg="white").pack()
entry_password = tk.Entry(frame, font=("Arial", 18), show="*", width=30)
entry_password.pack(pady=10)

tk.Button(frame, text="Login", font=("Arial", 20, "bold"),
          command=login, bg="green", fg="white",
          padx=20, pady=10).pack(pady=20)

tk.Button(root, text="Exit", font=("Arial", 18),
          command=root.quit, bg="red", fg="white",
          padx=10, pady=5).place(relx=0.9, rely=0.05)

root.mainloop()