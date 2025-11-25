import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import mysql.connector
from dataset_manager import refresh_dataset
from datetime import datetime
import csv
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import sys, os

def resource_path(filename):
    """Get absolute path to resource for PyInstaller."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)


# ----------------- Database Connection -----------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="System123@",
    database="phishguard_db"
)
cursor = db.cursor()

# ----------------- Logger -----------------
def log_event(event_type, description, source_module="AdminPanel", status="Success"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute(
        "INSERT INTO system_logs (event_type, description, source_module, status, timestamp) VALUES (%s, %s, %s, %s, %s)",
        (event_type, description, source_module, status, timestamp)
    )
    db.commit()

# ----------------- View Table Data -----------------
def view_table_data(table_name):
    for widget in data_frame.winfo_children():
        widget.destroy()

    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 1000")
        records = cursor.fetchall()

        if not records:
            messagebox.showinfo("Info", f"No records found in {table_name}")
            return

        columns = [desc[0] for desc in cursor.description]

        # Export to CSV Button
        export_btn = tk.Button(
            data_frame, text="Export to CSV",
            command=lambda: export_to_csv(table_name, records, columns),
            font=("Segoe UI", 10, "bold"), bg="#ff9800", fg="white",
            padx=10, pady=5
        )
        export_btn.pack(pady=5)

        # Scrollable Frame
        canvas = tk.Canvas(data_frame, bg="#1e1e1e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=canvas.yview, style="Vertical.TScrollbar")
        scrollable_frame = ttk.Frame(canvas, style="Dark.TFrame")

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Treeview
        tree = ttk.Treeview(scrollable_frame, columns=columns, show="headings", style="Dark.Treeview")
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150, anchor='w')
        for row in records:
            tree.insert("", "end", values=row)
        tree.pack(fill="both", expand=True)

    except Exception as e:
        messagebox.showerror("Error", f"Failed to load {table_name}:\n{str(e)}")

def export_to_csv(table_name, records, columns):
    with open(f"{table_name}_export.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(records)
    messagebox.showinfo("Exported", f"Data saved as {table_name}_export.csv")

# ----------------- Dataset Refresh -----------------
def refresh_data():
    try:
        refresh_dataset()
        log_event("Dataset Refresh", "Admin triggered dataset refresh.")
        messagebox.showinfo("Success", "Phishing dataset refreshed.")
    except Exception as e:
        log_event("Error", f"Dataset refresh failed: {str(e)}", status="Failed")
        messagebox.showerror("Error", f"Failed to refresh dataset.\n{str(e)}")

# ----------------- Feedback Chart -----------------
def show_feedback_chart():
    # Clear existing widgets
    for widget in data_frame.winfo_children():
        widget.destroy()
    
    try:
        cursor.execute("SELECT rating, COUNT(*) FROM user_feedback GROUP BY rating")
        results = cursor.fetchall()

        if not results:
            messagebox.showinfo("No Data", "No feedback found to generate chart.")
            return

        ratings = [str(r[0]) for r in results]
        counts = [r[1] for r in results]

        fig = plt.Figure(figsize=(7, 5), dpi=100)
        ax = fig.add_subplot(111)

        # Bar chart styling
        ax.bar(ratings, counts, color="#ff9800")
        ax.set_title("User Feedback Ratings", color="white", fontsize=14)
        ax.set_xlabel("Rating", color="white")
        ax.set_ylabel("Count", color="white")

        # Axis and spine color matching
        ax.set_facecolor('#1e1e1e')
        fig.patch.set_facecolor('#121212')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')
        for spine in ax.spines.values():
            spine.set_color('white')

        # Embedding in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=data_frame)
        canvas.draw()
        chart_widget = canvas.get_tk_widget()
        chart_widget.pack(fill="both", expand=True, padx=20, pady=20)

    except Exception as e:
        messagebox.showerror("Chart Error", f"Chart generation failed:\n{str(e)}")

# ----------------- GUI Setup -----------------
root = tk.Tk()
root.title("PhishGuard - Admin Panel")
root.geometry("1300x800")

# Background image
bg_img = Image.open(resource_path("bg(gui).jpg"))
bg_img = bg_img.resize((1300, 800), Image.LANCZOS)
bg_photo = ImageTk.PhotoImage(bg_img)

bg_label = tk.Label(root, image=bg_photo)
bg_label.place(x=0, y=0, relwidth=1, relheight=1)

# Overlay
overlay = tk.Frame(root, bg="#121212", bd=0)
overlay.place(relx=0, rely=0, relwidth=1, relheight=1)

# Header
header = tk.Label(overlay, text="PhishGuard Admin Panel", font=("Segoe UI", 24, "bold"),
                  bg="#121212", fg="#ffffff")
header.pack(pady=20)

# Button Frame
button_frame = tk.Frame(overlay, bg="#121212")
button_frame.pack(pady=10)

tables = [
    "phishing_dataset", "analyzed_urls",
    "user_urls", "chatbot_logs", "user_feedback",
    "system_logs"
]

for table in tables:
    btn = tk.Button(
        button_frame, text=f"View {table.replace('_', ' ').title()}",
        command=lambda t=table: view_table_data(t),
        font=("Segoe UI", 10, "bold"), bg="#4caf50", fg="white",
        padx=10, pady=5
    )
    btn.pack(side="left", padx=5)

# Extra Buttons (Refresh & Chart)
extra_btn_frame = tk.Frame(overlay, bg="#121212")
extra_btn_frame.pack(pady=10)

refresh_btn = tk.Button(
    extra_btn_frame, text="Refresh Phishing Dataset", command=refresh_data,
    font=("Segoe UI", 11, "bold"), bg="#2196f3", fg="white",
    padx=15, pady=8
)
refresh_btn.pack(side="left", padx=10)

# Button to show feedback chart (still present)
feedback_chart_btn = tk.Button(
    extra_btn_frame, text="Show Feedback Chart", command=show_feedback_chart,
    font=("Segoe UI", 11, "bold"), bg="#ff5722", fg="white",
    padx=15, pady=8
)
feedback_chart_btn.pack(side="left", padx=10)

# Data Display Frame
data_frame = tk.Frame(overlay, bg="#1e1e1e")
data_frame.pack(fill="both", expand=True, padx=20, pady=20)

# ----------------- Show Feedback Chart on Opening -----------------
show_feedback_chart()  # Call to display the feedback chart as soon as the admin panel opens

# Table layout using pack with expand and fill
table_frame = tk.Frame(data_frame, bg="#1e1e1e")
table_frame.pack(fill="both", expand=True)

# Create a Treeview for each table
treeviews = {}
for table in tables:
    treeview = ttk.Treeview(table_frame, columns=("Column 1", "Column 2", "Column 3"))
    treeview.pack(fill="both", expand=True, side="top", padx=5, pady=5)

    # Add some dummy data for the example
    treeview.insert("", "end", text="Row 1", values=("Data 1", "Data 2", "Data 3"))
    treeview.insert("", "end", text="Row 2", values=("Data 4", "Data 5", "Data 6"))
    
    # Store treeview references
    treeviews[table] = treeview

# ----------------- Treeview Styling -----------------
style = ttk.Style()
style.theme_use("clam")

style.configure("Dark.Treeview",
                background="#2e2e2e",
                foreground="white",
                fieldbackground="#2e2e2e",
                rowheight=25,
                font=("Segoe UI", 10))

style.configure("Dark.Treeview.Heading",
                background="#1f1f1f",
                foreground="white",
                font=("Segoe UI", 10, "bold"))

style.configure("Vertical.TScrollbar",
                gripcount=0,
                background="#2e2e2e",
                darkcolor="#1e1e1e",
                lightcolor="#1e1e1e",
                troughcolor="#1a1a1a",
                bordercolor="#1a1a1a",
                arrowcolor="#ffffff")

style.configure("Dark.TFrame", background="#1e1e1e")

root.mainloop()
