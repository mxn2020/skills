# OpenClaw Agent Skill Ideas

> A categorized and prioritized list of skills to extend OpenClaw's capabilities.
> Skills are tracked from Idea through to Done.

**Implementation Status Legend:**
`✅ Done` · `🔧 In Progress` · `📋 Planned` · `💡 Idea`

---

## 1. System Integrations

### 1.1 Version Control & Repository Management

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0001 | **GitHub Repo Manager** | Create, list, delete repos; manage collaborators | ✅ Done | Apache 2.0 |
| OC-0002 | **GitHub Issues Agent** | Label, triage, close, and prioritize issues automatically | ✅ Done | Apache 2.0 |
| OC-0003 | **GitHub PR Automated Reviewer** | Verify diffs against style guides and flag violations | ✅ Done | Apache 2.0 |
| OC-0004 | **GitHub Actions Trigger** | Manually dispatch workflows from agent commands | ✅ Done | Apache 2.0 |
| OC-0005 | **GitLab Pipeline Monitor** | Watch CI/CD status and report failures | ✅ Done | Apache 2.0 |
| OC-0006 | **GitLab Merge Request Manager** | Auto-assign reviewers and manage MR lifecycle | ✅ Done | Apache 2.0 |
| OC-0007 | **Bitbucket Integration** | Sync Jira tickets with commits | ✅ Done | Apache 2.0 |
| OC-0008 | **Changelog Generator** | Auto-generate changelogs from commit history and PR titles | ✅ Done | Apache 2.0 |

### 1.2 Deployment & Cloud Platforms

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0009 | **Vercel Deployment Manager** | Trigger builds, manage environment variables, alias domains | ✅ Done | Apache 2.0 |
| OC-0010 | **Netlify Site Controller** | Manage redirects, forms, and split testing | ✅ Done | Apache 2.0 |
| OC-0011 | **Railway Project Deployer** | Spin up new service instances from templates | ✅ Done | Apache 2.0 |
| OC-0012 | **Render Service Manager** | Scale services up/down based on demand | ✅ Done | Apache 2.0 |
| OC-0013 | **AWS S3 Bucket Explorer** | Upload assets, generate presigned URLs | ✅ Done | Apache 2.0 |
| OC-0014 | **AWS EC2 Instance Control** | Start/stop dev servers to save cost | ✅ Done | Apache 2.0 |
| OC-0015 | **AWS Lambda Invoker** | Trigger and monitor serverless functions on demand | ✅ Done | Apache 2.0 |
| OC-0016 | **Google Cloud Run Deployer** | Deploy containerized apps effortlessly | ✅ Done | Apache 2.0 |
| OC-0017 | **Google Cloud Storage Manager** | Manage buckets, IAM policies, and lifecycle rules | ✅ Done | Apache 2.0 |
| OC-0018 | **Cloudflare Worker Manager** | Update edge scripts instantly | ✅ Done | Apache 2.0 |
| OC-0019 | **Cloudflare DNS Manager** | Update A/CNAME records programmatically | ✅ Done | Apache 2.0 |
| OC-0020 | **Heroku Dyno Scaler** | Adjust resources dynamically | ✅ Done | Apache 2.0 |
| OC-0021 | **Azure Resource Manager** | List and audit resource groups | ✅ Done | Apache 2.0 |
| OC-0022 | **DigitalOcean Droplet Sniper** | Create short-lived VPS instances for testing | ✅ Done | Apache 2.0 |
| OC-0023 | **Fly.io App Manager** | Deploy and scale apps globally at the edge | ✅ Done | Apache 2.0 |
| OC-0024 | **Pulumi / Terraform Runner** | Execute infrastructure-as-code plans and apply changes | ✅ Done | Apache 2.0 |

### 1.3 Database & Storage

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0025 | **Neon Branch Manager** | Create instant Postgres branches for every PR | ✅ Done | Apache 2.0 |
| OC-0026 | **Supabase Bucket Manager** | Manage heavy media assets | ✅ Done | Apache 2.0 |
| OC-0027 | **Supabase Table Editor** | Run safe read/write operations against Supabase tables | ✅ Done | Apache 2.0 |
| OC-0028 | **PlanetScale Schema Inspector** | Check for safe migrations and schema diffs | ✅ Done | Apache 2.0 |
| OC-0029 | **MongoDB Atlas Cluster Monitor** | Check current connections and slow queries | ✅ Done | Apache 2.0 |
| OC-0030 | **Upstash Redis CLI** | Use serverless Redis for key-value jobs | ✅ Done | Apache 2.0 |
| OC-0031 | **Upstash Kafka Producer** | Send events to serverless Kafka topics | ✅ Done | Apache 2.0 |
| OC-0032 | **DynamoDB Item Browser** | Query NoSQL data efficiently | ✅ Done | Apache 2.0 |
| OC-0033 | **Firebase Firestore Admin** | Read/Write documents for admin dashboard tasks | ✅ Done | Apache 2.0 |
| OC-0034 | **Airtable Record Sync** | Treat Airtable as a lightweight CMS/DB | ✅ Done | Apache 2.0 |
| OC-0035 | **CockroachDB Query Runner** | Execute distributed SQL queries with resilience | ✅ Done | Apache 2.0 |
| OC-0036 | **Turso Edge DB Manager** | Manage lightweight SQLite databases at the edge | ✅ Done | Apache 2.0 |

### 1.4 Search & Vector Databases

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0037 | **Pinecone Index Manager** | Create/delete vector indexes for RAG apps | ✅ Done | Apache 2.0 |
| OC-0038 | **Weaviate Schema Manager** | Update class definitions | ✅ Done | Apache 2.0 |
| OC-0039 | **Algolia Indexer** | Push content updates to search indices | ✅ Done | Apache 2.0 |
| OC-0040 | **MeiliSearch Settings** | Configure ranking rules and stop words | ✅ Done | Apache 2.0 |
| OC-0041 | **Qdrant Collection Manager** | Manage vector collections and run similarity queries | ✅ Done | Apache 2.0 |
| OC-0042 | **Chroma DB Manager** | Manage local/hosted vector stores for RAG pipelines | ✅ Done | Apache 2.0 |

### 1.5 CMS & Content

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0043 | **Contentful Entry Manager** | Publish or archive content entries | ✅ Done | Apache 2.0 |
| OC-0044 | **Sanity Studio Helper** | Trigger webhooks or clear datasets | ✅ Done | Apache 2.0 |
| OC-0045 | **Strapi API Client** | Manage dynamic content types | ✅ Done | Apache 2.0 |
| OC-0046 | **WordPress Post Publisher** | Draft and publish blog posts via REST API | ✅ Done | Apache 2.0 |
| OC-0047 | **Ghost Admin** | Manage membership tiers and posts | ✅ Done | Apache 2.0 |
| OC-0048 | **Webflow CMS Updater** | Push collection item changes without touching the editor | ✅ Done | Apache 2.0 |
| OC-0049 | **Notion Page Publisher** | Create and update Notion pages from agent output | ✅ Done | Apache 2.0 |

### 1.6 Monitoring & Analytics

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0050 | **Sentry Error Triage** | Fetch recent exceptions and assign to developers | ✅ Done | Apache 2.0 |
| OC-0051 | **Datadog Dashboard Snapshotter** | Get a PNG of current system health metrics | ✅ Done | Apache 2.0 |
| OC-0052 | **Grafana Alert Manager** | Silence or acknowledge firing alerts | ✅ Done | Apache 2.0 |
| OC-0053 | **LogRocket Session Finder** | Find user sessions containing errors | ✅ Done | Apache 2.0 |
| OC-0054 | **Mixpanel Cohort Analyzer** | Query user retention and funnel data | ✅ Done | Apache 2.0 |
| OC-0055 | **PostHog Feature Flag Manager** | Toggle features for specific users or cohorts | ✅ Done | Apache 2.0 |
| OC-0056 | **Axiom Log Query** | Run structured log queries over high-volume streams | ✅ Done | Apache 2.0 |
| OC-0057 | **Better Stack Monitor** | Check uptime incidents and on-call escalations | ✅ Done | Apache 2.0 |
| OC-0058 | **Plausible Analytics Reporter** | Pull privacy-friendly web analytics summaries | ✅ Done | Apache 2.0 |

### 1.7 Authentication & User Management

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0059 | **Clerk User Admin** | Ban/unban users, manage sessions and roles | ✅ Done | Apache 2.0 |
| OC-0060 | **Auth0 Log Inspector** | Check for failed login attempts and anomalies | ✅ Done | Apache 2.0 |
| OC-0061 | **Supabase Auth Helper** | Send password reset emails, manage providers | ✅ Done | Apache 2.0 |
| OC-0062 | **WorkOS Directory Sync** | Manage enterprise SSO and SCIM provisioning | ✅ Done | Apache 2.0 |
| OC-0063 | **Firebase Auth Manager** | Disable accounts, revoke tokens, manage custom claims | ✅ Done | Apache 2.0 |

### 1.8 Assets & Media

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0064 | **Unsplash Photo Search** | Find and license high-res stock photos | ✅ Done | Apache 2.0 |
| OC-0065 | **Cloudinary Asset Manager** | Upload, transform, and optimize images on the fly | ✅ Done | Apache 2.0 |
| OC-0066 | **Mux Video Uploader** | Create video assets and retrieve playback IDs | ✅ Done | Apache 2.0 |
| OC-0067 | **Imgix URL Builder** | Generate on-demand image transformation URLs | ✅ Done | Apache 2.0 |
| OC-0068 | **Pexels / Pixabay Search** | Source free stock photos and video clips | ✅ Done | Apache 2.0 |

### 1.9 Commerce & Payments

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0069 | **Stripe Subscription Manager** | Cancel/refund subscriptions, manage products and prices | ✅ Done | Apache 2.0 |
| OC-0070 | **Stripe Webhook Debugger** | Inspect recent webhook events and replay failed ones | ✅ Done | Apache 2.0 |
| OC-0071 | **Lemon Squeezy License Check** | Verify license keys and manage activations | ✅ Done | Apache 2.0 |
| OC-0072 | **RevenueCat Customer Lookup** | Check in-app purchase status and entitlements | ✅ Done | Apache 2.0 |
| OC-0073 | **Shopify Order Manager** | Fetch, refund, or fulfill orders via Admin API | ✅ Done | Apache 2.0 |
| OC-0074 | **Paddle Subscription Inspector** | Audit billing history and manage paused plans | ✅ Done | Apache 2.0 |

### 1.10 Communication & Notifications

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0075 | **Resend Email Sender** | Send transactional emails with templates | ✅ Done | Apache 2.0 |
| OC-0076 | **Twilio SMS / WhatsApp** | Send and receive messages programmatically | ✅ Done | Apache 2.0 |
| OC-0077 | **Slack Bot Publisher** | Post messages and manage channels via Bot API | ✅ Done | Apache 2.0 |
| OC-0078 | **Discord Webhook Notifier** | Push structured alerts to Discord channels | ✅ Done | Apache 2.0 |
| OC-0079 | **PagerDuty Incident Creator** | Open and escalate incidents from monitoring triggers | ✅ Done | Apache 2.0 |
| OC-0080 | **Knock Notification Orchestrator** | Manage multi-channel notification workflows | ✅ Done | Apache 2.0 |
| OC-0081 | **Novu Notification Manager** | Trigger and manage in-app, email, and push notifications | ✅ Done | Apache 2.0 |

---

## 2. AI Media Generation & Manipulation

### 2.1 Image Generation

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0082 | **DALL-E 3 Artist** | Generate images from detailed natural language prompts | ✅ Done | Apache 2.0 |
| OC-0083 | **Midjourney Prompter** | Optimize prompts for MJ and interact via Discord bridge | ✅ Done | Apache 2.0 |
| OC-0084 | **Stable Diffusion (SDXL) Local** | Run generation on a local GPU with full control | ✅ Done | Apache 2.0 |
| OC-0085 | **Flux Schnell Generator** | High-speed image generation for rapid iteration | ✅ Done | Apache 2.0 |
| OC-0086 | **Leonardo AI Creative** | Generate game assets, icons, and concept art | ✅ Done | Apache 2.0 |
| OC-0087 | **Ideogram Typographer** | Generate images with accurate embedded text | ✅ Done | Apache 2.0 |
| OC-0088 | **Adobe Firefly Integration** | Generate commercially safe assets via Creative Cloud | ✅ Done | Apache 2.0 |

### 2.2 Image Editing & Enhancement

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0089 | **Background Remover** | Strip image backgrounds using remove.bg or local model | ✅ Done | Apache 2.0 |
| OC-0090 | **AI Upscaler** | Upscale low-res images using Real-ESRGAN or Topaz | ✅ Done | Apache 2.0 |
| OC-0091 | **Inpainting Agent** | Fill or replace regions of an image via diffusion | ✅ Done | Apache 2.0 |
| OC-0092 | **Style Transfer** | Apply artistic styles from a reference image | ✅ Done | Apache 2.0 |
| OC-0093 | **Face Restoration** | Enhance degraded or blurry portrait images (GFPGAN) | ✅ Done | Apache 2.0 |

### 2.3 Video Generation & Editing

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0094 | **Runway Gen-3 Director** | Text-to-video and image-to-video scene generation | ✅ Done | Apache 2.0 |
| OC-0095 | **Pika Labs Animator** | Animate static images into short video clips | ✅ Done | Apache 2.0 |
| OC-0096 | **Luma Dream Machine** | Generate detailed 3D and video content | ✅ Done | Apache 2.0 |
| OC-0097 | **Kling Video Generator** | High-quality cinematic video from text prompts | ✅ Done | Apache 2.0 |
| OC-0098 | **FFmpeg Processor** | Cut, merge, transcode, and watermark videos locally | ✅ Done | Apache 2.0 |
| OC-0099 | **Auto Subtitle Generator** | Add burned-in subtitles via Whisper + FFmpeg pipeline | ✅ Done | Apache 2.0 |

### 2.4 Audio & Music

| ID | Skill | Description | Status | License |
| :--- | :--- | :--- | :--- | :--- |
| OC-0100 | **Suno Songwriter** | Generate full songs with vocals and lyrics | ✅ Done | Apache 2.0 |
| OC-0101 | **Udio Composer** | Create high-quality instrumental tracks | ✅ Done | Apache 2.0 |
| OC-0102 | **ElevenLabs Voice Actor** | High-quality TTS with emotional range and voice cloning | ✅ Done | Apache 2.0 |
| OC-0103 | **Sound Effect Foley** | Generate SFX: footsteps, rain, ambient noise, blasts | ✅ Done | Apache 2.0 |
| OC-0104 | **Whisper Transcriber** | Transcribe audio/video files to text locally or via API | ✅ Done | Apache 2.0 |
| OC-0105 | **Audio Stem Splitter** | Separate vocals, drums, and instruments from a mix | ✅ Done | Apache 2.0 |

---

## 3. Realtime Audio & Conversation

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0106 | **Realtime Voice Interface** | STT (Whisper) + LLM + TTS pipeline with low-latency optimization | 💡 Idea |
| OC-0107 | **Live Translator** | Listen to an audio stream and output translated text or audio in real time | 💡 Idea |
| OC-0108 | **Voice Sentiment Analyzer** | Detect emotion and stress levels in audio input | 💡 Idea |
| OC-0109 | **Active Listener** | Detect pauses and interruptions to manage turn-taking naturally | 💡 Idea |
| OC-0110 | **Meeting Scribe (Realtime)** | Live transcription and action item extraction during calls | 💡 Idea |
| OC-0111 | **Voice Biometrics** | Identify speakers by voice print for personalization | 💡 Idea |
| OC-0112 | **Audio Noise Reducer** | Clean up microphone input in software in real time | 💡 Idea |
| OC-0113 | **Podcast Summarizer** | Fetch, transcribe, and summarize podcast episodes on demand | 💡 Idea |
| OC-0114 | **Call Quality Monitor** | Detect jitter, latency, and packet loss in VoIP streams | 💡 Idea |

---

## 4. AI Utilities & Meta-Skills

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0115 | **Prompt Version Control** | Save, tag, and rollback prompt templates (git-backed) | � Idea |
| OC-0116 | **Token Cost Estimator** | Calculate input/output tokens and cost before running a prompt | � Idea |
| OC-0117 | **Context Compressor** | Summarize or truncate conversation history to fit context windows | 💡 Idea |
| OC-0118 | **RAG Manager** | Handle document chunking, embedding, and storage logic | 💡 Idea |
| OC-0119 | **Model Benchmarker** | Run the same prompt against GPT-4, Claude, and Llama to compare output | 💡 Idea |
| OC-0120 | **Bias & Safety Checker** | Pre-screen outputs for sensitive or harmful content | 💡 Idea |
| OC-0121 | **System Prompt Optimizer** | Meta-prompting to iteratively improve the agent's own instructions | 💡 Idea |
| OC-0122 | **Knowledge Graph Builder** | Extract entities and relationships from chat to build long-term memory | 💡 Idea |
| OC-0123 | **Tool Use Validator** | Ensure JSON arguments generated by LLMs match the expected schema | 💡 Idea |
| OC-0124 | **Agent Chain Debugger** | Visualize and replay multi-step agent tool call chains | 💡 Idea |
| OC-0125 | **Embedding Drift Detector** | Alert when retrieved context chunks diverge significantly from the query | 💡 Idea |
| OC-0126 | **Eval Suite Runner** | Run automated evals against a golden dataset to catch regressions | 💡 Idea |

---

## 5. Productivity & Personal Assistant

### 5.1 Task & Project Management

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0127 | **Linear Issue Manager** | Create, update, and triage issues and cycles | 💡 Idea |
| OC-0128 | **Jira Ticket Handler** | Manage sprints, epics, and story point estimation | 💡 Idea |
| OC-0129 | **Todoist Task Sync** | Add, complete, and prioritize tasks across projects | 💡 Idea |
| OC-0130 | **Notion Task Manager** | Create, update, and filter database rows in Notion | 💡 Idea |
| OC-0131 | **Google Tasks Integrator** | Sync tasks with Google Workspace | 💡 Idea |
| OC-0132 | **ClickUp Workspace Manager** | Manage tasks, docs, and goals in ClickUp | 💡 Idea |

### 5.2 Calendar & Scheduling

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0133 | **Google Calendar Manager** | Create events, check availability, reschedule meetings | 💡 Idea |
| OC-0134 | **Calendly Link Generator** | Create one-off scheduling links with custom constraints | 💡 Idea |
| OC-0135 | **Meeting Prep Briefer** | Summarize attendees, agenda, and relevant docs before a meeting | 💡 Idea |
| OC-0136 | **Time Zone Converter** | Resolve scheduling across multiple time zones intelligently | 💡 Idea |

### 5.3 Email & Communication

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0137 | **Gmail Inbox Triage** | Summarize, label, and draft replies to unread emails | 💡 Idea |
| OC-0138 | **Outlook Mail Manager** | Manage emails and calendar within Microsoft 365 | 💡 Idea |
| OC-0139 | **Email Tone Adjuster** | Rewrite drafts to match a target tone (formal, concise, friendly) | 💡 Idea |
| OC-0140 | **Follow-up Reminder** | Track sent emails and flag those awaiting a response | 💡 Idea |

---

## 6. Health & Quantified Self

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0141 | **Workout Logger** | Log exercises to Apple Health or Strava via API | 💡 Idea |
| OC-0142 | **Nutrition Tracker** | Estimate calories from food descriptions or photos | 💡 Idea |
| OC-0143 | **Sleep Analyst** | Correlate sleep data (Oura/Apple Watch) with productivity metrics | 💡 Idea |
| OC-0144 | **Meditation Guide** | Generate and narrate personalized guided meditation scripts | 💡 Idea |
| OC-0145 | **Hydration Reminder** | Smart recurring reminders adjusted for activity level and climate | 💡 Idea |
| OC-0146 | **Symptom Checker** | Basic triage based on described symptoms (with medical disclaimers) | 💡 Idea |
| OC-0147 | **Habit Streaks** | Track daily habits such as reading, coding, and running | 💡 Idea |
| OC-0148 | **HRV & Recovery Scorer** | Parse Garmin/Polar data and recommend training load | 💡 Idea |
| OC-0149 | **Mental Load Journal** | Prompt daily reflection and surface patterns over time | 💡 Idea |

---

## 7. Research & Knowledge Management

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0150 | **Web Research Agent** | Search, scrape, and synthesize information from multiple sources | 💡 Idea |
| OC-0151 | **ArXiv Paper Summarizer** | Fetch and summarize recent research papers by topic | 💡 Idea |
| OC-0152 | **Wikipedia Deep Dive** | Extract structured information and related topics from Wikipedia | 💡 Idea |
| OC-0153 | **Zotero Citation Manager** | Add and organize research references automatically | 💡 Idea |
| OC-0154 | **Obsidian Note Creator** | Write structured markdown notes directly into an Obsidian vault | 💡 Idea |
| OC-0155 | **Perplexity Query Agent** | Use Perplexity's API for grounded, citation-backed answers | 💡 Idea |
| OC-0156 | **Patent Search Tool** | Query patent databases for prior art | 💡 Idea |
| OC-0157 | **News Aggregator** | Pull and summarize headlines by topic from RSS/APIs | 💡 Idea |

---

## 8. Finance & Business Intelligence

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0158 | **Crypto Wallet Watcher** | Monitor addresses for incoming/outgoing transactions | 💡 Idea |
| OC-0159 | **Stock Price Fetcher** | Get real-time quotes, charts, and earnings data | 💡 Idea |
| OC-0160 | **Budget Tracker** | Parse transactions and categorize spending automatically | 💡 Idea |
| OC-0161 | **Invoice Generator** | Create and send PDF invoices from structured data | 💡 Idea |
| OC-0162 | **CRM Data Puller** | Fetch deals and contact data from HubSpot or Salesforce | 💡 Idea |
| OC-0163 | **Google Sheets Analyst** | Read, write, and analyze data in spreadsheets | 💡 Idea |
| OC-0164 | **Financial Report Summarizer** | Parse 10-K/10-Q filings and extract key metrics | 💡 Idea |

---

## 9. Smart Home & IoT

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0165 | **Home Assistant Controller** | Voice-command lights, thermostat, locks, and scenes | 💡 Idea |
| OC-0166 | **MQTT Publisher** | Send messages to IoT device topics on any broker | 💡 Idea |
| OC-0167 | **Energy Monitor** | Track and report home energy consumption trends | 💡 Idea |
| OC-0168 | **Camera Feed Analyzer** | Describe or detect objects in a home camera snapshot | 💡 Idea |
| OC-0169 | **Smart Appliance Scheduler** | Schedule dishwashers, EV charging, etc. for off-peak hours | 💡 Idea |

---

## 10. miscellaneous & "Outside the Box"

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0170 | **Recipe Generator & Shopper** | Create a meal plan and export ingredients to Instacart or a shopping list | 💡 Idea |
| OC-0171 | **Legal Document Scanner** | Summarize TOS changes, lease agreements, and contracts | 💡 Idea |
| OC-0172 | **Dream Journal** | Log and interpret dreams using symbolic analysis | 💡 Idea |
| OC-0173 | **Travel Planner** | Build multi-day itineraries with flights, hotels, and activities | 💡 Idea |
| OC-0174 | **Gift Recommender** | Suggest personalized gifts based on recipient interests and budget | 💡 Idea |
| OC-0175 | **Language Tutor** | Run interactive vocabulary drills and grammar corrections | 💡 Idea |
| OC-0176 | **Debate Coach** | Argue both sides of a topic and score the strength of arguments | 💡 Idea |
| OC-0177 | **Code Explainer** | Narrate what a code snippet does in plain English for non-developers | 💡 Idea |

---

## 11. Skill Testing & Quality Assurance

| ID | Skill | Description | Status |
| :--- | :--- | :--- | :--- |
| OC-0178 | **Skill Runner CLI** | A unified CLI to execute any skill with defined inputs (meta-runner) | 💡 Idea |
| OC-0179 | **Mock Environment Generator** | Create sandboxed temp directories/files for safe file operation testing | 💡 Idea |
| OC-0180 | **API Response Mocker** | Intercept outgoing API calls and return fixture data for offline testing | 💡 Idea |
| OC-0181 | **Regression Suite Runner** | Execute a predefined set of skill interactions and diff output against golden master | 💡 Idea |
| OC-0182 | **Skill Linter** | Validate `SKILL.md` structure and ensure scripts follow OpenClaw conventions | 💡 Idea |
| OC-0183 | **Chaos Monkey for Skills** | Randomly inject network failures or bad inputs to test skill resilience | 💡 Idea |
| OC-0184 | **Performance Load Tester** | Run skills in parallel to test concurrency and resource usage bounds | 💡 Idea |
| OC-0185 | **Security Compliance Scanner** | Check skill scripts for hardcoded secrets or unsafe shell execution | 💡 Idea |
