# AI Content Creation Suite 🚀

<div align="center">
  
  ![Python](https://img.shields.io/badge/Python-3.11-blue)
  ![Streamlit](https://img.shields.io/badge/Streamlit-1.28-red)
  ![OpenAI](https://img.shields.io/badge/OpenAI-GPT4--mini-green)
  ![DALL·E](https://img.shields.io/badge/DALL·E-3-purple)
  ![License](https://img.shields.io/badge/License-MIT-yellow)
  
  **Three powerful AI-powered tools for content creation, SEO blogging, and software architecture**
</div>

---

## 📋 Overview

This repository contains three AI-powered tools developed as part of an internship assignment. Each tool automates a different aspect of content creation using OpenAI's GPT-4o-mini and DALL-E models.

### 🎯 The Three Tools

| Tool | Description | Key Features |
|------|-------------|--------------|
| **🎬 AI Video Generator** | Creates short-form videos from trending news | News scraping, AI script writing, DALL-E images, OpenCV video compilation |
| **✍️ SEO Blog Creator** | Generates SEO-optimized blog posts from products | Product scraping, keyword research, AI content generation, SEO scoring |
| **🏗️ Architecture Pipeline** | Converts business requirements to technical specs | Module breakdown, DB schemas, API design, pseudocode generation |

---

## 🏗️ System Architecture
┌─────────────────────────────────────────────────────────────────────┐
│ Streamlit Frontend │
│ (Multi-page Application) │
└─────────────────────────────────────────────────────────────────────┘
│
┌───────────────────────────┼───────────────────────────┐
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Task 1: │ │ Task 2: │ │ Task 3: │
│ Video Generator │ │ SEO Blog │ │ Architecture │
│ (Page 1) │ │ Creator │ │ Pipeline │
│ │ │ (Page 2) │ │ (Page 3) │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
│ │ │
▼ ▼ ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ Core Services │ │ Core Services │ │ Core Services │
│ • NewsAPI │ │ • Mock Products │ │ • GPT-4o-mini │
│ • Mock Data │ │ • GPT-4o-mini │ │ • JSON Schema │
│ • DALL-E 3 │ │ • SEO Analysis │ │ • Mermaid │
│ • OpenCV │ │ • Export Tools │ │ • Risk Analysis │
└─────────────────┘ └─────────────────┘ └─────────────────┘
│ │ │
└───────────────────────────┼───────────────────────────┘
▼
┌─────────────────────────────┐
│ OpenAI API Layer │
│ • GPT-4o-mini (text) │
│ • DALL-E 3 (images) │
└─────────────────────────────┘

