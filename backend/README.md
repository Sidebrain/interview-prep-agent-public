# AI Interviewer: Event-Driven Agent Framework

An advanced agent framework for conducting AI-powered interviews and workshops with an innovative event-based architecture at its core.

## 🌟 Overview

AI Interviewer is a sophisticated backend system built to power intelligent conversational agents that can conduct professional interviews, lead workshops, and adapt to a variety of conversational scenarios. At its heart lies a custom-built event-driven architecture that enables high flexibility, extensibility, and decoupling between components.

The system represents a significant evolution in agent design, moving beyond traditional sequential processing to a reactive, event-based model that allows for complex, non-linear interactions.

## 🏗️ Architecture

The codebase contains two primary architectural approaches:

### Event-Based Architecture (`app/event_agents/`)

The primary and most advanced system, built on a publish-subscribe pattern that decouples components and allows for flexible, reactive processing:

- **Broker**: Central event bus that manages publication and subscription of events
- **Thinker**: Core reasoning component that interfaces with AI models
- **Memory**: Sophisticated state management with multiple persistence options
- **Conversation Tree**: Flexible data structure for managing complex conversation flows
- **Event Handlers**: Specialized components that react to specific events
- **Manager Classes**: Coordinate operations within each subsystem
- **Factories**: Create and configure complex objects through dependency injection

Key subsystems include:

- **Interview**: Manages the interview lifecycle, questions, timing, and evaluation
- **Evaluations**: Mini-agents that assess interviews based on customizable criteria
- **Perspectives**: Generate alternative viewpoints on candidate responses
- **Ranking**: Compare and rank multiple interviews using AI-powered assessment
- **Memory**: Flexible state persistence through a provider-based design
- **Orchestration**: Coordinate complex workflows through commands and events

### DAG-Based Architecture (`app/agents/`)

An earlier approach using a more traditional directed acyclic graph structure:

- Linear flow of information between components
- Explicit dependencies between processing steps
- Generates structured artifacts like job descriptions, rating rubrics, and interview questions
- Feeds generated artifacts into the event-based system

## 🧩 Design Patterns

The system implements several advanced design patterns:

- **Event-Driven Architecture**: Core messaging system for loose coupling
- **Factory Pattern**: Creates complex objects like interview agents and memory stores
- **Strategy Pattern**: Interchangeable implementations for components like evaluators
- **Registry Pattern**: Dynamic discovery and registration of components
- **Manager Pattern**: Coordinates complex operations within subsystems
- **Command Pattern**: Encapsulates operations as first-class objects
- **Repository Pattern**: Abstracts data access through the memory store

## 🚀 Key Features

- **Flexible Interview Engine**: Conduct structured interviews with dynamic question generation
- **Multi-modal Evaluation**: Assess candidates through various lenses and perspectives
- **Conversation Management**: Sophisticated tree-based conversation structure
- **Asynchronous Processing**: Non-blocking operations for responsive interactions
- **Extensible Framework**: Easy addition of new evaluators, perspectives, and handlers
- **Role-based Customization**: Tailor interviews to specific job roles and requirements
- **Workshop Capability**: Beyond interviews, can facilitate learning workshops

## 💡 Architecture Evolution

The event-based architecture represents the 5th major iteration in the system's design evolution, addressing limitations of previous approaches:

- Decouples components for greater flexibility and testability
- Enables parallel processing of events by multiple handlers
- Allows dynamic reconfiguration of the agent's behavior
- Supports complex, non-linear conversation flows
- Facilitates composition of agent capabilities through event handlers

This architecture demonstrates an advanced understanding of LLM-powered agent design, moving beyond simple prompt chaining to a sophisticated system that models complex interactions between specialized components.

## 🔍 Technical Focus

This codebase showcases expertise in:

- Advanced software architecture design
- AI/LLM system engineering and integration
- Event-driven and reactive programming paradigms
- Design pattern application in complex systems
- Agent framework development
- Conversational AI implementation

---

*Note: This README focuses on architecture and design. For setup and running instructions, please see the separate documentation.*
