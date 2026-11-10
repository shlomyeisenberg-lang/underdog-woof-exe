"""Underdog Woof - offline Windows app (GUI + command line).

GUI:  double-click UnderdogWoof.exe
CLI:  UnderdogWoof.exe --text "Your order ships on March 3rd." --out hello.wav [--voice mira] [--seed 0]
"""
import argparse
import os
import sys
import tempfile
import threading
import traceback


def _bundle_dir():
    # When frozen by PyInstaller, model files are unpacked to sys._MEIPASS.
    if getattr(sys, "frozen", False):
        return sys._MEIPASS
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "underdog-woof")


BUNDLE = _bundle_dir()
if BUNDLE not in sys.path:
    sys.path.insert(0, BUNDLE)

_models = {}


def get_model(voice):
    if voice not in _models:
        cwd = os.getcwd()
        os.chdir(BUNDLE)  # the runtime looks for its weights next to itself
        try:
            from underdog_woof import Woof
            _models[voice] = Woof(voice=voice)
        finally:
            os.chdir(cwd)
    return _models[voice]


def synth_to_file(text, out_path, voice="juno", seed=0, normalize=True):
    out_path = os.path.abspath(out_path)
    tts = get_model(voice)
    audio = tts(text, seed=seed) if normalize else tts(text, seed=seed, normalize=False)
    tts.save(out_path, audio)
    return out_path


def run_cli(argv):
    p = argparse.ArgumentParser(prog="UnderdogWoof")
    p.add_argument("--text", required=True)
    p.add_argument("--out", default="woof.wav")
    p.add_argument("--voice", default="juno", choices=["juno", "mira"])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-normalize", action="store_true")
    a = p.parse_args(argv)
    try:
        path = synth_to_file(a.text, a.out, a.voice, a.seed, not a.no_normalize)
        print("Saved", path)
        return 0
    except Exception:
        err = traceback.format_exc()
        with open(os.path.abspath(a.out) + ".error.txt", "w", encoding="utf-8") as f:
            f.write(err)
        print(err, file=sys.stderr)
        return 1


def run_gui():
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
    import winsound

    root = tk.Tk()
    root.title("Underdog Woof - Offline Text to Speech")
    root.geometry("640x420")
    root.minsize(480, 320)

    top = ttk.Frame(root, padding=10)
    top.pack(fill="both", expand=True)

    ttk.Label(top, text="Type English text to speak:").pack(anchor="w")
    txt = tk.Text(top, wrap="word", height=10, font=("Segoe UI", 11))
    txt.pack(fill="both", expand=True, pady=(4, 8))
    txt.insert("1.0", "Hi! Your order ships on March 3rd and costs $24.99.")

    row = ttk.Frame(top)
    row.pack(fill="x")
    ttk.Label(row, text="Voice:").pack(side="left")
    voice = tk.StringVar(value="juno")
    ttk.Combobox(row, textvariable=voice, values=["juno", "mira"], width=8,
                 state="readonly").pack(side="left", padx=(4, 12))
    ttk.Label(row, text="Seed:").pack(side="left")
    seed = tk.StringVar(value="0")
    ttk.Spinbox(row, from_=0, to=9999, textvariable=seed, width=6).pack(side="left", padx=(4, 12))

    status = tk.StringVar(value="Ready. Everything runs offline on this computer.")
    last = {"path": None}

    def work(save_to=None):
        text = txt.get("1.0", "end").strip()
        if not text:
            return
        buttons(False)
        status.set("Loading voice and generating speech...")

        def job():
            try:
                out = save_to or os.path.join(tempfile.gettempdir(), "underdog_woof_last.wav")
                synth_to_file(text, out, voice.get(), int(seed.get() or 0))
                last["path"] = out
                if save_to:
                    root.after(0, status.set, "Saved: " + out)
                else:
                    root.after(0, status.set, "Playing...")
                    winsound.PlaySound(out, winsound.SND_FILENAME)
                    root.after(0, status.set, "Done.")
            except Exception as e:
                root.after(0, messagebox.showerror, "Error", str(e) + "\n\n" + traceback.format_exc())
                root.after(0, status.set, "Error.")
            finally:
                root.after(0, buttons, True)

        threading.Thread(target=job, daemon=True).start()

    def speak():
        work()

    def save():
        path = filedialog.asksaveasfilename(defaultextension=".wav",
                                            filetypes=[("WAV audio", "*.wav")],
                                            initialfile="woof.wav")
        if path:
            work(path)

    btns = ttk.Frame(top)
    btns.pack(fill="x", pady=(8, 4))
    b1 = ttk.Button(btns, text="Speak", command=speak)
    b2 = ttk.Button(btns, text="Save as WAV...", command=save)
    b1.pack(side="left")
    b2.pack(side="left", padx=8)

    def buttons(on):
        for b in (b1, b2):
            b.state(["!disabled"] if on else ["disabled"])

    ttk.Label(top, textvariable=status, foreground="#555").pack(anchor="w", pady=(6, 0))
    ttk.Label(top, text="Underdog Woof by ConwayResearch - Non-commercial license. See LICENSE/NOTICE.",
              foreground="#888", font=("Segoe UI", 8)).pack(anchor="w")
    root.mainloop()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        sys.exit(run_cli(sys.argv[1:]))
    run_gui()
