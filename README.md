<div align="center">

<img src="https://raw.githubusercontent.com/X5Coder/X5Models-Free/main/ai-platform-svgrepo-com.svg" width="120" height="120" alt="X5Models Free"/>

# X5Models Free

**One token. Every model. Zero setup.**

A lightweight, elegant web client that gives you instant access to a curated collection of the world's best AI models through a single, unified API — powered by Google Apps Script.

[![License](https://img.shields.io/badge/license-MIT-4A7DFF?style=flat-square)](LICENSE)
[![Made with](https://img.shields.io/badge/made%20with-HTML%20%2B%20CSS%20%2B%20JS-4A7DFF?style=flat-square)](#)
[![No build](https://img.shields.io/badge/build-none%20required-4A7DFF?style=flat-square)](#)

[Get Started](#-getting-your-token) · [Features](#-features) · [API](#-api-reference) · [Support](#-support)

</div>

---

## ✨ Overview

**X5Models Free** is a single-file web application that turns any modern browser into a powerful, distraction-free AI chat interface. No accounts to create, no SDKs to install — just paste your token and start talking to the model of your choice.

The entire app lives in **one HTML file**, backed by a **Google Apps Script** endpoint that routes your requests to the model you select. Everything is designed around three principles:

- **Minimal** — a beautiful, quiet interface that stays out of your way
- **Universal** — works on desktop, tablet, and mobile without any changes
- **Open** — OpenAI-compatible request format, so you can plug it into anything

---

## 🚀 Features

<table>
<tr>
<td width="50%">

### 🎨 Thoughtful Design
A refined dark interface with a live **Working** indicator, smooth streaming responses, and a typing animation that feels natural — not rushed.

</td>
<td width="50%">

### ⚡ Real-time Streaming
Responses arrive **character by character** via Server-Sent Events. You can stop generation at any moment with a single click.

</td>
</tr>
<tr>
<td width="50%">

### 🧠 Any Model, One Token
Switch between models mid-conversation. Your selection is remembered between sessions.

</td>
<td width="50%">

### 🔐 Persistent Sessions
Your token is stored locally — reopening the page fills the field automatically. Press **Connect** whenever you're ready.

</td>
</tr>
<tr>
<td width="50%">

### 📱 Fully Responsive
The same interface, from a 320px phone to a 4K monitor. No horizontal scroll, no broken layouts.

</td>
<td width="50%">

### 🔌 OpenAI-Compatible
The backend accepts standard OpenAI request shapes. Use it from your own scripts, tools, or agents.

</td>
</tr>
</table>

---

## 🎟 Getting Your Token

Getting a token takes less than a minute. Here's the full walkthrough:

### 1. Download the script

Grab [`start.py`](https://raw.githubusercontent.com/X5Coder/X5Models-Free/refs/heads/main/start.py) and save it anywhere on your device.

```bash
curl -O https://raw.githubusercontent.com/X5Coder/X5Models-Free/refs/heads/main/start.py
