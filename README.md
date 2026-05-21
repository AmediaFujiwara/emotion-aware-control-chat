# Emotion-Aware Control Chat

**A stability-first AI chat prototype based on the Anxiety Three-Axis Model**

> ⚠️ This application is **not** a medical diagnostic tool, treatment system, or substitute for professional mental health care.  
> It is an experimental tool for self-reflection, metacognition, and decision-support.

---

## Overview

Emotion-Aware Control Chat is a Streamlit-based AI chat prototype that analyzes user input not merely as an emotional state, but as a **structural risk vector**.

Instead of treating anxiety as a single intensity score, this application decomposes anxiety into three axes:

- **Boundary Violation**
- **Uncontrollability**
- **Anticipated Loss**

The resulting three-axis score is then used not only for visualization, but also as a **control signal for selecting the AI response policy**.

In other words, this application is not designed simply to comfort the user or provide generic advice.  
It is designed to help structure anxiety, distinguish controllable and uncontrollable factors, reduce unnecessary intervention, and support stability-first decision-making.

---

## Research Background and Origin

This project is part of a personal research line called **Emotion-Aware Control**.

The core idea is to treat emotions such as anxiety, fear, and agitation not as noise to be eliminated, but as **risk signals indicating possible instability in a human system**.

This framework emerged from long-term lived experience with anxiety disorder, self-reflection, cognitive behavioral therapy, metacognition, mindfulness, Zen, Stoic philosophy, data science, and control engineering.

The original theoretical framework is described in the related repository:

- [emotion-aware-control](https://github.com/AmediaFujiwara/emotion-aware-control)

This chat application is an experimental extension of that framework.  
It applies the three-axis risk vector to an interactive AI chat interface.

---

## Core Concept

A typical AI chatbot may respond to anxiety with:

- empathy
- encouragement
- advice
- problem-solving suggestions
- action lists

Emotion-Aware Control Chat takes a different approach.

It first asks:

> What kind of structural risk is this anxiety pointing to?

Then it selects the response policy according to the dominant anxiety structure.

For example:

- If **Boundary Violation** is high, the AI prioritizes boundary-setting and role clarification.
- If **Uncontrollability** is high, the AI separates controllable and uncontrollable factors.
- If **Anticipated Loss** is high, the AI separates future loss prediction from present facts.
- If intervention cost is high, the AI may suggest **Non-Intervention (NI)**.

The goal is not to maximize action.  
The goal is to preserve human stability.

---

## Anxiety Three-Axis Model

### 1. Boundary Violation

Boundary Violation refers to a state in which work, responsibility, evaluation, obligation, or other people’s expectations intrude into areas that should be protected.

These protected areas may include:

- rest
- recovery
- private life
- thinking space
- role boundaries
- responsibility boundaries
- time boundaries

Examples:

- Work messages intrude into rest time.
- Tasks outside one’s role gradually become one’s responsibility.
- One is repeatedly asked to explain more and more without a clear endpoint.
- Recovery time is invaded by guilt, duty, or evaluation anxiety.

When this axis is high, the AI should avoid increasing the user’s burden.  
It should support boundary clarification, role definition, and minimal response design.

---

### 2. Uncontrollability

Uncontrollability refers to the degree to which the situation is governed by factors outside the user’s direct control.

These may include:

- other people’s reactions
- organizational decisions
- market movements
- future events
- institutional rules
- health conditions
- ambiguous evaluation criteria

Examples:

- “I don’t know what the other person thinks.”
- “The company’s direction is unclear.”
- “I don’t know what I need to do for this to end.”
- “No matter what I do, the final decision depends on someone else.”

When this axis is high, the AI should help separate controllable and uncontrollable factors.  
It should avoid encouraging endless prediction or over-analysis.

---

### 3. Anticipated Loss

Anticipated Loss refers to anxiety caused by the possibility of losing something important in the future.

The anticipated loss may involve:

- evaluation
- health
- livelihood
- family relationships
- career stability
- social position
- self-efficacy
- future security

Examples:

- “My evaluation may drop.”
- “My position may become worse.”
- “My life may collapse.”
- “My family relationship may break down.”
- “This may become irreversible.”

When this axis is high, the AI should separate present facts from future loss predictions.  
It should avoid giving shallow reassurance, while also avoiding amplification of catastrophic expectations.

---

## NI / Non-Intervention

NI stands for **Non-Intervention**.

In this framework, NI does not mean neglect, avoidance, or giving up.

NI means:

> intentionally not intervening in a domain where intervention is unlikely to improve stability, or where the cost of intervention is too high.

NI is a stability-first control policy.

Examples of NI:

- Do not decide today.
- Do not try to obtain complete agreement from the other person.
- Do not handle a future loss that has not yet occurred.
- Do not predict the entire organization’s future direction today.
- Only write a draft and do not send it yet.
- Observe the situation without acting immediately.
- Stop continuing the conversation with AI and rest.

NI is especially important when uncontrollability is high and additional thinking or action would increase exhaustion.

---

## Control Loop

The application implements the following feedback loop:

```text
User input
    ↓
Analyzer estimates the three-axis risk vector
    ↓
Dominant pattern and response policy are selected
    ↓
Responder generates a stability-first reply
    ↓
Radar chart and score panel are displayed
    ↓
Score history is updated
    ↓
Next conversation turn
```

This loop is intended to support metacognition and stability, not to replace professional care.

---

## Response Policy Mapping

The three-axis score is used to guide the AI response.

### High Boundary Violation

Primary response policy:

- clarify responsibility boundaries
- protect rest and recovery
- reduce unnecessary obligations
- avoid adding tasks
- support minimal communication

Example response direction:

> “The issue may not be the task itself, but the way responsibility is entering your recovery space. Today’s minimum action may be to confirm the boundary, not to solve everything.”

---

### High Uncontrollability

Primary response policy:

- separate controllable and uncontrollable factors
- reduce prediction
- avoid mind-reading
- focus on one small controllable action
- consider observation instead of immediate action

Example response direction:

> “The other person’s final reaction is not directly controllable. What can be controlled today is the wording of one short message or the decision to wait.”

---

### High Anticipated Loss

Primary response policy:

- separate present facts from future loss predictions
- identify what is actually at risk
- avoid shallow reassurance
- reduce catastrophic projection
- preserve evidence or records if useful

Example response direction:

> “The fear is pointing toward a possible future loss, but that loss has not yet occurred. Today’s task is not to solve the whole future, but to preserve one stabilizing piece of information.”

---

### High Boundary Violation + High Uncontrollability

Primary response policy:

- limit the response scope
- avoid endless explanation
- clarify what is confirmed and what requires judgment
- avoid trying to fully control the other person’s satisfaction

Possible NI:

- do not try to obtain complete agreement today
- do not answer every possible concern
- do not expand the scope without confirmation

---

### High Uncontrollability + High Anticipated Loss

Primary response policy:

- stop long-range prediction
- separate uncertainty from actual loss
- observe rather than decide
- reduce intervention cost

Possible NI:

- do not decide today
- do not handle future outcomes without evidence
- do not continue predicting the organization, market, or other people’s reactions

---

### All Three Axes High

Primary response policy:

- reduce intervention
- avoid long analysis
- avoid adding tasks
- support physical and emotional stabilization
- suggest professional or emergency support if needed

Example response direction:

> “This is not a good moment to add more tasks. The priority is stabilization, not problem-solving.”

---

## Features

- Streamlit chat interface
- Three-axis anxiety scoring
- Radar chart visualization
- Score panel with dominant pattern and response policy
- Time-series score history
- LLM-based analysis and response generation
- Keyword-based fallback demo mode
- JSON export of session history
- Safety notice for crisis-related expressions

---

## Setup

### Requirements

- Python 3.11 or later
- [uv](https://github.com/astral-sh/uv)

### Installation

```bash
cd emotion-aware-control-chat
uv sync
uv run streamlit run app.py
```

---

## API Configuration

This application can run in two modes:

1. **Demo mode**  
   No API key required.  
   Uses keyword-based fallback rules.

2. **LLM mode**  
   Requires an Anthropic API key.  
   Uses Claude for three-axis analysis and response generation.

To use LLM mode, create a `.env` file:

```bash
cp .env.example .env
```

Then add your API key:

```env
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

You can also enter the API key from the Streamlit sidebar.  
The default model is `claude-sonnet-4-6`.

---

## Usage

1. Start the application.

```bash
uv run streamlit run app.py
```

2. Select demo mode or LLM mode from the sidebar.

3. Enter an anxious thought, concern, or situation into the chat input.

4. The application will generate:

- three-axis score
- dominant anxiety pattern
- response policy
- AI response
- radar chart
- score history

---

## Directory Structure

```text
emotion-aware-control-chat/
├── app.py
├── README.md
├── pyproject.toml
├── .env.example
├── .gitignore
├── prompts/
│   ├── analyzer_prompt.md
│   └── responder_prompt.md
├── schemas/
│   └── anxiety_risk_vector.py
├── services/
│   ├── llm_client.py
│   ├── analyzer.py
│   └── responder.py
├── components/
│   ├── radar_chart.py
│   ├── score_panel.py
│   └── history_chart.py
├── utils/
│   ├── storage.py
│   └── fallback_rules.py
├── docs/
│   ├── emotion_aware_chat_design_jp.md
│   ├── response_policy_mapping_jp.md
│   ├── non_intervention_policy_jp.md
│   └── safety_note_jp.md
└── examples/
    └── sample_dialogues_jp.md
```

---

## Safety Notice

This application is not:

- a medical device
- a diagnostic tool
- a therapy system
- a substitute for psychiatric or psychological care
- an emergency support system

If you are in immediate danger, feel unable to stay safe, or may harm yourself or others, please contact local emergency services or a trusted person immediately.

In Japan:

- Emergency: 119
- Yorisoi Hotline: 0120-279-338

If you are outside Japan, please contact your local emergency number or crisis support service.

---

## Privacy Notice

This application is intended primarily for local use.

However, if LLM mode is enabled, user input may be sent to the selected LLM API provider according to that provider’s terms and privacy policy.

Do not enter:

- personal identifiers
- confidential workplace information
- private medical records
- passwords
- API keys
- information about third parties without consent

For sensitive use, demo mode or a local/private model should be considered.

---

## Relationship to the Original Framework

This repository is an applied chat prototype based on the broader **Emotion-Aware Control** framework.

Original framework:

- [emotion-aware-control](https://github.com/AmediaFujiwara/emotion-aware-control)

The original framework defines emotions as risk signals and models structural emotional risk as:

```text
R = [b, u, l]
```

where:

- `b` = Boundary Violation
- `u` = Uncontrollability
- `l` = Loss / Anticipated Loss

This chat application applies that vector to AI response policy selection.

---

## Citation / Attribution

If this repository, the Anxiety Three-Axis Model, the NI concept, or the response-policy control idea inspires your research, implementation, or writing, please cite or refer to this repository as one of the originating public sources.

Suggested citation:

```bibtex
@misc{fujiwara2026emotionawarecontrolchat,
  author = {Amedia Fujiwara},
  title = {Emotion-Aware Control Chat: Anxiety Three-Axis Model and Stability-First AI Response Control},
  year = {2026},
  howpublished = {GitHub repository},
  url = {https://github.com/AmediaFujiwara/emotion-aware-control-chat}
}
```

Related theoretical repository:

```bibtex
@misc{fujiwara2026emotionawarecontrol,
  author = {Amedia Fujiwara},
  title = {Emotion-Aware Control: A Stability-First Decision and Control Framework for Emotional Risk Signals},
  year = {2026},
  howpublished = {GitHub repository},
  url = {https://github.com/AmediaFujiwara/emotion-aware-control}
}
```

---

## License

Please add a license file before public release.

Recommended options:

- **MIT License** for source code
- **CC BY 4.0** for documents, concepts, and explanatory materials

If attribution is especially important, clearly state that attribution is requested when using or extending the conceptual framework.

---

## Future Work

1. **Persistent session storage**  
   Store conversation history using SQLite or file-based storage.

2. **Custom NI templates**  
   Allow users to define their own Non-Intervention patterns.

3. **Local LLM support**  
   Support local models for privacy-sensitive use.

4. **Multilingual interface**  
   Add Japanese/English UI switching.

5. **Response policy evaluation**  
   Evaluate whether the selected response policy actually reduces perceived instability.

6. **Longitudinal pattern analysis**  
   Analyze repeated anxiety patterns over time.

---

## Disclaimer

This is an experimental personal research prototype.

It is intended to explore how anxiety can be represented as a structural risk signal and how AI responses can be guided by that structure.

It should not be used as a replacement for professional diagnosis, therapy, medical care, or emergency support.