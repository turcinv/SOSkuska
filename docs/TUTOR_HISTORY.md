# Saved AI Tutor conversations

[English](TUTOR_HISTORY.md) · [Čeština](cs/TUTOR_HISTORY.md) · [Slovenčina](sk/TUTOR_HISTORY.md) · [Русский](ru/TUTOR_HISTORY.md)

AI Tutor now saves conversations locally, including the original server/model and reply status. Open saved history without networking, reconnect explicitly to continue, or delete a selected conversation after confirmation. Schema 7 migrates existing study data transactionally; the published release remains v0.11.1 until a new release is authorized.

## Use saved history

Connect, choose a model/language, type a question and Send. The question is saved before the network request starts. Titles are generated from the first question. Replies save when completed, stopped or failed. New chat detaches the current conversation; confirmation clears its prompt draft but keeps saved history.

The selector shows 20 conversations per page, most recently updated first. Use Previous chats / Next chats and Refresh, select a title and Open. Opening does not connect or send anything. It restores the saved server/model and text; Connect / refresh is required before continuing. A conversation stays bound to its original server and model. Start New chat to use another owner; unavailable models are not silently replaced. The answer language can change per turn.

Delete requires a second confirmation and removes that selected conversation and all its turns. Revision checks reject stale edits/deletion from another window. Opening a different conversation keeps an unsent prompt by refusing the switch; clear it explicitly first. Reopening the same conversation preserves that draft.

## Interrupted replies and failures

Stop keeps received text with a stopped status. Failed, stopped, pending and interrupted turns are excluded from model context. Normal window close/Quit saves the visible partial reply as interrupted, then cancels networking without blocking on a thread join. A failed reply save keeps text visible, disables sending/switching chats and offers Retry save reply. Quit stays open and shows AI Tutor until the reply is saved or explicitly discarded. Discard unsaved requires confirmation, preserves the next prompt and does not delete saved history.

An abrupt process/system crash can leave a saved pending question; streaming chunks are not checkpointed, so its partial answer may be lost. Reopen it and use Mark interrupted, then confirm, before sending another question. This is explicit because another window might still be generating. Recovery/deletion invalidates late writes from that window; copy its unsaved text before discarding/reloading.

## Storage, privacy and limits

`tutor_conversations` holds title, endpoint, model, revision and UTC timestamps. `tutor_turns` holds ordered prompt/answer/language/status and timestamps. Revision checks and writes share a transaction; known terminal retries are idempotent. Network workers still never access Tk or SQLite. No request is sent on startup, history opening, navigation or Settings Save. Send transmits only the selected chat's bounded completed context.

Chats are plaintext in the selected local database and included in backups. They are not encrypted or synchronized. Maximum 12 turns per conversation, 4,000 characters per question, 16,000 per answer; context uses at most six completed pairs / 24,000 characters. Partial/malformed replies never become completed context. AI answers still require verification.

Restore accepts standalone schema 7 backups only. Keep original older backups. To reuse your own schema 6 backup, make a separate copy, open that copy with the new app using --data so startup migrates it, then export a new backup with Create backup. Do not replace your working database to perform this conversion. Schema migration does not recreate chats from earlier session-only versions.
