# Institutional Engineering: A System Builder's Guide to Political Regimes

> What if political regimes are just operating systems—patched, legacy-coded, and always one update away from crashing?

This book is a collaborative writing project that rethinks political systems from the lens of system architecture and software engineering. Instead of judging regimes by ideology, we ask: why do some systems keep running, while others crash?

We focus on **non-Western political operating systems**—from Vietnam’s one-party pragmatism to India’s democratic chaos, from Iran’s theological virtual machine to Singapore’s performance-optimized firmware.

---

## ✍️ What This Project Is

- A longform book-in-progress, written jointly by human + AI.
- A hybrid of political science, systems thinking, and coding metaphors.
- An invitation to think like a systems engineer when analyzing states.

## 🧠 Who This Is For

- Technologists trying to understand politics without moral tribalism.
- Policy thinkers open to metaphors beyond ideology.
- Readers tired of “freedom vs tyranny” binaries.

---

## 🚀 How to Create This Book on GitHub

This project is managed like an open-source software repository. Here’s how to set it up and contribute.

### 1. Repository Structure

The book is organized into a clear directory structure. When creating your repo, follow this layout:

```
/
├── README.md                    # Project overview (this file)
├── book.json                    # GitBook configuration file
├── SUMMARY.md                   # The table of contents for the book
├── LICENSE                      # Copyright and usage license
├── .cursor/
│   └── rules/
│       └── worldview.mdc        # AI worldview and context
└── chapters/
    ├── chapter1.md              # Chapter 1
    └── chapter2.md              # Chapter 2
```

- **`book.json`**: Configures the title, author, and plugins for GitBook.
- **`SUMMARY.md`**: Defines the navigation and chapter order. Each new chapter `.md` file must be linked here.
- **`chapters/`**: Contains the content of the book, with each chapter as a separate Markdown file.

### 2. Creating a GitHub Book

To turn this repository into a readable online book, you can use tools like **GitBook** (legacy CLI) or modern alternatives like **HonKit**, **mdBook**, or simply publish it as a GitHub Pages site.

A typical workflow using a tool like HonKit would be:
1.  Install the tool: `npm install honkit -g`
2.  Serve the book locally: `honkit serve`
3.  Build the static site: `honkit build`
4.  Deploy the output to GitHub Pages.

### 3. AI Collaboration: Prompts & Methodology

To ensure the AI collaborator (like me) stays aligned with the project's unique "Institutional Engineering" perspective, we use a set of guiding prompts. These prompts frame the analysis in system-engineering terms.

**Master Prompt (`.cursor/rules/worldview.mdc`):**
The `worldview.mdc` file should contain the core concepts of "Institutional Engineering," defining terms like "Political OS," "legacy code," "fault tolerance," and the overall neutral, analytical tone.

**Example Prompts for Chapter Writing:**

Use these prompts to generate or co-write content with the AI:

**Prompt 1: System Architecture Analysis**
> "Analyze the political system of [Country Name] as if it were a legacy software platform. Describe its core architecture (e.g., monolith, microservices), its primary programming language (i.e., its cultural/historical context), its methods for error handling (e.g., protests, purges), and its update mechanism (e.g., reforms, revolutions). Maintain a neutral, engineering-focused tone."

**Prompt 2: Comparative System Review**
> "Compare the political operating systems of [Country A] and [Country B]. Frame the comparison using software engineering concepts. Which system has better fault tolerance? Which has a more efficient resource scheduler (i.e., economy)? Which is more likely to suffer from a kernel panic (i.e., regime collapse) and why?"

**Prompt 3: Crash Report Analysis**
> "Write a post-mortem analysis of the collapse of the political system in [Fallen Regime, e.g., the Soviet Union]. Frame it as a `crash.log` report. What was the root cause of the system failure? Was it a memory leak (e.g., economic unsustainability), a segmentation fault (e.g., ethnic separatism), or a critical bug in the kernel (e.g., a flawed succession mechanism)?"

---

## 🤝 How to Collaborate

This is not a traditional book project. It's a live system. We welcome Pull Requests, system bug reports, political insights, and structural critiques.

See `CONTRIBUTING.md` for how to participate.

---

## 📜 License

This work is licensed under the **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0)**. You are free to share and adapt this work for non-commercial purposes, provided you give appropriate credit and distribute your contributions under the same license.