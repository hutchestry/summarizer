# Summarizer
This script creates a summary of browsing searches and using browsing history.

✅ Scans all major macOS browsers
✅ Merges visit/search data from all browsers into one timeline
✅ Google / Bing / DuckDuckGo / YouTube search detection
✅ Topic classification (AI, coding, news, shopping, etc.)
✅ Tag classification (Troubleshooting, Programming, Video, etc.)
✅ Daily Obsidian-friendly Markdown with YAML frontmatter
✅ Weekly merged Markdown summary

***

# Summarizer

Browser history summarizer for macOS. It aggregates Safari, Chrome, Brave, and Firefox history across all profiles, detects searches, classifies topics, generates daily and weekly Markdown summaries, and optionally syncs to an Obsidian vault.

---

## ✅ Features

* Multi-browser + multi-profile extraction
* Search detection (Google, DuckDuckGo, Bing, YouTube)
* Topic classification (AI, Coding, News, Shopping, Social, etc.)
* Tag classification (Troubleshooting, Programming, Research, Shopping, Video, etc.)
* Daily Markdown summaries
* Weekly merged summaries with:

  * Topic grouping
  * Domain statistics
  * Hourly histogram
* LLM-based tagger hook
* Obsidian vault integration
* CLI command via `summarizer`

---

## 📦 Installation

Clone your project directory and make sure the structure looks like:

```
project-root/
    summarizer/
        __init__.py
        extractors.py
        classify.py
        markdown_gen.py
        config.py
        utils.py
        main.py
    pyproject.toml
    README.md
```

Install in editable mode:

```bash
pip install -e .
```

---

## ▶️ Running the Summarizer

Once installed, the CLI entry point is available:

### Run once (daily + weekly)

```bash
summarizer
```

Or explicitly:

```bash
python -m summarizer.main
```

---

## 📂 Output Locations

By default:

```
~/browser-summaries/
    daily/
    weekly/
```

You can change these in `config.py`.

---

## 🗃 Obsidian Integration

To automatically sync summaries to an Obsidian vault:

1. Edit `config.py`:

```python
OBSIDIAN_VAULT = Path.home() / "Documents/Obsidian/MyVault"
SYNC_TO_OBSIDIAN = True
```

2. (Optional) Provide a daily note template:

```python
OBSIDIAN_DAILY_TEMPLATE = Path.home() / "Documents/Obsidian/Templates/Daily.md"
```

Daily files will be merged into the corresponding Obsidian daily note.
Weekly summaries will be copied to:

```
MyVault/Weekly/
```

---

## 🧠 LLM-Based Tagging (Optional)

You can inject a custom classifier:

```python
def my_llm_tagger(text, url, meta):
    # return list of tags based on model inference
    return ["AI", "DeepSearch"]

LLM_TAGGER = my_llm_tagger
```

Or external rules:

```python
EXTERNAL_TAGGER = lambda text, url, meta: ["CustomTag"]
```

---

## ⏱ Setting Up Automation (launchctl)

Create a LaunchAgent plist:

```
~/Library/LaunchAgents/com.user.summarizer.plist
```

Example plist:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.user.summarizer</string>

    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/project-root/summarizer/main.py</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key><integer>23</integer>
        <key>Minute</key><integer>55</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>/tmp/summarizer.out</string>

    <key>StandardErrorPath</key>
    <string>/tmp/summarizer.err</string>
</dict>
</plist>
```

Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.user.summarizer.plist
```

---

## 🧪 Testing

You can write tests using pytest:

```
tests/
    test_extractors.py
    test_classify.py
    test_markdown.py
```

Run tests:

```bash
pytest
```

---

## 📝 License

MIT License.

---

## ✅ Next Steps

If you'd like, I can also add:

* A richer CLI with subcommands (`summarizer daily`, `summarizer weekly`, etc.)
* A proper `tests/` suite scaffold
* A launchctl installer script
* A Homebrew formula to install via `brew install summarizer`
* A GUI wrapper using Swift or Python + PyObjC

