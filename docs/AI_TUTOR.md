# AI Tutor with Ollama (introduced in v0.7.0)

[English](AI_TUTOR.md) · [Čeština](cs/AI_TUTOR.md) · [Slovenčina](sk/AI_TUTOR.md) · [Русский](ru/AI_TUTOR.md)

## v0.23.0 — Statistics and AI Tutor design

AI Tutor groups server/model/language controls and saved-history controls into separate cards, side by side on wide screens and stacked in compact windows. The model selector has a full-width row. Conversation ownership, transcript, prompt and Send/Stop controls share a bordered reading/editing surface. Recovery feedback is repeated beside the retry/discard/interruption controls so confirmations remain readable after scrolling. Navigation and resizing keep drafts, widgets, history selection and active jobs. Connection remains explicit; opening history stays offline.

Connect your Ollama server through **Connect / refresh**, choose a model and answer language, type a question and select **Send**. Replies arrive progressively; **Stop** cancels generation. Other screens remain usable during generation and without Ollama. Chat is saved in the local database and can be reopened after restart; see the saved-history guide.

## First use

1. Install and run Ollama using its [official quickstart](https://docs.ollama.com/quickstart), [Windows guide](https://docs.ollama.com/windows) or [Linux guide](https://docs.ollama.com/linux). Choose a model that fits your computer's memory. SOSkúška does not download or install models.
2. Check in Ollama that at least one model is available. Normal study outside AI Tutor does not require Ollama.
3. Open AI Tutor. The default URL is `http://127.0.0.1:11434`. Connect / refresh loads models; if none appear, prepare a model in Ollama and refresh.
4. Choose Automatic, English, Czech, Slovak or Russian. Automatic asks the model to follow the latest question's language; detection quality depends on the model.
5. Stop retains received text. After an error, another question may be sent; failed/stopped replies are excluded from future context. New chat needs a second confirmation when chat exists. Navigation or Send/Connect cancels that confirmation.

## Privacy and limits

Only Connect or Send starts a request; startup and navigation send nothing. The selected server receives the question and bounded context from this chat, no automatic attachments. If you explicitly prepare a completed-question draft, the selected snapshot becomes part of the prompt sent after Send. Hint mode includes only the question and choices; other modes also include your answer, the stored answer key and explanation. Other SQLite records, subjects, results and files are not attached. The default server is local; another server/model determines how it processes data. Start New chat before connecting an existing chat to a different server. There is no automatic cloud fallback.

Chats are saved locally and included in backups. Connection choices may be explicitly saved in [Settings](SETTINGS.md), while conversations save separately when you Send. Limits: 12 turns per chat, 4,000 characters per question, 16,000 per answer. Context includes at most six complete pairs / 24,000 characters; the model may not know older content. Output is plain text without Markdown/LaTeX rendering or attached materials. Replies are not verified facts or automatic grading.

HTTP/HTTPS URLs may not contain credentials, a path, query or fragment. HTTPS certificates are verified; redirects and environment HTTP proxies are not used. Authenticated servers are unsupported. Socket timeout is 30 seconds; a wall-clock safeguard is 180 seconds. System DNS/TCP setup can delay cancellation. Connection failure alone does not prove Ollama is missing.

API references: [models](https://docs.ollama.com/api/tags) · [chat](https://docs.ollama.com/api/chat) · [streaming](https://docs.ollama.com/api/streaming).

## Saved AI Tutor conversations

AI Tutor now saves conversations locally, including the original server/model and reply status. Open saved history without networking, reconnect explicitly to continue, or delete a selected conversation after confirmation. Released in v0.12.0 with schema 7, which migrates existing study data transactionally. [Saved AI Tutor conversations](TUTOR_HISTORY.md).


## Question explanations · v0.25.0

Completed Practice results, including reopened history, offer **Explain this question**. Open the local preview, then choose **Prepare in Tutor**. It uses the saved question snapshot (all four choices, selected answer or Unanswered, stored answer key and explanation), even after the original question/subject is deleted. Nothing connects or sends during preview/preparation. In Tutor, review the server, model and answer language, explicitly Connect if needed, then Send. The draft is editable and uses ordinary local chat history, Stop and save-retry paths.

Tutor must be an idle, clean New chat with an empty prompt and no pending confirmation or unsaved reply. Existing work is preserved; finish it or explicitly use the confirmed New chat action before retrying. A complete generated prompt above 4,000 characters is rejected with its measured length; nothing is truncated. The saved answer key and AI explanation may be wrong; scores and source content never change. Automatic asks for the supplied question language; explicit answer language overrides it. Prompt instructions stay in English and user content stays unchanged. No schema change (10), released version is v0.26.0.

Implementation: `question_explanation.py` builds/validates the bounded snapshot prompt; `practice_page.py` owns preview and stale-result checks; `tutor_page.py` guards draft insertion. Existing Send persists the prompt before HTTP. Automated checks use disposable data and loopback FakeOllama; real-model quality and native platform/DPI acceptance remain manual.


## AI study modes · v0.26.0

In a completed result, open **Explain this question**, then choose **Study mode** before **Prepare in Tutor**. **Explain answer** keeps the existing explanation; **Explain simply** requests short beginner-friendly steps and an example; **Give me a hint** requests one conceptual hint and omits your selected answer, stored key and explanation from the prompt; **Quiz me** asks one new follow-up at a time, waiting for your response before feedback. This is informal practice and never writes a scored attempt or changes source content.

Changing mode regenerates the exact local preview and invalidates its previous Prepare action. Nothing connects, sends or creates a conversation until the existing explicit controls are used. The sent prompt is saved in ordinary local chat history, with the existing language, 4,000-character bound, clean-chat guard, Stop and save-retry rules. Hint mode still includes all four choices: a model may infer/reveal the answer, and text already visible in completed results remains visible. Mode following and explanation quality require later real-model testing, explicitly deferred by the user. Automated checks use loopback FakeOllama. Released version is v0.26.0 / schema 10.
