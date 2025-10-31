
# OMORI Community Digital Ethnography
Dataset and Interactive Reader

This repository contains:
- omori_posts.json — a cleaned, JSON dataset of r/OMORI posts and first‑level comments filtered by a mental‑health keyword gate.
- index.html — an interactive, OMORI‑themed reader that renders the dataset for close reading.
- dataextraction.py — a PRAW-based script to (re)create the dataset from Reddit’s API.
- a series of media and UI assets (soundtrack mp3, font ttf, images/gifs). Optional for core use.

The project accompanies the article “Harnessing Computational Social Science: A Framework for Digital Ethnography of Online Communities” (Di Leo, 2025), which formalizes an auditable loop between automated discovery and interpretive reading.

---

## Quick start

- View the interactive reader
  - Recommended: serve files locally to avoid browser restrictions on fetch/file URLs.
  - From the repository root:
    - Python 3: `python -m http.server 8000`
    - Node: `npx http-server .`
  - Open http://localhost:8000/ and click index.html (or go directly to http://localhost:8000/index.html).
  - The reader loads omori_posts.json from the same folder by default.
  - Alternatively, simply visit [https://nadiadileo.github.io/Omori-Prototype/](https://nadiadileo.github.io/Omori-Prototype/) to access the publicly released version of the reader, hosted on Github Pages.

- Use a different dataset file
  - Place your JSON file alongside index.html and rename it to omori_posts.json, or
  - Edit index.html to point the fetch(...) call at your file’s name.

---

## What’s in the dataset?

Top‑level structure: an array of post objects. Each post contains metadata, full selftext, and an array of first‑level comments (no deeper nesting).

Minimal example (truncated):
```json
[
  {
    "id": "1jorbr8",
    "title": "There is nothing we can do..",
    "author": "user_7dd0fea51c57",
    "created_utc": 1743499132.0,
    "created_date": "2025-04-01 11:18:52",
    "score": 187,
    "upvote_ratio": 0.94,
    "num_comments": 26,
    "url": "https://i.redd.it/4qnb8rlyx6se1.png",
    "selftext": "Very Sad day for the Sunburn Shippers in this subreddit 😞",
    "is_self": false,
    "is_video": false,
    "link_flair_text": "Meme",
    "over_18": false,
    "spoiler": false,
    "comments": [
      {
        "id": "mktuqx4",
        "author": "user_7539a7047220",
        "body": "They are just holding hands, like brest friends would!\n\nAlso where is the Silkpost flair?",
        "created_utc": 1743499276.0,
        "created_date": "2025-04-01 11:21:16",
        "score": 65,
        "is_submitter": false,
        "topics": ["character_relationships", "meta"]
      }
    ]
  }
]
```
 
### Post fields

- id: Reddit base36 string (post id).
- title: post title.
- author: hashed token.
- created_utc: Unix epoch (float, seconds).
- created_date: local timestamp string, YYYY-MM-DD HH:MM:SS.
- score: integer score at capture time.
- upvote_ratio: 0–1 float.
- num_comments: number of comments at capture time.
- url: link target (image, external URL, or post URL).
- selftext: Markdown/plaintext body (empty for link posts).
- is_self: boolean (text/self post).
- is_video: boolean (if known).
- link_flair_text: flair at capture time (may be null).
- over_18: boolean (NSFW flag).
- spoiler: boolean.
- topics: array of string tags assigned during qualitative coding.
- comments: array of first‑level comment objects (see below).

Note: Some distributions may omit or redact direct permalinks to preserve contextual integrity. If present, permalink is a Reddit path to the post.

### Comment fields

- id: comment id (base36).
- author: hashed token.
- body: comment text.
- created_utc, created_date: as above.
- score: integer score at capture time.
- is_submitter: boolean (comment author is also the post author).
- topics (optional): array of string tags assigned during qualitative coding.

### Topic tags (optional annotations)

Topics are drawn from a controlled vocabulary used in the study:

- meta, memes, storyline_discussion, character_relationships, ending_discussion
- therapy_and_coping_strategies, asking_for_mental_health_advice
- depression, sadness, loneliness, trauma_and_ptsd, guilt
- suicide_and_self_harm, venting, frustration, mutual_support
- gameplay_advice, opinions_about_the_games_emotional_intensity
- fan_creations_and_cosplays, positive_emotions, deleted_or_removed, links_or_images

---

## How the interactive reader works (index.html)

- Data loading
    - On load, the interface fetches omori_posts.json (same directory).
    - Posts are assigned stable, session‑local ordinal indices (post_index = 0..N-1).
    - First‑level comments are shown in the order provided (typically chronological).

- Layout and choreography
    - Post selector: a list/panel of post titles with indices; choose any to open.
    - Central scene: the selected post renders in a central “bubble,” paginated for long texts.
    - Peripheral replies: up to six comment “slots” surround the post; comments rotate in order across turns.
    - Turn‑taking: click anywhere (or use the Next control) to advance typing/pagination and cycle replies. This pacing supports close reading by slowing skimming.

- Accessibility and controls
    - High‑contrast theme; alt text for controls.
    - Audio toggle: background music can be turned on/off. It is optional for use.
    - Optional text‑to‑speech toggle to read the visible page aloud (if supported by the browser).
    - Note: Current build prioritizes desktop; small screens may require zooming. Keyboard navigation may be limited.

- Scope
    - Only first‑level comments are shown (no deep threaded nesting).
    - The reader is data‑driven: swap in any file named omori_posts.json with the same schema to reuse the interface.

---

## Recreate/extend the dataset (dataextraction.py)

The included script collects r/OMORI posts via Reddit’s API using PRAW and applies a keyword gate to titles/selftexts.

- Requirements
    - Python 3.9+ recommended
    - `pip install praw`
    - A Reddit app (script or installed app) with client id/secret and a descriptive user agent
    - Compliance with Reddit’s API Terms of Use

- Configure credentials
    - For security, prefer environment variables over hard‑coding secrets:
        - REDDIT_CLIENT_ID
        - REDDIT_CLIENT_SECRET
        - REDDIT_USER_AGENT
        - REDDIT_USERNAME (if using script auth)
        - REDDIT_PASSWORD (if using script auth)
    - The provided script includes placeholders; update safely before running.

- Run
    - `python dataextraction.py`
    - Output: omori_posts.json (default) or a filename you pass into `scrape_omori_subreddit(output_filename)`

- What the script does
    - Queries multiple listing types: hot, new, top(all), rising, controversial(all).
    - Deduplicates by post id across listings.
    - Keyword gate: configurable via `KEYWORDS` at the top of the file.
    - For matched posts, collects post metadata and all first‑level comments.
    - Periodic JSON saves; light sleep to respect rate limits.

- Important notes
    - Ethics: Review the article’s guidance and AoIR/IRB norms for sensitive content. Pseudonymize authors before public release; consider redacting links/permalinks for contextual integrity.
    - Reproducibility: API results are time‑varying; scores and comment counts reflect capture time.

---

## Repository structure

- index.html — interactive reader (loads omori_posts.json by default).
- omori_posts.json — dataset (array of posts with nested first‑level comments).
- dataextraction.py — Reddit API pipeline (PRAW).

You can remove or replace assets without affecting basic functionality; the reader will still render text.

---

## License and citation

- License: Creative Commons Attribution 4.0 (CC BY 4.0) for the dataset and visualization. Cite appropriately when reusing.
- Suggested citation:
    - Di Leo, N. (2025). Harnessing Computational Social Science: A Framework for Digital Ethnography of Online Communities. CSS+Qual Workshop, London School of Economics.

If you build on the code, please include attribution and note any changes.

---

## Disclaimer

This repository contains references to mental‑health topics (e.g., depression, self‑harm). Use care when reading or demonstrating the interface. For research use, follow Reddit’s API policies, your institution’s ethics guidance, and local laws on data handling and privacy.