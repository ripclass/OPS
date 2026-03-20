<div align="center">

<img src="./static/image/MiroFish_logo_compressed.jpeg" alt="OPS Logo" width="75%"/>

<a href="https://trendshift.io/repositories/16144" target="_blank"><img src="https://trendshift.io/api/badge/repositories/16144" alt="666ghj%2FMiroFish | Trendshift" style="width: 250px; height: 55px;" width="250" height="55"/></a>

A scenario forecasting stack for Organic Population Simulation
</br>
<em>Population-scale simulation for policy, crisis, and narrative forecasting across South Asia</em>

<a href="https://www.shanda.com/" target="_blank"><img src="./static/image/shanda_logo.png" alt="666ghj%2MiroFish | Shanda" height="40"/></a>

[![GitHub Stars](https://img.shields.io/github/stars/666ghj/MiroFish?style=flat-square&color=DAA520)](https://github.com/666ghj/MiroFish/stargazers)
[![GitHub Watchers](https://img.shields.io/github/watchers/666ghj/MiroFish?style=flat-square)](https://github.com/666ghj/MiroFish/watchers)
[![GitHub Forks](https://img.shields.io/github/forks/666ghj/MiroFish?style=flat-square)](https://github.com/666ghj/MiroFish/network)
[![Docker](https://img.shields.io/badge/Docker-Build-2496ED?style=flat-square&logo=docker&logoColor=white)](https://hub.docker.com/)
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/666ghj/MiroFish)

[English](./README-EN.md) | [Project README](./README.md)

</div>

## Overview

**OPS (Organic Population Simulation)** is a scenario-forecasting platform built on top of the existing interface layer and the OASIS multi-agent engine. It turns short briefs, policy notes, field reports, and media narratives into simulated populations with memory, behavior, and network structure so you can test reactions before events unfold.

> Start from a scenario brief, optionally add supporting documents, and define the response you want to forecast.</br>
> OPS returns a structured report plus an interactive agent environment for follow-up analysis.

### Our Vision

OPS is focused on population response forecasting across South Asia. By capturing the collective emergence created by individual interactions, it moves beyond the limits of traditional forecasting and static polling.

- **Policy Opinion Forecasting**: Rehearse likely public reaction before major announcements and test where sentiment or rumor may concentrate.
- **Crisis Communication Simulation**: Model how warnings, leaks, and narrative shifts could move through districts, communities, and online networks.
- **Academic and Research Use**: Run controlled experiments on information propagation, trust, coordination, and group behavior across South Asian populations.

OPS is designed for India, Bangladesh, and Pakistan first, while keeping the workflow portable to other regions.

## Live Demo

This fork is intended for local or private deployment. For a reference walkthrough of the upstream interface, see: [mirofish-live-demo](https://666ghj.github.io/mirofish-demo/)

## Screenshots

<div align="center">
<table>
<tr>
<td><img src="./static/image/Screenshot/%E8%BF%90%E8%A1%8C%E6%88%AA%E5%9B%BE1.png" alt="Screenshot 1" width="100%"/></td>
<td><img src="./static/image/Screenshot/%E8%BF%90%E8%A1%8C%E6%88%AA%E5%9B%BE2.png" alt="Screenshot 2" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/%E8%BF%90%E8%A1%8C%E6%88%AA%E5%9B%BE3.png" alt="Screenshot 3" width="100%"/></td>
<td><img src="./static/image/Screenshot/%E8%BF%90%E8%A1%8C%E6%88%AA%E5%9B%BE4.png" alt="Screenshot 4" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/%E8%BF%90%E8%A1%8C%E6%88%AA%E5%9B%BE5.png" alt="Screenshot 5" width="100%"/></td>
<td><img src="./static/image/Screenshot/%E8%BF%90%E8%A1%8C%E6%88%AA%E5%9B%BE6.png" alt="Screenshot 6" width="100%"/></td>
</tr>
</table>
</div>

## Upstream Demo Videos

### 1. Wuhan University Public Opinion Simulation + Upstream Engine Introduction

<div align="center">
<a href="https://www.bilibili.com/video/BV1VYBsBHEMY/" target="_blank"><img src="./static/image/%E6%AD%A6%E5%A4%A7%E6%A8%A1%E6%8B%9F%E6%BC%94%E7%A4%BA%E5%B0%81%E9%9D%A2.png" alt="Upstream engine demo video" width="75%"/></a>

Click the image to watch the upstream demo that originally introduced the engine workflow.
</div>

### 2. Dream of the Red Chamber Lost Ending Simulation

<div align="center">
<a href="https://www.bilibili.com/video/BV1cPk3BBExq" target="_blank"><img src="./static/image/%E7%BA%A2%E6%A5%BC%E6%A2%A6%E6%A8%A1%E6%8B%9F%E6%8E%A8%E6%BC%94%E5%B0%81%E9%9D%A2.jpg" alt="Upstream engine demo video" width="75%"/></a>

Click the image to watch the upstream engine run a large-scale narrative simulation.
</div>

> **Financial prediction**, **political news prediction**, and more examples are coming soon.

## Workflow

1. **Graph Building**: Seed extraction & Individual/collective memory injection & GraphRAG construction
2. **Environment Setup**: Entity relationship extraction & Persona generation & Agent configuration injection
3. **Simulation**: Dual-platform parallel simulation & Auto-parse prediction requirements & Dynamic temporal memory updates
4. **Report Generation**: ReportAgent with rich toolset for deep interaction with post-simulation environment
5. **Deep Interaction**: Chat with any agent in the simulated world & Interact with ReportAgent

## Quick Start

### Option 1: Source Code Deployment (Recommended)

#### Prerequisites

| Tool | Version | Description | Check Installation |
|------|---------|-------------|-------------------|
| **Node.js** | 18+ | Frontend runtime, includes npm | `node -v` |
| **Python** | >=3.11, <=3.12 | Backend runtime | `python --version` |
| **uv** | Latest | Python package manager | `uv --version` |

#### 1. Configure Environment Variables

```bash
# Copy the example configuration file
cp .env.example .env

# Edit the .env file and fill in the required API keys
```

**Suggested local environment variables:**

```env
# Local Ollama configuration
LLM_API_KEY=ollama
LLM_BASE_URL=http://localhost:11434/v1
LLM_MODEL_NAME=qwen2.5:7b

# Optional Zep Cloud key. Leave blank to run locally without graph persistence.
ZEP_API_KEY=
```

#### 2. Install Dependencies

```bash
# One-click installation of all dependencies (root + frontend + backend)
npm run setup:all
```

Or install step by step:

```bash
# Install Node dependencies (root + frontend)
npm run setup

# Install Python dependencies (backend, auto-creates virtual environment)
npm run setup:backend
```

#### 3. Start Services

```bash
# Start both frontend and backend (run from project root)
npm run dev
```

**Service URLs:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

**Start Individually:**

```bash
npm run backend   # Start backend only
npm run frontend  # Start frontend only
```

### Option 2: Docker Deployment

```bash
# 1. Configure environment variables (same as source deployment)
cp .env.example .env

# 2. Pull image and start
docker compose up -d
```
By default, Docker reads the `.env` file in the project root and maps ports `3000 (frontend) / 5001 (backend)`.

> Docker is configured for a local Ollama instance. Containers use `host.docker.internal` to reach the model server running on Windows.

## Deployment Notes

<div align="center">
<img src="./static/image/QQ%E7%BE%A4.png" alt="QQ Group" width="60%"/>
</div>

This OPS fork is currently optimized for local and private deployments. Replace the logo asset, community links, and contact details with your own organization-owned branding before public release.

## Acknowledgments

OPS builds on the open-source interface layer originally released as MiroFish and is powered by **[OASIS (Open Agent Social Interaction Simulations)](https://github.com/camel-ai/oasis)**. We sincerely thank the CAMEL-AI team for their open-source contributions!

## Project Statistics

<a href="https://www.star-history.com/#666ghj/MiroFish&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=666ghj/MiroFish&type=date&legend=top-left" />
 </picture>
</a>
