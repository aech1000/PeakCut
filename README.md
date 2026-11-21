# Clipverse

**Turn long videos and live streams into short, captioned clips.**

Clipverse (the project repository and some compatibility settings are named **PeakCut**) helps creators find engaging moments in long videos and live streams, turn them into vertical clips, add captions and on-screen hooks, and publish finished clips to connected social accounts.

It is free and open source. Run it on your own computer or on a server, and use an AI provider you choose. You can also run it without an AI key; clip selection then falls back to loudness-based detection.

- **Source code:** [aech1000/PeakCut](https://github.com/aech1000/PeakCut)
- **Deployment guide:** [DEPLOY.md](DEPLOY.md)
- **Configuration reference:** [.env.example](.env.example)
- **Contributor guide:** [AGENTS.md](AGENTS.md)
- **License:** [MIT](LICENSE)

---

## Contents

- [Highlights](#highlights)
- [How it works](#how-it-works)
- [AI-generated hook suggestions](#ai-generated-hook-suggestions)
- [Supported sources and publishing](#supported-sources-and-publishing)
- [Requirements](#requirements)
- [Run locally](#run-locally)
- [Choose and configure an AI provider](#choose-and-configure-an-ai-provider)
- [Configuration](#configuration)
- [Accounts and administration](#accounts-and-administration)
- [Storage and data](#storage-and-data)
- [Deploy with Docker](#deploy-with-docker)
- [Testing](#testing)
- [Project structure](#project-structure)
- [Security and privacy](#security-and-privacy)
- [Operational notes](#operational-notes)
- [Responsible use](#responsible-use)
- [Contributing](#contributing)
- [License](#license)

## Highlights

- **Long-form video clipping:** Submit a supported video URL or upload a video file. Clipverse analyses the content and identifies moments that may hold a viewer's attention.
- **Live-stream clipping:** Record a supported live stream into a rolling buffer and identify potential highlights while the stream is still running.
- **Vertical video rendering:** Create 9:16 clips with word-by-word captions, selectable caption styles and layouts, and editable opening text.
- **AI-assisted hooks:** Generate several short hook suggestions for a clip, rank them using quality signals that give factual accuracy the greatest weight, and choose or edit the text before rendering.
- **Creator workspaces:** Keep creators, clip settings, posting rules and activity separate for each account.
- **Publishing workflows:** Connect supported social accounts, queue clips, or enable automatic posting with spacing and daily caps.
- **Bring your own AI:** Use a supported provider, an OpenAI-compatible endpoint, or a local model through Ollama.
- **Self-hosted:** Run locally without sign-in, or enable accounts when hosting the app for multiple people.

## How it works

1. **Add a source.** Paste a supported video or live-stream link, or upload a local video.
2. **Analyse the content.** Clipverse obtains or generates a transcript and evaluates candidate moments. With an AI provider configured, the model helps identify compelling moments and produce clip metadata. Without an AI key, selection can use loudness instead.
3. **Review the candidates.** Inspect the suggested clips and their context before rendering.
4. **Customise the clip.** Edit the hook, title, captions, caption style and layout.
5. **Render and publish.** Create the vertical clip, then download it or send it through a connected publishing workflow.

The exact processing time depends on video length, source accessibility, hardware, and whether transcription and AI analysis can use accelerated or remote services.

## AI-generated hook suggestions

Clipverse can ask the configured AI model for **3–5 distinct opening-hook options** for a clip. The suggestions are intended to be short, specific and supported by what actually happens in the clip.

Each candidate is evaluated on four signals:

| Signal | Weight | What it measures |
|---|---:|---|
| Accuracy | 35% | Whether the wording is supported by the clip |
| Curiosity | 25% | Whether it gives a viewer a reason to keep watching |
| Clarity | 20% | Whether the wording is immediately understandable |
| Relevance | 20% | Whether it fits the moment being clipped |

The application sanitises the model response, removes empty, duplicate and over-length suggestions, ranks the remaining options, and exposes up to five. The highest-ranked valid option is selected as the initial hook. You can choose another suggestion in the clip editor or edit the hook text yourself.

**Hook length is limited to five words.** The same limit is enforced on the legacy single-hook fallback, so older or model-limited responses cannot bypass the rule. If no valid generated options are returned, Clipverse can retain a valid legacy fallback; an over-length fallback is rejected.

The ranking is a quality aid, not a guarantee that a hook will perform well. Review the wording for accuracy and context before publishing.

## Supported sources and publishing

### Video and live-stream sources

The default allowed-site configuration includes:

- YouTube (youtube.com, youtu.be)
- Twitch (twitch.tv)
- Kick (kick.com)

The allowed-site list can be changed with **PEAKCUT_ALLOWED_SITES**. Actual access also depends on the source platform, network, video visibility, and its current download restrictions.

You can upload a video file instead of using a URL.

### Connected publishing accounts

Clipverse includes connection and publishing workflows for:

- **YouTube** — YouTube Shorts
- **Instagram** — Instagram publishing for eligible Creator and Business accounts
- **TikTok** — TikTok video publishing

Each platform requires its own developer application and OAuth credentials. An administrator can configure the app credentials in **Settings → Connected apps**. See the detailed [platform setup instructions in DEPLOY.md](DEPLOY.md#connecting-youtube-instagram-and-tiktok).

Platform review and audit requirements may restrict publishing capabilities. For example, an app that has not completed the relevant platform review may only be able to publish private posts.

## Requirements

### Local installation

- Python **3.10 or newer**
- [FFmpeg](https://ffmpeg.org/) available on your PATH
- Internet access for installing dependencies, downloading the speech model on first start, and accessing supported source platforms
- An AI API key is optional

Install FFmpeg:

| Operating system | Example |
|---|---|
| Windows | **winget install Gyan.FFmpeg** |
| macOS | **brew install ffmpeg** |
| Debian / Ubuntu | **sudo apt install ffmpeg** |

Clipverse downloads its speech model on first start (approximately 480 MB). Allow additional disk space for source videos, rendered clips, recordings and temporary processing files.

### Server deployment

For a multi-user server, use Linux and Docker with Docker Compose. Video processing and transcription are CPU- and storage-intensive. The deployment guide recommends planning for **8+ CPU cores, 16 GB RAM and 200+ GB disk** when several people will use the service. Actual requirements depend on workload and concurrency.

See [DEPLOY.md](DEPLOY.md) for the complete server deployment guide.

## Run locally

Choose a short, permanent installation directory. Avoid temporary folders and deeply nested paths; long Windows paths can prevent native speech-processing libraries from loading.

### 1. Clone the repository

Windows:

~~~powershell
git clone https://github.com/aech1000/PeakCut.git C:\peakcut
cd C:\peakcut
~~~

macOS or Linux:

~~~bash
git clone https://github.com/aech1000/PeakCut.git ~/peakcut
cd ~/peakcut
~~~

### 2. Install dependencies

It is recommended to use a virtual environment.

Windows:

~~~powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

macOS or Linux:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

### 3. Start Clipverse

~~~bash
python -m studio.server
~~~

Open [http://127.0.0.1:8765](http://127.0.0.1:8765).

On a personal installation, accounts are disabled by default and the dashboard opens directly. Configure an AI provider under **Settings → AI** to enable AI-assisted clip selection and hook generation.

## Choose and configure an AI provider

The simplest setup is in the app:

1. Open **Settings → AI**.
2. Choose a provider.
3. Paste your API key, if the provider requires one.
4. Use **Find models** to select a model offered by the provider.
5. Select **Save and test**.

The key is stored in Clipverse's data folder and is not shown again in the dashboard.

You can alternatively configure the provider in a **.env** file:

~~~ini
PEAKCUT_AI_PROVIDER=gemini
PEAKCUT_AI_MODELS=gemini-2.5-flash
PEAKCUT_AI_KEY=your-api-key
~~~

Available provider identifiers:

| Provider | Value | Key or setup |
|---|---|---|
| Google Gemini | **gemini** | [Google AI Studio](https://aistudio.google.com/apikey) |
| OpenAI | **openai** | [OpenAI API keys](https://platform.openai.com/api-keys) |
| xAI Grok | **xai** | [xAI Console](https://console.x.ai) |
| Groq | **groq** | [Groq Console](https://console.groq.com/keys) |
| OpenRouter | **openrouter** | [OpenRouter](https://openrouter.ai/keys) |
| Anthropic Claude | **anthropic** | [Anthropic Console](https://console.anthropic.com) |
| Ollama | **ollama** | [Ollama](https://ollama.com) |
| Custom OpenAI-compatible API | **custom** | Set **PEAKCUT_AI_BASE_URL** as well |

Notes:

- Model identifiers are provider-specific and change over time. Use the provider's current model list.
- You can specify multiple model identifiers separated by commas in **PEAKCUT_AI_MODELS**; Clipverse tries them in order.
- Without an AI key, Clipverse can still identify candidate moments using loudness-based selection. AI-generated titles and hook suggestions require a configured model.
- AI usage is billed by the provider you choose. Clipverse does not add an AI usage charge.
- Speech transcription is performed by the local speech model by default; it is separate from the AI provider used for clip analysis.

## Configuration

Copy the example file when configuring a server or when you prefer environment-based settings:

~~~bash
cp .env.example .env
~~~

The full list of settings and comments is maintained in [.env.example](.env.example). Common settings include:

| Setting | Purpose |
|---|---|
| **PEAKCUT_AI_PROVIDER** | AI provider identifier |
| **PEAKCUT_AI_MODELS** | One or more model identifiers, tried in order |
| **PEAKCUT_AI_KEY** / **PEAKCUT_AI_KEY_FILE** | AI provider key, supplied directly or through a secret file |
| **PEAKCUT_AI_BASE_URL** | Base URL for a custom OpenAI-compatible provider |
| **PEAKCUT_ACCOUNTS** | Set to **1** to enable sign-in and multi-user accounts |
| **PEAKCUT_DATA** | Explicit path for application data |
| **PEAKCUT_PORT** | Local application port; default is **8765** |
| **PEAKCUT_PUBLIC_URL** | Public URL used by the application |
| **PEAKCUT_ALLOWED_SITES** | Comma-separated list of allowed source domains |
| **PEAKCUT_YT_TRANSCRIPT** | Use YouTube's available transcript where supported; set to **0** to always transcribe locally |
| **PEAKCUT_UPDATE_CHECK** | Check GitHub for updates; set to **0** to disable |
| **PEAKCUT_JOB_WORKERS** | Upper bound for concurrent video jobs |
| **PEAKCUT_MAX_LIVE** | Upper bound for concurrent live recordings |

For server deployments, also configure **PEAKCUT_DOMAIN** and a strong **POSTGRES_PASSWORD**. See [.env.example](.env.example) and [DEPLOY.md](DEPLOY.md) for the full list and deployment-specific options.

Never commit **.env**, API keys, OAuth secrets, session credentials, or files in **secrets/**.

## Accounts and administration

### Personal installation

Accounts are disabled by default. The local installation opens directly into the dashboard and uses a single local owner.

### Shared or public server

Enable accounts for a server that other people can reach. The Docker Compose deployment enables accounts by default. Each new account is a normal user and has access to its own workspace and data.

After creating your account, grant administrator access from the machine running Clipverse:

Local installation:

~~~bash
python -m studio.admin grant you@example.com
~~~

Docker:

~~~bash
docker compose exec app python -m studio.admin grant you@example.com
~~~

The command also supports **revoke** and **list**. The admin dashboard is available at **/admin** to administrators.

## Storage and data

Clipverse keeps its application data in one data directory. Depending on configuration, this includes:

- Uploaded source videos and downloaded media
- Rendered clips and live-stream recordings
- Creator workspaces, jobs and per-user files
- Local database files when SQLite is used
- Speech models, fonts, temporary processing files and application settings

The default local data directory is **./data**. You can set **PEAKCUT_DATA** or choose another location in **Settings → Storage**. When moving storage through the app, follow the on-screen instructions and allow the move to finish before removing the old location.

Database selection:

- **Local installation:** SQLite is used by default.
- **Docker server deployment:** PostgreSQL is configured by Docker Compose.

Back up both the database and the data directory. For a Docker PostgreSQL backup, see the backup command in [DEPLOY.md](DEPLOY.md).

## Deploy with Docker

The standard Docker Compose deployment runs:

| Service | Responsibility |
|---|---|
| **app** | Clipverse application and video-processing workers |
| **db** | PostgreSQL 16 database |
| **caddy** | HTTPS and reverse proxy when the **own-https** profile is enabled |

### 1. Prepare configuration

~~~bash
cp .env.example .env
~~~

Set at least:

- **PEAKCUT_DOMAIN** to a domain whose DNS points to the server
- **POSTGRES_PASSWORD** to a strong, unique password
- AI provider settings, if AI-assisted analysis is required
- **COMPOSE_PROFILES=own-https** if this server is dedicated to Clipverse and Caddy should manage HTTPS

Keep credentials and key files out of Git. File-based secrets can be placed in **./secrets/** and referenced by the corresponding **_FILE** settings.

### 2. Start the services

~~~bash
docker compose up -d --build
~~~

The first start downloads the speech model and initialises the database. When the **own-https** profile is enabled, open the configured domain over HTTPS.

### 3. Create an administrator

Sign up through the site, then run:

~~~bash
docker compose exec app python -m studio.admin grant you@example.com
~~~

### 4. Configure connected apps

An administrator can configure YouTube, Instagram and TikTok OAuth applications under **Settings → Connected apps**. The app displays the redirect URLs that must be registered with each platform.

This section is a quick start, not a substitute for the production checklist. Read [DEPLOY.md](DEPLOY.md) for server sizing, OAuth setup, SMTP, Cloudflare, reverse-proxy options, backups and optional remote GPU transcription.

**Production deployment note:** If you use a custom Compose override, image tag, or systemd unit, make sure the same Compose file set and deployment configuration are used by both manual operations and the VM's startup service. Otherwise, a reboot-time **docker compose up** using only the base file may recreate containers with a different image or configuration.

## Testing

Run the full isolated test runner:

~~~bash
python tests/run.py
~~~

The runner starts a temporary copy of the app on a spare port with an empty data directory, runs its tests, and removes the temporary environment. It does not require production credentials or use your normal application data.

To run the focused hook-option tests:

~~~bash
python -m unittest tests.test_hook_options
~~~

The hook tests cover ranking, accuracy weighting, duplicate and over-length filtering, legacy fallback handling, and the maximum number of exposed suggestions.

Before submitting a change, run the relevant focused tests and the full test runner where practical.

## Project structure

| Path | Responsibility |
|---|---|
| **studio/server.py** | FastAPI application and HTTP routes |
| **studio/config.py** | Environment and application configuration |
| **studio/ai.py** | AI provider integrations and saved AI settings |
| **studio/brain.py** | Clip analysis prompts, hook ranking, titles and metadata |
| **studio/jobs.py** | Video-processing pipeline and job queue |
| **studio/live.py** | Live-stream recording and clipping |
| **studio/transcribe.py** | Local speech-to-text processing |
| **studio/asr_worker.py** | Optional remote transcription worker |
| **studio/render.py** | Clip rendering, layouts and captions |
| **studio/media.py** | Media download, probing and audio extraction |
| **studio/auth.py**, **studio/account.py**, **studio/admin.py** | Authentication, accounts and administration |
| **studio/db.py** | SQLite and PostgreSQL database access |
| **web/** | Front-end pages and static assets |
| **tests/** | Automated tests |
| **deploy/** | Deployment configurations and supporting files |
| **Dockerfile**, **docker-compose.yml** | Container build and standard server deployment |
| **.env.example** | Documented environment settings |

The front end uses plain HTML, CSS and JavaScript; there is no separate front-end build step.

## Security and privacy

- Enable accounts on any server reachable by other people. Do not expose a personal, no-sign-in installation to the public internet.
- Passwords are stored as salted scrypt hashes. Session tokens are stored hashed and session cookies are HTTP-only.
- User identity is derived from the authenticated session, and each account's data is isolated from other accounts.
- Administrator privileges are granted through the local admin command, not through a public registration field or web request.
- Keep API keys, OAuth secrets, SMTP credentials and other private values in environment variables or secret files. Do not commit them.
- Use HTTPS for public deployments and configure email verification and SMTP as appropriate.
- Treat downloaded video content and transcripts as untrusted input.

If you discover a security vulnerability, report it privately through the repository's [GitHub security advisories](https://github.com/aech1000/PeakCut/security/advisories/new) rather than posting exploit details in a public issue.

## Operational notes

- **YouTube availability:** YouTube may refuse requests from data-centre IP addresses with a bot-verification challenge. The server may temporarily pause YouTube URL attempts after such a refusal. Uploading a file or using another supported source may still work. This is a source-platform restriction, not necessarily an application outage.
- **Processing capacity:** Video rendering and transcription use CPU, memory and disk. Tune concurrency limits to match the server rather than increasing them blindly.
- **Single application instance:** Job queues and live recordings run inside the application process. Do not run multiple app instances against the same application data unless the deployment has been designed for that.
- **Updates:** The app can check GitHub for a newer version. For a standard source deployment, review the update and then follow the documented update procedure. For Docker, the basic update command is **git pull && docker compose up -d --build**; custom production deployments may require their own override files and rollout steps.
- **Restarts:** A restart interrupts active processing temporarily. Follow the deployment guide and maintain database and data-directory backups before upgrades.

## Responsible use

Only download, clip, and publish videos that you own or have permission to use. You are responsible for complying with copyright law, the terms of the source platforms, and the publishing rules of the services you connect.

## Contributing

Contributions, bug reports and focused improvements are welcome.

1. Fork the repository and create a branch for your change.
2. Keep changes focused and add or update tests where behaviour changes.
3. Run the relevant tests before opening a pull request.
4. Include a clear description of the problem, implementation and test results.

See [AGENTS.md](AGENTS.md) for the code map, development workflow and project-specific guidance.

## License

Clipverse is released under the [MIT License](LICENSE).

Caption fonts in **studio/fonts/** (Anton, Archivo Black and Poppins) are distributed under the SIL Open Font License; the corresponding licence texts are included in that directory.
