#!/usr/bin/env python3

import os
import sys
import io

# FIX pythonw stdout/stderr
if sys.stdout is None:
    sys.stdout = io.StringIO()
if sys.stderr is None:
    sys.stderr = io.StringIO()

import ttkbootstrap as tb
from ttkbootstrap.constants import *
import tkinter as tk
from tkinter import filedialog
import threading
import time
import subprocess
import multiprocessing
import shutil
import webbrowser

# -----------------------------
# GLOBAL STATE
# -----------------------------
is_running = False
timer_running = False

# -----------------------------
# PATH SETUP
# -----------------------------
if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INPUT_DIR = os.path.join(BASE_DIR, "input-files")
OUTPUT_DIR = os.path.join(BASE_DIR, "output-files")
GPTMULTI_PATH = os.path.join(BASE_DIR, "GPTmulti.py")

# -----------------------------
# APP SETUP
# -----------------------------
app = tb.Window(themename="flatly")
app.title("Grammar Checker Pipeline")
app.minsize(580, 420)

# -----------------------------
# ICON (SAME AS CRAFT)
# -----------------------------
def apply_icon():
    try:
        if getattr(sys, "frozen", False):
            base = os.path.dirname(sys.executable)
        else:
            base = os.path.dirname(os.path.abspath(__file__))

        data_dir = os.path.join(base, "app", "data")

        ico_path = os.path.normpath(os.path.join(data_dir, "icon.ico"))
        png_path = os.path.normpath(os.path.join(data_dir, "icon.png"))

        if os.name == "nt" and os.path.exists(ico_path):
            try:
                app.iconbitmap(ico_path)
            except Exception as e:
                print("⚠️ iconbitmap failed:", e)

        if os.path.exists(png_path):
            try:
                img = tk.PhotoImage(file=png_path)
                app.iconphoto(True, img)
                app._icon_ref = img
            except Exception as e:
                print("⚠️ iconphoto failed:", e)

    except Exception as e:
        print("❌ icon setup failed:", e)

app.after(100, apply_icon)

# -----------------------------
# SAFE UI HELPER
# -----------------------------
def safe_ui(func, *args, **kwargs):
    app.after(0, lambda: func(*args, **kwargs))

# -----------------------------
# API KEY
# -----------------------------
def ensure_api_key():

    import os
    import subprocess
    import platform

    # -----------------------------
    # 1. Already set?
    # -----------------------------
    key = os.getenv("OPENAI_API_KEY")
    if key:
        return True

    key_path = os.path.expanduser("~/.gptmulti_api_key")

    # -----------------------------
    # 2. Try loading from file
    # -----------------------------
    if os.path.exists(key_path):
        try:
            with open(key_path) as f:
                key = f.read().strip()
                if key:
                    os.environ["OPENAI_API_KEY"] = key
                    return True
        except:
            pass

    # -----------------------------
    # 3. Prompt user (your existing dialog)
    # -----------------------------
    dialog = tb.Toplevel(app)
    dialog.title("Setup API Key")
    dialog.geometry("500x300")

    frame = tb.Frame(dialog, padding=20)
    frame.pack(fill=BOTH, expand=YES)

    tb.Label(
        frame,
        text=(
            "An OpenAI API key is required.\n\n"
            "Create one here:"
        ),
        wraplength=440
    ).pack(anchor="w", pady=(0, 5))

    api_url = "https://platform.openai.com/api-keys"

    link = tb.Label(frame, text=api_url, foreground="#4A90E2", cursor="hand2")
    link.pack(anchor="w", pady=(0, 10))
    link.bind("<Button-1>", lambda e: webbrowser.open(api_url))

    entry_var = tk.StringVar()
    tb.Entry(frame, textvariable=entry_var).pack(fill=X)

    result = {"key": None}

    def submit():
        result["key"] = entry_var.get()
        dialog.destroy()

    tb.Button(frame, text="OK", command=submit, bootstyle="success").pack(pady=10)

    dialog.grab_set()
    dialog.wait_window()

    key = result["key"]

    if not key:
        return False

    key = key.strip().strip('"').strip("'")

    if not key:
        return False

    # -----------------------------
    # 4. Save locally (fallback)
    # -----------------------------
    try:
        with open(key_path, "w") as f:
            f.write(key)
        os.chmod(key_path, 0o600)
    except:
        pass

    # -----------------------------
    # 5. Set for current process
    # -----------------------------
    os.environ["OPENAI_API_KEY"] = key

    system = platform.system()

    # -----------------------------
    # 6. Persist globally
    # -----------------------------
    try:
        if system == "Windows":
            # user-level env var
            subprocess.run(
                ["setx", "OPENAI_API_KEY", key],
                shell=True
            )

        elif system == "Darwin":
            # macOS (zsh/bash profile)
            shell = os.environ.get("SHELL", "")

            if "zsh" in shell:
                rc_file = os.path.expanduser("~/.zshrc")
            else:
                rc_file = os.path.expanduser("~/.bashrc")

            line = f'\nexport OPENAI_API_KEY="{key}"\n'

            # avoid duplicates
            if os.path.exists(rc_file):
                with open(rc_file, "r") as f:
                    if "OPENAI_API_KEY" not in f.read():
                        with open(rc_file, "a") as f:
                            f.write(line)
            else:
                with open(rc_file, "w") as f:
                    f.write(line)

    except Exception as e:
        print("⚠️ Failed to persist API key:", e)

    return True

# -----------------------------
# LAYOUT
# -----------------------------
content = tb.Frame(app, padding=20)
content.pack(fill=BOTH, expand=YES)

bottom_bar = tb.Frame(app, padding=(20, 10))
bottom_bar.pack(fill=X)

# -----------------------------
# INFO TEXT
# -----------------------------
info_text = (
    "Grammar Checker Pipeline:\n"
    "This tool processes TSV files and runs automated grammar analysis using ChatGPT.\n\n"
    "Input format:\n"
    "- Tab Separated Value (TSV)\n"
    "- MUST include header row\n"
    "- Required columns: student_number, text\n"
)

tb.Label(content, text=info_text, justify=LEFT, wraplength=580).pack(anchor="w")

# -----------------------------
# EXAMPLE TABLE (WITH HEADERS)
# -----------------------------
tb.Label(content, text="Example (TSV with headers):").pack(anchor="w", pady=(10, 5))

table = tb.Frame(content)
table.pack(fill=X, pady=(0, 15))

def cell(parent, text, bold=False):
    return tb.Label(
        parent,
        text=text,
        borderwidth=1,
        relief="solid",
        padding=5,
        anchor="w",
        font=("Segoe UI", 10, "bold" if bold else "normal"),
        wraplength=400
    )

# Header
cell(table, "student_number", True).grid(row=0, column=0, sticky="nsew")
cell(table, "text", True).grid(row=0, column=1, sticky="nsew")

# Example row
cell(table, "N6MAA10816").grid(row=1, column=0, sticky="nsew")
cell(
    table,
    "I've seen things you people wouldn't believe. Attack ships on fire off the shoulder of Orion. I watched C-beams glitter in the dark near the Tannhäuser Gate. All those moments will be lost in time, like tears in rain."
).grid(row=1, column=1, sticky="nsew")

table.columnconfigure(0, weight=1)
table.columnconfigure(1, weight=3)

# -----------------------------
# FILE PICKER
# -----------------------------
file_var = tk.StringVar()

def browse():
    f = filedialog.askopenfilename(filetypes=[("TSV files", "*.tsv")])
    if f:
        file_var.set(f)

tb.Label(content, text="Input TSV:").pack(anchor="w")

row = tb.Frame(content)
row.pack(fill=X, pady=5)

tb.Entry(row, textvariable=file_var).pack(side=LEFT, fill=X, expand=YES)
tb.Button(row, text="Browse", command=browse).pack(side=RIGHT)

# -----------------------------
# STATUS
# -----------------------------
status_var = tk.StringVar(value="Idle")
timer_var = tk.StringVar(value="")

tb.Label(content, textvariable=status_var).pack(pady=(10, 0))
tb.Label(content, textvariable=timer_var).pack()

# -----------------------------
# PROGRESS
# -----------------------------
progress = tb.Progressbar(content, mode="indeterminate", bootstyle="info-striped")
progress.pack(fill=X, pady=10)

# -----------------------------
# TIMER
# -----------------------------
def update_timer(start):
    if not timer_running:
        return
    elapsed = int(time.time() - start)
    timer_var.set(f"Running... {elapsed}s")
    app.after(1000, update_timer, start)

# -----------------------------
# OPEN FILE
# -----------------------------
def open_file(path):
    if sys.platform == "darwin":
        subprocess.call(["open", path])
    elif os.name == "nt":
        os.startfile(path)
    else:
        subprocess.call(["xdg-open", path])

# -----------------------------
# RUN
# -----------------------------
def run_pipeline():

    global is_running, timer_running

    if is_running:
        return

    if not ensure_api_key():
        return

    f = file_var.get()

    if not f:
        status_var.set("❌ Select file")
        return

    # -----------------------------
    # PREP INPUT
    # -----------------------------
    base = os.path.splitext(os.path.basename(f))[0]

    if base.endswith("raw"):
        run_name = base[:-3]
        input_name = base + ".tsv"
    else:
        run_name = base
        input_name = base + "raw.tsv"

    input_path = os.path.join(INPUT_DIR, input_name)

    try:
        shutil.copy(f, input_path)
    except Exception as e:
        status_var.set(f"❌ Failed to copy input: {e}")
        return

    # -----------------------------
    # CREATE PLACEHOLDER
    # -----------------------------
    placeholder_path = os.path.join(
        OUTPUT_DIR,
        f"__placeholder_{int(time.time()*1000)}.tmp"
    )

    try:
        with open(placeholder_path, "w") as f:
            f.write("placeholder")
    except Exception as e:
        status_var.set(f"❌ Could not create placeholder: {e}")
        return

    placeholder_time = os.path.getmtime(placeholder_path)

    # -----------------------------
    # LOCK UI
    # -----------------------------
    is_running = True
    timer_running = True

    status_var.set("Running GPTmulti...")
    timer_var.set("")
    run_button.config(state="disabled")
    progress.start(10)

    app.update_idletasks()

    # -----------------------------
    # TASK THREAD
    # -----------------------------
    def task():
        global is_running, timer_running

        try:
            start = time.time()
            safe_ui(update_timer, start)

            # -----------------------------
            # RUN SUBPROCESS
            # -----------------------------
            python_exec = sys.executable or "python"
            cmd = [python_exec, "-u", GPTMULTI_PATH, run_name]

            proc = subprocess.Popen(
                cmd,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="ignore"
            )

            if proc.stdout:
                for line in proc.stdout:
                    line = line.strip()
                    if line:
                        safe_ui(status_var.set, line[:120])

            return_code = proc.wait()

            if return_code != 0:
                raise Exception(f"GPTmulti exited with code {return_code}")

            # -----------------------------
            # FIND NEWEST FILE AFTER PLACEHOLDER
            # -----------------------------
            safe_ui(status_var.set, "Locating output...")

            candidates = []

            for fname in os.listdir(OUTPUT_DIR):

                if not fname.endswith(".csv"):
                    continue

                if run_name not in fname:
                    continue

                full_path = os.path.join(OUTPUT_DIR, fname)

                try:
                    mtime = os.path.getmtime(full_path)
                except Exception:
                    continue

                if mtime > placeholder_time:
                    candidates.append((mtime, full_path))

            if not candidates:
                raise Exception("No new output file detected")

            found_file = max(candidates, key=lambda x: x[0])[1]

            # -----------------------------
            # OPEN RESULT
            # -----------------------------
            safe_ui(open_file, found_file)
            safe_ui(status_var.set, "✔ Done")

        except Exception as e:
            safe_ui(status_var.set, f"❌ {e}")

        finally:
            timer_running = False

            # cleanup placeholder
            try:
                if os.path.exists(placeholder_path):
                    os.remove(placeholder_path)
            except Exception:
                pass

            def cleanup():
                global is_running
                progress.stop()
                run_button.config(state="normal")
                is_running = False

            safe_ui(cleanup)

    # -----------------------------
    # START THREAD
    # -----------------------------
    threading.Thread(target=task, daemon=True).start()

# -----------------------------
# BUTTON
# -----------------------------
run_button = tb.Button(bottom_bar, text="Run", command=run_pipeline, bootstyle="success")
run_button.pack()

# -----------------------------
# START
# -----------------------------
if __name__ == "__main__":
    multiprocessing.freeze_support()
    app.mainloop()