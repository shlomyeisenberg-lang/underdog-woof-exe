# Underdog Woof — offline Windows EXE

A single `UnderdogWoof.exe` that runs [Underdog Woof](https://huggingface.co/ConwayResearch/Underdog-Woof)
text-to-speech fully offline. Python, numpy and both voices (Juno, Mira) are packed inside. No install, no internet.

## Use

- **Double-click** `UnderdogWoof.exe` → type text → **Speak** or **Save as WAV**.
- **Command line:**
  ```
  UnderdogWoof.exe --text "Your order ships on March 3rd." --out hello.wav --voice mira --seed 0
  ```

The first run takes a few seconds while Windows unpacks the bundled files.

## Build

GitHub Actions (`.github/workflows/build.yml`) downloads the model at build time on a Windows runner and
packs it with PyInstaller. The model weights are not stored in this repository.

## License

The model is © ConwayResearch / Underdog under the **Underdog Non-Commercial License 1.0**: personal,
research, teaching and non-profit use only, with credit. Commercial use needs a license from Underdog.
See the model card and the `LICENSE`/`NOTICE` files shipped next to the EXE.
