# Use Case Catalog: AI Applications with Prompt Exposure in Insurance

> **Version:** v0.1 Draft  
> **Date:** 2026-04-22  
> **Purpose:** Define six representative AI application patterns deployed within an insurance enterprise, each involving distinct prompt architectures and risk profiles. This document serves as an index — each use case will be expanded into a dedicated document with full prompt specifications and risk analysis.

---

## Overview

A large-scale insurance company operates AI-powered applications across its value chain — from policy quoting and underwriting to claims handling, legal review, and customer engagement. These applications vary significantly in their **architecture** (single-turn vs. multi-step orchestration, retrieval-augmented vs. tool-augmented), **autonomy level** (human-in-the-loop vs. fully autonomous), and **exposure surface** (internal-only vs. customer-facing, static data vs. live external data).

To systematically analyze prompt-level risks, we define six use cases that collectively cover the spectrum of LLM integration patterns found in insurance operations. Each use case is grounded in a specific business function and describes:

- **Business context** — What the application does and who uses it
- **Architecture pattern** — How the LLM is orchestrated (single call, chained calls, RAG, agent loop, etc.)
- **Prompt inventory** — Which prompts exist in the system and where they act in the workflow
- **Data flow** — What data enters the LLM context and from which sources

The six use cases are ordered by increasing architectural complexity:

| # | Use Case | Architecture Pattern | Business Function | User Type |
|---|----------|---------------------|-------------------|-----------|
| 1 | Multi-Step Claim Intake Processing | LLM Orchestration (chained pipeline) | Claims — FNOL Processing | Internal adjuster |
| 2 | Underwriting Knowledge Assistant | RAG over internal knowledge base | Underwriting | Internal underwriter |
| 3 | Market Intelligence Research Agent | Web-fetch research agent | Strategy / Competitive Intel | Internal analyst |
| 4 | Litigation Support Agent | Autonomous agent with basic tools | Legal / Litigation | Internal attorney |
| 5 | Claims Automation Agent | Advanced autonomous agent with privileged tools | Claims Operations | System (automated) |
| 6 | Policyholder Self-Service AI | Customer-facing conversational agent | Customer Service | External policyholder |

---

## Use Case 1: Multi-Step Claim Intake Processing

**Pattern:** LLM Orchestration — Chained Multi-Step Pipeline

### Business Context

When a policyholder reports a loss (First Notice of Loss — FNOL), the incoming information arrives in unstructured form: a phone transcript, a web form narrative, uploaded photos, and supporting documents. Before a human adjuster can begin working the claim, this raw input must be transformed into a structured claim record — categorized by line of business, assessed for severity, checked for coverage applicability, and routed to the appropriate handling team.

This application automates the FNOL intake pipeline. It is used by **internal claims staff** who review and approve the structured output before it enters the claims management system.

### Architecture

The application is a **deterministic multi-step LLM pipeline** — a fixed sequence of LLM calls where the output of each step feeds into the next. There is no autonomous decision-making; the orchestration logic is hardcoded in application code. Each step calls the LLM with a different prompt tailored to a specific subtask.

```
Raw FNOL Input
    │
    ▼
┌─────────────────────────┐
│ Step 1: Information      │  ← Prompt A: Extraction Prompt
│ Extraction               │
└────────────┬────────────┘
             │ (structured fields)
             ▼
┌─────────────────────────┐
│ Step 2: Line of Business │  ← Prompt B: Classification Prompt
│ Classification           │
└────────────┬────────────┘
             │ (LoB label + confidence)
             ▼
┌─────────────────────────┐
│ Step 3: Severity &       │  ← Prompt C: Triage Prompt
│ Priority Triage          │
└────────────┬────────────┘
             │ (severity score + priority)
             ▼
┌─────────────────────────┐
│ Step 4: Coverage         │  ← Prompt D: Coverage Check Prompt
│ Applicability Check      │
└────────────┬────────────┘
             │ (coverage determination)
             ▼
┌─────────────────────────┐
│ Step 5: Summary &        │  ← Prompt E: Routing Prompt
│ Routing Recommendation   │
└────────────┬────────────┘
             │
             ▼
    Structured Claim Record → Human Review
```

### Prompt Inventory

| Prompt | Role in Workflow | Input Sources |
|--------|-----------------|---------------|
| **Prompt A — Extraction Prompt** | Parses raw FNOL narrative into structured fields (date of loss, location, parties involved, damage description, injury indicators) | Customer-submitted text, phone transcripts |
| **Prompt B — Classification Prompt** | Determines line of business (auto, property, general liability, workers' comp, etc.) based on extracted fields | Output of Prompt A |
| **Prompt C — Triage Prompt** | Assigns severity level (1–5) and handling priority based on damage indicators, injury presence, and estimated exposure | Output of Prompts A + B |
| **Prompt D — Coverage Check Prompt** | Cross-references extracted claim details against policy coverage rules to flag potential coverage issues | Output of Prompt A + policy summary data from internal systems |
| **Prompt E — Routing Prompt** | Generates a human-readable claim summary and recommends the appropriate handling unit and adjuster skill level | Output of all previous steps |

### Key Characteristics

- **Fixed orchestration** — No LLM autonomy; the pipeline sequence is determined by application code.
- **Prompt chaining risk** — Errors or injections in early steps propagate and amplify through downstream prompts.
- **External data ingestion** — Prompt A directly processes customer-submitted content, making it the primary injection surface.
- **Internal reference data** — Prompt D incorporates policy data from internal systems, introducing hardcoded-data risk if policy rules are embedded in the prompt.

---

## Use Case 2: Underwriting Knowledge Assistant

**Pattern:** Retrieval-Augmented Generation (RAG) over Internal Knowledge Base

### Business Context

Insurance underwriting requires deep expertise across product lines — commercial property, general liability, professional liability, marine, cyber, and more. Underwriters must constantly reference internal guidelines, appetite documents, rate filings, reinsurance treaties, and regulatory bulletins. Historically, this knowledge is scattered across SharePoint sites, PDF manuals, and tribal expertise.

This application provides underwriters with a **conversational knowledge assistant** that answers questions by retrieving relevant content from an internal knowledge base and synthesizing a response. It is used by **internal underwriters** during the quoting and risk evaluation process.

### Architecture

The application follows the standard **RAG pattern**: the user's question is embedded, matched against a vector store of indexed internal documents, and the top-k retrieved passages are injected into the LLM context alongside the question.

```
Underwriter Question
    │
    ▼
┌─────────────────────────┐
│ Query Processing         │  ← Prompt F: Query Rewrite Prompt
│ (rewrite for retrieval)  │
└────────────┬────────────┘
             │ (optimized query)
             ▼
┌─────────────────────────┐
│ Vector Store Retrieval   │  (no LLM — embedding similarity search)
│ (internal knowledge base)│
└────────────┬────────────┘
             │ (top-k document chunks)
             ▼
┌─────────────────────────┐
│ Response Generation      │  ← Prompt G: RAG System Prompt
│                          │     + retrieved context + user question
└────────────┬────────────┘
             │
             ▼
    Answer with Source Citations → Underwriter
```

### Prompt Inventory

| Prompt | Role in Workflow | Input Sources |
|--------|-----------------|---------------|
| **Prompt F — Query Rewrite Prompt** | Transforms the underwriter's natural language question into an optimized retrieval query (keyword expansion, disambiguation) | User question (internal employee) |
| **Prompt G — RAG System Prompt** | Defines the assistant's identity, behavior constraints, citation requirements, and instructions for synthesizing an answer from retrieved passages | Static system prompt + dynamically retrieved document chunks + user question |

### Key Characteristics

- **Knowledge base as attack surface** — If any indexed document contains adversarial content (whether planted or accidentally ingested), it enters the LLM context via retrieval, creating an **indirect prompt injection** vector.
- **Sensitive internal content** — Retrieved passages may contain proprietary underwriting guidelines, pricing logic, risk appetite thresholds, or reinsurance terms. The RAG System Prompt must enforce boundaries on what the model can quote verbatim vs. summarize.
- **Single-turn interaction** — Each question is independent; no multi-turn planning or tool use.
- **Source attribution** — The prompt must instruct the model to cite specific source documents, adding complexity around hallucination control.

---

## Use Case 3: Market Intelligence Research Agent

**Pattern:** Web-Fetch Research Agent with External Data Gathering

### Business Context

The insurance market is shaped by catastrophe events, regulatory changes, competitor moves, emerging risks (cyber, climate, autonomous vehicles), and macroeconomic trends. Strategy and actuarial teams need to continuously monitor the external landscape to inform pricing decisions, product development, and risk appetite adjustments.

This application is a **research agent** that, given a research question, autonomously searches the web, retrieves and reads relevant pages, and produces a structured research brief. It is used by **internal analysts and strategists**.

### Architecture

The agent operates in a **research loop**: it plans what information it needs, executes web searches, fetches and reads pages, evaluates whether it has enough information, and either searches for more or synthesizes a final report.

```
Research Question (from analyst)
    │
    ▼
┌─────────────────────────┐
│ Research Planning        │  ← Prompt H: Research Planner Prompt
│                          │
└────────────┬────────────┘
             │ (search plan: queries + angles)
             ▼
        ┌────────────┐
        │ Search Loop │ ◄──────────────────────────┐
        └─────┬──────┘                              │
              │                                     │
              ▼                                     │
┌─────────────────────────┐                         │
│ Web Search + Fetch      │  (tool execution)       │
│                          │                         │
└────────────┬────────────┘                         │
             │ (raw web content)                    │
             ▼                                     │
┌─────────────────────────┐                         │
│ Content Analysis         │  ← Prompt I: Content   │
│ & Relevance Assessment   │    Analysis Prompt      │
└────────────┬────────────┘                         │
             │                                     │
             ▼                                     │
┌─────────────────────────┐     (need more?) ──YES──┘
│ Sufficiency Check        │  ← Prompt J: Sufficiency
│                          │    Evaluation Prompt
└────────────┬────────────┘
             │ NO (enough data)
             ▼
┌─────────────────────────┐
│ Report Synthesis         │  ← Prompt K: Report Synthesis Prompt
└────────────┬────────────┘
             │
             ▼
    Structured Research Brief → Analyst Review
```

### Prompt Inventory

| Prompt | Role in Workflow | Input Sources |
|--------|-----------------|---------------|
| **Prompt H — Research Planner Prompt** | Decomposes the research question into specific search queries and investigation angles | User research question (internal) |
| **Prompt I — Content Analysis Prompt** | Extracts key facts, data points, and relevant insights from a fetched web page | Raw web page content (external, untrusted) |
| **Prompt J — Sufficiency Evaluation Prompt** | Determines whether the accumulated findings adequately answer the research question or if additional searches are needed | Aggregated findings from previous iterations |
| **Prompt K — Report Synthesis Prompt** | Compiles all gathered findings into a structured research brief with source attribution and confidence indicators | All accumulated analysis results |

### Key Characteristics

- **Uncontrolled external content** — The agent fetches arbitrary web pages, making every fetched page a potential **indirect prompt injection** vector. Adversarial content on public web pages (invisible text, misleading instructions) directly enters the LLM context.
- **Iterative autonomy** — The agent decides how many searches to conduct and when to stop, introducing a feedback loop where early-stage injection could steer subsequent search behavior.
- **No privileged tool access** — The agent can search and read, but cannot modify any internal system. Impact is limited to **information integrity** (producing a biased or manipulated research brief).
- **Multi-source synthesis** — The Report Synthesis Prompt must reconcile potentially contradictory information from multiple external sources.

---

## Use Case 4: Litigation Support Agent

**Pattern:** Autonomous Agent with Basic Tool Access

### Business Context

When insurance claims escalate to litigation, legal teams must review large volumes of documents — pleadings, depositions, medical records, expert reports, and correspondence — to build case strategy. An individual litigated claim file can contain hundreds of documents spanning years.

This application is a **litigation support agent** that helps internal attorneys analyze case files. Given a legal question or task, it autonomously plans an approach, reads relevant documents from the case file, and produces structured analysis. It has access to a small set of **read-only tools** for navigating the document repository. It is used by **internal legal staff**.

### Architecture

The agent follows an **autonomous plan-and-execute loop** with access to basic tools. Unlike Use Case 3 (which fetches external web content), this agent works exclusively with internal case documents accessed through controlled tool interfaces.

```
Attorney Task / Question
    │
    ▼
┌─────────────────────────┐
│ Task Planning            │  ← Prompt L: Litigation Planner Prompt
│                          │
└────────────┬────────────┘
             │ (analysis plan: steps + document needs)
             ▼
        ┌────────────────┐
        │ Execution Loop  │ ◄─────────────────────────┐
        └───────┬────────┘                             │
                │                                      │
                ▼                                      │
┌───────────────────────────┐                          │
│ Tool Selection & Execution │  ← Prompt M: Agent      │
│                            │    Reasoning Prompt      │
│  Tools available:          │                          │
│  • search_case_files       │                          │
│  • read_document           │                          │
│  • list_case_documents     │                          │
│  • get_document_metadata   │                          │
└───────────────┬───────────┘                          │
                │ (tool results)                       │
                ▼                                      │
┌───────────────────────────┐                          │
│ Reasoning & Next Step      │  (more steps?) ──YES────┘
│ Decision                   │
└───────────────┬───────────┘
                │ NO (task complete)
                ▼
┌───────────────────────────┐
│ Response Synthesis         │  ← Prompt N: Legal Analysis
│                            │    Synthesis Prompt
└───────────────┬───────────┘
                │
                ▼
    Structured Legal Analysis → Attorney Review
```

### Prompt Inventory

| Prompt | Role in Workflow | Input Sources |
|--------|-----------------|---------------|
| **Prompt L — Litigation Planner Prompt** | Analyzes the attorney's question and creates a step-by-step plan for which documents to review and what to look for | Attorney question (internal) |
| **Prompt M — Agent Reasoning Prompt** | Core agent loop prompt that governs tool selection, result interpretation, and next-step reasoning. Defines available tools, their usage rules, and the agent's behavioral constraints | Attorney question + plan + tool results (internal documents) |
| **Prompt N — Legal Analysis Synthesis Prompt** | Compiles findings from multiple document reviews into a structured legal analysis with citations and risk assessment | Accumulated tool results and intermediate reasoning |

### Key Characteristics

- **Read-only tool access** — The agent can search and read documents but cannot modify, delete, or transmit anything. This limits the blast radius of any prompt-related failure to **information output quality**.
- **Internal data only** — All data sources (case files, document repository) are internal and managed. The injection surface is narrower than Use Case 3 but not zero — adversarial content could exist in externally originated documents (e.g., opposing counsel's pleadings) stored in the case file.
- **Autonomous planning** — The agent decides its own investigation path, meaning a compromised reasoning step could lead it to ignore critical documents or over-weight favorable ones.
- **Sensitive output context** — Legal analysis directly informs litigation strategy and settlement decisions. Inaccurate or manipulated output carries significant financial and legal consequences.

---

## Use Case 5: Claims Automation Agent

**Pattern:** Advanced Autonomous Agent with Privileged Tool Access

### Business Context

For high-volume, lower-complexity claims (e.g., auto glass replacement, minor property damage, straightforward medical payments), insurers seek to automate end-to-end processing — from intake through investigation to resolution — with minimal human intervention. This reduces cycle time, improves customer experience, and frees adjusters to focus on complex claims.

This application is an **advanced claims automation agent** that can autonomously investigate a claim and take actions in enterprise systems. Unlike Use Case 4 (read-only tools), this agent has **write access to production systems** and can trigger real-world business outcomes. It operates as a **system-level automated process** with human oversight at defined checkpoints.

### Architecture

The agent operates with a **rich tool set** that includes both read and write capabilities across multiple enterprise systems. It follows an autonomous plan-execute-verify loop with escalation logic.

```
New Claim Assignment (auto-routed)
    │
    ▼
┌─────────────────────────┐
│ Claim Assessment &       │  ← Prompt O: Claims Agent
│ Planning                 │    System Prompt
└────────────┬────────────┘
             │ (investigation plan)
             ▼
        ┌────────────────┐
        │ Execution Loop  │ ◄──────────────────────────┐
        └───────┬────────┘                              │
                │                                       │
                ▼                                       │
┌───────────────────────────────┐                       │
│ Tool Selection & Execution     │  ← Prompt P: Agent   │
│                                │    Reasoning Prompt   │
│  Tools available:              │                       │
│  • query_policy_database       │ (read)                │
│  • query_claims_history        │ (read)                │
│  • retrieve_claimant_profile   │ (read)                │
│  • search_fraud_indicators     │ (read)                │
│  • request_vendor_estimate     │ (read/write — external│
│                                │  vendor API)          │
│  • update_claim_status         │ (write)               │
│  • set_reserve_amount          │ (write)               │
│  • schedule_inspection         │ (write)               │
│  • issue_payment               │ (write)               │
│  • escalate_to_adjuster        │ (write)               │
│  • send_claimant_notification  │ (write)               │
│  • log_investigation_notes     │ (write)               │
└───────────────┬───────────────┘                       │
                │ (tool results)                        │
                ▼                                       │
┌───────────────────────────┐                           │
│ Reasoning, Verification    │  (more steps?) ──YES─────┘
│ & Escalation Check         │
└───────────────┬───────────┘
                │ NO (resolution reached)
                ▼
┌───────────────────────────┐
│ Resolution Execution       │  ← Prompt Q: Resolution
│ & Documentation            │    Prompt
└───────────────┬───────────┘
                │
                ▼
    Claim Resolved / Escalated → Audit Log
```

### Prompt Inventory

| Prompt | Role in Workflow | Input Sources |
|--------|-----------------|---------------|
| **Prompt O — Claims Agent System Prompt** | Master system prompt defining the agent's identity, authority boundaries, escalation rules, compliance constraints, and the complete tool inventory with usage policies | Static configuration |
| **Prompt P — Agent Reasoning Prompt** | Governs each iteration of the agent loop: which tool to call next, how to interpret results, when to escalate vs. proceed autonomously, and how to handle ambiguous or conflicting data | Claim data + tool results (mix of internal systems and external vendor responses) |
| **Prompt Q — Resolution Prompt** | Generates the final claim resolution documentation, including decision rationale, payment justification, and compliance attestation | All accumulated investigation data and reasoning |

### Key Characteristics (Contrast with Use Case 4)

| Dimension | Use Case 4 (Litigation Support) | Use Case 5 (Claims Automation) |
|-----------|--------------------------------|-------------------------------|
| **Tool access** | 4 read-only tools on a single system | 11+ tools across multiple systems, including write operations |
| **System scope** | Single document repository | Policy DB, claims system, fraud detection, vendor APIs, payment system, notification service |
| **Action consequences** | Output is advisory — attorney decides | Agent can issue payments, update records, and notify claimants directly |
| **Autonomy level** | Plans and researches; human synthesizes conclusions | Plans, investigates, decides, and executes with checkpoint-based human oversight |
| **Failure blast radius** | Flawed analysis (fixable) | Unauthorized payment, incorrect reserve, missed fraud, regulatory violation |
| **External data exposure** | Opposing counsel documents (within case file) | Vendor API responses, claimant-submitted materials, fraud database results |

- **Privileged write access** — The agent can trigger irreversible business actions (payments, status changes, notifications). Prompt vulnerabilities here have **direct financial and operational consequences**.
- **Multi-system integration** — Data flows from and actions execute against multiple enterprise systems, each with its own trust boundary. The prompt must correctly enforce which tools are appropriate for which situations.
- **External data injection surface** — Vendor estimate responses and claimant-submitted materials enter the agent's context and could carry adversarial content designed to influence claim outcomes.
- **Compliance-critical decisions** — Every action must be explainable and auditable. The Resolution Prompt must produce documentation that satisfies regulatory scrutiny.

---

## Use Case 6: Policyholder Self-Service AI

**Pattern:** Customer-Facing Conversational Agent

### Business Context

Policyholders interact with their insurer for a wide range of needs: checking policy details, filing claims, requesting certificates of insurance, understanding coverage, updating personal information, and asking billing questions. Traditionally these interactions flow through call centers, web portals, or local agents.

This application is a **customer-facing AI agent** embedded in the insurer's website, mobile app, and messaging channels. It is the first point of contact for **external policyholders** — the general public — and must handle a vast range of intents while maintaining strict brand, compliance, and security standards.

### Architecture

The agent operates as a **multi-turn conversational system** with access to customer-specific data via authenticated API calls. It combines intent classification, data retrieval, and response generation in a controlled dialogue flow.

```
Policyholder Message (via web/app/SMS)
    │
    ▼
┌─────────────────────────┐
│ Intent Classification    │  ← Prompt R: Intent Router Prompt
│ & Safety Screening       │
└────────────┬────────────┘
             │ (intent label + safety flag)
             ▼
┌─────────────────────────┐
│ Context Retrieval        │  (no LLM — API calls to policy
│ (policy data, claim      │   management system based on
│  status, billing info)   │   authenticated session)
└────────────┬────────────┘
             │ (customer-specific data)
             ▼
┌─────────────────────────┐
│ Response Generation      │  ← Prompt S: Conversational
│                          │    Agent System Prompt
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│ Output Safety Filter     │  ← Prompt T: Output Guard Prompt
│                          │
└────────────┬────────────┘
             │
             ▼
    Response → Policyholder
```

### Prompt Inventory

| Prompt | Role in Workflow | Input Sources |
|--------|-----------------|---------------|
| **Prompt R — Intent Router Prompt** | Classifies the customer's message into a predefined intent category and performs initial safety screening (detecting prompt injection attempts, abusive content, or out-of-scope requests) | Customer message (external, untrusted) |
| **Prompt S — Conversational Agent System Prompt** | Master system prompt defining the agent's persona, tone, compliance boundaries (what it can/cannot disclose), escalation triggers (when to route to a human agent), and response formatting rules | Static system prompt + customer-specific data from APIs + conversation history + customer message |
| **Prompt T — Output Guard Prompt** | Reviews the generated response before delivery to check for: accidental disclosure of internal system details, non-compliant language, hallucinated policy information, and prompt leakage | Generated response + original customer message |

### Key Characteristics

- **Untrusted user input** — Every message comes from an external user with unknown intent. This is the **highest direct prompt injection exposure** of all six use cases.
- **Brand and compliance stakes** — Every response is delivered under the company's brand. Inappropriate, inaccurate, or manipulated responses directly impact customer trust and regulatory standing.
- **Multi-turn conversation** — Extended dialogue creates opportunities for **gradual context manipulation** — an attacker can slowly steer the conversation across multiple turns to bypass safety boundaries.
- **Output filtering layer** — The inclusion of a dedicated Output Guard Prompt (Prompt T) adds a defense layer but also introduces its own prompt — which itself must be secured against bypass.
- **No write actions** — The agent can retrieve customer data but cannot modify policies, process payments, or update records. Actions requiring changes are escalated to human agents or authenticated self-service portals.
- **Highest volume** — This is the most frequently invoked application, meaning even low-probability prompt failures will occur at scale.

---

## Cross-Use-Case Comparison

| Dimension | UC1 Pipeline | UC2 RAG | UC3 Web Research | UC4 Basic Agent | UC5 Advanced Agent | UC6 Customer-Facing |
|-----------|:-----------:|:------:|:----------------:|:--------------:|:-----------------:|:------------------:|
| **Autonomy** | None (fixed pipeline) | None (single-turn) | Moderate (search loop) | Moderate (plan + read) | High (plan + read/write) | Low (classification + response) |
| **External data exposure** | Customer FNOL text | None (internal KB) | Web pages (fully untrusted) | Opposing counsel docs | Vendor APIs + claimant docs | Customer messages (untrusted) |
| **Write access to systems** | No | No | No | No | Yes (payments, records, notifications) | No |
| **User type** | Internal | Internal | Internal | Internal | System (automated) | External (public) |
| **Prompt count** | 5 | 2 | 4 | 3 | 3 | 3 |
| **Primary risk vector** | Injection via FNOL content; chain propagation | KB poisoning; sensitive data in retrieved context | Web content injection; research steering | Document-borne injection; planning manipulation | Privileged action abuse; multi-system injection | Direct prompt injection; brand/compliance violation |

---

## Next Steps

Each use case will be expanded into a dedicated document covering:

1. Detailed prompt specifications (purpose, structure, constraints)
2. Threat model (specific attack scenarios for each prompt)
3. Risk assessment using the Prompt Risk Matrix framework
4. Recommended mitigations mapped to the Governance framework

---

*Document maintained as part of the `prompt_risk` project — Last updated: 2026-04-22*
