import sys
import tkinter as tk
from tkinter.ttk import Checkbutton

import ttkbootstrap as ttk
from ttkbootstrap import Style

from modules.command_controllers import GuiCommandController
from modules.commands.gui.bans import handle_ban, handle_list_bans, handle_unban
from modules.commands.gui.openai import handle_gpt3
from modules.commands.gui.state import handle_start, handle_stop
from modules.logs import get_logger
from modules.utils.path import resource_path

PROMPT_PLACEHOLDER = "Type your commands here... Or start with 'help' command"

gui_logger = get_logger("gui")
main_logger = get_logger("main")

command_controller = GuiCommandController()

command_controller.register_command("stop", handle_stop, "Start the bot.")
command_controller.register_command("start", handle_start, "Stop the bot.")
command_controller.register_command("ban", handle_ban, "Ban user by username. e.g ban <username>")
command_controller.register_command(
    "unban", handle_unban, "Unban user by username. e.g unban <username>"
)
command_controller.register_command("bans", handle_list_bans, "Show all banned players.")
command_controller.register_command(
    "gpt3", handle_gpt3, "Send a response to GPT3 model. e.g gpt3 <prompt>"
)
command_controller.register_command("quit", lambda *args: sys.exit(0), "Quit the program.")


class LogWindow(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.log_text = None
        self.cmd_line = None
        self.create_widgets()
        self.master.title("TF2-GPTChatBot")
        self.master.resizable(False, False)
        # self.master.iconbitmap(resource_path("icon.ico"))

        # Set the style to "simplex"
        style = Style(theme="cosmo")
        style.configure(".", font=("TkDefaultFont", 11), foreground="black")
        style.configure("TButton", padding=6, relief="flat")
        style.configure("TEntry", padding=6)
        style.configure("TFrame", background="white")

    def create_widgets(self):
        # Add a Text widget to the window for displaying logs
        self.log_text = ttk.Text(self, height=20, width=100, state="disabled")
        self.log_text.grid(row=0, column=0, padx=10, pady=10, columnspan=2)

        # Add another Text widget below the log_text widget for displaying additional text
        self.cmd_line = ttk.Text(self, height=1, width=89)
        self.cmd_line.grid(row=1, column=0, padx=10, pady=10)

        self.toggle_var = tk.BooleanVar(value=True)
        self.toggle_button = Checkbutton(
            self,
            text=" Stick \n Logs",
            variable=self.toggle_var,
            bootstyle="round-toggle",
            command=lambda: self.log_text.see(tk.END) if self.toggle_var.get() else None,
        )

        self.toggle_button.grid(row=1, column=1, padx=(0, 18))

        self.cmd_line.bind("<Return>", self.handle_commands)

        # Add a placeholder to the additional_text widget
        self.cmd_line.insert("1.0", PROMPT_PLACEHOLDER)

        # Binds to make the placeholder work
        self.cmd_line.bind("<FocusIn>", self.handle_additional_text_focus_in)
        self.cmd_line.bind("<FocusOut>", self.handle_additional_text_focus_out)

    def update_logs(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"{message}")
        self.log_text.config(state="disabled")
        if self.toggle_var.get():
            self.log_text.see(tk.END)  # Scroll to the end of the text widget

    def exit_program(self):
        self.master.destroy()

    def handle_commands(self, event):
        text = self.cmd_line.get("1.0", tk.END).strip()

        if text.strip == "":
            return

        gui_logger.info(f"> {text}")

        command_controller.process_line(text)

        # Clear the additional_text widget after the function is executed
        self.cmd_line.delete("1.0", tk.END)

    def handle_additional_text_focus_in(self, event):
        # Clear the placeholder text when the additional_text widget receives focus
        if self.cmd_line.get("1.0", tk.END).strip() == PROMPT_PLACEHOLDER:
            self.cmd_line.delete("1.0", tk.END)

    def handle_additional_text_focus_out(self, event):
        # Show the placeholder text when the additional_text widget loses focus and is empty
        if not self.cmd_line.get("1.0", tk.END).strip():
            self.cmd_line.insert("1.0", PROMPT_PLACEHOLDER)


class RedirectStdoutToLogWindow:
    def __init__(self, window: LogWindow):
        self.window = window

    def write(self, message):
        self.window.update_logs(message)

    def flush(self):
        ...
