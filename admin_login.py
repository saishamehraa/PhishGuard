import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import mysql.connector
import subprocess
import hashlib
import os

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="System123@",
    database="phishguard_db"
)
cursor = conn.cursor()

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Login function
def login():
    username = entry_username.get().strip()
    password = entry_password.get().strip()
    hashed_password = hash_password(password)  # Convert input to SHA-256

    # Query to fetch the hashed password from the database
    query = "SELECT password FROM admin WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()

    if result and result[0] == hashed_password:
        messagebox.showinfo("Login Success", "Welcome, Admin!")
        root.destroy()  # Close login window
        subprocess.Popen(["python", "admin_panel.py"])  # Open Admin Panel
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# Initialize Tkinter window
root = tk.Tk()
root.title("Admin Login")
root.attributes('-fullscreen', True)  # Fullscreen mode

# Check if background image exists
bg_path = "bg_admin.jpg"
if not os.path.exists(bg_path):
    messagebox.showerror("Error", "Background image not found!")

# Load and display background image
bg_image = Image.open(bg_path)
bg_image = bg_image.resize((root.winfo_screenwidth(), root.winfo_screenheight()), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_image)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(relwidth=1, relheight=1)

# Frame for centering elements
frame = tk.Frame(root, bg="black", padx=50, pady=50, bd=5)
frame.place(relx=0.5, rely=0.5, anchor="center")

# Title
tk.Label(frame, text="Admin Login", font=("Arial", 30, "bold"), bg="white").pack(pady=20)

# Username
tk.Label(frame, text="Username:", font=("Arial", 20), bg="white").pack()
entry_username = tk.Entry(frame, font=("Arial", 18), width=30)
entry_username.pack(pady=10)

# Password
tk.Label(frame, text="Password:", font=("Arial", 20), bg="white").pack()
entry_password = tk.Entry(frame, font=("Arial", 18), show="*", width=30)
entry_password.pack(pady=10)

# Login Button
tk.Button(frame, text="Login", font=("Arial", 20, "bold"), command=login, bg="green", fg="white", padx=20, pady=10).pack(pady=20)

# Exit Button
tk.Button(root, text="Exit", font=("Arial", 18), command=root.quit, bg="red", fg="white", padx=10, pady=5).place(relx=0.9, rely=0.05)

# Run main loop
root.mainloop()
