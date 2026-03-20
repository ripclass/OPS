<div align="center">

<img src="./static/image/ops_logo_compressed.jpeg" alt="OPS Logo" width="75%"/>

A scenario forecasting stack for Organic Population Simulation.
</br>
<em>Population-scale simulation for policy, crisis, and narrative forecasting across South Asia</em>

[English](./README-EN.md) | [Project README](./README.md)

</div>

## Project Overview

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

1. **Spectrum Construction**: Real seed extraction & individual and group memory injection & GraphRAG construction
2. **Environment Setup**: Entity Relationship Extraction & Character Generation & Environment Configuration Agent Injection Simulation Parameters
3. **Start Simulation**: Parallel simulation on dual platforms & automatic parsing of predictive requirements & dynamic updating of temporal memory
4. **Report Generation**: ReportAgent possesses a rich set of tools to deeply interact with the post-simulation environment
5. **Deep Interaction**: Engage in conversation with any character in the simulated world & converse with ReportAgent

## Quick Start

### Option 1: Source Code Deployment (Recommended)

#### Prerequisites

| Tool | Version Requirement | Description | Installation Verification |
|------|---------|------|---------|
| **Node.js** | 18+ | frontend runtime environment, including npm | `node -v` |
| **Python** | >=3.11, <=3.12 | Backend runtime environment | `python --version` |
| **uv** | latest version | Python package manager | `uv --version` |

#### 1. Configure Environment Variables

```bash
# Copy the example configuration file
cp .env.example .env

# Edit the .env file and fill in necessary API keys
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
# One-click installation of all dependencies (root directory + frontend + backend)
npm run setup:all
```

or step-by-step installation:

```bash
# Install Node.js dependencies (root directory + frontend)
npm run setup

# Install Python dependencies (backend, automatically creates a virtual environment)
npm run setup:backend
```

#### 3. Start the Service

```bash
# Start both front-end and back-end simultaneously (execute in the project root directory)
npm run dev
```

**Service Address:**
- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:5001`

**Start Separately:**

```bash
npm run backend   # Start only the back-end
npm run frontend  # Start only the front-end
```

### Option 2: Docker Deployment

```bash
# 1. Configure environment variables (for source code deployment)
cp .env.example .env

# 2. Pull the image and start it
docker compose up -d
```

By default, Docker reads the `.env` file in the project root and maps ports `3000 (frontend) / 5001 (backend)`.

> Docker is configured for a local Ollama instance. Containers use `host.docker.internal` to reach the model server running on Windows.

## Deployment Notes

This OPS fork is currently optimized for local and private deployments. Replace the logo asset, community links, and contact details with your own organization-owned branding before public release.

## Acknowledgments

OPS is powered by **[OASIS](https://github.com/camel-ai/oasis)**. We sincerely thank the CAMEL-AI team for their open-source contributions!
