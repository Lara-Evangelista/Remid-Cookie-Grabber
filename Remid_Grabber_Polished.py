import asyncio
import json
import os
import pyperclip
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from playwright.async_api import async_playwright

SAVE_FILE = os.path.join(os.path.expanduser("~"), ".remid_config.json")

def load_credentials():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as f:
            return json.load(f)
    return {"email": "", "password": ""}

def save_credentials(email, password):
    with open(SAVE_FILE, "w") as f:
        json.dump({"email": email, "password": password}, f)

async def get_remid(email, password, status_callback):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
        """)

        status_callback("Opening EA login page...")
        await page.goto("https://www.ea.com/login", wait_until="domcontentloaded")
        
        status_callback("Waiting for email field...")
        await page.wait_for_selector('input[id="email"]', timeout=20000)
        await asyncio.sleep(1.5)

        status_callback("Typing email...")
        await page.click('input[id="email"]')
        await page.type('input[id="email"]', email, delay=80)
        await asyncio.sleep(1)

        status_callback("Submitting email...")
        await page.keyboard.press("Enter")
        await asyncio.sleep(3)

        status_callback("Waiting for password field...")
        try:
            await page.wait_for_function("""
                () => {
                    const pwd = document.getElementById('password');
                    return pwd && pwd.offsetParent !== null;
                }
            """, timeout=15000)
        except:
            pass

        await asyncio.sleep(1)
        await page.evaluate("""
            const pwd = document.getElementById('password');
            if (pwd) {
                pwd.style.display = 'block';
                pwd.style.visibility = 'visible';
            }
        """)

        status_callback("Typing password...")
        await page.click('input[id="password"]')
        await page.type('input[id="password"]', password, delay=80)
        await asyncio.sleep(1)

        status_callback("Logging in...")
        await page.keyboard.press("Enter")

        status_callback("Handling interstitial pages...")
        for _ in range(8):
            await asyncio.sleep(2)
            current_url = page.url
            remind_later = page.locator('a:has-text("Remind me later"), button:has-text("Remind me later")')
            if await remind_later.count() > 0:
                status_callback("Dismissing email confirmation...")
                await remind_later.first.click()
                continue
            if "signin.ea.com" not in current_url:
                break

        await asyncio.sleep(2)
        status_callback("Grabbing remid cookie...")
        await page.goto("https://accounts.ea.com/connect", wait_until="domcontentloaded")
        await asyncio.sleep(2)

        all_cookies = await context.cookies()
        remid = next((c for c in all_cookies if c["name"] == "remid"), None)
        await browser.close()

        return remid["value"] if remid else None


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sims 4 Remid Grabber")
        self.resizable(False, False)
        self.configure(bg="#1a1a2e")
        self._center()
        self._build_ui()
        self._load()

    def _center(self):
        self.update_idletasks()
        w, h = 420, 340
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

    def _build_ui(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TEntry", fieldbackground="#16213e", foreground="white",
                        bordercolor="#0f3460", relief="flat", padding=6)
        style.configure("Accent.TButton", background="#0f3460", foreground="white",
                        font=("Segoe UI", 10, "bold"), borderwidth=0, padding=8)
        style.map("Accent.TButton", background=[("active", "#1a4a8a")])

        tk.Label(self, text="🎮 Sims 4 Remid Grabber", bg="#1a1a2e", fg="white",
                 font=("Segoe UI", 14, "bold")).pack(pady=(20, 4))
        tk.Label(self, text="Automatically grabs your remid cookie from EA",
                 bg="#1a1a2e", fg="#aaaaaa", font=("Segoe UI", 9)).pack(pady=(0, 20))

        frame = tk.Frame(self, bg="#1a1a2e")
        frame.pack(padx=30, fill="x")

        tk.Label(frame, text="EA Email", bg="#1a1a2e", fg="#cccccc",
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.email_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.email_var, width=40).pack(fill="x", pady=(2, 10))

        tk.Label(frame, text="EA Password", bg="#1a1a2e", fg="#cccccc",
                 font=("Segoe UI", 9)).pack(anchor="w")
        self.pass_var = tk.StringVar()
        ttk.Entry(frame, textvariable=self.pass_var, show="●", width=40).pack(fill="x", pady=(2, 10))

        self.status_var = tk.StringVar(value="Ready.")
        tk.Label(self, textvariable=self.status_var, bg="#1a1a2e", fg="#4fc3f7",
                 font=("Segoe UI", 9), wraplength=380).pack(pady=(6, 10))

        btn_frame = tk.Frame(self, bg="#1a1a2e")
        btn_frame.pack(pady=(0, 20))
        ttk.Button(btn_frame, text="Grab Remid Cookie", style="Accent.TButton",
                   command=self._run).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Clear Saved", style="Accent.TButton",
                   command=self._clear).pack(side="left", padx=6)

    def _load(self):
        creds = load_credentials()
        self.email_var.set(creds.get("email", ""))
        self.pass_var.set(creds.get("password", ""))

    def _clear(self):
        self.email_var.set("")
        self.pass_var.set("")
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        self.status_var.set("Credentials cleared.")

    def _run(self):
        email = self.email_var.get().strip()
        password = self.pass_var.get().strip()
        if not email or not password:
            messagebox.showerror("Missing info", "Please enter your email and password.")
            return
        save_credentials(email, password)
        self.status_var.set("Starting...")
        threading.Thread(target=self._run_async, args=(email, password), daemon=True).start()

    def _run_async(self, email, password):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(get_remid(email, password, self._set_status))
            if result:
                pyperclip.copy(result)
                with open("remid.txt", "w") as f:
                    f.write(result)
                self._set_status("Copied to clipboard! Paste into Sims 4 popup.")
            else:
                self._set_status("remid not found. Try again.")
        except Exception as e:
            self._set_status(f"Error: {str(e)}")
        finally:
            loop.close()

    def _set_status(self, msg):
        self.after(0, lambda: self.status_var.set(msg))


if __name__ == "__main__":
    app = App()
    app.mainloop()