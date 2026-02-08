import asyncio
import os
import threading
from datetime import datetime
from tkinter import filedialog, messagebox

import customtkinter as ctk

from .core import CyberFind, OutputFormat, SearchMode

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class CyberFindGUI:
    def __init__(self, cyberfind: CyberFind = None):
        self.cyberfind = cyberfind or CyberFind()
        self.setup_window()
        self.build_ui()

    def setup_window(self):
        self.root = ctk.CTk()
        self.root.title("CyberFind")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)

    def build_ui(self):
        top_frame = ctk.CTkFrame(self.root)
        top_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(top_frame, text="Users (one per line):").pack(
            anchor="w", padx=5, pady=(0, 5)
        )
        self.users_text = ctk.CTkTextbox(top_frame, height=80, font=("Consolas", 12))
        self.users_text.pack(fill="x", padx=5, pady=(0, 10))

        settings_frame = ctk.CTkFrame(self.root)
        settings_frame.pack(fill="x", padx=10, pady=5)

        sites_label = ctk.CTkLabel(settings_frame, text="Sites file:")
        sites_label.pack(anchor="w", padx=5, pady=(5, 0))

        sites_entry_frame = ctk.CTkFrame(settings_frame, height=35)
        sites_entry_frame.pack(fill="x", padx=5, pady=(0, 5))

        self.sites_file = ctk.StringVar(value="")
        sites_entry = ctk.CTkEntry(
            sites_entry_frame, textvariable=self.sites_file, height=30
        )
        sites_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        browse_btn = ctk.CTkButton(
            sites_entry_frame,
            text="Browse",
            width=80,
            command=self.browse_sites,
            height=30,
        )
        browse_btn.pack(side="right")

        format_frame = ctk.CTkFrame(settings_frame)
        format_frame.pack(fill="x", padx=5, pady=5)

        ctk.CTkLabel(format_frame, text="Format:").pack(side="left", padx=5)
        self.output_format = ctk.StringVar(value="json")
        format_menu = ctk.CTkOptionMenu(
            format_frame,
            values=["json", "html", "csv", "txt"],
            variable=self.output_format,
            width=100,
        )
        format_menu.pack(side="left", padx=5)

        ctk.CTkLabel(format_frame, text="Mode:").pack(side="left", padx=(20, 5))
        self.search_mode = ctk.StringVar(value="standard")
        mode_menu = ctk.CTkOptionMenu(
            format_frame,
            values=["standard", "deep", "stealth", "aggressive"],
            variable=self.search_mode,
            width=120,
        )
        mode_menu.pack(side="left", padx=5)

        self.start_btn = ctk.CTkButton(
            self.root,
            text="Start Search",
            command=self.start_search,
            height=40,
            font=("Arial", 14, "bold"),
        )
        self.start_btn.pack(pady=10)

        self.log_text = ctk.CTkTextbox(self.root, font=("Consolas", 11))
        self.log_text.pack(fill="both", expand=True, padx=10, pady=10)

        self.status = ctk.StringVar(value="Ready")
        status_bar = ctk.CTkLabel(
            self.root, textvariable=self.status, anchor="w", font=("Arial", 10)
        )
        status_bar.pack(fill="x", padx=10, pady=(0, 5))

    def browse_sites(self):
        initial_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "..", "sites"
        )
        if not os.path.exists(initial_dir):
            initial_dir = os.path.dirname(os.path.abspath(__file__))

        file = filedialog.askopenfilename(
            title="Select sites file",
            initialdir=initial_dir,
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
        )
        if file:
            self.sites_file.set(file)

    def start_search(self):
        users = self.users_text.get("1.0", "end").strip().splitlines()
        users = [u.strip() for u in users if u.strip()]
        sites = self.sites_file.get().strip()

        if not users:
            messagebox.showerror("Error", "Enter at least one user")
            return
        if not sites and not os.path.exists("sites"):
            messagebox.showerror(
                "Error", "Select sites file or create 'sites' folder with files"
            )
            return

        try:
            output_format = OutputFormat(self.output_format.get())
            search_mode = SearchMode(self.search_mode.get())
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid settings: {e}")
            return

        self.start_btn.configure(state="disabled")
        self.log_text.delete("1.0", "end")
        self.status.set("Search started...")

        threading.Thread(
            target=self.run_search,
            args=(users, sites if sites else None, output_format, search_mode),
            daemon=True,
        ).start()

    def run_search(
        self,
        users: list,
        sites_file: str,
        output_format: OutputFormat,
        search_mode: SearchMode,
    ):
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            results = loop.run_until_complete(
                self.cyberfind.search_async(
                    usernames=users,
                    sites_file=sites_file,
                    mode=search_mode,
                    output_format=output_format,
                    output_file=f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    max_concurrent=50,
                )
            )
            self.root.after(0, self.show_results, results)
            self.root.after(0, self.on_complete)
        except Exception as e:
            import traceback

            error_msg = f"{str(e)}\n\n{traceback.format_exc()}"
            self.root.after(0, self.on_error, error_msg)
        finally:
            try:
                loop.close()
            except Exception:
                pass

    def show_results(self, results: dict):
        if not results or "results" not in results:
            self.log_text.insert("end", "No results received\n")
            return

        self.log_text.insert("end", "=" * 60 + "\n")
        self.log_text.insert("end", "SEARCH RESULTS\n")
        self.log_text.insert("end", "=" * 60 + "\n\n")

        found_any = False
        for user, data in results["results"].items():
            self.log_text.insert("end", f"User: {user}\n")
            if data and "found" in data and data["found"]:
                self.log_text.insert("end", "FOUND:\n")
                for item in data["found"]:
                    if isinstance(item, dict) and "site" in item and "url" in item:
                        self.log_text.insert(
                            "end", f"  • {item['site']}: {item['url']}\n"
                        )
                found_any = True
            else:
                self.log_text.insert("end", "Not found\n")
            self.log_text.insert("end", "\n")

        if not found_any:
            self.log_text.insert("end", "Accounts not found on checked sites\n")

        if "statistics" in results:
            stats = results["statistics"]
            self.log_text.insert("end", "\nSTATISTICS:\n")
            self.log_text.insert("end", f"  Checks: {stats.get('total_checks', 0)}\n")
            self.log_text.insert("end", f"  Found: {stats.get('found_accounts', 0)}\n")
            self.log_text.insert("end", f"  Errors: {stats.get('errors', 0)}\n")

        self.log_text.see("end")

    def on_error(self, msg: str):
        messagebox.showerror("Error", f"Search failed:\n{msg[:500]}...")
        self.log_text.insert("end", f"\nERROR: {msg[:1000]}\n")
        self.status.set("Error")

    def on_complete(self):
        self.start_btn.configure(state="normal")
        self.status.set("Search completed")

    def run(self):
        self.root.mainloop()


def run_gui():
    cyberfind = CyberFind()
    app = CyberFindGUI(cyberfind)
    app.run()
