<div align="center">

# Hex Forensics Analyzer

### Advanced Hex File Extractor & Builder

**Extract, analyze, and rebuild multiple files from raw hex data — built for digital forensics, malware analysis, and reverse engineering.**

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?logo=windows&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter-informational)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/Use-Educational%20%26%20Research-orange)

[Features](#features) •
[Screenshots](#screenshots) •
[Installation](#installation) •
[Usage](#usage) •
[How It Works](#how-it-works) •
[Project Structure](#project-structure) •
[Author](#author)

</div>

---

## Overview

**Hex Forensics Analyzer** is a desktop application that takes raw hexadecimal data — pasted directly or loaded from a text/hex file — and automatically locates, extracts, analyzes, and reconstructs the files hidden inside it.

It is designed for situations where several files are concatenated in a single hex stream, such as memory dumps, network captures, carved disk regions, or embedded payloads.

**Typical use cases**

| Field | Example |
|---|---|
| Malware Analysis | Extracting embedded executables or droppers from a hex payload |
| Digital Forensics | Carving files out of raw dumps during an investigation |
| File Recovery | Rebuilding files from partially damaged or mixed data |
| Reverse Engineering | Inspecting headers, trailers, and structure of unknown binaries |

---

## Features

### Smart Extraction Engine
- Cleans and validates raw hex input
- Detects file signatures and boundaries automatically
- Extracts **multiple files from a single hex stream**
- Tolerates corrupted or mixed data

### Supported File Types

| Category | Formats |
|---|---|
| Images | `JPG`, `PNG`, `BMP` |
| Executables | `EXE`, `DLL` |
| Documents | `PDF`, `TXT` |
| Media | `MP3`, `MP4`, `MOV` |

### Deep File Analysis
- Signature (magic bytes) detection
- Header and trailer inspection, with sizes and hex previews
- **MD5** hash for every extracted file
- Detailed per-file view (double-click any file in the list)
- Full hex data viewer

### Reconstruction & Export
- Rebuild all extracted files into an output folder
- Save each file's raw hex
- Export a complete **JSON extraction report**

### Modern Desktop GUI
- Clean multi-tab interface: **Hex Input → Extracted Files → File Reconstruction**
- Real-time console log and progress bar
- Background processing, so the interface stays responsive
- Statistics panel and one-click *Clear All Data*

---

## Screenshots

> Add your screenshots to `docs/screenshots/` and keep the paths below.

<div align="center">

![Main Window](docs/screenshots/main.png)

</div>

---

## Installation

### Requirements
- **Python 3.10** or newer
- **Windows** (the app uses Windows-specific features such as opening result folders automatically)
- Tkinter (included with the standard Python installer)

### 1. Clone the repository

```bash
git clone https://github.com/451646464/Hex-Forensics-Analyzer.git
cd Hex-Forensics-Analyzer
```

### 2. Create a virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python Hex_Bulding_GUI.py
```

---

## Usage

1. **Provide hex data**
   Open the **Hex Input** tab, then either paste hex data into the text area or load it from a `.txt` / `.hex` file.
2. **Process**
   Click **Process Hex Data** (or**Load and Process File**). Watch progress in the console and progress bar.
3. **Review the results**
   The app jumps to **Extracted Files**, listing each file's ID, type, size, header/trailer preview, and signature. Double-click a file for full details, including its MD5 hash.
4. **Rebuild and export**
   In **File Reconstruction**, choose an output directory and:
   - **Rebuild All Files** — write the reconstructed files to disk
   - **Save Hex Files** — save each file's hex representation
   - **Save Extraction Report** — export everything as JSON

---

## How It Works

```
 Raw Hex Input
      │
      ▼
 ┌──────────────┐   ┌────────────────────┐   ┌──────────────────┐
 │ Clean &      │ → │ Detect signatures  │ → │ Extract file     │
 │ validate hex │   │ & file boundaries  │   │ segments         │
 └──────────────┘   └────────────────────┘   └──────────────────┘
                                                      │
                                                      ▼
 ┌──────────────┐   ┌────────────────────┐   ┌──────────────────┐
 │ Rebuild &    │ ← │ Report (JSON) &    │ ← │ Analyze header,  │
 │ save files   │   │ hex export         │   │ trailer, MD5     │
 └──────────────┘   └────────────────────┘   └──────────────────┘
```

---

## Project Structure

```
Hex-Forensics-Analyzer/
├── Hex_Bulding_GUI.py     # Tkinter desktop application (entry point)
├── Hex_Bulding.py         # Core engine: parsing, extraction, analysis, rebuilding
├── hex_config.json        # Configuration file
├── hex..py, hexr.py,
│   rakan.py               # Additional helper scripts
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

---

## Limitations

- Very large hex inputs can take longer to process.
- Encrypted or heavily obfuscated data may not be detected.
- Accuracy depends on the integrity of the input hex data.
- Currently targeted at Windows.

---

## Roadmap

- [ ] Cross-platform support (Linux / macOS)
- [ ] Support for more file signatures (ZIP, GIF, DOCX, ELF, …)
- [ ] Command-line interface for scripting and automation
- [ ] Additional hashes (SHA-1, SHA-256)

---

## Security & Responsible Use

This tool is intended **only** for educational purposes, authorized security research, and legitimate forensic work. Only analyze data you own or have explicit permission to examine. The author is not responsible for any misuse of this software.

---

## Contributing

Contributions, bug reports, and feature suggestions are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push the branch: `git push origin feature/your-feature`
5. Open a Pull Request

If you find this project useful, please consider giving it a star — it helps a lot.

---

## Author

<table>
  <tr>
    <td>
      <b>Rakan Al-Moliki (راكان المليكي)</b><br>
      Cybersecurity & Networks Graduate<br><br>
      Email: <a href="mailto:rakanalmoliki33@gmail.com">rakanalmoliki33@gmail.com</a><br>
      GitHub: <a href="https://github.com/451646464">github.com/451646464</a>
    </td>
  </tr>
</table>

---

## License

This project is provided for **educational and research purposes**. See the repository for license updates.

<div align="center">

Made by **Rakan Al-Moliki**

</div>
