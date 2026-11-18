# AI Tutor with Ollama (introduced in v0.7.0)

[English](AI_TUTOR.md) · [Čeština](cs/AI_TUTOR.md) · [Slovenčina](sk/AI_TUTOR.md) · [Русский](ru/AI_TUTOR.md)

Connect your Ollama server through **Connect / refresh**, choose a model and answer language, type a question and select **Send**. Replies arrive progressively; **Stop** cancels generation. Other screens remain usable during generation and without Ollama. Chat is not stored in the database and lasts only for the current app session.

## First use

1. Install and run Ollama using its [official quickstart](https://docs.ollama.com/quickstart), [Windows guide](https://docs.ollama.com/windows) or [Linux guide](https://docs.ollama.com/linux). Choose a model that fits your computer's memory. SOSkúška does not download or install models.
2. Check in Ollama that at least one model is available. Normal study outside AI Tutor does not require Ollama.
3. Open AI Tutor. The default URL is `http://127.0.0.1:11434`. Connect / refresh loads models; if none appear, prepare a model in Ollama and refresh.
4. Choose Automatic, English, Czech, Slovak or Russian. Automatic asks the model to follow the latest question's language; detection quality depends on the model.
5. Stop retains received text. After an error, another question may be sent; failed/stopped replies are excluded from future context. New chat needs a second confirmation when chat exists. Navigation or Send/Connect cancels that confirmation.

## Privacy and limits

Only Connect or Send starts a request; startup and navigation send nothing. The selected server receives the question and bounded context from this chat, never automatic attachments of SQLite records, subjects, results or files. The default server is local; another server/model determines how it processes data. Start New chat before connecting an existing chat to a different server. There is no automatic cloud fallback.

Chat stays in memory; copy it before closing if you need it. Connection choices may be explicitly saved in [Settings](SETTINGS.md), but saving preferences does not preserve chat. Limits: 12 turns per chat, 4,000 characters per question, 16,000 per answer. Context includes at most six complete pairs / 24,000 characters; the model may not know older content. Output is plain text without Markdown/LaTeX rendering or attached materials. Replies are not verified facts or automatic grading.

HTTP/HTTPS URLs may not contain credentials, a path, query or fragment. HTTPS certificates are verified; redirects and environment HTTP proxies are not used. Authenticated servers are unsupported. Socket timeout is 30 seconds; a wall-clock safeguard is 180 seconds. System DNS/TCP setup can delay cancellation. Connection failure alone does not prove Ollama is missing.

API references: [models](https://docs.ollama.com/api/tags) · [chat](https://docs.ollama.com/api/chat) · [streaming](https://docs.ollama.com/api/streaming).
