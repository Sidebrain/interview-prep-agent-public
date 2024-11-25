# Release Notes

## Version 0.0.3

### Customer-Facing Release Notes

**Release Date:** January 31, 2024
**Version:** 0.0.3
**Compatibility:** Python 3.9+
**License:** MIT

This release brings significant improvements to the interview experience with enhanced evaluation capabilities, streamlined question flow, and improved feedback visualization. The update focuses on providing a more structured and intuitive interview process while maintaining robust performance and reliability.

#### New Features

1. **Enhanced Evaluation System**
   - Real-time feedback for interview answers with structured and text-based evaluations
   - Improved clarity and insight through specialized evaluation types such as relevance and structured thinking

2. **Streamlined Interview Flow**
   - Questions are now delivered one at a time for a more organized interview experience
   - Real-time updates on question progress and feedback

3. **Improved Feedback Visualization**
   - JSON responses now display with pretty-printed formatting for easier readability
   - Enhanced structured feedback renders seamlessly alongside unstructured content

4. **Robust Time Management**
   - Configurable interview time limits ensure sessions stay on track
   - Timeout mechanisms provide clear notifications for session endings

#### Reliability Enhancements

- Reduced errors and improved stability during interview question gathering and processing
- Streamlined the overall experience with fewer interruptions and better flow

#### Performance Improvements

- Faster processing of interview responses with optimized backend systems
- Enhanced logging ensures smoother operation with quicker troubleshooting

### Developer Release Notes

#### Major Updates

1. **Structured Evaluation System**
   - Refactored evaluation system with EvaluatorSimple and EvaluatorStructured base classes
   - Introduced Pydantic schemas for structured thinking and framework-based evaluations
   - Added type-safe dispatchers and context builders for both simple and structured evaluation

2. **Evaluation Infrastructure**
   - Configurable evaluators allow for specialized assessments like relevance, exaggeration, and structured thinking
   - EvaluationManager introduced to coordinate modular evaluator instances
   - Extended evaluation instructions for parallel and flexible assessment handling

3. **Interview Management Overhaul**
   - InterviewManager split into specialized components:
     - TimeManager: Manages timeout tracking
     - QuestionManager: Handles question iteration
     - InterviewEventHandler: Centralizes event-related logic
   - Introduced session tracking with structured events like AskQuestionEvent and InterviewEndEvent

4. **Frontend Updates**
   - Pretty-printing for structured JSON responses
   - Enhanced WebSocket endpoints (migrated to V3) for better compatibility
   - Improved rendering logic to seamlessly handle Markdown and JSON

5. **Event-Driven Architecture**
   - Introduced an event broker system using a pub/sub pattern for async communication
   - New events added for real-time updates:
     - MessageReceivedEvent, ThinkEvent, and MemoryUpdateEvent

#### Breaking Changes

- Memory store operations are now asynchronous (MemoryStore.add requires async calls)
- InterviewManager and related logic significantly restructured—backward compatibility may require adaptation
- Dispatcher moved to a dedicated module (app/agents/dispatcher.py)

#### Refactors

- Modularized codebase:
  - Memory management extracted into dedicated modules with clear protocols (InMemoryStore)
  - Dispatcher and debug configurations decoupled for better maintainability
  - Improved separation of concerns across multiple components

#### Other Notable Changes

- Centralized question delivery logic in ask_next_question for maintainable interview flow
- Improved error handling and logging across agents, memory management, and evaluation systems
- Added create_task for non-blocking interview initialization, reducing latency

#### Known Issues

- Duplication and inconsistency between V2 and V3 APIs require further clean-up (pending future updates)
- Evaluation system base classes remain somewhat rigid; flexibility improvements are in progress
