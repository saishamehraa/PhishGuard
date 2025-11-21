import tkinter as tk
from tkinter import scrolledtext
from PIL import Image, ImageTk
from chatbot_logic import chatbot_response, get_user_ip
from utils import normalize_url
import uuid
from chatbot_logger import log_chatbot_message, log_user_url, log_analyzed_url, log_user_feedback


class ChatbotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Phishing Detection Chatbot")
        self.root.geometry("1280x720")
        self.root.configure(bg="black")

        self.user_id = str(uuid.uuid4())

        # Load Background Image
        try:
         image = Image.open("bg_gui.jpg").resize((1280, 720))
         self.bg_image = ImageTk.PhotoImage(image)
         self.bg_label = tk.Label(self.root, image=self.bg_image)
         self.bg_label.place(relwidth=1, relheight=1)
        except Exception as e:
         print(f"Error loading background: {e}")
        # Fallback to solid color if image fails
        self.root.configure(bg="#121212")

        # ✅ Opaque Chatbox with Better Readability
        self.chat_area = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, width=80, height=18,
            bg="#252525", fg="white", font=("Arial", 12), bd=3, relief="solid"
        )
        self.chat_area.place(relx=0.5, rely=0.48, anchor="center", width=800, height=400)
        self.chat_area.insert(tk.END, "Chatbot: Hello! Send me a URL to check if it's safe.\n")
        self.chat_area.config(state=tk.DISABLED)

        # ✅ Larger & Centered Input Field
        self.entry = tk.Entry(
            root, width=70, bg="#333333", fg="white",
            font=("Arial", 14), bd=3, relief="solid"
        )
        self.entry.place(relx=0.49, rely=0.80, anchor="center", height=40)
        self.entry.bind("<Return>", self.send_message)

        # ✅ Bigger Send Button
        self.send_button = tk.Button(
            root, text="➤", command=self.send_message, bg="purple", fg="white",
            font=("Arial", 18, "bold"), padx=15, pady=5, bd=3, relief="raised"
        )
        self.send_button.place(relx=0.80, rely=0.80, anchor="center", height=40, width=50)

        # ✅ Exit Button Fixed
        self.exit_button = tk.Button(
            root, text="Exit", command=self.root.quit, bg="red", fg="white",
            font=("Arial", 14, "bold"), padx=15, pady=5, bd=3, relief="raised"
        )
        self.exit_button.place(relx=0.05, rely=0.05, anchor="center")

    def send_message(self, event=None):
        user_input = self.entry.get().strip()
        if user_input:  # Only process non-empty input
            # Get the user's IP address
            user_ip = get_user_ip()
            
            # Normalize the URL if it's a URL input
            url = normalize_url(user_input)
            
            # Display the user's message in the chat window
            self.display_message("You", user_input, "lavender")
            
            # Call the chatbot_response with the user IP passed as an argument
            response = chatbot_response(self.user_id, user_input, user_ip)
            
            # Display the chatbot's response in the chat window
            self.display_message("Chatbot", response, "black")
            
            # Clear the input field after sending the message
            self.entry.delete(0, tk.END)
            
        else:
            self.display_message("Chatbot", "⚠️ Please enter a valid message or URL.", "red")

    def display_message(self, sender, message, bg_color):
        self.chat_area.config(state=tk.NORMAL)
        tag_name = f"{sender}_tag"

        if tag_name not in self.chat_area.tag_names():
            self.chat_area.tag_config(
                tag_name,
                background=bg_color,
                foreground="black" if bg_color == "lavender" else "white",
                font=("Courier New", 12, "bold" if sender == "You" else "italic"),
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

if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = ChatbotGUI(root)
        print("🚀 GUI is launching...")
        root.mainloop()
    except Exception as e:
        print(f"Failed to launch GUI: {e}")
        input("Press Enter to exit...")