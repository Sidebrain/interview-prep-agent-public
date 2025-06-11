# Audition

**Audition** is a fully‑configurable, AI‑driven recruiting platform whose fundamental premise is that *every company should be able to build its own recruiter, not inherit somebody else’s*.
Unlike traditional “black‑box” recruiting agents—whose prompts and scoring rubrics are hard‑wired by the vendor—Audition exposes the entire talent‑evaluation pipeline so you can design, observe, and tweak it to fit **any** role in **any** industry.

---

## Table of Contents

1. [Key Ideas](#key-ideas)
2. [Feature Highlights](#feature-highlights)
3. [System Architecture](#system-architecture)
4. [Getting Started](#getting-started)
5. [End-to-End Usage Walk-Through](#end-to-end-usage-walk-through)
6. [Development Journey & Design Rationale](#development-journey--design-rationale)
7. [Known Limitations](#known-limitations)
8. [Contributing](#contributing)
9. [License](#license)

---

## Key Ideas

| Concept                        | What It Means in Audition                                                                                                                                                                            |
| ------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **“Build your own recruiter”** | You control every prompt, rubric, and decision rule instead of accepting a vendor-defined model.                                                                                                     |
| **Job-Description Engine**     | A wizard that asks targeted questions and auto‑generates four artifacts: 1) full job description, 2) curated interview questions, 3) simulation / take‑home exercises, 4) a scoring *rating rubric*. |
| **Total Transparency**         | Toggle an **admin view** (see [Usage Walk‑Through](#end-to-end-usage-walk-through)) to watch every event, agent decision, and LLM call in real time.                                                 |
| **Event-Based Agents**         | Each rubric item gets its own mini‑agent that listens to the interview timeline, forms an opinion, and proposes follow‑ups. A master agent “democratically” chooses the next question.               |
| **Industry-Agnostic**          | Works for software engineers *and* warehouse managers, baristas, VPs of Sales—anything.                                                                                                              |

---

## Feature Highlights

* **Interactive Job‑Description Wizard** – converts your answers into four production‑ready artifacts.
* **Configurable Interview Flow** – every mini‑agent is derived from your custom rubric, so the conversation tree matches *your* priorities.
* **Real‑Time Admin Dashboard** – view all events, agent prompts, model outputs, and time stamps as they happen.
* **Regenerate Artifacts at Will** – tweak a single answer and instantly refresh the JD, questions, rubric, and simulations.
* **Built‑In Timer Control** – configure time limits per interview or per question.
* **Camera & Audio Ready** – browser flow requests mic/video permissions out of the box.

---

## System Architecture

```
                ┌──────────────────────────┐
                │   Interview Timeline     │  ← central event bus
                └──────────┬───────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
┌──────────────┐  ┌────────────────┐  ┌────────────────┐
│ Mini-Agent #1│  │ Mini-Agent #2  │  │ Mini-Agent #N  │  ← One per rubric item
└──────┬───────┘  └──────┬─────────┘  └──────┬─────────┘
       │                 │                   │
      opinions &        opinions &          opinions &
  follow-up proposals    proposals           proposals
       │                 │                   │
       └──────────┬──────┴──────────┬────────┘
                  ▼                 ▼
              ┌────────────────────────┐
              │ Master “Chooser” Agent │  ← selects next question
              └────────────────────────┘
```

* **Event Bus**: every utterance, LLM response, or system action emits an event onto the timeline.
* **Mini‑Agents**: subscribe to the bus, update internal scores, and emit *suggested follow‑up questions* when confidence is low.
* **Master Agent**: collects suggestions and chooses the highest‑value next question via democratic pooling.
* **Stateless Front‑End**: subscribes to the same bus to render candidate view & admin dashboard in real time.

---

## Getting Started

> **Prerequisites**
>
> * Node.js & npm (front‑end)
> * Python ≥ 3.10 (back‑end)
> * An OpenAI (or compatible) API key in `OPENAI_API_KEY`

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-org/audition.git
   cd audition
   ```

2. **Install dependencies**

   ```bash
   # Back‑end
   cd backend
   uv venv --python 3.11
   uv sync
   source .venv/bin/activate


   # Front‑end
   cd ../frontend
   npm install
   ```

3. **Run both services in separate terminals**

   ```bash
   # Back‑end (default http://localhost:8000)
   uvicorn app.main:app --reload

   # Front‑end (default http://localhost:3000)
   npm run dev
   ```

---

## End-to-End Usage Walk-Through

1. **Navigate to *Home*** (`http://localhost:8000`).
2. Click **Create Job** → complete the *Job‑Description Engine* questionnaire.
3. On submission you receive **four artifacts**:

   * Job Description
   * Interview Questions
   * Simulation / Take‑Home Tasks
   * Rating Rubric
     You can **Regenerate** any artifact from this screen.
4. There is an **Interview Link** generated. Copy the URL.
5. **Open the Link** in a new tab (this is the *candidate view*).

   * Grant microphone / camera permissions when prompted.
   * after going through all the steps, the interviewer takes 1-2 minutes to confugure itself. It is done configuring when the AI asks you the first question.
6. **Toggle Admin View**:

   * Append `/admin` (or the route you find in `client/src/router.ts`) to the interview URL.
   * After the interview is loaded, change the route from `/interview?interview_session_id=ba914e9c-da02-49f4-87d3-311ec28a0752` to `/simulate-interview?interview_session_id=ba914e9c-da02-49f4-87d3-311ec28a0752`
    * This is the under the hood view and shows the Evaluation agents, and shows the sample answer that gets generated (you can also switch on perspectives by going to backend/app/event_agents/itnerview/factory.py and setting the flag to true)
7. **Adjust Timers** if desired (same factory as above).
8. Conduct the interview; watch the conversation tree evolve in real time.
9. Review final rubric scores and exported transcript.

---

## Development Journey & Design Rationale

| Version                               | What We Tried                           | Why We Moved On                                                            |
| ------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------- |
| **v0 – Simple Agent**                 | Single LLM prompt; no branching.        | Zero flexibility, hard‑coded flow.                                         |
| **v1 – LangGraph Prototype**          | Adopted LangGraph for node‑edge graphs. | Extra framework abstraction limited low‑level control.                     |
| **v2 – Hand‑Rolled Graph**            | Custom Python graph engine.             | Graphs still too rigid; adding/removing nodes painful.                     |
| **v3 – Event‑Based System (Current)** | Central timeline + subscriber agents.   | Maximum configurability, mirrors real‑world “events happen, agents react.” |

**Why Events?**

* Mirrors conversational reality.
* Lets mini‑agents act independently yet remain synchronized.
* Unlocks features like real‑time dashboards and replay.

**Trade‑Offs**

* **Traceability** – when *everything* is an event, pinpointing a failure path is harder.
* **Observability** – we solved this with the admin dashboard, but deeper tracing tools are on the roadmap.

---

## Known Limitations

* **Debugging Complexity** – event storms can hide the root cause of a failed LLM call.
* **Localhost‑Only Quick‑Start** – no one‑click cloud deployment script (yet).
* **Admin Route Discoverability** – currently requires manual URL edit; a UI toggle is planned.

---

## Contributing

1. Fork → create feature branch → open pull request.
2. For major changes, open an issue first to discuss scope.
3. Follow the existing event schema; new event types belong in `/server/app/events/`.

---

## License

Distributed under the MIT License. See `LICENSE` for details.

---

*“The world is auditioning for a role. Give it a fair script.”*

