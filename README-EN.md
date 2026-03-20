<div align="center">

<img src="./static/image/ops_logo_compressed.jpeg" alt="OPS Logo" width="75%"/>

A scenario forecasting stack for Organic Population Simulation
</br>
<em>Population-scale simulation for policy, crisis, and narrative forecasting across South Asia</em>

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

## Deployment Model

This repository is intended for local or private deployment of OPS.

## Screenshots

<div align="center">
<table>
<tr>
<td><img src="./static/image/Screenshot/ops_screenshot_1.png" alt="Screenshot 1" width="100%"/></td>
<td><img src="./static/image/Screenshot/ops_screenshot_2.png" alt="Screenshot 2" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/ops_screenshot_3.png" alt="Screenshot 3" width="100%"/></td>
<td><img src="./static/image/Screenshot/ops_screenshot_4.png" alt="Screenshot 4" width="100%"/></td>
</tr>
<tr>
<td><img src="./static/image/Screenshot/ops_screenshot_5.png" alt="Screenshot 5" width="100%"/></td>
<td><img src="./static/image/Screenshot/ops_screenshot_6.png" alt="Screenshot 6" width="100%"/></td>
</tr>
</table>
</div>

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

This OPS fork is currently optimized for local and private deployments. Replace the logo asset, community links, and contact details with your own organization-owned branding before public release.

## Acknowledgments

OPS is powered by **[OASIS (Open Agent Social Interaction Simulations)](https://github.com/camel-ai/oasis)**. We sincerely thank the CAMEL-AI team for their open-source contributions!
