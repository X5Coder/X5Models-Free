<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>X5Models Free</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">

<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }

  :root {
    --bg: #000;
    --line: #1a1a1a;
    --line-2: #1e1e1e;
    --txt: #e0e0e0;
    --mut: #6a6a6a;
    --mut-2: #4a4a4a;
    --err: #ff4d4d;
    --err-bg: #1a0808;
    --err-border: #3a1212;
  }

  html, body {
    height: 100%;
    background: var(--bg);
    color: var(--txt);
    font-family: 'Space Grotesk', sans-serif;
    overflow: hidden;
  }

  .layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    height: 100dvh;
    width: 100%;
  }

  /* Header */
  .header {
    padding: 14px 24px;
    border-bottom: 1px solid var(--line);
    display: flex;
    align-items: center;
    gap: 10px;
    flex-shrink: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    position: relative;
    z-index: 10;
  }

  .logo-dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: #fff;
    box-shadow: 0 0 10px rgba(255, 255, 255, 0.6);
    animation: pulse 1.8s ease-in-out infinite;
    flex-shrink: 0;
  }

  @keyframes pulse { 0%, 100% { opacity: 0.5; } 50% { opacity: 1; } }

  .header-title {
    font-size: 0.85rem;
    font-weight: 500;
    color: #888;
    letter-spacing: 0.02em;
    white-space: nowrap;
    text-decoration: none;
    transition: color 0.2s ease;
    cursor: pointer;
  }

  .header-title:hover { color: #fff; }

  .header-spacer { flex: 1; }

  .model-btn {
    display: none; align-items: center; gap: 8px;
    background: #0f0f0f; border: 1px solid var(--line-2);
    color: var(--txt); padding: 7px 12px; border-radius: 10px;
    font-family: inherit; font-size: 0.78rem; font-weight: 500;
    cursor: pointer; transition: background 0.2s ease, border-color 0.2s ease;
    white-space: nowrap; max-width: 220px;
  }

  .model-btn.show { display: inline-flex; }
  .model-btn:hover { background: #161616; border-color: #2a2a2a; }
  .model-btn .name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .model-btn svg { width: 10px; height: 10px; flex-shrink: 0; opacity: 0.6; }

  .icon-btn {
    display: none;
    background: transparent;
    border: 1px solid var(--line-2);
    color: #888;
    width: 32px; height: 32px;
    border-radius: 10px;
    cursor: pointer;
    align-items: center;
    justify-content: center;
    transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    flex-shrink: 0;
  }

  .icon-btn.show { display: flex; }
  .icon-btn:hover { background: #161616; border-color: #2a2a2a; color: #e0e0e0; }
  .icon-btn svg { width: 14px; height: 14px; }

  /* Login */
  .login-screen {
    flex: 1;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 40px 20px;
    transition: opacity 0.4s ease, transform 0.4s ease;
    overflow-y: auto;
  }

  .login-screen.hide {
    opacity: 0; transform: scale(0.96);
    pointer-events: none; position: absolute; inset: 0;
  }

  .login-box {
    width: 100%; max-width: 440px;
    display: flex; flex-direction: column; gap: 14px; text-align: center;
    margin: auto 0;
  }

  .login-icon {
    width: 56px; height: 56px; border-radius: 16px;
    background: linear-gradient(145deg, #141414, #0a0a0a);
    border: 1px solid #1f1f1f;
    display: flex; align-items: center; justify-content: center;
    margin: 0 auto 8px; color: #fff;
    transition: border-color 0.3s ease, background 0.3s ease, color 0.3s ease;
  }

  .login-icon svg { width: 26px; height: 26px; }

  .login-box.error .login-icon {
    border-color: var(--err-border);
    background: linear-gradient(145deg, #1a0808, #0a0404);
    color: var(--err);
  }

  .login-title {
    font-size: 1.4rem; font-weight: 600; color: #fff;
    letter-spacing: -0.02em; transition: color 0.3s ease;
  }

  .login-box.error .login-title { color: var(--err); }

  .login-sub {
    font-size: 0.82rem; color: var(--mut);
    margin-bottom: 8px; line-height: 1.5;
    transition: color 0.3s ease;
  }

  .login-box.error .login-sub { color: #a06060; }

  .login-input-wrap {
    display: flex; gap: 6px; align-items: center;
    background: #0a0a0a; border: 1px solid var(--line-2);
    border-radius: 12px; padding: 4px 4px 4px 14px;
    transition: border-color 0.3s ease, background 0.3s ease, box-shadow 0.3s ease;
  }

  .login-input-wrap:focus-within { border-color: #333; }

  .login-box.error .login-input-wrap {
    border-color: var(--err); background: var(--err-bg);
    box-shadow: 0 0 0 3px rgba(255, 77, 77, 0.08);
  }

  .login-input-wrap input {
    flex: 1; min-width: 0; background: transparent;
    border: 0; color: var(--txt); font-family: inherit;
    font-size: 0.88rem; outline: none; padding: 10px 0;
  }

  .login-input-wrap input::placeholder { color: var(--mut-2); }
  .login-box.error .login-input-wrap input::placeholder { color: #6a3030; }

  .login-input-wrap button {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    color: #e0e0e0; padding: 10px 16px; border-radius: 9px;
    font-family: inherit; font-size: 0.82rem; font-weight: 600;
    cursor: pointer; transition: background 0.2s ease, border-color 0.2s ease;
    white-space: nowrap; flex-shrink: 0;
  }

  .login-input-wrap button:hover:not(:disabled) { background: #222; border-color: #3a3a3a; }

  .login-box.error .login-input-wrap button {
    background: #2a0a0a; border-color: #3a1212; color: var(--err);
  }

  .login-box.error .login-input-wrap button:hover:not(:disabled) {
    background: #351010; border-color: #4a1818;
  }

  .login-input-wrap button:disabled { opacity: 0.5; cursor: not-allowed; }

  .login-error {
    display: flex; align-items: center; gap: 10px;
    padding: 12px 14px; border-radius: 12px;
    background: var(--err-bg); border: 1px solid var(--err-border);
    color: var(--err); font-size: 0.82rem; font-weight: 500;
    text-align: left; line-height: 1.4;
    max-height: 0; padding-top: 0; padding-bottom: 0;
    opacity: 0; overflow: hidden;
    transition: max-height 0.35s cubic-bezier(0.4, 0, 0.2, 1),
                opacity 0.3s ease, padding 0.3s ease;
  }

  .login-error.show {
    max-height: 120px; padding-top: 12px; padding-bottom: 12px; opacity: 1;
  }

  .login-error svg { width: 18px; height: 18px; flex-shrink: 0; }

  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    20% { transform: translateX(-8px); }
    40% { transform: translateX(8px); }
    60% { transform: translateX(-5px); }
    80% { transform: translateX(5px); }
  }

  .login-box.shake .login-input-wrap {
    animation: shake 0.45s cubic-bezier(0.36, 0.07, 0.19, 0.97);
  }

  /* Steps section */
  .login-steps {
    text-align: left;
    background: #060606;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 18px;
    margin-top: 6px;
  }

  .login-steps-head {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.78rem;
    font-weight: 600;
    color: #b0b0b0;
    letter-spacing: 0.02em;
    margin-bottom: 14px;
    text-transform: uppercase;
  }

  .login-steps-head svg {
    width: 14px; height: 14px;
    color: #6a6a6a;
  }

  .steps-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 12px;
    counter-reset: step;
  }

  .steps-list li {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    font-size: 0.78rem;
    color: #909090;
    line-height: 1.55;
    counter-increment: step;
  }

  .steps-list li::before {
    content: counter(step);
    width: 20px;
    height: 20px;
    border-radius: 6px;
    background: #101010;
    border: 1px solid #1e1e1e;
    color: #888;
    font-size: 0.7rem;
    font-weight: 600;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
  }

  .steps-list a {
    color: #d0d0d0;
    text-decoration: none;
    border-bottom: 1px dashed #2a2a2a;
    transition: color 0.2s ease, border-color 0.2s ease;
    word-break: break-all;
  }

  .steps-list a:hover {
    color: #fff;
    border-color: #4a4a4a;
  }

  .steps-list code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.72rem;
    background: #101010;
    border: 1px solid #1e1e1e;
    padding: 1px 5px;
    border-radius: 4px;
    color: #c0c0c0;
    word-break: break-all;
  }

  /* Chat */
  .chat-screen { flex: 1; display: none; flex-direction: column; min-height: 0; }
  .chat-screen.show { display: flex; }

  .chat {
    flex: 1; overflow-y: auto; padding: 24px;
    display: flex; flex-direction: column; gap: 18px;
    max-width: 780px; width: 100%; margin: 0 auto;
  }

  .chat::-webkit-scrollbar { width: 6px; }
  .chat::-webkit-scrollbar-thumb { background: #222; border-radius: 3px; }

  .msg {
    max-width: 85%; padding: 10px 14px; border-radius: 14px;
    font-size: 0.92rem; line-height: 1.55;
    white-space: pre-wrap; word-break: break-word;
    animation: msgIn 0.3s ease;
  }

  @keyframes msgIn {
    from { opacity: 0; transform: translateY(6px); }
    to { opacity: 1; transform: translateY(0); }
  }

  .msg.user {
    align-self: flex-end; background: #1a1a1a; color: #e0e0e0;
    border-bottom-right-radius: 4px;
  }

  .msg.error {
    align-self: flex-start; background: var(--err-bg);
    border: 1px solid var(--err-border); color: var(--err);
    font-size: 0.82rem; max-width: 100%;
  }

  /* Thinking Block - Working only, no steps, no arrow */
  .thinking-block {
    align-self: flex-start;
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 4px 0;
  }

  .dot-square {
    display: grid; grid-template-columns: repeat(5, 1fr);
    gap: 2px; align-self: center;
  }

  .dot-square span {
    width: 2px; height: 2px; border-radius: 50%;
    background: #0f0f0f; box-shadow: none;
    transition: background 0.18s ease-out, box-shadow 0.18s ease-out;
  }

  .dot-square span.on {
    background: #ffffff;
    box-shadow: 0 0 3px rgba(255, 255, 255, 0.85), 0 0 6px rgba(255, 255, 255, 0.35);
  }

  .thinking-block.done .dot-square span {
    transition: background 0.7s cubic-bezier(0.4, 0, 0.2, 1),
                box-shadow 0.7s cubic-bezier(0.4, 0, 0.2, 1);
  }

  .thinking-block.done .dot-square span.lit-white {
    background: #ffffff;
    box-shadow: 0 0 3px rgba(255, 255, 255, 0.85), 0 0 6px rgba(255, 255, 255, 0.35);
  }

  .thinking-block.done .dot-square span.lit-black {
    background: #2a2a2a; box-shadow: none;
  }

  .working-text {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 0.95rem; font-weight: 700;
    letter-spacing: -0.02em; white-space: nowrap;
    background-image: repeating-linear-gradient(
      90deg, #ffffff 0px, #ffffff 55px, #4a4a4a 100px, #ffffff 145px, #ffffff 200px
    );
    background-size: 200px 100%; background-repeat: repeat;
    -webkit-background-clip: text; background-clip: text;
    -webkit-text-fill-color: transparent; color: transparent;
    animation: continuousWave 2.8s linear infinite;
  }

  @keyframes continuousWave {
    0% { background-position: 0px 0; }
    100% { background-position: 200px 0; }
  }

  .thinking-block.done .working-text {
    animation: none; background-image: none;
    -webkit-text-fill-color: #ffffff; color: #ffffff;
  }

  .final {
    align-self: flex-start; max-width: 100%;
    font-size: 0.92rem; line-height: 1.7; color: #d0d0d0;
    padding: 4px 0; white-space: pre-wrap; word-break: break-word;
  }

  .cursor {
    display: inline-block; width: 7px; height: 15px;
    background: #d0d0d0; vertical-align: text-bottom;
    margin-left: 2px;
    animation: blink 0.9s steps(2, start) infinite;
  }

  @keyframes blink { to { visibility: hidden; } }

  /* Composer */
  .composer-wrap {
    border-top: 1px solid var(--line);
    padding: 16px 24px 24px; flex-shrink: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
  }

  .composer {
    display: flex; gap: 10px; align-items: center;
    max-width: 780px; margin: 0 auto;
    background: #0a0a0a; border: 1px solid var(--line-2);
    border-radius: 14px; padding: 4px 4px 4px 18px;
    transition: border-color 0.2s ease;
  }

  .composer:focus-within { border-color: #333; }

  .composer input {
    flex: 1; min-width: 0; background: transparent;
    border: 0; color: var(--txt); font-family: inherit;
    font-size: 0.9rem; outline: none; padding: 12px 0;
  }

  .composer input::placeholder { color: var(--mut-2); }

  .send-btn {
    background: #1a1a1a; border: 1px solid #2a2a2a;
    color: #e0e0e0; width: 42px; height: 42px; border-radius: 11px;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: background 0.2s ease, border-color 0.2s ease, transform 0.1s ease;
    flex-shrink: 0;
  }

  .send-btn:hover:not(:disabled) { background: #222; border-color: #3a3a3a; }
  .send-btn:active:not(:disabled) { transform: scale(0.94); }
  .send-btn:disabled { opacity: 0.4; cursor: not-allowed; }
  .send-btn svg { width: 16px; height: 16px; pointer-events: none; }

  /* Dialog base */
  .dialog-overlay {
    position: fixed; inset: 0;
    background: rgba(0, 0, 0, 0.6);
    backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px);
    opacity: 0; pointer-events: none;
    transition: opacity 0.3s ease; z-index: 100;
  }

  .dialog-overlay.show { opacity: 1; pointer-events: auto; }

  .dialog {
    position: fixed; left: 50%; bottom: 0;
    transform: translate(-50%, 100%);
    width: 100%; max-width: 520px;
    background: #0a0a0a; border: 1px solid var(--line-2); border-bottom: 0;
    border-radius: 20px 20px 0 0; padding: 0 20px 20px;
    transition: transform 0.45s cubic-bezier(0.16, 1, 0.3, 1);
    z-index: 101; max-height: 80vh;
    display: flex; flex-direction: column;
    box-shadow: 0 -20px 60px rgba(0, 0, 0, 0.7);
    will-change: transform;
  }

  .dialog.show { transform: translate(-50%, 0); }

  .dialog-drag-area {
    padding: 12px 0 4px;
    cursor: grab;
    user-select: none;
    touch-action: none;
    flex-shrink: 0;
  }

  .dialog-drag-area:active { cursor: grabbing; }

  .dialog-handle {
    width: 40px; height: 4px; background: #2a2a2a;
    border-radius: 2px; margin: 0 auto 16px;
  }

  .dialog-title {
    font-size: 1rem; font-weight: 600; color: #fff;
    letter-spacing: -0.01em; margin-bottom: 4px;
  }

  .dialog-sub { font-size: 0.78rem; color: var(--mut); margin-bottom: 16px; }

  /* Model list */
  .model-list {
    overflow-y: auto; display: flex; flex-direction: column;
    gap: 6px; flex: 1; min-height: 0;
    margin: 0 -6px; padding: 0 6px;
  }

  .model-list::-webkit-scrollbar { width: 4px; }
  .model-list::-webkit-scrollbar-thumb { background: #222; border-radius: 2px; }

  .model-item {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 14px; border-radius: 12px;
    background: transparent; border: 1px solid transparent;
    cursor: pointer; transition: background 0.2s ease, border-color 0.2s ease;
    text-align: left; width: 100%; font-family: inherit; color: var(--txt);
    opacity: 0; transform: translateY(8px);
    animation: dialogItemIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
  }

  @keyframes dialogItemIn { to { opacity: 1; transform: translateY(0); } }

  .model-item:hover { background: #101010; border-color: var(--line-2); }
  .model-item.active { background: #101010; border-color: #2a2a2a; }

  .model-item-icon {
    width: 32px; height: 32px; border-radius: 9px;
    background: linear-gradient(145deg, #141414, #0a0a0a);
    border: 1px solid #1f1f1f;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; color: #888;
  }

  .model-item.active .model-item-icon {
    background: #1a1a1a; border-color: #2a2a2a; color: #fff;
  }

  .model-item-icon svg { width: 14px; height: 14px; }

  .model-item-info { flex: 1; min-width: 0; }

  .model-item-name {
    font-size: 0.86rem; font-weight: 500; color: #d0d0d0;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }

  .model-item.active .model-item-name { color: #fff; }

  .model-item-id {
    font-size: 0.72rem; color: var(--mut); margin-top: 2px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  }

  .model-item-check { color: #4ade80; flex-shrink: 0; display: none; }
  .model-item.active .model-item-check { display: block; }
  .model-item-check svg { width: 16px; height: 16px; }

  /* Info dialog - specific */
  .info-list {
    overflow-y: auto;
    display: flex;
    flex-direction: column;
    gap: 14px;
    padding: 0 2px 4px;
  }

  .info-list::-webkit-scrollbar { width: 4px; }
  .info-list::-webkit-scrollbar-thumb { background: #222; border-radius: 2px; }

  .info-section {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .info-label {
    font-size: 0.68rem;
    color: #555;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }

  .info-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.74rem;
    color: #d0d0d0;
    background: #060606;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 10px 12px;
    word-break: break-all;
    line-height: 1.55;
  }

  .info-value.masked {
    color: #6a6a6a;
  }

  .info-row {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .info-row .info-value {
    flex: 1;
    min-width: 0;
  }

  .info-reveal {
    background: #101010;
    border: 1px solid var(--line-2);
    color: #888;
    width: 34px;
    height: 34px;
    border-radius: 10px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: background 0.2s ease, border-color 0.2s ease, color 0.2s ease;
    flex-shrink: 0;
  }

  .info-reveal:hover { background: #161616; border-color: #2a2a2a; color: #e0e0e0; }
  .info-reveal svg { width: 14px; height: 14px; }

  .info-pre {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #b0b0b0;
    background: #060606;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 12px 14px;
    white-space: pre;
    overflow-x: auto;
    line-height: 1.7;
  }

  .info-pre::-webkit-scrollbar { height: 4px; }
  .info-pre::-webkit-scrollbar-thumb { background: #222; border-radius: 2px; }

  .info-pre .k { color: #c0c0c0; }
  .info-pre .s { color: #8ab4ff; }
  .info-pre .p { color: #888; }

  /* Connecting */
  .connecting {
    position: fixed; inset: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(6px); -webkit-backdrop-filter: blur(6px);
    display: none; align-items: center; justify-content: center;
    z-index: 200;
  }

  .connecting.show { display: flex; }

  .connecting-box {
    display: flex; flex-direction: column;
    align-items: center; gap: 16px;
  }

  .connecting .dot-square {
    grid-template-columns: repeat(5, 1fr); gap: 3px;
  }

  .connecting .dot-square span { width: 3px; height: 3px; }

  .connecting-text {
    font-size: 0.82rem; color: var(--mut); letter-spacing: 0.02em;
  }

  @media (max-width: 640px) {
    .header { padding: 12px 16px; }
    .chat { padding: 16px; }
    .composer-wrap { padding: 12px 16px 16px; }
    .msg { max-width: 92%; font-size: 0.88rem; }
    .header-title { font-size: 0.8rem; }
    .login-screen { padding: 24px 16px; }
  }
</style>
</head>
<body>

  <div class="layout">

    <div class="header">
      <span class="logo-dot"></span>
      <a class="header-title" href="https://github.com/X5Coder/X5Models-Free" target="_blank" rel="noopener noreferrer">X5Models Free</a>
      <div class="header-spacer"></div>

      <button class="model-btn" id="modelBtn">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="3" width="7" height="7" rx="1.5"/>
          <rect x="14" y="3" width="7" height="7" rx="1.5"/>
          <rect x="3" y="14" width="7" height="7" rx="1.5"/>
          <rect x="14" y="14" width="7" height="7" rx="1.5"/>
        </svg>
        <span class="name" id="modelBtnName">Select model</span>
      </button>

      <button class="icon-btn" id="infoBtn" title="Connection info">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="16" x2="12" y2="12"/>
          <line x1="12" y1="8" x2="12.01" y2="8"/>
        </svg>
      </button>

      <button class="icon-btn" id="logoutBtn" title="Disconnect">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </div>

    <!-- ============================================
         Login Screen
    ============================================ -->
    <div class="login-screen" id="loginScreen">
      <div class="login-box" id="loginBox">
        <div class="login-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M12 2 L2 7 L12 12 L22 7 Z"/>
            <path d="M2 17 L12 22 L22 17"/>
            <path d="M2 12 L12 17 L22 12"/>
          </svg>
        </div>
        <div class="login-title">Connect to X5Models</div>
        <div class="login-sub">Paste your access token to start</div>

        <div class="login-input-wrap" id="loginWrap">
          <input type="password" id="tok" placeholder="sk-..." autocomplete="off" spellcheck="false">
          <button id="go" type="button">Connect</button>
        </div>

        <div class="login-error" id="loginError">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          <span id="loginErrorText">Invalid token. Please check and try again.</span>
        </div>

        <!-- Steps -->
        <div class="login-steps">
          <div class="login-steps-head">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 20h9"/>
              <path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/>
            </svg>
            How to get your token
          </div>
          <ol class="steps-list">
            <li>
              Copy the Python script from
              <a href="https://raw.githubusercontent.com/X5Coder/X5Models-Free/refs/heads/main/start.py" target="_blank" rel="noopener noreferrer">start.py</a>
            </li>
            <li>
              Run it in any Python editor on your PC or phone
            </li>
            <li>
              It will print a URL like
              <code>https://authkit.cline.bot/device?user_code=XXXX-XXXX</code>
            </li>
            <li>
              Open that URL in Chrome and sign in with your Google account
            </li>
            <li>
              Confirm the code shown on the page, then go back to the script
            </li>
            <li>
              Copy the token shown in the terminal
              <code>sk-xxxxxxxxxxxx</code>
              and paste it above
            </li>
          </ol>
        </div>
      </div>
    </div>

    <!-- ============================================
         Chat Screen
    ============================================ -->
    <div class="chat-screen" id="chatScreen">
      <div class="chat" id="chat"></div>

      <div class="composer-wrap">
        <form class="composer" id="composer" autocomplete="off">
          <input type="text" id="input" placeholder="Type a message..." autocomplete="off">
          <button type="submit" class="send-btn" id="sendBtn" aria-label="Send">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M22 2 L11 13"/>
              <path d="M22 2 L15 22 L11 13 L2 9 Z"/>
            </svg>
          </button>
        </form>
      </div>
    </div>

  </div>

  <!-- Model dialog -->
  <div class="dialog-overlay" id="dialogOverlay"></div>
  <div class="dialog" id="dialog">
    <div class="dialog-drag-area" id="dialogDragArea">
      <div class="dialog-handle"></div>
      <div class="dialog-title">Select a model</div>
      <div class="dialog-sub">Choose which AI model to chat with</div>
    </div>
    <div class="model-list" id="modelList"></div>
  </div>

  <!-- Info dialog -->
  <div class="dialog-overlay" id="infoOverlay"></div>
  <div class="dialog" id="infoDialog">
    <div class="dialog-drag-area" id="infoDragArea">
      <div class="dialog-handle"></div>
      <div class="dialog-title">Connection Info</div>
      <div class="dialog-sub">Details about your current session</div>
    </div>
    <div class="info-list" id="infoList"></div>
  </div>

  <div class="connecting" id="connecting">
    <div class="connecting-box">
      <div class="dot-square" id="connectingDots"></div>
      <div class="connecting-text">Connecting...</div>
    </div>
  </div>

  <script>
    /* ============================================
       Config
    ============================================ */
    const API_URL = "https://script.google.com/macros/s/AKfycbwE4MgcyATsiJUUUvArDC1BX5JLpeinJUvgFG7_3vwNBgny-BSoSS28dPoWu2fMeUA7/exec";
    const STORAGE_KEY = "x5models_token";
    const MODEL_KEY = "x5models_model";
    const FETCH_TIMEOUT = 20000;

    /* ============================================
       State
    ============================================ */
    let token = "";
    let history = [];
    let isProcessing = false;
    let currentModel = null;
    let modelsList = [];
    let connectingBusy = false;
    let tokenRevealed = false;

    /* ============================================
       Elements
    ============================================ */
    const chat = document.getElementById('chat');
    const composer = document.getElementById('composer');
    const input = document.getElementById('input');
    const sendBtn = document.getElementById('sendBtn');
    const tokInput = document.getElementById('tok');
    const goBtn = document.getElementById('go');
    const loginScreen = document.getElementById('loginScreen');
    const loginBox = document.getElementById('loginBox');
    const chatScreen = document.getElementById('chatScreen');
    const modelBtn = document.getElementById('modelBtn');
    const modelBtnName = document.getElementById('modelBtnName');
    const infoBtn = document.getElementById('infoBtn');
    const logoutBtn = document.getElementById('logoutBtn');
    const dialog = document.getElementById('dialog');
    const dialogOverlay = document.getElementById('dialogOverlay');
    const dialogDragArea = document.getElementById('dialogDragArea');
    const modelList = document.getElementById('modelList');
    const infoDialog = document.getElementById('infoDialog');
    const infoOverlay = document.getElementById('infoOverlay');
    const infoDragArea = document.getElementById('infoDragArea');
    const infoList = document.getElementById('infoList');
    const connectingEl = document.getElementById('connecting');
    const connectingDots = document.getElementById('connectingDots');
    const loginError = document.getElementById('loginError');
    const loginErrorText = document.getElementById('loginErrorText');

    /* ============================================
       Helpers
    ============================================ */
    function scrollBottom() { chat.scrollTop = chat.scrollHeight; }
    function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
    function escapeHtml(str) {
      const div = document.createElement('div');
      div.textContent = str == null ? "" : str;
      return div.innerHTML;
    }

    async function gasFetch(url, options = {}) {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT);
      try {
        const res = await fetch(url, {
          ...options,
          signal: controller.signal,
          redirect: "follow",
          cache: "no-store"
        });
        clearTimeout(timer);
        const text = await res.text();
        try { return JSON.parse(text); }
        catch (e) { return { _raw: text, _parseError: true }; }
      } catch (e) {
        clearTimeout(timer);
        throw e;
      }
    }

    /* ============================================
       Login Error UI
    ============================================ */
    let errorTimer = null;

    function showLoginError(message) {
      loginErrorText.textContent = message;
      loginError.classList.add('show');
      loginBox.classList.add('error');

      loginBox.classList.remove('shake');
      void loginBox.offsetWidth;
      loginBox.classList.add('shake');

      clearTimeout(errorTimer);
      errorTimer = setTimeout(() => loginBox.classList.remove('shake'), 500);
    }

    function clearLoginError() {
      loginError.classList.remove('show');
      loginBox.classList.remove('error');
      loginBox.classList.remove('shake');
    }

    /* ============================================
       Connecting Dots Animation
    ============================================ */
    function buildDotSquare(container) {
      container.innerHTML = '';
      const SIZE = 5;
      const center = 2;
      for (let row = 0; row < SIZE; row++) {
        for (let col = 0; col < SIZE; col++) {
          const dot = document.createElement('span');
          const ring = Math.max(Math.abs(row - center), Math.abs(col - center));
          dot.dataset.ring = ring;
          container.appendChild(dot);
        }
      }
    }

    const connectingAnim = {
      timers: [],
      stopped: false,
      start() {
        this.stopped = false;
        const dots = [...connectingDots.querySelectorAll('span')];
        const rings = [[], [], []];
        dots.forEach(d => rings[+d.dataset.ring].push(d));

        const runCycle = () => {
          if (this.stopped) return;
          dots.forEach(d => d.classList.remove('on'));
          this.timers.push(setTimeout(() => { if (!this.stopped) rings[0].forEach(d => d.classList.add('on')); }, 60));
          this.timers.push(setTimeout(() => { if (!this.stopped) rings[1].forEach(d => d.classList.add('on')); }, 360));
          this.timers.push(setTimeout(() => { if (!this.stopped) rings[2].forEach(d => d.classList.add('on')); }, 660));
          this.timers.push(setTimeout(() => { if (!this.stopped) dots.forEach(d => d.classList.remove('on')); }, 1300));
          this.timers.push(setTimeout(runCycle, 1600));
        };
        runCycle();
      },
      stop() {
        this.stopped = true;
        this.timers.forEach(t => clearTimeout(t));
        this.timers = [];
      }
    };

    /* ============================================
       Connect
    ============================================ */
    async function connect(t, silent = false) {
      if (connectingBusy) return;
      connectingBusy = true;

      t = (t || tokInput.value).trim();
      if (!t) {
        connectingBusy = false;
        if (!silent) {
          showLoginError("Please enter a token to continue.");
          tokInput.focus();
        }
        return;
      }

      if (!silent) clearLoginError();
      goBtn.disabled = true;
      tokInput.disabled = true;

      if (!silent) {
        buildDotSquare(connectingDots);
        connectingEl.classList.add('show');
        connectingAnim.start();
      }

      const finish = (ok, errMsg) => {
        connectingBusy = false;
        connectingAnim.stop();
        connectingEl.classList.remove('show');
        goBtn.disabled = false;
        tokInput.disabled = false;
        if (!ok && !silent) showLoginError(errMsg || "Something went wrong.");
        else if (!ok && silent) { tokInput.value = ""; tokInput.focus(); }
      };

      try {
        const url = API_URL + "?action=models&token=" + encodeURIComponent(t);
        const data = await gasFetch(url, { method: "GET" });

        if (!data || data._parseError) { finish(false, "Invalid response from server."); return; }

        if (data.error) {
          const msg = (data.error && data.error.message) || "";
          if (/invalid|unauthor|forbidden|token|auth|denied|expired/i.test(msg)) {
            finish(false, "Invalid token. Please check and try again.");
          } else {
            finish(false, msg || "Server returned an error.");
          }
          return;
        }

        const list = data.data;
        if (!list || !list.length) { finish(false, "No models available with this token."); return; }

        token = t;
        modelsList = list;

        try { localStorage.setItem(STORAGE_KEY, token); } catch (e) {}

        let savedModelId = null;
        try { savedModelId = localStorage.getItem(MODEL_KEY); } catch (e) {}

        currentModel = modelsList.find(m => m.id === savedModelId) || modelsList[0];

        loginScreen.classList.add('hide');
        chatScreen.classList.add('show');
        modelBtn.classList.add('show');
        infoBtn.classList.add('show');
        logoutBtn.classList.add('show');
        modelBtnName.textContent = currentModel.label || currentModel.id;

        finish(true);
        input.focus();

      } catch (e) {
        const msg = (e && e.message) || "";
        const isTimeout = /abort|timeout/i.test(msg);
        const isNetwork = /network|failed to fetch|load failed/i.test(msg);
        if (isTimeout) finish(false, "Connection timed out. Please check your internet and try again.");
        else if (isNetwork) finish(false, "Unable to reach server. Please check your internet.");
        else finish(false, "Connection failed. Please try again.");
      }
    }

    /* ============================================
       Auto-restore
    ============================================ */
    async function autoRestore() {
      let saved = null;
      try { saved = localStorage.getItem(STORAGE_KEY); } catch (e) {}
      if (!saved) { tokInput.focus(); return; }
      tokInput.value = saved;
      await connect(saved, true);
    }

    /* ============================================
       Drag-to-dismiss (Model dialog + Info dialog)
    ============================================ */
    function setupDragToDismiss(dialogEl, overlayEl, dragArea, onClose) {
      let startY = 0;
      let currentY = 0;
      let dragging = false;

      const start = (y) => {
        startY = y;
        currentY = y;
        dragging = true;
        dialogEl.style.transition = 'none';
      };

      const move = (y) => {
        if (!dragging) return;
        currentY = y;
        const diff = Math.max(0, currentY - startY);
        dialogEl.style.transform = `translate(-50%, ${diff}px)`;
        const op = Math.max(0, 1 - diff / 400);
        overlayEl.style.opacity = op;
      };

      const end = () => {
        if (!dragging) return;
        dragging = false;
        const diff = currentY - startY;
        dialogEl.style.transition = '';
        overlayEl.style.opacity = '';
        if (diff > 100) {
          onClose();
        } else {
          dialogEl.style.transform = '';
        }
      };

      dragArea.addEventListener('pointerdown', (e) => {
        if (e.button !== undefined && e.button !== 0) return;
        start(e.clientY);
        try { dragArea.setPointerCapture(e.pointerId); } catch (err) {}
      });
      dragArea.addEventListener('pointermove', (e) => {
        if (dragging) {
          move(e.clientY);
          if (e.cancelable) e.preventDefault();
        }
      });
      dragArea.addEventListener('pointerup', end);
      dragArea.addEventListener('pointercancel', end);
      dragArea.addEventListener('pointerleave', () => { if (dragging) end(); });
    }

    /* ============================================
       Model Dialog
    ============================================ */
    function openDialog() {
      modelList.innerHTML = '';
      modelsList.forEach((m, idx) => {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'model-item' + (m.id === currentModel?.id ? ' active' : '');
        item.style.animationDelay = (idx * 0.03) + 's';

        item.innerHTML = `
          <div class="model-item-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M12 2 L2 7 L12 12 L22 7 Z"/>
              <path d="M2 17 L12 22 L22 17"/>
              <path d="M2 12 L12 17 L22 12"/>
            </svg>
          </div>
          <div class="model-item-info">
            <div class="model-item-name">${escapeHtml(m.label || m.id)}</div>
            <div class="model-item-id">${escapeHtml(m.id)}</div>
          </div>
          <div class="model-item-check">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </div>
        `;

        item.addEventListener('click', () => {
          currentModel = m;
          modelBtnName.textContent = m.label || m.id;
          try { localStorage.setItem(MODEL_KEY, m.id); } catch (e) {}
          closeDialog();
        });

        modelList.appendChild(item);
      });

      dialogOverlay.classList.add('show');
      requestAnimationFrame(() => dialog.classList.add('show'));
    }

    function closeDialog() {
      dialog.classList.remove('show');
      dialogOverlay.classList.remove('show');
      dialog.style.transform = '';
    }

    /* ============================================
       Info Dialog
    ============================================ */
    function maskToken(t) {
      if (!t) return "";
      if (t.length <= 12) return t;
      return t.slice(0, 8) + "•".repeat(Math.min(20, t.length - 12)) + t.slice(-4);
    }

    function buildInfoDialog() {
      const displayToken = tokenRevealed ? token : maskToken(token);
      const exampleJSON = `{
  "model": "${escapeHtml(currentModel?.id || "model-id")}",
  "messages": [
    { "role": "user", "content": "Hello" }
  ],
  "max_tokens": 800,
  "_tok": "sk-..."
}`;

      infoList.innerHTML = `
        <div class="info-section">
          <div class="info-label">Server</div>
          <div class="info-value">${escapeHtml(API_URL)}</div>
        </div>

        <div class="info-section">
          <div class="info-label">Token</div>
          <div class="info-row">
            <div class="info-value ${tokenRevealed ? '' : 'masked'}" id="tokenDisplay">${escapeHtml(displayToken)}</div>
            <button class="info-reveal" id="revealBtn" type="button" title="Toggle token visibility">
              ${tokenRevealed ? `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                  <line x1="1" y1="1" x2="23" y2="23"/>
                </svg>
              ` : `
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                  <circle cx="12" cy="12" r="3"/>
                </svg>
              `}
            </button>
          </div>
        </div>

        <div class="info-section">
          <div class="info-label">Current Model</div>
          <div class="info-value">${escapeHtml(currentModel?.id || "—")}</div>
        </div>

        <div class="info-section">
          <div class="info-label">API Format (OpenAI compatible)</div>
          <div class="info-pre"><span class="p">POST</span> <span class="s">{server}?action=chat</span>
<span class="p">Content-Type:</span> <span class="s">application/json</span>

${exampleJSON}</div>
        </div>
      `;

      // Bind reveal button
      const revealBtn = infoList.querySelector('#revealBtn');
      if (revealBtn) {
        revealBtn.addEventListener('click', () => {
          tokenRevealed = !tokenRevealed;
          buildInfoDialog();
        });
      }
    }

    function openInfo() {
      if (!token) return;
      buildInfoDialog();
      infoOverlay.classList.add('show');
      requestAnimationFrame(() => infoDialog.classList.add('show'));
    }

    function closeInfo() {
      infoDialog.classList.remove('show');
      infoOverlay.classList.remove('show');
      infoDialog.style.transform = '';
      tokenRevealed = false;
    }

    /* ============================================
       Dot Square Animation
    ============================================ */
    const squareAnimations = new Map();

    function startSquareAnimation(square) {
      stopSquareAnimation(square);

      const dots = [...square.querySelectorAll('span')];
      const rings = [[], [], []];
      dots.forEach(dot => rings[+dot.dataset.ring].push(dot));

      let timers = [];
      let stopped = false;

      function runCycle() {
        if (stopped) return;
        dots.forEach(d => d.classList.remove('on'));
        timers.push(setTimeout(() => { if (!stopped) rings[0].forEach(d => d.classList.add('on')); }, 60));
        timers.push(setTimeout(() => { if (!stopped) rings[1].forEach(d => d.classList.add('on')); }, 360));
        timers.push(setTimeout(() => { if (!stopped) rings[2].forEach(d => d.classList.add('on')); }, 660));
        timers.push(setTimeout(() => { if (!stopped) dots.forEach(d => d.classList.remove('on')); }, 1300));
        timers.push(setTimeout(runCycle, 1600));
      }

      squareAnimations.set(square, {
        stop: () => {
          stopped = true;
          timers.forEach(t => clearTimeout(t));
          timers = [];
        }
      });
      runCycle();
    }

    function stopSquareAnimation(square) {
      const anim = squareAnimations.get(square);
      if (anim) { anim.stop(); squareAnimations.delete(square); }
    }

    /* ============================================
       Message Helpers
    ============================================ */
    function addUserMessage(text) {
      const el = document.createElement('div');
      el.className = 'msg user';
      el.textContent = text;
      chat.appendChild(el);
      scrollBottom();
      return el;
    }

    function addErrorMessage(text) {
      const el = document.createElement('div');
      el.className = 'msg error';
      el.textContent = text;
      chat.appendChild(el);
      scrollBottom();
      return el;
    }

    /* ============================================
       Thinking Block (Working only — no steps, no arrow)
    ============================================ */
    function createDotSquare() {
      const square = document.createElement('div');
      square.className = 'dot-square';
      const SIZE = 5;
      const center = 2;
      for (let row = 0; row < SIZE; row++) {
        for (let col = 0; col < SIZE; col++) {
          const dot = document.createElement('span');
          const ring = Math.max(Math.abs(row - center), Math.abs(col - center));
          dot.dataset.ring = ring;
          const isWhite = row >= 1 && row <= 3 && col >= 1 && col <= 3;
          if (isWhite) dot.classList.add('lit-white');
          else dot.classList.add('lit-black');
          square.appendChild(dot);
        }
      }
      return square;
    }

    function createThinkingBlock() {
      const block = document.createElement('div');
      block.className = 'thinking-block';

      const dotSquare = createDotSquare();

      const workingText = document.createElement('span');
      workingText.className = 'working-text';
      workingText.textContent = 'Working';

      block.appendChild(dotSquare);
      block.appendChild(workingText);

      chat.appendChild(block);
      scrollBottom();

      startSquareAnimation(dotSquare);
      block._dotSquare = dotSquare;
      return block;
    }

    function finishThinkingBlock(block) {
      if (block._dotSquare) {
        stopSquareAnimation(block._dotSquare);
        block._dotSquare.querySelectorAll('span').forEach(d => d.classList.remove('on'));
      }
      block.classList.add('done');
    }

    /* ============================================
       Chat Request — SSE + JSON fallback
    ============================================ */
    async function sendChat(payload, onDelta, onDone, onError) {
      try {
        const res = await fetch(API_URL + "?action=chat", {
          method: "POST",
          body: JSON.stringify(payload),
          headers: { "Accept": "text/event-stream, application/json" },
          redirect: "follow"
        });

        if (!res.ok) {
          onError("Server error: HTTP " + res.status);
          return;
        }

        const contentType = (res.headers.get("content-type") || "").toLowerCase();

        // -------- SSE streaming path --------
        if (contentType.includes("event-stream") && res.body && res.body.getReader) {
          const reader = res.body.getReader();
          const decoder = new TextDecoder();
          let buffer = "";
          let finished = false;

          while (!finished) {
            const { value, done: rdone } = await reader.read();
            if (rdone) break;

            buffer += decoder.decode(value, { stream: true });

            let idx;
            while ((idx = buffer.indexOf("\n\n")) !== -1) {
              const event = buffer.slice(0, idx);
              buffer = buffer.slice(idx + 2);

              const lines = event.split("\n");
              for (const line of lines) {
                const trimmed = line.trim();
                if (!trimmed.startsWith("data:")) continue;
                const data = trimmed.slice(5).trim();
                if (data === "[DONE]") { finished = true; break; }

                try {
                  const parsed = JSON.parse(data);
                  if (parsed.error) { onError(parsed.error.message || "Server error"); return; }
                  const delta = parsed.choices?.[0]?.delta?.content;
                  const msg = parsed.choices?.[0]?.message?.content;
                  const chunk = delta != null ? delta : msg;
                  if (chunk) onDelta(chunk);
                } catch (e) { /* ignore non-JSON line */ }
              }
              if (finished) break;
            }
          }
          onDone();
          return;
        }

        // -------- Text response path --------
        const text = await res.text();
        const trimmedAll = text.trim();

        // SSE-formatted body delivered as one chunk
        if (trimmedAll.startsWith("data:")) {
          const lines = trimmedAll.split("\n");
          for (const line of lines) {
            const trimmed = line.trim();
            if (!trimmed.startsWith("data:")) continue;
            const data = trimmed.slice(5).trim();
            if (data === "[DONE]") continue;
            try {
              const parsed = JSON.parse(data);
              if (parsed.error) { onError(parsed.error.message || "Server error"); return; }
              const delta = parsed.choices?.[0]?.delta?.content;
              const msg = parsed.choices?.[0]?.message?.content;
              const chunk = delta != null ? delta : msg;
              if (chunk) onDelta(chunk);
            } catch (e) {}
          }
          onDone();
          return;
        }

        // Plain JSON
        try {
          const parsed = JSON.parse(trimmedAll);
          if (parsed.error) { onError(parsed.error.message || "Server error"); return; }
          const content = parsed.choices?.[0]?.message?.content || "";
          if (content) onDelta(content);
          onDone();
        } catch (e) {
          onError("Invalid response from server");
        }
      } catch (e) {
        onError((e && e.message) || "Network error");
      }
    }

    /* ============================================
       Send
    ============================================ */
    async function handleSend() {
      const text = input.value.trim();
      if (!text || !token || !currentModel || isProcessing) return;

      isProcessing = true;
      input.value = '';
      sendBtn.disabled = true;

      addUserMessage(text);
      history.push({ role: "user", content: text });

      const block = createThinkingBlock();

      // Prepare the final element (only inserted on first delta)
      const final = document.createElement('div');
      final.className = 'final';
      const textNode = document.createElement('span');
      const cursor = document.createElement('span');
      cursor.className = 'cursor';
      final.appendChild(textNode);
      final.appendChild(cursor);

      let hasContent = false;
      let fullContent = "";
      let errorMsg = null;

      await new Promise((resolve) => {
        sendChat(
          {
            model: currentModel.id,
            messages: history.slice(-20),
            max_tokens: 800,
            _tok: token
          },
          (delta) => {
            if (!hasContent) {
              chat.appendChild(final);
              hasContent = true;
            }
            fullContent += delta;
            textNode.textContent += delta;
            scrollBottom();
          },
          () => resolve(),
          (err) => { errorMsg = err; resolve(); }
        );
      });

      cursor.remove();

      if (errorMsg) {
        if (!hasContent) final.remove();
        addErrorMessage("Error: " + errorMsg);
        if (/invalid|unauthor|forbidden|token|auth|denied|expired/i.test(errorMsg)) {
          setTimeout(() => {
            disconnect();
            showLoginError("Your token has expired or is invalid. Please sign in again.");
          }, 1500);
        }
      } else if (fullContent) {
        history.push({ role: "assistant", content: fullContent });
      } else {
        if (!hasContent) final.remove();
        addErrorMessage("Empty response from model.");
      }

      await sleep(300);
      finishThinkingBlock(block);

      isProcessing = false;
      sendBtn.disabled = false;
      input.focus();
    }

    /* ============================================
       Disconnect
    ============================================ */
    function disconnect() {
      token = "";
      history = [];
      currentModel = null;
      modelsList = [];
      chat.innerHTML = "";

      try {
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(MODEL_KEY);
      } catch (e) {}

      modelBtn.classList.remove('show');
      infoBtn.classList.remove('show');
      logoutBtn.classList.remove('show');
      chatScreen.classList.remove('show');
      loginScreen.classList.remove('hide');
      tokInput.value = "";
      tokInput.disabled = false;
      goBtn.disabled = false;
      clearLoginError();
      closeInfo();
      closeDialog();
      tokInput.focus();
    }

    /* ============================================
       Drag setup
    ============================================ */
    setupDragToDismiss(dialog, dialogOverlay, dialogDragArea, closeDialog);
    setupDragToDismiss(infoDialog, infoOverlay, infoDragArea, closeInfo);

    /* ============================================
       Events
    ============================================ */
    goBtn.addEventListener('click', () => connect());
    tokInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') { e.preventDefault(); connect(); }
    });
    tokInput.addEventListener('input', () => {
      if (loginBox.classList.contains('error')) clearLoginError();
    });

    composer.addEventListener('submit', (e) => { e.preventDefault(); handleSend(); });

    modelBtn.addEventListener('click', openDialog);
    dialogOverlay.addEventListener('click', closeDialog);
    infoBtn.addEventListener('click', openInfo);
    infoOverlay.addEventListener('click', closeInfo);
    logoutBtn.addEventListener('click', disconnect);

    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { closeDialog(); closeInfo(); }
    });

    /* ============================================
       Init
    ============================================ */
    autoRestore();
  </script>

</body>
</html>
