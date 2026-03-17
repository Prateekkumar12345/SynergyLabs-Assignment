# 🚀 AI Content Creation Suite

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT4--mini-green)
![DALL·E](https://img.shields.io/badge/DALL·E-3-purple)
![License](https://img.shields.io/badge/License-MIT-yellow)

**A multi-tool AI platform for automated video creation, SEO blogging, and software architecture generation**

</div>

---

## 📌 Overview

This project is a **multi-functional AI-powered application** that automates content creation and system design workflows using modern Generative AI techniques.

It consists of **three independent tools**, each solving a real-world problem using AI pipelines:

- 🎬 Automated video generation from trending content  
- ✍️ SEO blog generation from product data  
- 🏗️ Conversion of business requirements into technical architecture  

---

## 🎯 Features

### 🎬 AI Video Generator
- Scrapes trending news articles
- Generates engaging video scripts using LLMs
- Creates images using DALL·E
- Converts scripts to audio (TTS)
- Compiles video using OpenCV

---

### ✍️ SEO Blog Creator
- Scrapes trending/best-selling products
- Generates SEO keywords automatically
- Creates optimized blog posts (150–200 words)
- Ensures natural keyword integration
- Supports publishing-ready output

---

### 🏗️ Architecture Pipeline Generator
- Converts high-level requirements into:
  - System modules
  - Database schema
  - API design
  - Pseudocode
- Uses structured LLM outputs
- Helps in rapid system design prototyping

---

## 🏗️ System Architecture

```text
User Interface (Streamlit)
        ↓
Backend Logic (Python)
        ↓
AI Processing Layer (OpenAI APIs)
        ↓
External Data Sources (News / Products)
        ↓
Output Generation (Video / Blog / Architecture)
