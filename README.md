## How to Get Your Token

<img src="https://raw.githubusercontent.com/X5Coder/X5Models-Free/main/ai-platform-svgrepo-com.svg" width="80" height="80" alt="X5Models Free"/>

Follow these steps to generate your X5Models token:

1. Copy the Python script from [`start.py`](https://raw.githubusercontent.com/X5Coder/X5Models-Free/refs/heads/main/start.py).
2. Run the script using any Python editor on your PC or phone.
3. The script will display a verification URL similar to:

   ```text
   https://authkit.cline.bot/device?user_code=XXXX-XXXX
   ```
4. Open the URL in Chrome and sign in with your Google account.
5. Confirm the verification code shown on the page.
6. Return to the Python script and copy the generated token:

   ```text
   sk-xxxxxxxxxxxx
   ```
7. Paste the token into the token field above and connect.

You're ready to use X5Models Free.

---

## Use as an OpenAI-compatible API

Base URL: `https://x5models-free.x5coder.workers.dev/v1`

- `GET /v1/models` — full models list (no key needed for discovery).
- `POST /v1/chat/completions` — OpenAI format, `stream: true` returns real-time SSE.
- Header: `Authorization: Bearer sk-...`.
