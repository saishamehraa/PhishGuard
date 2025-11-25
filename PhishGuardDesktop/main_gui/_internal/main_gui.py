import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
from chatbot_logic import chatbot_response, get_user_ip
from utils import normalize_url
import uuid
import subprocess
import sys, os
from chatbot_logger import log_chatbot_message, log_user_url, log_analyzed_url, log_user_feedback


# -------- RESOURCE PATH (For PyInstaller) ----------
def resource_path(filename):
    """Get absolute path for PyInstaller bundle"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, filename)
    return os.path.join(os.path.abspath("."), filename)



class ChatbotGUI:

    # -------- ADMIN BUTTON HANDLER ----------
    def open_admin_login(self):
        exe_name = "admin_login.exe"

        # Path changes depending on PyInstaller vs normal run
        if hasattr(sys, '_MEIPASS'):
            exe_path = os.path.join(os.path.dirname(sys.executable), exe_name)
        else:
            exe_path = os.path.join(os.getcwd(), exe_name)

        if os.path.exists(exe_path):
            subprocess.Popen([exe_path])
        else:
            from tkinter import messagebox
            messagebox.showerror("Error", f"{exe_name} not found!")



    # -------- GUI INITIALIZATION ----------
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Detection Chatbot")
        self.root.geometry("1280x720")
        self.root.configure(bg="black")

        self.user_id = str(uuid.uuid4())

        # Load Background Image
        try:
            image = Image.open(resource_path("bg_gui.jpg")).resize((1280, 720))
            self.bg_image = ImageTk.PhotoImage(image)
            self.bg_label = tk.Label(self.root, image=self.bg_image)
            self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
            print(f"Error loading background: {e}")
            self.root.configure(bg="#121212")

        # Chat area
        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, width=80, height=18,
            bg="#252525", fg="white", font=("Arial", 12), bd=3, relief="solid"
        )
        self.chat_area.place(relx=0.5, rely=0.48, anchor="center", width=800, height=400)
        self.chat_area.insert(tk.END, "Chatbot: Hello! Send me a URL to check if it's safe.\n")
        self.chat_area.config(state=tk.DISABLED)

        # Input field
        self.entry = tk.Entry(
            root, width=70, bg="#333333", fg="white",
            font=("Arial", 14), bd=3, relief="solid"
        )
        self.entry.place(relx=0.49, rely=0.80, anchor="center", height=40)
        self.entry.bind("<Return>", self.send_message)

        # Send button
        self.send_button = tk.Button(
            root, text="➤", command=self.send_message, bg="purple", fg="white",
            font=("Arial", 18, "bold"), padx=15, pady=5, bd=3, relief="raised"
        )
        self.send_button.place(relx=0.80, rely=0.80, anchor="center", height=40, width=50)

        # Exit button
        self.exit_button = tk.Button(
            root, text="Exit", command=self.root.quit, bg="red", fg="white",
            font=("Arial", 14, "bold"), padx=15, pady=5, bd=3, relief="raised"
        )
        self.exit_button.place(relx=0.05, rely=0.05, anchor="center")

        # -------- ADMIN BUTTON ----------
        self.admin_button = tk.Button(
            root, text="Admin", command=self.open_admin_login,
            bg="orange", fg="black",
            font=("Arial", 12, "bold"), padx=10, pady=5
        )
        self.admin_button.place(relx=0.95, rely=0.05, anchor="center")



    # -------- SEND MESSAGE ----------
    def send_message(self, event=None):
        user_input = self.entry.get().strip()
        if user_input:
            user_ip = get_user_ip()
            url = normalize_url(user_input)

            self.display_message("You", user_input, "lavender")

            response = chatbot_response(self.user_id, user_input, user_ip)
            self.display_message("Chatbot", response, "black")

            self.entry.delete(0, tk.END)
        else:
            self.display_message("Chatbot", "⚠️ Please enter a valid message or URL.", "red")



    # -------- DISPLAY MESSAGE ----------
    def display_message(self, sender, message, bg_color):
        self.chat_area.config(state=tk.NORMAL)
        tag_name = f"{sender}_tag"

        if tag_name not in self.chat_area.tag_names():
            self.chat_area.tag_config(
                tag_name,
                background=bg_color,
                foreground="black" if bg_color == "lavender" else "white",
                font=("Courier New", 12,
                      "bold" if sender == "You" else "italic"),
                lmargin1=20,
                lmargin2=20,
                rmargin=10,
                spacing1=5,
                spacing3=5,
            )

        self.chat_area.insert(tk.END, f"{sender}:\n", tag_name)
        self.chat_area.insert(tk.END, f"{message}\n\n", tag_name)
        self.chat_area.config(state=tk.DISABLED)
        self.chat_area.yview(tk.END)



# -------- MAIN LOOP ----------
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ChatbotGUI(root)
        print("🚀 GUI is launching...")
        root.mainloop()
    except Exception as e:
        print(f"Failed to launch GUI: {e}")
        input("Press Enter to exit...")