# Project README

## Detailed Git Log
*Last updated: 2025-03-01 00:35:30*

### Commit: 982a366
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Feb 22 22:29:17 2025 +0530

> refactor: removed unecessary init methods in abstract implementaion of asking strategy



---

### Commit: 7c1ee5e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Feb 22 18:00:10 2025 +0530

> feat(roles): Integrate role context into interview lifecycle

Adds role context generation and integration with the interview system. The role
builder now analyzes job descriptions to create structured role definitions and
system prompts that guide agent behavior.

Key changes:
- Role context is built during interview initialization
- Thinker can now boost messages with role-specific system prompts
- Moved role types to dedicated module for better organization

Areas for future work:
- Role context persistence is not implemented yet
- Need to add different behavior modes beyond service delivery
- Question generation does not directly incorporate role context
- Consider caching role analysis results for performance
- May want to add role-specific evaluation criteria

Breaking changes: None


---

### Commit: 489b7f3
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Feb 22 12:46:38 2025 +0530

> feat: enhance shell script infrastructure

• Add MongoDB Docker setup script for local development
• Create utility for copying Python files to clipboard
• Add README auto-generation script with git history, this will run
inpre-commit hook
• Set executable permissions on shell scripts

The changes streamline development workflows by adding convenient
utilities for local database setup, code sharing, and documentation
management.


---

### Commit: 8ae1674
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Feb 22 12:44:55 2025 +0530

> feat: add AI interview cost calculator with Streamlit UI

Add a sophisticated cost calculator for AI-driven interviews with an interactive Streamlit interface. Features include:

- Token-based cost modeling for questions, answers, and evaluations
- Configurable parameters for fine-tuning simulation scenarios
- Interactive visualizations with Altair for cost analysis
- Support for accumulative context modes in evaluation and question generation
- Detailed cost breakdowns and metrics

The calculator helps estimate and analyze costs for AI interview systems while providing intuitive controls for experimentation.


---

### Commit: 1d9c9ac
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Feb 8 22:49:40 2025 +0530

> feat: Add configurable interview abilities system

Introduce a new InterviewAbilities system to make evaluation and perspective
generation optional and configurable per interview. This change improves system
flexibility and resource efficiency by:

- Adding InterviewAbilities dataclass to control feature flags
- Making evaluation and perspective systems conditionally initialized
- Adding safety checks before attempting to initialize disabled systems
- Improving error handling with detailed traceback logging
- Setting default configuration (evaluations enabled, perspectives disabled)

The changes make the interview system more modular and allow for better resource
management by only initializing and running the components that are needed for
each specific interview session.

Technical changes:
- Added InterviewAbilities to InterviewContext
- Updated factory.py to configure abilities during interview creation
- Modified LifecycleManager to respect ability settings
- Enhanced error messages with full stack traces
- Removed unused max_depth parameter from Prober class

Updated README


---

### Commit: f888b55
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Feb 8 16:54:01 2025 +0530

> feat: Enhance conversation tree visualization and add debug controls

Improve the conversation tree's structure and visualization with several key enhancements:

- Add debug mode toggle for detailed logging of tree operations
- Refactor tree visualization to better handle breadth-first relationships
- Sort children by breadth for more consistent visual output
- Improve marker logic for clearer parent-child relationships
- Increase default tree bounds (max_depth: 4, max_breadth: 6)
- Add randomized probe direction selection for more natural conversation flow

The changes make the conversation tree more flexible and easier to debug while
providing a clearer visual representation of the dialogue structure.


---

### Commit: 20d6a29
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Feb 8 15:29:37 2025 +0530

> fix: improve conversation tree handling of broader probes (sibling nodes)

- Fix parent assignment in broader probes to maintain correct tree structure
  - When adding a broader turn, it becomes a sibling node by attaching to the current turn's parent
  - This differs from deeper turns which attach directly to the current turn as children
- Replace print debugging with structured logging for better observability
- Add comprehensive tests for:
  - Adding sibling nodes via broader probes
  - Mixed probe directions (deeper + broader)
  - Verifying correct parent/child relationships


---

### Commit: 1eb87b1
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Feb 8 15:09:10 2025 +0530

> feat: added new simulation assignmen artifact type



---

### Commit: c3698f6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Jan 31 15:10:06 2025 +0530

> refactor: split conversation tree into separate components

BREAKING CHANGE: Renamed ConversationTree to Tree and ConversationalTurn to Turn

This commit improves the organization and maintainability of the conversation
tree implementation by:

- Splitting the monolithic tree_and_turn.py into separate modules:
  - tree.py: Core tree structure and navigation logic
  - turn.py: Individual conversation turn representation

- Simplifying class names for better readability:
  - ConversationTree -> Tree
  - ConversationalTurn -> Turn

- Maintaining all existing functionality while reducing code complexity
- Improving separation of concerns between tree structure and turn data
- Updating all relevant imports and references across the codebase

The new structure makes the code more modular and easier to maintain while
preserving the elegant tree-based conversation model.


---

### Commit: b3ebb35
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Jan 31 14:56:05 2025 +0530

> refactor: reorganize conversation tree implementation into dedicated module

Refactored the conversation tree implementation from questions/types.py into a dedicated
conversations module to improve code organization and maintainability. The new structure
better reflects the domain model and separates concerns.

Key changes:
- Created new conversations package with dedicated modules:
  - tree_and_turn.py: Core conversation tree and turn implementations
  - types.py: ProbeDirection enum definition
  - utils.py: Probability helpers for tree navigation
- Updated imports across affected modules to use new package structure
- Kept ConversationalTurn and ConversationTree in same file to avoid circular imports
- Added __init__.py with clear public API exports

The conversation tree is a central concept in our interview system, managing the
branching dialogue structure. While initially considered splitting the turn and tree
implementations, they remain tightly coupled due to their recursive nature. This
refactor improves code organization while maintaining practical considerations around
circular dependencies.

No functional changes, purely organizational improvements.


---

### Commit: 70baa6f
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Jan 31 11:54:05 2025 +0530

> feat(conversation): Add historic context and improve tree navigation

Enhance the ConversationalTurn model with methods to track and retrieve conversation history:

- Add get_full_historic_context() to build complete conversation chain
- Add get_parent() and get_context() helper methods for context building
- Update current_position tracking in ConversationTree after adding new turns
- Replace verbose debug printing with simplified tree state output
- Add comprehensive tests validating conversation context and tree navigation

The changes improve the conversation tree's ability to maintain context as the
discussion grows deeper or broader, while making the implementation more elegant
and easier to follow. The new context methods enable proper tracking of the
conversation flow in a format ready for LLM consumption.


---

### Commit: d7446ef
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Jan 31 10:56:55 2025 +0530

> feat: add probability-based conversation direction control

Introduces a flexible system for controlling how conversations grow through the tree structure:

- Add normalize_probabilities() utility that:
  - Handles cases where one or both probabilities are missing
  - Normalizes any two probabilities to sum to 1.0
  - Defaults to 50/50 split when no preferences given

- Add choose_probe_direction() to make weighted random choices between:
  - DEEPER: vertical conversation growth (follow-up questions)
  - BROADER: horizontal growth (alternative topics)

- Add comprehensive test suite covering:
  - Edge cases in probability normalization
  - Deterministic direction choices
  - Statistical distribution validation
  - Biased probability scenarios

This lays groundwork for more sophisticated conversation steering, though the
functionality is not yet integrated into the main conversation flow. Future work
will tie this into ConversationTree to enable dynamic conversation patterns.


---

### Commit: e940d31
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 30 20:26:20 2025 +0530

> feat: Implement conversation tree for structured interview dialogue

Add a sophisticated tree-based conversation structure to better manage and track
the flow of interview questions and answers. This enhancement provides more
control over conversation depth and breadth while enabling future support for
dynamic question generation.

Key changes:
- Introduce ConversationalTurn and ConversationTree models for managing dialogue structure
- Add ProbeDirection enum to control conversation growth (depth vs breadth)
- Integrate conversation tree with answer processing pipeline
- Simplify perspective handling and logging with debug flag
- Refactor question asking strategies with cleaner abstractions

Technical details:
- ConversationTree tracks max_depth/breadth and current position
- Tree visualization with ASCII art for debugging
- Abstract base class for question asking strategies
- Memory-efficient tree traversal and growth validation
- Structured logging with context for better debugging

This change sets the foundation for more intelligent conversation management
and dynamic question generation based on candidate responses.


---

### Commit: 78b683f
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 30 14:00:26 2025 +0530

> refactor(questions): streamline question strategy initialization

Improve the QuestionManager initialization flow by consistently handling strategy classes:

- Refactor QuestionManager to accept strategy classes instead of instances
- Move strategy instantiation into QuestionManager for better encapsulation
- Remove default InterviewQuestionGenerationStrategy fallback
- Update InterviewManager to pass ServiceQuestionGenerationStrategy class instead of instance
- Add explicit current_question assignment for evaluation/perspective generation

This change makes the strategy initialization more consistent and predictable while
maintaining separation of concerns. The QuestionManager now has full control over
when and how strategies are instantiated, reducing complexity in the calling code.


---

### Commit: af65429
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 30 13:45:01 2025 +0530

> refactor: introduce BaseQuestionAskingStrategy to decouple question management

Separates question asking logic from QuestionManager into a dedicated strategy pattern to improve separation of concerns and flexibility. This change:

- Creates new BaseQuestionAskingStrategy class to handle question iteration logic
- Updates QuestionManager to delegate question asking responsibilities
- Injects question asking strategy via constructor dependency injection
- Maintains existing question generation strategy while adding clear separation between generation and asking

This refactoring improves the codebase by:
- Making the question asking behavior more modular and extensible
- Clarifying the distinction between question generation and question asking
- Enabling easier testing and maintenance of question asking logic
- Following SOLID principles by separating responsibilities

The change is backwards compatible and sets up the foundation for implementing different question asking strategies in the future.


---

### Commit: a13f6b1
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 30 13:17:52 2025 +0530

> refactor: simplify question management by removing mutable state

- Remove questions list from BaseQuestionGenerationStrategy, making it more functional
- Return questions directly from initialize() instead of storing state
- Move question state management solely to QuestionManager
- Improve type safety with explicit return types


---

### Commit: 236b325
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 30 13:03:02 2025 +0530

> refactor: improve question loading from memory

Split question parsing logic into a dedicated method and improve error handling when loading questions from memory. Renamed method to better reflect its purpose.


---

### Commit: 33b09ed
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 30 12:44:39 2025 +0530

> refactor: streamline interview initialization and question management

- Remove unused interview config validation
- Improve error handling in question manager initialization
- Add type hint for onboarding link URL
- Clean up imports and remove unused code


---

### Commit: 92ea53f
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Jan 28 15:44:36 2025 +0530

> feat: main interview is now linking to interview-new page



---

### Commit: f475629
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Jan 28 15:32:42 2025 +0530

> fix: restore artifacts and refactor agent artifact handling

- Refactored artifact generation flow in Agent class to be more modular
- Added save_artifacts_to_mongo_return_interviewer method to return interviewer object
- Added send_onboarding_link method to handle final user communication,
  this sends the onboarding link to the user for immediate use
- Restored accidentally removed YAML artifacts needed for agent creation flow
- code formatting improved in ArtifactContext


---

### Commit: 332671d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 27 21:38:16 2025 +0530

> fix(chat): improve message container scroll behavior and layout

Refines the chat interface layout and scroll behavior for a better user experience:

- Remove redundant overflow-y-auto from MessageContainer as it's handled by parent
- Fix message container height and flex layout to prevent content overflow
- Adjust text color in message bubbles for better contrast
- Ensure proper height inheritance through layout hierarchy

Technical changes:
- MessageContainer now relies on parent for scroll behavior
- InterviewLayout uses proper flex column layout with h-full
- Message bubble text color only applies white to user messages

The changes improve the overall stability of the chat interface while
maintaining the core functionality. The message container now properly
fills available space and scrolls smoothly.


---

### Commit: 7a1c2dd
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 27 21:26:41 2025 +0530

> feat(chat): implement core chat interface with voice/text input

Implements the foundational chat interface with working voice and text input functionality.
While the UI needs polish, the core features are operational:

- Text input with auto-resizing textarea
- Voice transcription with start/stop controls
- Message bubbles with proper styling and timestamps
- Input mode switching between voice and text
- Proper message threading and scrolling behavior

Technical improvements:
- Refactored MessageContainer for better state management
- Consolidated input handling logic in UserInputArea component
- Improved frame selection logic for message rendering
- Added proper TypeScript types throughout components

Note: UI needs cleanup work:
- Message bubble styling needs refinement
- Input area layout could be more polished
- Voice/text mode switching UI needs better transitions
- Some spacing and alignment issues to address
- MessageContainer does not scroll

Next steps:
- Polish UI/UX details
- Add loading states and error handling
- Improve accessibility
- Add proper animations for mode switching

The core chat functionality is working well, providing a solid foundation
for UI polish and feature additions.


---

### Commit: 1376906
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 27 19:36:57 2025 +0530

> fix: readding a config yaml that I accently removed in the prev commit



---

### Commit: 44dcaf3
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 27 16:16:19 2025 +0530

> refactor: consolidate notification system and streamline websocket types

This commit introduces a comprehensive notification system and improves type organization across the application.

Key Changes:
- Migrate types from frontend/lib/types.ts to ScalableWebsocketTypes.ts for better organization
- Add notification address type and handlers for websocket frames
- Implement NotificationPanel component with real-time feedback display
- Remove interview-store.ts in favor of direct websocket state management
- Add logging improvements to websocket event handlers

Frontend Improvements:
- Create modular notification components with severity-based styling
- Add progress tracking for interview feedback
- Implement expandable notification panel with smooth animations
- Update message bubble to handle streaming state more elegantly

Type System:
- Consolidate MediaContent and notification-related types
- Add proper type definitions for notification severity and categories
- Improve type safety across websocket frame handling

Backend Changes:
- Update notification manager to use dedicated "notification" address type
- Enhance error handling and logging in websocket events

This refactor improves code organization, type safety, and provides a more
maintainable foundation for the real-time notification system.


---

### Commit: 31254f2
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 27 15:21:01 2025 +0530

> refactor: streamline message handling and improve frame deduplication

BREAKING CHANGE: Removes legacy agent configuration files and updates websocket frame handling

Key Changes:
- Enhance frame deduplication by checking both frameId and address
- Migrate message rendering to use WebSocket frames directly
- Add notification address type for system messages
- Remove deprecated agent configuration files
- Update message bubble component to handle new frame structure

Technical Details:
- Refactored MessageThread to use frameRenderers.messageBubble for consistent rendering
- Added address-aware deduplication in frameReducer to prevent duplicate messages with different contexts
- Updated frameSelectors.messageBubble to prefer content frames over thought frames
- Introduced notification as a new AddressType for system-level messages
- Removed legacy YAML configs (agent.yaml, agent_v2.yaml, game_manager.yaml) in favor of new architecture
- Temporarily disabled RoleBuilder in lifecycle manager for future improvements

This commit improves message handling consistency and reduces duplicate renders while setting up for future system notifications. The removal of legacy configs helps streamline the codebase as we move towards the new architecture.


---

### Commit: c75999b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 27 13:48:45 2025 +0530

> feat: integrated the bolt.new version of the interview

Generated a bolt.dev project for the UI. Integrated that into the main project. Merged both of them and kept it in the interview-new page.


---

### Commit: 00c0613
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Jan 25 18:20:38 2025 +0530

> feat(roles): Implement dynamic role analysis and system prompt generation

Introduces a new RoleBuilder system that analyzes job descriptions and generates
tailored system prompts for AI agents. This enhancement allows agents to better
embody specific professional roles during interviews.

Key changes:
- Add RoleBuilder class with structured role analysis capabilities
- Implement StructuredRole model to capture key role attributes
- Create RoleContext to manage system prompts and role metadata
- Update ServiceQuestionGenerationStrategy with more natural conversation flow
- Remove legacy role handling from Thinker class

Integration status:
While the RoleBuilder is functional, it's currently only initialized in
InterviewLifecycleManager without full integration into the agent system. The
generated system prompts are not yet being utilized to influence agent behavior.

Future improvements:
- Integrate role context into agent decision making and responses
- Store and retrieve role contexts for consistent behavior across sessions
- Add role-specific evaluation criteria based on structured analysis
- Consider caching frequently used role analyses
- Implement the unfinished persist() method in RoleBuilder
- Add validation for generated system prompts
- Consider moving role initialization earlier in the interview lifecycle

Technical debt:
- RoleBuilder.persist() is currently a stub
- System prompt generation could benefit from additional validation
- Role context is generated but not fully utilized in the interview flow


---

### Commit: d748652
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 23 12:46:13 2025 +0530

> refactor: Enhance question generation with robust strategy implementation

- Reorganizes question generation strategies into dedicated module structure
- Moves question persistence from Interviewer to AgentProfile
- Implements BaseQuestionGenerationStrategy with shared functionality
- Adds comprehensive logging for question generation lifecycle
- Improves error handling and type safety in Interviewer.get()
- Adds connection logging for better debugging

Part of multi-mode interviewer system, providing a robust foundation for different question generation approaches while improving maintainability and observability.


---

### Commit: ec18903
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 22 16:25:21 2025 +0530

> feat: Implement strategy pattern for question generation

- Extracts question generation logic into dedicated strategies
- Creates BaseQuestionGenerationStrategy and InterviewQuestionGenerationStrategy
- Refactors QuestionManager to use strategy pattern
- Adds question_bank_structured to AgentProfile for future behavior modes
- Improves type hints and error handling
- Fixes minor type issues in evaluator_base

Part of multi-mode interviewer system, enabling flexible question generation strategies for different interview modes while maintaining clean separation of concerns.


---

### Commit: e399c89
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 22 16:01:15 2025 +0530

> feat: Add AgentProfile sync and validation (backward compatible)

- Adds AgentProfile to InterviewContext for behavior management
- Implements sync_agent_profile method in Interviewer model
- Overrides Interviewer.get() to ensure AgentProfile exists
- Adds validation checks for AgentProfile in interview creation
- Mirrors AgentProfile data from Interviewer operations, maintaining backward compatibility
- No breaking changes - AgentProfile transparently shadows Interviewer data

Part of multi-mode interviewer system, ensuring agent profiles are always in sync with interviewer data while maintaining existing functionality.


---

### Commit: 9158eed
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 22 15:10:45 2025 +0530

> refactor: Move question management into dedicated module

- Relocates question_manager.py to new questions/ module
- Updates imports across interview components
- Maintains existing functionality while improving code organization
- Prepares for future question-related features across different behavior modes


---

### Commit: 7392cec
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 22 15:06:09 2025 +0530

> feat: Add AgentProfile model for persistent interviewer behavior

- Creates AgentProfile document to store interviewer capabilities and preferences
- Overrides Interviewer.save() to automatically sync with AgentProfile
- Updates database initialization to include AgentProfile collection
- Extends EntityType to support AgentProfile in memory stores

Part of multi-mode interviewer system, enabling persistent storage of interviewer behavior configurations and capabilities.


---

### Commit: 4d9a64e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 22 14:03:57 2025 +0530

> feat: Add behavior modes to enable flexible interviewer roles

- Adds BehaviorMode enum (INTERVIEW, PEER_INTERVIEW, SERVICE) as part of multi-mode interviewer system
- Implements RoleBuilder.build() with basic role prompt
- Simplifies hiring requirements to focus on core Role concept

Part of larger feature enabling interviewers to flexibly switch between conducting interviews, peer interviews, or offering services. Architecture supports adding additional modes as needed.


---

### Commit: 9c338c6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Jan 21 11:49:06 2025 +0530

> feat: Refactor rating rubric to use job description

- Replace YAML-based rating rubric with dynamic generation from job description
- Add Interviewer dependency to RatingRubricEvaluationBuilder
- Clean up type hints and imports
- Add RoleBuilder class scaffold for future enhancement


---

### Commit: 9ccc235
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Jan 21 10:40:01 2025 +0530

> refactor: improve media service initialization and error handling

BREAKING CHANGES:
- Update TypeVar definition for BaseModel to use type[BaseModel]
- Modify evaluator schema messages to be more question-focused

Key Changes:
- Media Service:
  - Move MediaService initialization outside useEffect for more predictable behavior
  - Improve error handling and state management in recording flows
  - Fix cleanup logic to prevent null reference issues
  - Add better logging for video stream initialization

- Evaluators:
  - Update relevance and exaggeration evaluators to use question-based schemas
  - Modify type definition for BaseModel to be more accurate
  - Improve structured evaluation response handling

- UI Components:
  - Re-enable SuggestionArea component in simulate-interview page
  - Add await to startStream call in interview page for proper initialization

This commit focuses on improving the reliability and predictability of the media
service initialization while also enhancing the evaluation system's type safety
and user interaction patterns.


---

### Commit: 413f085
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Jan 17 11:44:15 2025 +0530

> refactor: simplify video recording logic and improve error handling

- Remove unnecessary initialization flags and cleanup commented code
- Add proper error handling for video upload failures
- Add CORS configuration for local development
- Simplify media service initialization logic


---

### Commit: 4df8806
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 16 18:24:33 2025 +0530

> feat(video): Implement video recording and upload functionality

This commit adds video recording and upload capabilities to the interview page,
including backend storage integration with Google Cloud Storage.

Key changes:
- Add storage_router.py for handling secure video uploads to GCS
- Implement VideoUploadProcessor for managing video upload workflow
- Add recording controls (start/stop/upload) to VideoPlayer component
- Configure signed URL generation for secure uploads
- Update useVideo and useMedia hooks to handle recording state

Known issues:
1. Upload button requires explicit start/stop recording first
2. Live video preview not displaying after recent changes
3. Recording preview needs investigation

Next steps:
- Debug live video preview issues
- Improve upload flow to work without explicit recording steps
- Add proper error handling and user feedback
- Add loading states for upload operations

Technical details:
- Uses Google Cloud Storage for secure video storage
- Implements file validation and sanitization
- Configures CORS and content-type restrictions
- Adds TypeScript types for API responses


---

### Commit: 8c9a8f3
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 15 20:41:44 2025 +0530

> feat(interview): add draggable video feed component

Implement a draggable video player component for the interview page that allows users
to reposition their camera feed during sessions.

Key changes:
- Create VideoPlayer component with drag-and-drop functionality using react-draggable
- Add useVideo hook to manage video stream lifecycle and state
- Update MediaService to expose streamManager for direct stream access
- Refactor useMedia hook to be more generic and reusable
- Style video container with minimal dark theme and clear drag handle

Technical details:
- Video feed dimensions set to 128x128px (w-32 h-32)
- Bounds constrained to parent container
- Auto-cleanup of video streams on component unmount
- Error handling for failed stream initialization

Dependencies:
- Add react-draggable@4.4.6


---

### Commit: c3e7ba8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 15 20:07:24 2025 +0530

> refactor: extract media handling logic into dedicated hook

Separates core media functionality from voice transcription to improve reusability
and separation of concerns. This change introduces a new `useMedia` hook that
handles all media recording, playback, and processing operations.

Key changes:
- Create new `useMedia` hook to manage recording state and media operations
- Simplify `useVoiceTranscription` by leveraging the new media hook
- Improve error handling with centralized error management
- Add support for custom error callbacks
- Standardize media blob and service management

This refactor makes the codebase more maintainable and allows for easier
implementation of additional media-related features in the future.er the commit message for your changes. Lines starting


---

### Commit: de9470a
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 15 17:03:10 2025 +0530

> refactor: enhance media processor management with type-safe registry

Improves the media processor implementation by:
- Converting processor array to a typed registry object for better processor management
- Adding dedicated runProcessor method for targeted processor execution
- Maintaining backwards compatibility with runAllProcessors
- Strengthening type safety with ProcessorType union and MediaProcessorMap

This change builds on the previous processor pattern by making it more
maintainable and type-safe. Processors are now accessed by key rather than
array index, making the code more explicit and reducing potential runtime errors.


---

### Commit: 872c1bd
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 15 16:46:17 2025 +0530

> refactor: implement media processor pattern for audio transcription

Introduces a more flexible and extensible approach to media processing by:
- Adding a generic MediaProcessor interface with type-safe processing capabilities
- Creating a BaseMediaProcessor abstract class with shared validation logic
- Refactoring AudioTranscriber to use the processor pattern
- Updating MediaService to support multiple processors in a processing chain

This change decouples media processing logic from the MediaService, making it
easier to add new processors (like translation or sentiment analysis) without
modifying existing code. The validation logic is now centralized in the base
class, reducing duplication and ensuring consistent error handling.

Technical changes:
- AudioTranscriber now extends BaseMediaProcessor<TranscriptionResult>
- MediaService accepts an array of processors in its configuration
- Simplified error handling and media validation
- Improved type safety throughout the processing chain

Areas for future improvement:
- Add processor composition to combine results from multiple processors
- Implement processor priority/ordering mechanism
- Add retry logic for failed processing attempts
- Consider adding processor-specific configuration options
- Add unit tests for the processor chain
- Consider adding progress tracking for long-running processes
- Add type validation for processor results


---

### Commit: 8ed1c29
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 15 15:47:48 2025 +0530

> refactor: consolidate media services into unified MediaService

BREAKING CHANGE: AudioService replaced with MediaService

- Introduced MediaService as a unified interface for handling media operations
- Replaced AudioService with more flexible MediaService implementation
- Added MediaServiceConfig interface for type-safe initialization
- Simplified StreamManager to accept generic media constraints
- Made timeslice parameter optional in MediaStreamRecorder
- Updated useVoiceTranscription hook to use new MediaService

This change completes the media handling refactor by introducing a unified
MediaService that can handle both audio and video streams. The service now
accepts configuration through a strongly-typed interface, making it more
maintainable and flexible for future media types.

The optional transcriber dependency allows MediaService to handle pure
recording scenarios without unnecessary transcription overhead. This
separation of concerns makes the codebase more modular and easier to test.


---

### Commit: 25aaadc
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 15 14:59:22 2025 +0530

> refactor: generalize audio recorder to handle multiple media types

BREAKING CHANGE: Renamed AudioRecorder to MediaStreamRecorder

- Refactored AudioRecorder into MediaStreamRecorder to support both audio and video streams
- Introduced MediaMimeType type to handle different media formats
- Reorganized media infrastructure files into a dedicated media directory
- Moved audio-specific components into audio subdirectory
- Updated import paths and dependencies throughout the codebase
- Created new InterviewArea component for video-enabled interviews
- Split interview functionality between /interview and /simulate-interview routes

This change prepares the codebase for upcoming video recording features while
maintaining existing audio functionality. The MediaStreamRecorder now serves as
a more flexible foundation for handling different types of media streams.


---

### Commit: 00d1ec1
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 15 12:12:47 2025 +0530

> refactor: move interview components to shared directory for multi-user support

WHAT:
- Relocated all components, hooks, services, and infrastructure from /app/interview to /app/shared
- Updated import paths across all affected files
- Maintained existing functionality while improving code organization

WHY:
- Enables creation of separate interview experiences for different user roles (recruiter/candidate)
- Promotes code reuse by centralizing common components and utilities
- Improves maintainability by avoiding duplication of shared functionality
- Prepares codebase for future role-specific UI implementations

Technical Details:
- Moved components (UserArea, EvaluationArea, etc.) to /shared/components
- Relocated context providers (WebsocketProvider, InputProvider) to /shared/context
- Transferred infrastructure code (websocket, audio) to /shared/infrastructure
- Updated all import paths to reflect new directory structure
- No functional changes or behavior modifications

This refactoring sets the foundation for implementing role-specific interview
interfaces while maintaining a single source of truth for shared functionality.


---

### Commit: 46f1b5d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 15 11:48:38 2025 +0530

> chore: minor type hints and cleanup

- Add type hints to firebase auth return type
- Remove unused main() function from interview_concept_types
- Uncomment hiring requirements list items


---

### Commit: 6c16861
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 15 11:40:32 2025 +0530

> fix: restore auth_router.py after accidental deletion

Restored the Firebase authentication router that was accidentally deleted in a
previous commit. The file contains essential endpoints for token verification
and Firebase Auth proxy functionality.


---

### Commit: b3a086a
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Jan 14 18:18:13 2025 +0530

> feat: Add device permissions stage to onboarding flow

Add a new ProvidePermissions component that handles requesting and managing
microphone, camera, and screen sharing permissions before starting the interview.
This creates a smoother user experience by ensuring all required permissions are
granted before entering the interview.

Key changes:
- Add new "provide_permissions" stage to onboarding wizard
- Create ProvidePermissions component with:
  - Permission state management for mic, camera and screen
  - Live camera preview
  - Error handling for permission denials
  - Cleanup of media streams on unmount
- Update flow to request permissions before redirecting to interview
- Store interview session data in component state

This change improves the user experience by validating technical requirements
before starting the interview, reducing potential issues during the actual
interview session.


---

### Commit: f576dbb
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Jan 14 17:59:57 2025 +0530

> feat(ui): enhance onboarding form styling and layout

Improve the visual presentation and user experience of the onboarding flow:

- Add polished styling to registration form with consistent spacing and shadows
- Improve form field labels and descriptions for better clarity
- Make form layout responsive with max-width constraints
- Fix page height issues by ensuring proper min-height on root layout
- Add loading state feedback during form submission

The changes create a more professional and guided registration experience while
maintaining accessibility and usability.


---

### Commit: 14967a8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Jan 14 17:45:13 2025 +0530

> feat: Implement two-step onboarding flow with interview details

This commit introduces a more polished onboarding experience by:

- Adding an interview details preview page showing job description and interviewer info
- Creating a two-stage wizard flow (details -> user profile form)
- Moving auth router from v1 to v3 with improved user creation
- Fixing layout issues with full height containers
- Adding Markdown support for job description display
- Improving type safety with Zod schemas for Interviewer model

The new flow gives candidates context about the position before collecting their information, creating a more professional and informative experience.


---

### Commit: 32f559b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Jan 10 12:16:38 2025 +0530

> feat(agent): Implement MongoDB persistence for interview artifacts

This commit marks a significant step towards completing the interview flow,
introducing MongoDB persistence while maintaining YAML storage for backwards
compatibility.

Key Changes:
- Add save_artifacts_to_mongo() method to persist interview artifacts
- Store question bank, rating rubric, and job description in MongoDB
- Streamline hiring requirements to focus on core Role concept initially
- Maintain YAML storage temporarily for smooth transition

The interview flow now supports:
1. Agent initialization
2. User registration via link
3. Interview experience launch
4. Question generation from local memory
5. Dual persistence (MongoDB + YAML)

Areas for Future Refactoring:
- Remove YAML storage dependency
- Extract artifact management into dedicated service
- Implement proper separation of concerns for storage operations
- Consider caching layer for frequently accessed artifacts
- Streamline error handling in artifact regeneration

Progress:
This brings us closer to a complete interview flow while maintaining
stability through transitional storage mechanisms.


---

### Commit: dfde6ee
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Jan 10 11:34:44 2025 +0530

> refactor: migrate question persistence from files to MongoDB

BREAKING CHANGE: Questions are now stored in MongoDB instead of local files

This commit moves question persistence from local JSON files to MongoDB, allowing
for better scalability and data consistency across distributed systems. The
QuestionManager now saves structured questions directly to the Interviewer model
instead of using the ConfigBuilder file-based approach.

Key Changes:
- Add `question_bank_structured` field to Interviewer model
- Remove file-based ConfigBuilder dependencies from QuestionManager
- Implement JSON encoder/decoder for question serialization
- Add colored console logging with severity-based colors:
  - Grey: DEBUG
  - Green: INFO
  - Yellow: WARNING
  - Red: ERROR
  - Bold Red: CRITICAL
- Enable all hiring requirement concepts (previously disabled)

Technical Debt & Future Improvements:
1. Question Loading:
   - Current MongoDB question loading uses a hacky JSON parse/stringify cycle
   - Should implement proper CQRS pattern for question management
   - Consider moving question bank to separate collection

2. Session Management:
   - Interview session configuration still partially hardcoded
   - Need to implement flexible session configuration system
   - Consider moving session state management to dedicated service

3. Memory Management:
   - Memory operations scattered across multiple classes
   - Should consolidate memory operations into dedicated service
   - Consider implementing proper event sourcing

Testing:
- Manual testing completed for question persistence
- Verified backward compatibility with existing interviews
- Logging improvements tested across different log levels


---

### Commit: 33c93ac
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 9 16:21:10 2025 +0530

> feat(interview): Implement end-to-end interview session flow with dynamic question loading

This commit establishes a complete interview session flow from candidate registration
through websocket connection, with dynamic question loading from interviewer configs.

Key Changes:
- Implement end-to-end interview session creation and management
- Add search param based websocket connection for interview sessions
- Integrate interviewer-based question generation

Interview Flow:
1. Candidate registers through OnboardingWizard component
2. Backend creates InterviewSession linking candidate and interviewer
3. Frontend redirects to interview page with session ID in URL params
4. Websocket connects using session ID to establish dedicated interview channel

Question Management:
- QuestionManager now initializes questions from interviewer.question_bank
- KNOWN ISSUE: Question initialization currently results in empty question set,
  likely due to improper loading of interviewer config

Technical Details:
- Add InterviewSession model with PENDING/IN_PROGRESS/COMPLETED/CANCELLED states
- Update websocket endpoint to accept interview_session_id param
- Modify connection manager to validate session before establishing connection
- Enhance frontend routing to pass session ID through URL params

Frontend Changes:
- Add interview session ID handling in WebsocketProvider
- Update OnboardingWizard to handle session creation and routing
- Implement proper type definitions for interview session flow

Backend Changes:
- Modify QuestionManager to use interviewer config for question generation
- Update connection handling to validate interview sessions
- Add proper error handling for invalid session IDs

Next Steps:
- Debug question initialization to properly load from interviewer config
- Add proper session state management
- Implement session cleanup on disconnect

This establishes the foundation for personalized interview experiences while
maintaining session isolation and proper resource management.


---

### Commit: 5f7c7e6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 9 15:14:05 2025 +0530

> feat: implement candidate onboarding form with validation

Added a new onboarding wizard component with a form to collect candidate
information (name, email, phone). The form includes:

- Client-side validation using Zod schema
- Loading states and error handling
- Backend integration to create candidate records
- Type safety with TypeScript

Note: Interview flow after candidate creation is still pending implementation.
Next steps include:
- Creating interview session
- Redirecting to interview room
- Handling websocket connection

Related: #[ticket-number]


---

### Commit: c0d5ac0
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 9 11:54:59 2025 +0530

> feat: Enhance interviewer details page and refine API response

This commit evolves the onboarding flow by:

Frontend improvements:
- Create comprehensive interviewer details view with formatted sections
- Add MemoryFrames component to display websocket frame history
- Implement proper TypeScript types for Interviewer model
- Style page with clean, consistent spacing and typography
- Add fallback handling for optional fields with 'N/A' display

Backend refinements:
- Modify GET /interview/{id} endpoint to return full Interviewer object
- Rename endpoint function for clarity (validate_and_return_interviewer)
- Maintain strict type safety with proper return types

The changes create a more polished and informative interface while strengthening
the type safety and clarity of the API contract. The interviewer details page
now serves as both a validation check and a useful debugging/inspection tool.

This builds on the previous validation work by providing a complete view of
the interviewer data rather than just confirming validity.


---

### Commit: 6e26df6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Jan 9 11:30:42 2025 +0530

> feat: Improve interview validation endpoint and add onboarding page structure

This commit enhances the interview validation flow by:

Backend changes:
- Update validate_interview endpoint to accept string input and handle UUID conversion
- Add proper error handling for invalid UUIDs (400) and non-existent interviewers (404)
- Improve response structure to include interviewer_id and validation status

Frontend changes:
- Add new onboarding page with basic interviewer validation (unstyled)
- Implement test mode with fallback UUID for development
- Add initial structure for candidate registration flow

Note: Current pages are bare text without styling - UI improvements will be added
in subsequent commits. This establishes the core validation and routing logic.

The changes improve error handling and provide a more robust foundation for the
onboarding process while maintaining a clean separation between frontend and
backend validation.


---

### Commit: f1a799c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 8 11:35:38 2025 +0530

> feat(memory): Implement MongoDB-based memory store with entity-specific persistence

This commit introduces a significant architectural change to how memory is stored
and managed across the application, representing an intermediate step towards a
more robust and scalable memory system.

Key Changes:
- Refactored memory store to use MongoDB for persistence
- Introduced entity-based memory architecture (Interviewer, Candidate, Session)
- Decoupled episodic memory (interview sessions) from entity-specific memory
- Added UUID-based entity tracking in memory store
- Updated factory pattern to support entity-specific memory creation

Schema Evolution:
- Underwent three major rewrites to arrive at current structure
- Removed circular references between Session/Candidate/Interviewer entities
- Separated episodic memory (interview sessions) from entity-specific memory
- Designed for future scalability (e.g., long-term memory derived from episodes)

Known Incomplete/Broken Features:
1. create_interview() method is non-functional
   - Needs updates to handle new memory store structure
   - Interview flow currently broken

2. Artifact Management Incomplete
   - MongoDB schema fields (job_description, rating_rubric, question_bank)
     not being populated
   - Data exists in memory but not persisted to correct fields

Architecture Notes:
- Memory system now supports hierarchical structure:
  * Entity-specific memory (internal state)
  * Episodic memory (interview sessions)
  * Future: Long-term memory derived from episodes

Next Steps:
- Fix create_interview() method
- Implement artifact persistence
- Add long-term memory aggregation
- Update tests to reflect new architecture

Breaking Changes:
- Memory store initialization now requires entity and agent_id
- Existing interview flows will fail until create_interview is updated


---

### Commit: c2a6a3b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Jan 7 17:09:54 2025 +0530

> refactor: clean up artifact generating agent_v2 implementation and remove unused code

- Remove experimental ListeningAgent class and related setup/cleanup methods
- Remove unused MockInterview class implementation
- Clean up imports and organize code structure
- Add proper type hints throughout the codebase
- Update websocket disconnect handling to use client_id
- Add memory field to Interviewer schema
- Simplify agent initialization by removing pubsub pattern

This commit focuses on code cleanup and removing experimental features
that were not being used in production. The core agent functionality
remains unchanged while improving code quality and maintainability.


---

### Commit: a007d1a
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Jan 7 16:39:33 2025 +0530

> refactor: simplify schemas and standardize UUID usage

- Streamline Candidate and Interviewer models by removing non-essential fields
- Replace string IDs with UUID across models and endpoints
- Add memory field to InterviewSession for websocket frame storage
- Remove unused enums (Gender, Education, Race, Citizenship)
- Temporarily keep UUID instead of PydanticObjectId for pragmatic reasons

Note: Technical debt - UUID usage should be revisited when scaling


---

### Commit: 8f17b86
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 6 22:43:04 2025 +0530

> feat(interview): scaffold InterviewSession model and endpoint

Add initial structure for interview session tracking (schema TBD):
- Create basic InterviewSession document model with placeholder fields
- Add duration property to calculate interview length
- Implement POST endpoint for creating new interview sessions
- Register InterviewSession model with MongoDB connection

The InterviewSession model currently includes:
- Basic timestamp tracking (created_at, updated_at)
- Session status management (pending, in_progress, completed, cancelled)
- Start/end time tracking
- References to interviewer and candidate IDs

NOTE: This is initial scaffolding only - schema and field requirements
will be finalized based on product requirements. Current implementation
uses placeholder fields and basic status tracking.


---

### Commit: a5921f8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 6 20:56:12 2025 +0530

> feat(backend): Add MongoDB integration with Candidate model

This commit introduces MongoDB integration and adds a new Candidate model for storing user information. Key changes include:

- Database Configuration:
  - Added MongoDB connection settings to .env.local
  - Set up MongoDB URI and database name for local development

- New Models:
  - Implemented Candidate document model with comprehensive user fields
  - Added enums for standardized data: Gender, Education, Race, and Citizenship
  - Extended mongo_schemas.py with new document classes

- API Endpoints:
  - Added new POST endpoint /candidate for creating candidate profiles
  - Updated response_model typing for interviewer endpoint
  - Integrated Candidate model with Beanie ODM

- Dependencies:
  - Pinned beanie version to 1.27.0 for stability (1.28.0 had problems
    with PydanticObjectId encoding to json)
  - Updated database initialization to include Candidate model

This change sets up the foundation for storing and managing candidate profiles in the application.


---

### Commit: ff4ac66
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 6 11:00:16 2025 +0530

> feat: implement MongoDB integration and interview session management

This commit introduces MongoDB integration for persistent storage and adds interview session management capabilities. Key changes include:

Core Features:
- Add MongoDB storage implementation with in-memory cache for WebsocketFrames
- Create interview session router with validation and creation endpoints
- Implement Beanie ODM integration for MongoDB document modeling
- Add environment variables for MongoDB configuration

Technical Details:
- Replace InMemoryStore with MongoStore as default memory implementation
- Add error handling for WebSocket disconnections
- Implement memory synchronization between MongoDB and cache
- Add Interviewer document model with status tracking

Infrastructure:
- Add MongoDB connection initialization in FastAPI lifespan
- Update environment template with MongoDB variables
- Add motor and beanie dependencies

Currently Unused but Implemented:
- Interviewer status tracking (ACTIVE/INACTIVE enum)
- Interviewer document timestamps (created_at, updated_at)
- MongoDB collection configuration options
- WebSocket disconnect cleanup hooks

This change sets the foundation for persistent storage and session management while maintaining backwards compatibility with existing memory store interfaces.


---

### Commit: 0323d62
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Jan 6 10:30:47 2025 +0530

> feat: prepare FastAPI setup for beanie integration

Add placeholder lifecycle management via asynccontextmanager (currently unused).
Enhance type safety with proper annotations throughout and reorganize imports for better readability.


---

### Commit: 5ae6bea
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Jan 5 10:25:59 2025 +0530

> refactor(memory): extract base memory store functionality into abstract class

Improves the memory store implementation by:
- Creating a new BaseMemoryStore abstract class to handle common functionality
- Moving shared methods like find_parent_frame and extract_memory_for_generation to base class
- Simplifying InMemoryStore by inheriting from BaseMemoryStore
- Adding persistent storage via save_state() method to write frames to memory.json

This refactoring enhances maintainability and makes it easier to implement
alternative memory store backends while ensuring consistent behavior across
implementations.


---

### Commit: 39b8b28
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 1 13:23:48 2025 +0530

> fix: prevent question list depletion on reload

- Move state saving to after question gathering only
- Remove redundant state saves in lifecycle manager
- Add defensive checks for empty question lists
- Improve error handling in cleanup process
- Add defensive value checking in config builder


---

### Commit: 6edb72e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Jan 1 12:26:33 2025 +0530

> refactor: standardize command naming to plural form

- Rename GenerateEvaluationCommand to GenerateEvaluationsCommand
- Rename GeneratePerspectiveCommand to GeneratePerspectivesCommand
- Update all related imports and usages across files to maintain consistency


---

### Commit: ea99bdd
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 31 20:46:26 2024 +0530

> refactor: implement command pattern for evaluation and perspective generation

Decouples the answer processing flow by introducing dedicated commands and events
for evaluation and perspective generation. This change improves the system's
modularity and maintainability through:

- Add `GenerateEvaluationCommand` and `GeneratePerspectiveCommand` to orchestrate
  generation flows
- Create dedicated event handlers for `EvaluationsGeneratedEvent` and
  `PerspectivesGeneratedEvent`
- Simplify `AnswerProcessor` by removing direct dependencies on managers
- Update `Broker` to handle commands alongside events
- Add command subscriber setup in interview lifecycle initialization

This architectural change makes the system more maintainable by:
- Clearly separating concerns between components
- Making the flow of operations more explicit and traceable
- Reducing tight coupling between components
- Enabling easier testing and modification of individual pieces


---

### Commit: 5ee8976
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 31 19:34:58 2024 +0530

> refactor: reorganize event handlers into dedicated modules

This refactor improves code organization and maintainability by:

- Moving event handlers from monolithic event_handlers.py into dedicated modules
- Creating a new event_handlers package with clear separation of concerns:
  - ask_question_event_handler.py
  - message_received_event_handler.py
  - websocket_message_event_handler.py
- Extracting AnswerProcessor into its own module
- Relocating InterviewLifecycleManager to lifecycle_manager.py

The changes follow single responsibility principle and make the codebase more
modular while preserving existing functionality. Each handler now lives in its
own focused module with clear boundaries and responsibilities.


---

### Commit: 371749f
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 31 19:22:57 2024 +0530

> refactor: extract interview lifecycle management into dedicated class

BREAKING CHANGE: Moves interview initialization and lifecycle management from InterviewManager to new InterviewLifecycleManager class

Key Changes:
- Created new InterviewLifecycleManager class to handle interview initialization,
  timer management, and cleanup responsibilities
- Moved max_time_allowed from InterviewManager constructor to InterviewContext
- Simplified InterviewManager by delegating lifecycle operations to dedicated manager
- Updated factory and manager classes to reflect new architecture

This refactor improves separation of concerns by:
- Isolating lifecycle management logic into a focused class
- Reducing complexity in InterviewManager
- Making interview timing configuration more consistent via InterviewContext
- Improving testability of lifecycle-related functionality

The changes maintain backwards compatibility while providing a more maintainable
and extensible architecture for interview management.


---

### Commit: fc12032
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 31 19:11:56 2024 +0530

> refactor: extract AnswerProcessor and move question handling logic

- Create new AnswerProcessor class to handle answer processing and evaluation
- Move answer processing logic from InterviewManager to dedicated handler
- Move ask_next_question and related methods to QuestionManager
- Remove redundant answer processing methods from InterviewManager
- Simplify InterviewManager by reducing its responsibilities

Part of ongoing refactoring to improve separation of concerns. This change:
- Consolidates question-related logic in QuestionManager
- Moves answer processing to a dedicated handler
- Reduces InterviewManager complexity
- Maintains consistent handler pattern established in previous commits


---

### Commit: dfcbe53
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 31 18:44:45 2024 +0530

> refactor: extract AskQuestionEventHandler and standardize handler interfaces

- Create new AskQuestionEventHandler class
- Move question event handling logic from InterviewManager to dedicated handler
- Standardize handler method names to 'handler' across all event handlers
- Simplify handler registration in setup_subscribers
- Remove redundant handle_ask_question_event method from InterviewManager

Part of ongoing handler extraction effort. This change establishes a consistent pattern for event handlers with a standard interface, making the codebase more maintainable and predictable. Each handler now follows the same structure with a common method name.


---

### Commit: f28f640
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 31 17:51:09 2024 +0530

> refactor: improved code organization, and inlining class initialization



---

### Commit: 9b35f50
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 31 17:48:31 2024 +0530

> refactor: extract WebsocketEventHandler and improve error handling

- Create dedicated WebsocketEventHandler class for websocket frame handling
- Add ErrorEvent for centralized error handling
- Move channel from InterviewManager to InterviewContext
- Add error event handling in InterviewManager
- Improve error propagation with structured logging
- Clean up error handling flow with proper event publishing

Part of ongoing refactor to improve error handling and continue extracting handlers into dedicated classes. This change creates a more robust error handling pattern while maintaining clean separation of concerns.


---

### Commit: a8bab3f
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 31 13:53:57 2024 +0530

> refactor: remove StartEvent and its handler

- Remove StartEvent class from events.py
- Remove handle_start_event method from InterviewManager
- Remove StartEvent subscription from setup_subscribers
- Simplify event handling flow by removing unnecessary start event

Part of ongoing refactor to streamline event handling and remove redundant initialization patterns. The initialize() method is now called directly rather than through an event handler.


---

### Commit: 747f7b8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 31 13:51:01 2024 +0530

> refactor: extract MessageEventHandler to dedicated class

- Move message handling logic from InterviewManager to new MessageEventHandler class
- Simplify InterviewManager by removing message handling responsibility
- First step in breaking down handlers into dedicated classes for better separation of concerns
- Update subscriber setup to use new handler class

Part of ongoing refactor to extract event handlers into dedicated classes for improved maintainability and single responsibility principle.


---

### Commit: 1481a03
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Dec 30 00:17:49 2024 +0530

> refactor: consolidate AgentContext into InterviewContext

BREAKING CHANGE: AgentContext has been replaced with InterviewContext across the codebase

This commit introduces a significant architectural change by replacing AgentContext
with a more focused InterviewContext dataclass. The change improves type safety and
clarifies the relationship between components in the interview system.

Key Changes:
- Replaced AgentContext with InterviewContext across all managers and evaluators
- Made InterviewContext immutable by marking it as frozen=True
- Reordered InterviewContext fields to prioritize interview_id before agent_id
- Updated all dependent classes to use the new context structure
- Simplified broker access in NotificationManager by passing broker directly
- Removed redundant type hints and imports
- Fixed type annotations in evaluator and perspective bases

Affected Components:
- Evaluation system (manager, registry, evaluator base)
- Interview system (manager, notifications, question manager, time manager)
- Perspective system (manager, registry, perspective base)
- Factory and type definitions

The change reduces coupling between components and makes the flow of dependencies
more explicit. The frozen InterviewContext ensures thread safety and immutability
of core interview parameters.


---

### Commit: 6f8a6ae
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 29 22:40:39 2024 +0530

> refactor: remove deprecated memory types module

Removes the unused types.py module from event_agents/memory directory while
retaining core memory protocols. This simplifies the memory management
architecture by eliminating redundant type definitions.


---

### Commit: 6bd2f48
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 29 22:35:26 2024 +0530

> refactor: rename session_id to interview_id across codebase

Standardize terminology by renaming session_id to interview_id throughout the application for better clarity and consistency. This change affects:

- Event classes and their properties
- AgentContext data class
- InterviewManager and TimeManager classes
- Connection and websocket handling
- Logging contexts and error messages

No functional changes, purely a terminology standardization.


---

### Commit: 691194a
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 29 22:23:15 2024 +0530

> refactor: extract interview factory logic into separate module

- Move interview creation logic from manager.py to new factory.py
- Clean up imports and remove unused code in connection_manager.py
- Fix memory store typing to use protocol instead of concrete class
- Add Broker and Thinker to orchestrator __init__ exports
- Remove commented out code and debug print statements


---

### Commit: 3ca586c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 29 12:36:45 2024 +0530

> refactor: migrate from Agent to InterviewManager architecture

This commit represents a major architectural shift from the Agent-based system to a more focused InterviewManager-driven approach. The change simplifies the system by removing the generic Agent abstraction layer and directly handling interview-specific logic.

Key Changes:
- Removed Agent class entirely, moving core functionality to InterviewManager
- Simplified connection management to work directly with InterviewManager
- Introduced InterviewConfig and InterviewCollection for configuration management
- Added file-based interview configuration loading
- Streamlined websocket handling through Channel class
- Consolidated event handling within InterviewManager

Technical Improvements:
- Reduced event propagation complexity
- Simplified state management
- More direct handling of websocket connections
- Clearer separation of interview-specific concerns

Cleanup Needed:
1. Redundant Events:
- StartEvent is now mostly unused and can be removed
- MessageReceivedEvent could be simplified or merged with websocket handling

2. Legacy Code to Remove:
- Commented out code in ConnectionManager related to old Agent architecture
- Unused imports throughout the codebase
- Old Agent-related type hints and comments

3. Consolidation Opportunities:
- Memory store initialization could be moved to InterviewManager
- Channel and Broker relationship could be simplified
- Config loading logic could be centralized

4. Type Improvements:
- Session ID vs Interview ID terminology needs standardization
- More consistent use of UUID types across the system

Next Steps:
- Clean up unused event types
- Standardize configuration loading
- Remove commented-out code
- Consolidate websocket handling logic
- Improve error handling consistency
- Add proper type hints for all components

Testing Impact:
- Existing tests will need significant updates
- New integration tests needed for InterviewManager
- WebSocket handling tests should be simplified


---

### Commit: 989bc9c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 29 10:16:43 2024 +0530

> fix: correct websocket disconnect handling

- Add async/await to manager.disconnect call
- Fix disconnect method to use client_id instead of websocket object
- Add return type annotation for websocket_endpoint


---

### Commit: a56f8ba
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Dec 28 15:55:07 2024 +0530

> fix: removed unused import LongTermMemory



---

### Commit: 823f8a1
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Dec 28 15:10:42 2024 +0530

> refactor: remove unused interview summary generation code

Removes unused methods _generate_summary() and summary_instruction() from
InterviewManager class. These methods were likely part of an unused feature
for generating interview summaries.


---

### Commit: f51bab4
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Dec 28 13:05:12 2024 +0530

> refactor: add null checks and type ignore annotations in InterviewManager to satisfy mypy

- Add null checks for current_question in _generate_evaluations and _generate_perspectives
- Add type ignore annotations for WebsocketFrame transformations to handle type checking issues


---

### Commit: f12e9ed
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Dec 28 12:36:01 2024 +0530

> refactor: added types for the broker class to satisfy mypy



---

### Commit: d4e4b80
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 27 12:32:50 2024 +0530

> test(memory): Add comprehensive test coverage for state persistence system

Add thorough test coverage for the recently implemented state persistence and JSON
serialization system, with a focus on type safety and edge cases.

Key Additions:
- Create TestAgentConfigJSONDecoder test suite:
  - Validate proper decoding of QuestionAndAnswer models
  - Test simple and structured evaluator deserialization
  - Verify field type conversions and schema mapping
  - Add schema validation tests for evaluator types

- Implement ConfigBuilder test suite:
  - Test state loading from existing and non-existent files
  - Verify state saving functionality
  - Add schema verification helpers
  - Test error handling for invalid states

- Enhance mock objects for testing:
  - Add strict type annotations
  - Implement input validation
  - Add error case handling
  - Create comprehensive validation tests

- Improve test providers:
  - Add compatibility tests between mock and real implementations
  - Verify consistent behavior across provider types
  - Test WebsocketFrame handling

Technical Notes:
- Some advanced test cases are commented out pending additional implementation
- Added sample test data and fixtures for evaluator testing
- UUID handling tests are included for state persistence
- Mock objects now enforce stricter type checking

Future Work:
- Implement parametrized field type mapping tests
- Add coverage for full state persistence cycle
- Expand integration test coverage


---

### Commit: 219f99b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 27 12:29:33 2024 +0530

> feat(memory): Implement persistent state management and JSON serialization

This commit introduces a robust state persistence system for the AI interviewer agent,
focusing on maintaining interview state across sessions and improving data handling
architecture.

Key Changes:
- Implement `ConfigBuilder` class for centralized state management
- Add specialized JSON encoders/decoders for handling complex types
- Refactor Question and Evaluator management to support persistence
- Remove unused Coordinator component
- Enhance error handling and logging

Technical Details:
- Add custom JSON encoder/decoder classes to handle:
  - Pydantic models
  - UUID serialization
  - Evaluator instances (both Simple and Structured)
  - Complex nested data structures
- Implement state loading/saving mechanisms in:
  - QuestionManager
  - EvaluatorRegistry
  - PerspectiveRegistry
- Add type checking improvements and typing fixes throughout
- Update test suite to reflect new persistence capabilities

Breaking Changes:
- Modify Agent.create() to optionally accept agent_id parameter
- Update evaluator schema handling in EvaluatorBase
- Remove deprecated Coordinator class and associated tests

This implementation provides the foundation for persistent state management while
maintaining type safety and proper serialization of complex objects. The system now
supports resuming interrupted interviews and maintaining evaluation state across
sessions.

Note: PerspectiveRegistry state persistence is currently a placeholder and needs
further implementation for full functionality.


---

### Commit: a843eb8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 19 13:36:31 2024 +0530

> refactor: centralize agent context in perspective and evaluator systems

- Refactor perspective and evaluator systems to use centralized AgentContext
- Remove redundant memory_store and thinker instance variables
- Update registry initialization to pass agent_context
- Simplify method signatures by passing agent_context instead of individual components
- Fix type annotations and minor linting issues


---

### Commit: 7a2f81d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 19 12:59:20 2024 +0530

> refactor: convert NotificationManager to static utility class

- Convert NotificationManager from instance-based to static utility class
- Update TimeManager to use AgentContext instead of NotificationManager instance
- Remove NotificationManager instance from InterviewManager
- Update all notification calls to use static send_notification method


---

### Commit: e8cb751
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 19 12:52:34 2024 +0530

> refactor: consolidate agent dependencies using AgentContext

- Replace individual dependency injection (thinker, memory_store) with AgentContext
- Update managers (Question, Evaluation, Perspective) to use AgentContext
- Simplify constructor parameters across manager classes


---

### Commit: 084854c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 19 12:44:53 2024 +0530

> refactor: moved the AgentContext type to a type file since its being used many places



---

### Commit: 62e6229
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 19 12:37:59 2024 +0530

> refactor: introduce AgentContext to simplify dependency management

- Add new AgentContext dataclass to encapsulate agent dependencies
  - Consolidates: agent_id, session_id, broker, thinker, memory_store
- Refactor InterviewManager to use AgentContext
  - Replace individual parameter passing with single agent_context parameter
  - Simplify constructor interface by reducing parameter count
- Fix schema field naming in EvaluationSchema
  - Rename 'schema' to 'schema_' to avoid built-in property conflict

This change improves code maintainability by reducing parameter passing and
consolidating related dependencies into a single context object.


---

### Commit: d1d3ab0
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 19 12:17:07 2024 +0530

> refactor: simplify Agent initialization and dependency management

This commit introduces several improvements to the Agent class and its dependencies:

- Convert Agent class to use @dataclass for cleaner initialization
- Add factory method `Agent.create()` for instantiating new agents
- Move dependent manager initialization from Agent to InterviewManager
- Reduce coupling between Agent and evaluation/perspective systems
- Simplify InterviewManager constructor by moving manager initialization to __post_init__

These changes improve separation of concerns by having InterviewManager handle its own dependencies rather than receiving them from Agent. The @dataclass annotation reduces boilerplate while making the required attributes more explicit.

The refactor maintains existing functionality while making the code more maintainable and testable by:

1. Reducing complexity in Agent initialization
2. Making dependencies more explicit and self-contained
3. Simplifying constructor interfaces
4. Localizing related initialization code


---

### Commit: b4c398b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Dec 18 11:13:03 2024 +0530

> feat: implement agent state persistence and cleanup

Note:
- This is a simplisting state saving mechanism, i will likely change
this in teh next commit.
- The main change is that I am handling agent cleanup, so multiple
  connections are being avoided.

- Add config-based state persistence for agents
- Improve connection lifecycle management
- Enhance error handling and logging

Details:
- Store agent state in JSON config files
- Add proper cleanup on connection termination
- Implement structured logging with context
- Add memory types for long-term storage
- Improve error handling with stack traces

Breaking: No


---

### Commit: c58e31c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 17 10:25:43 2024 +0530

> chore: updated type definition for running evaluation, and added pyproject.toml



---

### Commit: 8ee6b87
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 15 23:20:41 2024 +0530

> refactor: improve type safety and code organization

Bug fixes:
- Fix EvaluationManager imports to use concrete class instead of type hints only
- Add proper type hints to Protocol classes and add runtime checking

Code quality improvements:
- Remove unused imports across all files
- Sort imports according to PEP8 standards
- Add missing return type annotations
- Fix f-string usage and string formatting
- Clean up logging statements and improve debug formatting
- Add proper type hints to generic classes and decorators

Performance:
- Remove redundant type checking and assertions
- Optimize memory usage with proper typing

This is primarily a maintenance commit focused on type safety, code organization and fixing a subtle but impactful import bug in the evaluation manager.


---

### Commit: cc8de56
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 15 18:36:08 2024 +0530

> refactor(interview): simplify event handling and notifications

Major changes:
- Replace InterviewEventHandler with a dedicated NotificationManager for cleaner event handling
- Remove redundant event types (QuestionsGathering, InterviewEnd) in favor of direct notifications
- Consolidate interview state management into InterviewManager
- Add type hints throughout the codebase for better maintainability

Minor improvements:
- Add proper typing to Broker event handling
- Sort and organize imports
- Clean up logging statements
- Improve docstrings and error handling
- Fix type annotations in dispatcher.py


---

### Commit: cd93cb2
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 13 15:18:59 2024 +0530

> feat(interview): Add QuestionManager and scaffold Coordinator

- Introduce QuestionManager for handling interview questions lifecycle
- Add initial Coordinator class (not yet integrated) for future interview orchestration
- Implement comprehensive test coverage for QuestionManager functionality
- Add structured question extraction and management capabilities
- Set up test infrastructure for both components


---

### Commit: 97445d3
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 13 10:35:43 2024 +0530

> chore: added ruff formatter + linter, and autofixed unused imports, import order, and some other autofixable errors



---

### Commit: 89201c8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Dec 11 10:31:24 2024 +0530

> chore: asyncio gathered evaluations and perspective generation in interview manager to reduce latency



---

### Commit: 6823d11
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Dec 11 10:16:12 2024 +0530

> feat: Add max_tokens parameter to Thinker.generate()

- Add optional max_tokens parameter to Thinker.generate() method
- Implement kwargs handling to conditionally include max_tokens in API call
- Set max_tokens=200 in PerspectiveBase._generate_analysis()


---

### Commit: 499c6fa
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Dec 11 10:07:55 2024 +0530

> refactor: improve interview manager and perspective handling

- Refactor InterviewManager by breaking down handle_add_to_memory_event into smaller, focused methods
- Add config/*.txt to gitignore for perspective configuration files
- Update perspective evaluation with simpler description option
- Clean up code formatting in thinker.py

The main changes improve code organization and maintainability by:
- Breaking large methods into smaller, single-responsibility functions
- Adding better type hints and documentation
- Introducing a simpler perspective description option for evaluations
- Improving error handling and logging


---

### Commit: 096743d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Dec 11 09:30:06 2024 +0530

> feat: Implement perspective-based evaluation UI and refactor backend evaluation logic

Backend Changes:
- Refactored PerspectiveBase class to use "perspective" address type instead of "evaluation"
- Removed description generation and storage functionality temporarily to simplify perspective evaluation
- Streamlined evaluation instruction formatting to focus on core perspective analysis
- Maintained core evaluation pipeline while removing dependency on perspective descriptions

Frontend Changes:
- Added new PerspectiveArea component for dedicated perspective feedback display
- Created PerspectiveFrame component for rendering perspective evaluations with Markdown support
- Updated frame selectors and renderers to handle new "perspective" address type
- Modified interview page layout to replace SuggestionArea with PerspectiveArea
- Enhanced WebSocket types to include "perspective" in AddressType enum

This change introduces a more focused perspective-based evaluation system with
dedicated UI components while simplifying the backend evaluation logic. The new
implementation provides clearer separation between different types of feedback
and improves the overall user experience through specialized rendering of
perspective-based insights.


---

### Commit: b42754b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 8 21:59:32 2024 +0530

> refactor: reorganize event agents and add perspective tests

This commit introduces a significant reorganization of the event agents
structure and adds comprehensive test coverage for the perspective system.

Key Changes:
- Move memory-related modules from app.agents to app.event_agents
- Add extensive test suite for PerspectiveBase class
- Create new test fixtures and helpers for perspective testing

Test Coverage:
- Unit tests for atomic PerspectiveBase functions
- Integration tests for perspective initialization and evaluation
- Mock implementations for WebsocketFrames and memory store
- Comprehensive test fixtures in conftest.py

The changes improve the overall architecture by:
1. Better organizing the event agent system
2. Ensuring robust test coverage for perspective evaluation
3. Providing reusable test utilities for future perspective implementations

Path updates:
- app.agents.memory -> app.event_agents.memory
- Added tests/event_agents/perspectives/*


---

### Commit: 3c6b8ad
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 8 21:57:27 2024 +0530

> feat: Add multi-perspective evaluation system for interview responses

This commit introduces a new perspective-based evaluation system that analyzes candidate responses from different professional viewpoints. The system runs concurrent evaluations from multiple role-specific perspectives (Product, Sales, Engineering, and Design managers).

Key Changes:
- Create new PerspectiveBase class for standardized perspective evaluation
- Implement PerspectiveManager to orchestrate concurrent perspective analysis
- Add PerspectiveRegistry for managing and initializing perspective instances
- Update memory store to handle perspective-specific context extraction
- Extend WebSocket frame types to support perspective evaluations
- Integrate perspective system with interview manager workflow

Technical Improvements:
- Make memory store config path optional with safe fallback
- Enhance logging with additional context and structured JSON formatting
- Implement concurrent initialization of perspectives using asyncio.gather
- Add correlation ID tracking for linking related evaluations
- Update memory extraction to support filtered address types

The perspective system provides deeper insights into candidate responses by analyzing them through different professional lenses, enabling a more comprehensive evaluation of interview responses.


---

### Commit: 19890d6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Dec 7 20:49:27 2024 +0530

> refactor(interview): Enhance interview manager with perspective handling

- Refactor initialize() method into smaller, focused methods for better maintainability
- Split question gathering, timer initialization, and evaluation system setup into separate methods
- Improve code organization and readability through method extraction
- Add proper initialization of perspective registry alongside evaluator registry


---

### Commit: 149445e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 6 12:27:38 2024 +0530

> refactor: optimize evaluation concurrency using asyncio.gather()

- Refactor handle_evaluation to run evaluations concurrently
- Add helper method run_evaluation for individual evaluation tasks
- Improve error handling to maintain parallel execution
- Replace sequential evaluation loop with asyncio.gather()


---

### Commit: 9918864
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 6 11:49:38 2024 +0530

> feat: Implement dynamic evaluator registry with rating rubric support

This commit introduces a new evaluator registry system that dynamically loads and manages evaluators, including a new rating rubric evaluator. Main reason for an evaluation registry is to support the async addition of new evaluators, like the rating rubric one that gets generated based on the agent config generated artifacts.

Key changes include:

Core Changes:
- Add new RatingRubricEvaluationBuilder class for dynamic rubric creation
- Implement EvaluatorRegistry to manage evaluator lifecycle
- Modify EvaluationManager to use registry instead of static evaluator list
- Initialize evaluator registry during interview startup

Technical Details:
- RatingRubricEvaluationBuilder extracts structured rubrics from YAML config
- Dynamic Pydantic model creation for evaluation schemas
- Async initialization of evaluators with proper error handling
- JSON-based logging formatter for improved debugging

Configuration Updates:
- Update .gitignore to exclude development artifacts
- Enable interview debugging in constants.py
- Remove commented-out communication evaluator code

The new registry system provides better scalability and maintainability for adding new evaluators, while the rating rubric support enables more structured candidate assessments.


---

### Commit: 020abc1
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 6 10:38:10 2024 +0530

> refactor: move Agent class to dedicated file

Organizational change only - moved the Agent class from broker.py to its own
dedicated file (agent.py) to improve code organization and separation of
concerns. No functional changes were made to the implementation.

- Created new agent.py file
- Updated imports in connection_manager.py to reference new location
- Removed Agent class from broker.py


---

### Commit: 65936a9
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 6 10:25:54 2024 +0530

> feat: changed the order of UI view of the interview



---

### Commit: dd46e2d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 6 10:14:53 2024 +0530

> refactor: reorganize interview components into dedicated module

BREAKING CHANGE: Moved interview-related code from orchestrator into a new dedicated module

- Split interview_manager.py into separate components:
  - event_handler.py: Handles interview-related events
  - manager.py: Core interview orchestration logic
  - question_manager.py: Question gathering and management
  - time_manager.py: Interview timing and timeout handling
- Updated broker.py imports to reference new module structure
- Improved time display formatting to show minutes for longer interviews
- Fixed config file path to use artifacts_v2.yaml
- Removed unused communication_evaluator import

This refactor improves code organization by grouping related interview functionality together and makes the codebase more maintainable.


---

### Commit: 02d7d11
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 6 09:42:41 2024 +0530

> chore: update diff shell script to not error when finding a deleted file



---

### Commit: 5c3b8b3
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 6 09:41:20 2024 +0530

> feat: Implement artifact persistence and management

- Add artifact dictionary to store and manage generated artifacts
- Implement YAML file persistence for artifacts in config/artifacts_v2.yaml
- Add methods to clean, save, and track artifacts
- Fix memory store parent frame lookup method name
- Remove debug print statements from memory store


---

### Commit: ae2adc8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Dec 6 08:58:30 2024 +0530

> bug: fixed passing of wrong config and wrong custom instruction passing in artifact generating agent agent_v2



---

### Commit: 9108f8e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 5 13:58:44 2024 +0530

> feat: Refactor evaluation components and improve display [STABLE]

- Enhanced EvaluationFrame with better width handling and consistent margins
- Updated RecursiveEvaluationFrame to use cleaner type definitions and improved rendering
- Added text-sm class to EvaluationArea for better readability
- Simplified component exports and imports
- Removed redundant tailwind configuration

Note: This version fixes display issues and removes problematic tailwind config that caused instability in the previous commit. The evaluation components now render correctly.


---

### Commit: eb71b77
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 5 13:40:36 2024 +0530

> bug: updated agents_v2 to correctly read the config



---

### Commit: bddf1c0
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 5 13:39:01 2024 +0530

> feat: Add SuggestionFrame and SuggestionArea components

- Introduced `SuggestionFrame` component to display sample answers and options with copy-to-clipboard functionality.
- Added `SuggestionArea` component to render suggestions using `frameRenderers`.
- Updated `ConversationFrame` to parse and display questions from structured content.
- Refactored `tryParseJSON` into a shared helper function.
- Enhanced `frameRenderers` and `frameSelectors` to support suggestion frames.
- Updated `ScalableWebsocketTypes` to export enums and schemas for better type safety.
- Added Tailwind CSS animation for fade-out effect.


---

### Commit: e84762f
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 5 11:07:13 2024 +0530

> feat: Add recursive JSON rendering for evaluation frames

- Implement JSON parsing and structured display of websocket frame content
- Add new RecursiveEvaluationFrame component for nested data visualization
- Support rendering of arrays, objects, and primitive values
- Improve readability with proper indentation and formatting
- Add fallback for non-JSON content


---

### Commit: 0aa50fb
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Dec 5 10:12:00 2024 +0530

> feat: implement evaluation display system

This commit introduces a complete evaluation display system, connecting
backend evaluation generation to frontend rendering.

Core Changes:
- Add "evaluation" address type across the stack:
  - Backend: Add to AddressType enum in websocket_types.py
  - Frontend: Update ScalableWebsocketTypes.ts to match
  - Update evaluator_base.py to use new address type

Frontend Implementation:
- Add dedicated EvaluationArea component with:
  - Sticky header and scrollable content area
  - Custom styling and layout
  - Proper frame filtering and rendering
- Create frame handling architecture:
  - Split rendering into ConversationFrame and EvaluationFrame
  - Add frameSelectors service for filtering by address type
  - Implement generic frame renderer factory pattern

UI/UX:
- Visual separation between conversation and evaluation areas
- Responsive layout with proper scrolling behavior
- Clear evaluation header for better navigation

Code Quality:
- Improve TypeScript types with centralized enums
- Remove deprecated components and unused code
- Add proper type annotations throughout
- Clean up imports and file organization

This change creates a complete system for displaying evaluations,
from backend generation through frontend rendering, while maintaining
code quality and type safety.


---

### Commit: 0c8ce77
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Dec 4 18:49:28 2024 +0530

> feat: add evaluation area for thought frames

- Add new EvaluationArea component to display thought-addressed frames
- Rename frames to websocketFrames for clarity
- Update frame state management to support evaluation display


---

### Commit: 96443cc
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Dec 4 18:06:08 2024 +0530

> refactor: organized all literal types separately



---

### Commit: a765642
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Dec 4 11:42:08 2024 +0530

> refactor(websocket): Improve WebSocket connection architecture and logging

- Extract WebSocket handlers into separate classes for better separation of concerns
  - HeartbeatHandler for managing ping/pong heartbeats
  - ReconnectHandler for connection retry logic
  - EventHandler for WebSocket event management
- Add comprehensive debug logging throughout WebSocket lifecycle
- Implement proper cleanup and resource management
- Improve error handling and type safety
- Standardize message formatting and validation

This refactor improves maintainability, testability, and observability of the
WebSocket implementation while maintaining existing functionality.


---

### Commit: a06aa1e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 3 13:31:50 2024 +0530

> refactor: improve WebSocket cleanup and disconnection handling

Note: Mainly got rid of the duplicate frames being added. It was a
problem with eventlisteners accumulating on reconnect. Handled that a
lot better here, in the right order too.

- Add comprehensive event listener cleanup by explicitly removing all event types
- Reorder disconnect operations to ensure proper cleanup sequence


---

### Commit: a89bcc2
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Dec 3 12:53:11 2024 +0530

> refactor: relocate WebsocketConnection and update imports

- Move WebsocketConnection from /infrastructure to /interview/infrastructure/websocket
- Update import paths in useWebsocketCore hook
- Adjust UserArea container styling with responsive width and margin


---

### Commit: ae317eb
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Dec 2 20:32:15 2024 +0530

> feat: Enhance UserInputArea with send button and styling improvements

- The height autoadjust upto a maximum of 70% of the container height
- Add send button with icon to UserInputArea
- Extract handleSubmit logic into separate function
- Add placeholder text to TextareaResizable
- Improve input area styling with background, border and spacing
- Reorganize component layout for better UX


---

### Commit: 9fef9af
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Dec 2 20:09:12 2024 +0530

> refactor: reorganize websocket handling and split UI components

- Extract AudioRecorder and MessageContainer into separate components
- Implement dedicated websocket message formatters and sender
- Improve type safety and error handling for websocket communications


---

### Commit: 16a32e8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Dec 2 17:19:05 2024 +0530

> feat(websocket): enhance message handling and UI structure

- Introduce cn utility in MessageFrame for dynamic styling based on user roles, improving visual distinction between user and assistant messages.
- Refactor UserArea component:
  - Split into UserInputArea and MessageContainer for better separation of concerns.
  - Implement dynamic textarea height adjustment in UserInputArea to enhance user experience.
- Add sendMessage function to useWebsocketCore:
  - Utilize useCallback for efficient message dispatching.
  - Ensure robust error handling when WebSocket connection is not initialized.
- Create createHumanInputFrame helper function:
  - Generate WebSocket frames with unique IDs and timestamps, standardizing message format.
- Enhance WebsocketMessageSender:
  - Implement detailed logging for message formatting and sending processes.
  - Improve error handling to ensure reliable message delivery.
- Update WebSocketConnection:
  - Manage message sending and connection status with improved heartbeat and reconnection logic.
  - Introduce sendHumanInput method for streamlined human input message creation and dispatch.

Note: While the core messaging functionality is operational, the UI layout is currently disorganized. The next step involves cleaning up the UI and refactoring the architecture by splitting the UserArea into separate components for improved maintainability and readability.


---

### Commit: 1a3c4f5
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Dec 2 14:26:39 2024 +0530

> feat: Implement voice transcription UI with resizable text input

Note: The resizable text area element is buggy and needs work. Here is
enough to test that the transcription pipeline works.

This commit introduces a new user interface for voice transcription and text input:

- Add AudioRecorder component with recording status indicator and error handling
- Create TextareaResizable component supporting dynamic height adjustment
- Implement MessageContainer for displaying conversation history
- Update UserArea layout with responsive design and centered content
- Refactor audio transcription service to better handle state and cleanup
- Improve error handling and logging throughout audio processing pipeline

The new UI provides a more polished experience with visual feedback during
recording and seamless integration between voice and text input methods.


---

### Commit: 404b4aa
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Dec 2 12:19:02 2024 +0530

> feat: auto-stop recording when transcribing

Allow transcription to work even when recording is still in progress by
automatically stopping the recording first. This improves the user experience
by eliminating the need to manually stop recording before transcription.

- Add check for active recording state in transcribeAudio
- Stop recording and update state if recording is active
- Use latest blob for transcription


---

### Commit: c52035e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Dec 2 12:03:08 2024 +0530

> refactor: split AudioService into modular components

BREAKING CHANGE: AudioService interface now requires audioBlob parameter for transcribeAudio()

This commit breaks down the monolithic AudioService into smaller, more focused classes:
- StreamManager: Handles MediaStream acquisition and cleanup
- AudioRecorder: Manages MediaRecorder and audio chunk collection
- AudioTranscriber: Handles audio transcription requests
- AudioService: Orchestrates the above components

Key changes:
- Improved error handling and logging throughout
- Removed unused audio analysis functionality
- Added explicit audioBlob state management in useVoiceTranscription
- Moved audio-related code to dedicated /audio directory
- Simplified cleanup procedures to better handle resource release
- Added validation checks for audio blobs before transcription

This refactor improves code maintainability, testability, and separation of concerns while fixing potential memory leaks from unreleased resources.


---

### Commit: 6b77f4e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 1 20:39:45 2024 +0530

> feat: Implement voice recording and transcription functionality

Add comprehensive audio recording system with real-time analysis and playback capabilities:

- Create AudioService class to handle audio stream management and recording
- Add useVoiceTranscription hook for React components to easily integrate audio features
- Implement audio level monitoring and silence detection
- Add playback functionality with audio controls
- Include proper cleanup and resource management
- Add error handling and debug logging throughout
- Update UserArea component with recording controls and audio playback

Technical details:
- Uses WebAudio API for audio analysis
- Implements MediaRecorder API for audio capture
- Handles audio chunks with configurable timeslice
- Supports audio/webm format
- Includes proper stream and resource cleanup

Breaking changes: None


---

### Commit: dd1b9f8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Dec 1 13:41:03 2024 +0530

> feat: Add AudioService and voice types for audio recording functionality

Implements a robust AudioService class to handle audio recording and transcription,
along with corresponding voice parameter types. The service provides:

- Audio stream initialization and management
- Recording controls (start/stop)
- Audio transcription capabilities
- Proper resource cleanup and error handling

The VoiceHookParams type supports configurable chunk sizes, recording time limits,
and transcription callbacks for flexible integration.


---

### Commit: 4cbc6c4
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Nov 29 10:48:31 2024 +0530

> feat(interview): Relocate WebSocket contexts to interview page scope

Reorganizes WebSocket and input management specifically for the interview page:
- Move WebSocket and input contexts into /interview directory for page-specific state
- Create MessageFrame component for interview message display with Markdown
- Add interview-specific UserArea component to display message frames
- Implement InputContext scoped to interview page for managing user responses
- Set up dedicated WebsocketContext provider for interview WebSocket state
- Extract WebSocketCoreOptions type for interview connection configuration

This restructuring makes the interview page fully self-contained by moving all its state management and components into the page directory. This pattern allows for better isolation of interview-specific logic and easier reuse of WebSocket patterns in other features.


---

### Commit: 372d07d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Nov 29 09:49:24 2024 +0530

> bug: temporary fix for double frames by skipping duplicates in frame reducer



---

### Commit: d6a6dc5
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 28 23:32:24 2024 +0530

> feat(websocket): Implement core websocket infrastructure with validation

This commit introduces a robust websocket infrastructure with type-safe message handling
and validation. The implementation includes:

- Core websocket connection class with heartbeat, reconnection, and event handling
- Generic websocket hook (useWebsocketCore) that handles state management and message validation
- Specialized hook (useWebSocket) for frame-specific websocket handling
- Message validation layer using Zod schemas
- Basic interview page UI to demonstrate websocket functionality

Key components:
- WebsocketConnection: Base class handling low-level websocket operations
- useWebsocketCore: Generic hook for websocket state management
- ZodMessageValidator: Type-safe message validation
- frameReducer: State management for received frames

Known Issues:
- Messages are currently being displayed twice in the UI despite backend sending
  single messages. This appears to be a frontend issue, possibly related to
  duplicate event handling or state updates. Need to investigate event binding
  and state management flow.

Next Steps:
- Debug duplicate message display issue
- Add error boundaries and loading states
- Implement proper cleanup of websocket connections
- Add retry mechanisms for failed connections
- Enhance UI for better message display

Technical Debt:
- Consider implementing a message queue for failed sends
- Add proper typescript generics for better type inference
- Consider adding middleware support for message processing


---

### Commit: e1c3efb
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 25 22:37:59 2024 +0530

> feat: Add correlation_id support for message tracking

This commit adds correlation_id tracking across the application to better trace
message flows and improve debugging capabilities.

Note: Not all the places have the correlation_id set explicitly. The
Dispatcher generates a uuid4 if you dont supply one. This is to support
backward compatibility.

Key changes:
- Add correlation_id parameter to Dispatcher.package_and_transform_to_webframe()
- Update WebsocketFrame to include correlation_id field
- Propagate correlation_id from user input through evaluation pipeline
- Add correlation_id to EvaluationLogContext for better tracing

The correlation_id allows tracking related messages through the system, from user
input through evaluations and responses. This enables better debugging and
monitoring of message flows.

Also adds commit_message_concatenate.sh utility script for generating commit
messages from git history.


---

### Commit: 626caec
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 25 18:28:21 2024 +0530

> chore: improved logging in interview manager, and updated gitignore



---

### Commit: cb06fe8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 25 18:17:51 2024 +0530

> feat: Add correlationId to WebSocket frame types

- Add correlationId field to both frontend and backend WebSocket frame types
- Use UUID4 as default generator for correlationId in backend
- Maintain type consistency between frontend (Zod) and backend (Pydantic) implementations
- websocketMessageSender sets a uuid correlation id when sending a new
  frame


---

### Commit: fa9f70b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 25 14:24:07 2024 +0530

> Merge branch 'main' into product



---

### Commit: 173fc90
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 25 14:08:25 2024 +0530

> refactor: improve logging and add structured context tracking

This commit enhances the logging system and adds structured context tracking across multiple components:

- Add JsonFormatter for structured JSON logging output
- Implement LogContext base class for standardized context tracking
- Add __repr__ methods to core classes for better debugging
- Replace string-based logging with structured context logging
- Improve logging messages with additional context and metadata
- Update logging configuration with standardized levels and handlers

Key changes:
- Add EvaluationLogContext for tracking evaluation metrics
- Enhance InterviewManager logging with detailed session state
- Update ConnectionManager to use structured logging for client events
- Add debug context tracking in EvaluatorBase
- Standardize logging format across all components

This improves observability and makes debugging easier by providing consistent, structured logging with relevant context throughout the application.


---

### Commit: d0f0188
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 25 14:08:25 2024 +0530

> refactor: improve logging and add structured context tracking

This commit enhances the logging system and adds structured context tracking across multiple components:

- Add JsonFormatter for structured JSON logging output
- Implement LogContext base class for standardized context tracking
- Add __repr__ methods to core classes for better debugging
- Replace string-based logging with structured context logging
- Improve logging messages with additional context and metadata
- Update logging configuration with standardized levels and handlers

Key changes:
- Add EvaluationLogContext for tracking evaluation metrics
- Enhance InterviewManager logging with detailed session state
- Update ConnectionManager to use structured logging for client events
- Add debug context tracking in EvaluatorBase
- Standardize logging format across all components

This improves observability and makes debugging easier by providing consistent, structured logging with relevant context throughout the application.


---

### Commit: 5b6c39b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 25 12:13:54 2024 +0530

> Merge branch 'product'



---

### Commit: a64f293
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 25 12:13:43 2024 +0530

> chore: added a README with release notes



---

### Commit: 1158af7
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Nov 24 21:02:12 2024 +0530

> Merge branch 'product'



---

### Commit: c95ce36
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Nov 24 20:59:42 2024 +0530

> feat: Implement structured evaluation system and JSON response handling

This commit introduces a major refactor of the evaluation system and improves JSON response handling in the frontend.

Core Changes:
- Refactored evaluator system to support both simple text and structured Pydantic responses
- Added type hints to dispatcher methods for better type safety
- Improved frontend JSON rendering for structured responses
- Removed embellishment evaluator in favor of more structured evaluation approaches

Backend Changes:
- Created new base classes `EvaluatorSimple` and `EvaluatorStructured` for different evaluation types
- Introduced generic type `T` to support both string and BaseModel evaluation schemas
- Added `StructuredThinkingSchema` with defined fields for framework evaluation
- Updated dispatcher return type hints for better type safety
- Modified evaluation context building to handle structured schemas

Frontend Changes:
- Renamed `frameRenderHandler` to `FrameRenderHandler` for consistency
- Added JSON pretty-printing for structured responses
- Updated WebSocket URL to use V3 endpoint
- Improved frame rendering logic to handle both markdown and JSON content

This change enables more structured and type-safe evaluations while maintaining
backwards compatibility with simple text-based evaluations. The frontend now
properly handles and displays both structured and unstructured responses.


---

### Commit: f42887f
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Nov 24 20:15:10 2024 +0530

> feat(evaluations): Implement specialized evaluators with configurable instructions

Note: Mainly achieved having multiple simple evaluators running
parallely

- Refactor EvaluatorBase to be an abstract base class with configurable evaluation instructions
- Create new Evaluator class that inherits from EvaluatorBase
- Add specialized evaluator instances for different assessment types:
  - Relevance evaluator
  - Exaggeration evaluator
  - Embellishment evaluator
  - Structured thinking evaluator
- Update broker.py to use the new specialized evaluators
- Rename retreive_context_messages to retreive_and_build_context_messages for clarity
- Add address_filter and custom_user_instruction parameters for more flexible context building

This change allows for more specialized and configurable evaluation of interview responses through different lenses while maintaining a common evaluation infrastructure.


---

### Commit: 0968c76
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Nov 24 19:40:15 2024 +0530

> feat(evaluations): Add evaluation system for interview answers

Implements a new evaluation system that provides real-time feedback on interview answers.
The system uses a modular evaluator architecture that can be extended with different
evaluation strategies.

Note: Evaluator base is rigid right now. Will add flexibility into it in
the next commit.

Key changes:
- Add EvaluatorBase class for implementing evaluation strategies
- Create EvaluationManager to coordinate multiple evaluators
- Integrate evaluation system with InterviewManager and memory store
- Update broker to handle evaluation events and results
- Add async memory store operations for thread safety
- Improve logging and error handling throughout evaluation flow

The evaluation system runs after each answer is stored in memory and before the next
question is asked, providing immediate feedback to users on their responses.

Breaking changes:
- MemoryStore.add() is now async
- Memory store operations require explicit typing


---

### Commit: 1056c1c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Nov 22 11:25:04 2024 +0530

> refactor: reorganize interview manager into separate classes

BREAKING CHANGE: Restructures the InterviewManager class into separate components
for better separation of concerns and maintainability.

- Split InterviewManager into 3 specialized classes:
  - TimeManager: Handles interview timeout tracking
  - QuestionManager: Manages question gathering and iteration
  - InterviewEventHandler: Handles all event-related logic
- Add line numbers to logging format for better debugging
- Remove redundant logging in broker websocket handler
- Set default interview time limit to 2 minutes
- Improve type hints and documentation

This refactor improves code organization, reduces class complexity, and makes
the interview management system more modular and testable.


---

### Commit: 23dc76d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Nov 22 10:27:18 2024 +0530

> feat: Improve interview flow management and reduce logging noise

- Add `current_question` tracking to InterviewManager
- Centralize question asking logic in `ask_next_question` method
- Remove redundant logging statements from Broker
- Add new AnswerReceivedEvent for better event handling
- Clean up debug parameter handling in Thinker class

The main improvement is centralizing the question management logic in the InterviewManager class, making the flow more maintainable and reducing code duplication. The changes also improve the overall system observability by cleaning up noisy logging while maintaining important debug information.


---

### Commit: 522927b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 21 18:58:31 2024 +0530

> feat: Implement interview flow control and timeout mechanism

This commit adds comprehensive interview management features:

- Add question-by-question flow control in MessageReceivedEvent handler
- Implement interview timeout mechanism with configurable max duration
- Add new events: AskQuestionEvent, InterviewEndEvent with various end reasons
- Remove UserReadyEvent in favor of direct question flow
- Add session tracking and proper event handling for interview completion
- Improve error handling and logging throughout interview process

The changes create a more robust interview system that properly manages
question flow, handles timeouts, and provides clear status updates to users.


---

### Commit: 0592fad
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 21 15:35:00 2024 +0530

> Merge branch 'product'



---

### Commit: 892fdea
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 21 15:32:31 2024 +0530

> feat: Implement interview question flow and error handling

This commit introduces a new interview question flow system and improves error handling across the orchestrator components. Key changes include:

- Add UserReadyEvent to manage the interview question flow
- Implement question-by-question delivery through ask_question method
- Add session_id to InterviewManager constructor for better session tracking
- Improve error handling in Agent class methods with try/catch blocks
- Add debug logging for better visibility into the interview process
- Refactor initialize() method to publish UserReadyEvent after questions are gathered
- Reduced the size of the questions in the artifact to help with
  debugging

The changes enable a more structured interview process where questions are delivered one at a time, with proper error handling and logging throughout the flow. This provides better control over the interview process and improved debugging capabilities.


---

### Commit: 9dd238c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 21 13:33:35 2024 +0530

> feat: Improve questions gathering flow with status updates

- Add Status enum to track question gathering states (in_progress, completed, failed, idle)
- Rename QuestionsGatheredEvent to QuestionsGatheringEvent to better reflect its purpose
- Add status updates during question gathering process with user-friendly messages
- Improve error handling in Broker by processing events sequentially instead of concurrently
- Make interview initialization non-blocking by using create_task
- Enhance logging throughout the question gathering flow

This change provides better visibility into the question gathering process and improves
the overall reliability of the interview system.


---

### Commit: 6ac5afb
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 20 19:16:58 2024 +0530

> feat: Implement InterviewManager and structured question gathering

This commit introduces a new InterviewManager class to handle the interview process
and question gathering functionality. Key changes include:

- Add new InterviewManager class to orchestrate the interview process
- Create QuestionsGatheredEvent for handling structured question responses
- Update Agent class to use InterviewManager for handling start events
- Add string handler to Dispatcher for simple text responses
- Remove direct Dispatcher dependency from broker.py
- Move interview questions template to agent_v2.yaml config

The InterviewManager now handles:
- Loading questions from config
- Structured parsing of questions using Thinker
- Publishing gathered questions through the event system
- Converting responses to WebSocket frames

This change improves the separation of concerns and provides a more structured
approach to managing the interview process.


---

### Commit: 511ddf4
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 20 17:52:43 2024 +0530

> chore: removed userAnswer as field from both frontend and backend QuestionAnswer type



---

### Commit: 11490f8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 20 10:27:17 2024 +0530

> feat: implement event-driven message storage flow

Implements a complete flow for storing frontend messages in memory:
1. Receive websocket message from client
2. Convert to MessageReceivedEvent
3. Parse message into WebsocketFrame
4. Store in memory via AddToMemoryEvent

Key changes:
- Add MessageReceivedEvent and AddToMemoryEvent
- Update Channel to publish received messages as events
- Add message parsing and validation in Agent
- Implement async memory storage with logging
- Remove message echo functionality

This creates a clear path for frontend messages to flow through the system and be stored in memory for future use.


---

### Commit: e79dd70
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 20 09:58:45 2024 +0530

> Merge branch 'product'



---

### Commit: 06bd16a
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 20 09:57:01 2024 +0530

> refactor: reorganize agent code and improve event handling

User facing change:
- The first message that comes in is AI generated and not hardcoded

BREAKING CHANGES:
- Moved Dispatcher class to its own file at app/agents/dispatcher.py
- Extracted DEBUG_CONFIG and model constants to app/constants.py
- Removed memory_topic parameter from memory store creation

Features:
- Added new event types: ThinkEvent and MemoryUpdateEvent
- Implemented Thinker class with OpenAI integration
- Added structured response extraction capability using instructor

Changes:
- Simplified memory store initialization by removing memory_topic dependency
- Enhanced broker event handling with improved logging
- Added debug configuration controls for different components
- Improved type hints and documentation
- Reorganized code structure for better separation of concerns

The main goal of this refactor is to improve code organization and make the event handling system more robust. The Dispatcher and debug configurations have been moved to their own files to reduce coupling. The new Thinker class provides a cleaner interface for AI interactions.


---

### Commit: 44a6e96
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Nov 19 13:02:45 2024 +0530

> refactor: reorganize agent system and implement event-driven websocket handling

Note:
- The startevent is emitted and the initial hardcoded message is
  available on the frontend
- Move agent-related code to new event_agents directory
- Implement new websocket connection manager and channel handler
- Add broker system for event-driven agent communication
- Create v3 API routes for websocket endpoints
- Update logging configuration for better debugging
- Reorganize memory management system under event_agents

Note:
Lots of code duplication, organization broken between v2 and v3. But
will remove later.


---

### Commit: 916b7f6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Nov 19 11:19:40 2024 +0530

> feat: Add event broker system with pub/sub pattern

Checkpoint: The prev version works to this point

Note:
- This is not integrated into the main stack. It is being developed.

Implements a new event broker system with:
- Base event infrastructure with UUID tracking and timestamps
- Pub/sub pattern for event handling
- Async event processing queue
- Basic Agent integration with broker support


---

### Commit: 7c347d0
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 18 11:26:52 2024 +0530

> refactor: Extract memory management into dedicated module

BREAKING CHANGE: Memory class has been moved to its own module

- Created new memory management module with protocols and implementations
- Extracted Memory class into InMemoryStore with better separation of concerns
- Added ConfigProvider and MessagePublisher protocols for dependency injection
- Updated Agent class to use new memory store factory
- Added tests for memory management components
- Updated dependencies and package configurations

This refactoring improves code organization, testability, and maintainability by properly separating memory management concerns into their own module with clear protocols and implementations.


---

### Commit: 6f68d9b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Nov 16 00:41:01 2024 +0530

> refactor: centralize logging configuration

- Move logging configuration from agent_v2.py to a dedicated setup_logging.py module
- Add new setup_logging function to handle all logging configuration
- Create services/__init__.py to expose setup_logging function
- Add MockInterviewQuestion import to agent_v2.py

This change improves code organization by centralizing logging configuration and
making it more maintainable across the application.


---

### Commit: 373463b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 13 14:45:52 2024 +0530

> feat: Add ListeningAgent and improve UI layout

This commit introduces a new ListeningAgent class for contextual information gathering
and makes several UI improvements to the artifact viewing experience.

Backend Changes:
- Add new ListeningAgent class to monitor conversations with specific purposes
- Implement setup_listening_agents() in Agent class with initial agents for:
  - Emotional qualities tracking
  - Physical qualities tracking
- Add Context model to interview_concept_types
- Integrate listening agents with the main Agent's memory system

Frontend Changes:
- Adjust layout proportions:
  - Change artifact view width from 1/2 to 2/3
  - Reduce user area width from 1/2 to 1/3 when artifact is visible
- Improve ArtifactFrame styling:
  - Add left padding to version buttons
  - Adjust content padding and margins
  - Remove unnecessary margin from frame container
- Fix PDF generation formatting and text extraction
- Improve dropdown menu click-outside behavior

The ListeningAgent addition provides a foundation for more sophisticated
context gathering during interviews, while the UI changes create a better
balance between conversation and artifact display areas.


---

### Commit: 37bb227
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Nov 12 13:58:44 2024 +0530

> feat: Add pub/sub functionality to Agent memory system

- Integrate pypubsub library for memory event handling
- Add unique agent_id and memory_topic to Agent class
- added setup and cleanup function for agent instantiation and
  destruction
- Implement memory update subscription and callback
- Update DEBUG_CONFIG settings for agent and memory debugging
- Add commit_details.txt to gitignore


---

### Commit: 6df9c9f
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Nov 12 11:28:08 2024 +0530

> chore: enhance interview flow and debug logging

Main intent:
Rolled back userAnswer as the suggested answer can be modified to incorporate user inputs, its simpler and fewer changes.

- Enable interview debug mode and disable agent/memory debugging
- Add debug logging for question generation context
- Update QuestionAndAnswer description for better clarity
- Enable Backup and CultureFit concepts in hiring requirements
- Remove input auto-population in HelperContent component

The changes focus on improving the interview process debugging and refining
the question generation workflow while simplifying the frontend helper content
functionality.


---

### Commit: de44013
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 11 21:25:06 2024 +0530

> Merge branch 'product'



---

### Commit: 24d9569
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 11 21:24:36 2024 +0530

> chore: Add git diff script for automated commit messages

Add shell script to generate structured diff output including:
- Git diff of staged changes
- Full contents of modified files
- Formatted section markers for parsing


---

### Commit: 57feb1a
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 11 21:16:00 2024 +0530

> feat: Add user answer tracking and filtering in interview system

- Add user_answer field to QuestionAndAnswer model
- Implement address filtering in memory extraction
- Add automatic input population from user answers in HelperContent
- Optimize frame rendering with useMemo
- Add useInput hook for better context management


---

### Commit: 3735ced
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 11 19:53:53 2024 +0530

> refactor: made Q&A type translate snake to camel bw backend to frontend, specificaly sample_answer to sampleAnswer



---

### Commit: 60e9d0d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 11 15:34:21 2024 +0530

> refactor: Extract artifact regeneration logic into separate method

- Add cognition_router to debug config
- Extract regeneration logic from receive_message into new regenerate_artefact method
- Improve error handling for artifact regeneration


---

### Commit: 59b16c0
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 11 12:26:08 2024 +0530

> fix: properly release microphone after recording stops

- Stop and release MediaStream tracks after recording completes
- Request fresh MediaStream for each new recording session
- Clear streamRef after stopping to ensure proper cleanup
- Maintains browser permission without showing repeated prompts
- Fixes battery drain and persistent microphone indicator issues


---

### Commit: 92555ce
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Nov 11 11:40:47 2024 +0530

> chore: made message container black and white



---

### Commit: e8dc8bb
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Nov 10 15:43:57 2024 +0530

> chore: removed the useEffect to load the websocket url



---

### Commit: 2b50952
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Nov 10 15:26:24 2024 +0530

> chore: made login screen responsive



---

### Commit: f9c351d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Nov 10 14:59:19 2024 +0530

> big: managed logged in conditional routing for auth and index page



---

### Commit: 0f018c5
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Nov 10 01:24:32 2024 +0530

> chore: allmost all AI generated code to download in pdf or markdown



---

### Commit: 9bb727d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Nov 10 00:41:23 2024 +0530

> chore: fixed the scroll to the bottom not working on regeneration



---

### Commit: c8220c9
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Nov 9 18:33:56 2024 +0530

> Merge branch 'product'



---

### Commit: ba3aa15
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Nov 9 16:40:16 2024 +0530

> feat: regenerate feature fully working

Notes:
wip: changed Frame.tsx render to use the new Artifact Context
- Added useEffect to set the frameId on mount
- mapped over the entries of the artifactObject to render all the
  artifacts
chore: removed the older ArtifactContext


---

### Commit: f4f96b6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Nov 9 16:01:28 2024 +0530

> feat: regenerate button is working but with a bug

Note:
- The list of versions in the bottom tray of the ArtifactFrame does not
  update when a new version is available. You have to manually exit out
  of it and come back to see the new versions. This is a function of how
  Artifact is built, it controls itself which is what causes this
  problem. THere is no way to get it to react to a change, without it
  being weird. Hence it fails. Need to fix this.


---

### Commit: e888119
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Nov 9 12:39:35 2024 +0530

> feat: renerate button works, still needs polish though

Notes:
- The frontend now sends the completionframe with signal.regenerate type
  on it to the backend
- backend receives it, and regenerates that particular artifact
	- first it finds the parent frame id
	- regenerates using the title as the thing to generate
	- packages the webframe with frame_id of the parent
	- sends it to the frontend
- when frontend receives it, it adds a newly generated artifact

Improvements:
- Add versions like, so you can switch between versions
- refactor the backend to make the regeneration cleaner, right now it is
  being handled in isolation in the receive message logic
- generate all artifacts and generate single artifact need to be
  refactored, see if both are needed if you are sequentially generating.


---

### Commit: eac955c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Nov 8 17:50:23 2024 +0530

> chore: moved the Artifact from handling its own mini state to just using the CompletionFrameChunk

Note:
- This is needed to build the regenerate logic. Handling a minified
  version of the completion frame was turnign out to be painful. So on
  regenrate click the entire frame is sent back with a signal.regenerate
  type


---

### Commit: 12e71c7
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Nov 8 17:22:50 2024 +0530

> feat: added a changelog



---

### Commit: 7c4b642
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Nov 8 12:14:19 2024 +0530

> refactor: added context for websocket, separated types into their own file

Notes:
- was using websocket functions everywhere, so took the plunge and
  created a websocket context which can be easily reused.
- this removed a lot of prop drilling, although the components
  themselves are less reusable, which is fine because I didnt make them
  to be reusable, rather functional.
- separated types into a type file, not all but the ones i encountered
  during implmenting websocket context. The handler and sender types I
  will deal with later.
- fixed the key error, was passing keys willy nilly and not at the level
  that where it was needed. Also learnt, you cant pass key as a prop.


---

### Commit: 4a40017
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Nov 8 10:54:19 2024 +0530

> feat: artifact now uses title

Note:
- Updated the artifact context from being a single text state to an
  object with a text and title fields
- The server sends the title in title case
- the title is displayed on the artifact button as well as the Artifact
  Frame


---

### Commit: 775bb0f
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Nov 8 10:02:16 2024 +0530

> chore: added human.signal to object type in websocket frame



---

### Commit: 5680d36
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 7 19:10:56 2024 +0530

> chore: added class level and function level logging with switches to turn on and off



---

### Commit: 94af651
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 7 16:22:54 2024 +0530

> refactor: separated dispatch from generation, better separation of responsiblity



---

### Commit: dc37356
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 7 14:36:07 2024 +0530

> refactor: moved the frame creation from UserArea to websocketMessageSender, better separation of concerns



---

### Commit: 3e1a2eb
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 7 14:15:59 2024 +0530

> chore: refactored to unify spellings, added fields to completion frames

Note:
- Spelling of artifact was previously set as artefact, the inconcistency
  in spelling was fixed. Involved both frontend and backend changes.
- Added title and createdTs fields to start capturing the timestamps. I
  am using unix timestamps because they are ints, and make it easy to
  sort.
- the fields are not currently being consumed but the protocol is
  updated on both front and backend


---

### Commit: 3c833dd
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 7 10:21:58 2024 +0530

> bug: voice last 2 seconds were being cut off, resolved by removing chunk size



---

### Commit: 3932a53
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Nov 7 10:02:24 2024 +0530

> feat: chat is now responsive, mimics claude UX more closely

Note:
- The chat window now shows up in the center
- when you open an artefact it goes to the side and displays the
  artefact
- on closing the artefact you come back to the chat in the center view
- responsive on mobile, where either chat or artifact view shows


---

### Commit: f1ea19e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 6 19:53:34 2024 +0530

> feat: artefacts now show up in their own separate generative area

Note:
- THe old Generative area is removed
- The artefacts now show up close to Anthropic style, clickable
- WHen you click on an artefact it shows up in the generative area on
  the right
- Added a context for the artifact text


---

### Commit: 95541ba
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 6 15:31:37 2024 +0530

> feat; Suggestion and options show up for the user to use

Note:
- both opttins and suggestions show up for the user to view
- user can click on a single button and pull the suggestion into the
  input area and use for submission
- the tablist on the left side is removed, thoughts are also removed,
  now it is empty and only filled when artefacts become available


---

### Commit: 0675038
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 6 14:44:14 2024 +0530

> feat: added a button that allows you to use suggestion



---

### Commit: e421311
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Nov 6 12:07:08 2024 +0530

> feat: added a suggestion box above the input area



---

### Commit: 8c5edcf
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Nov 5 13:37:19 2024 +0530

> chore: added scroll to current frame where thoughts are rendered



---

### Commit: 6a3fd00
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Nov 5 12:13:07 2024 +0530

> Merge branch 'product'



---

### Commit: dff420c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Nov 5 12:10:11 2024 +0530

> chore: handled local vs cloud env loading

Note:
- added a separate function to handle loading local env variables if
  .env.local exists otherwise uses env
- this ahelps me avoid having to remember to switch the variables


---

### Commit: 26c99c5
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Nov 5 12:09:30 2024 +0530

> chore: miscellaneous changes

Note:
- added keys to some components
- prevented empty input submission
- code refactor and cleanup in handlers


---

### Commit: 6819719
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Nov 5 12:01:15 2024 +0530

> chore: all the artefacts to push the app to gcp

Notes:
- All the cloudbuild files and so on are generated on the fly
- the main shell script is `deploy_cache` this takes advantage of cache
  and pushes the changes to the cloud
- `verify_secrets` is to ensure the secrets are in place
- added dockerignore for some frontend stuff


---

### Commit: 7407d7a
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 30 21:14:30 2024 +0530

> feat: yayyy the artefacts are being generated

Notes:
- Artefacts for jd, rubric and questions are being generated
- They show up on the frontend
- the fronted rendering is in markdown


---

### Commit: 2cdfa40
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 30 19:31:27 2024 +0530

> Merge branch 'product'



---

### Commit: fa9fe23
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 30 19:28:02 2024 +0530

> chore: added dispatch class to handle frame transformation

Note:
- The dispatch class uses single dispatch function to handle different
  types of the payload.
- Readded Agent.think from a prev commit because it is needed to start
  the agent
- keep the textarea open by default


---

### Commit: 72c644e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 30 17:06:32 2024 +0530

> feat: big update, the interview is losely working

Notes:
- The interview is a new class that conducts the interview and shows
  helpful information to the user
- After finishing all the questions, the interview indexErrors out.
- Next we will catch the index error and generate artefacts based on
  that.


---

### Commit: edbc902
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 30 16:47:10 2024 +0530

> chore: added syntax highlighting for thought blocks



---

### Commit: fff952c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 30 10:44:13 2024 +0530

> chore: removed components that dont need or shouldnt take user input

Notes:
- This includes model selector as well as model controls for temperature
  and so on. This anyway was not plugged in, and we dont want the user
  controlling this.
- Light and dark mode because dark mode for now looks like shit. Havent
  designed for that.


---

### Commit: 9183172
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Oct 29 20:29:35 2024 +0530

> feat: Added a generative area, added types for conversation

Notes:
- This is a big change, forgot to commit thrice
- There is now a generative area, and the thoughts (intenal thoughts)
  and artefacts can be rendered.
- frame rendering handler added that can render content, thought, etc
  per need
- some work on deployment also is in here. It doesnt fully work, I still
  need to deal with environment variables but it is a solid step
  forward.


---

### Commit: 3903a64
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Oct 27 15:30:01 2024 +0530

> feat: multi turn communicatin is enabled, and types were removed

Notes:
- Consolidation of types. The protocol between frontend and backend
  updated to send the same WebsocketFrame both sides. This simplified
  so much of the memory management, and parsing and efficiency.
- With this the frotnend and backend send the same packets back and
  forth.


---

### Commit: d7d4cb7
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Oct 26 17:51:56 2024 +0530

> feat: frontend can send a message and get a reply

Note:
- User can send a message and the backend consumes it and responds to it
  with another message

To work on:
- My memory is a collection of frames, but the user input is not a
  frame. I have to think about the right way to abstract those two
  concepts.


---

### Commit: fd43cc8
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Oct 26 17:23:42 2024 +0530

> feat: added a message sender to the websocket

Note:
- This is a SOLID principle followign sender similar to the handler I
  built in the last commit
- You can keep adding strategies


---

### Commit: 1af5b90
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Oct 26 11:46:31 2024 +0530

> Merge branch 'product'



---

### Commit: ed3bb9c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Oct 26 11:43:32 2024 +0530

> feat: frontend now sends a message to the backend

Note:
- quite simple, the frontend now sends a message to the backend
- the backend receives it and prints it to console
- Added a new concept of Memory to an agent, even though it is not
  actively being used right now
- the receive message in the agent is also updated to listen for
  messages


---

### Commit: 283a707
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Oct 26 11:05:49 2024 +0530

> feat: added a handler for routing messages to relevant dispatch strategy

Note:
- Used solid principles to create a frameHandler router, that takes care
  of routing the message to the right dispatch
- it is scalable, meaning you can add a new strategy and follows SOLID
  principles
- Will build something similar on backend too.
- learnt about classes and how to work with classes and react in js
  (hint: useRef)


---

### Commit: 31a920d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Oct 26 11:05:22 2024 +0530

> chore: added a select to chose ai models (could be misplaced)



---

### Commit: ca1f260
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Oct 25 23:17:12 2024 +0530

> chore: added a disconnected popover for model configuration



---

### Commit: 94667df
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Oct 25 22:56:44 2024 +0530

> feat: added show and hide textarea to improve readability



---

### Commit: bcd81be
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Oct 25 20:13:39 2024 +0530

> feat: the ui is reactive, a frame shows on the screen yayy

Notes:
- this is a team effort and we couldnt have done it without the boys.
  But yasss
- the ui is reactive, meaning that the state, dispattch adn websocket
  are interconnected. The dispatch acts as a router, the websocket is
  doing thet routing based on the message it gets. The reducer then is
  updating the state and the ui is reacting to it.
- you can see one message come in from the backend because thatt is all
  it has been programmed to do.
- No serious testing done


---

### Commit: c867280
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Oct 25 11:23:24 2024 +0530

> feat: typed communication open between backend and frontend

Notes:
- Mostly backend update, but a big one.
- the frontend and backend are communicatin via typed schemas
- the backend is sending the type that the frontend expects to receive
- you did good on removing types, now the general message object is a
  single type only, no union between streaming and completion
- did a good job separating responsibility between the channel and
  agent. A circular import error showed up which was a code smell.

Next Steps:
- Although right now, only completion is tested. Need to test streaming.
- frontend receives and console logs the object but it isnt going into
  the state and the ui is not reacting to it yet.


---

### Commit: 506a70e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Oct 24 16:49:27 2024 +0530

> chore: separated responsibility of connection manager and websocket handler

Note:
- the connection manager was also responsible for sending and receiving
  messages which was mixing up responsibilities.
- refactored to separate responsibilities


---

### Commit: 544f1c1
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Oct 24 13:29:01 2024 +0530

> feat: basic websocket that calls the v2 websocket

Notes:
- Currently only heartbeat processing is supported
- type support for routing will be added next


---

### Commit: bfa84eb
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Oct 24 13:23:40 2024 +0530

> feat: added a new websocket hook v2

Notes:
- this is aset up with a class that manages the connections
- right now only the heartbeat goes through, but it is the starting
  point
- associated frontend implementation will be in the next commit


---

### Commit: b46e9ef
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Oct 22 13:09:26 2024 +0530

> debug: removed overflowing div in text box



---

### Commit: b7ebf4a
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Oct 22 10:38:12 2024 +0530

> feat: voice recording and transcription added

Note:
- voice transcriptin is added as a button that updates the input value
  inside the textarea
- Added a slight modification to the transcribe audio that makes the
  chunk optional, if no chunk given then the internal audiochunks are
  used to do the transcription.
- This is now a nice independent component that can be used separately
  given a textarea input value exists


---

### Commit: 51dc5e6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 21 22:19:54 2024 +0530

> bug: textarea resize was not working, fixed



---

### Commit: 42d6bf9
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 21 21:55:56 2024 +0530

> chore: big refactor of the UI

Notes:
- Cleaned up the code for textarea
- using a context for inputValue because a bunch of components required
  it and a lot of prop drilling was happening.
  	- used a reducer along with the context because my state
	  management with that is likely going to become more complex
- moved reducers into their own folder in the root
- reorganized components so that every page has its own component folder
  to pull from. If something ends up being used in multiple places then
  I will move it to the global components folder
- moved the old page to `home/create2`, while the new one i am building is
  at `home/create`


---

### Commit: aa897cc
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 21 11:33:09 2024 +0530

> Merge branch 'product'



---

### Commit: 1365cec
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 21 11:22:20 2024 +0530

> feat: working threads agent (my sample agent)

Special Note:
- The config file is needed for the main agent (not the threads agent)
  to work. I deleted that, so I am also restoring it in this commit. The
  right place for this would have been a commit ago, but doing it here
  for ease.

Notes:
- Generates a datacard and a rating rubric to fill out
- On every conversational turn the rubric and the datacard are filled
  out. This makes latency very high.

Improvements:
- Will use instructor to do structured extraction rather than writing
  long ass random prompts
- the rubric shoul dbe filled in at the end, not for every turn


---

### Commit: 6d54372
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 21 11:22:20 2024 +0530

> feat: working threads agent (my sample agent)

Notes:
- Generates a datacard and a rating rubric to fill out
- On every conversational turn the rubric and the datacard are filled
  out. This makes latency very high.

Improvements:
- Will use instructor to do structured extraction rather than writing
  long ass random prompts
- the rubric shoul dbe filled in at the end, not for every turn


---

### Commit: e86e849
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 21 11:22:04 2024 +0530

> feat: updated the voice endpoint to output text response

Notes:
- Simple change that moved from verbose json to a text response


---

### Commit: ed3cc82
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 21 11:00:28 2024 +0530

> chore: refactored folders, moved hooks and context out of app folder



---

### Commit: dffdd5c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Oct 20 01:50:36 2024 +0530

> feat: frontend, working record and transcribe endpoint

Notes:
- There are a few new buttons to record, play and transcribe the
  audiochunks
- there is an action for server side rendering that is used by the
  client component. I understood the boundary a bit better.
- currently the transcript returned is verbose json object that needs
  to be parsed, I will do it later.
- I felt like I was using AI well, but felt a bit of anxiety
  unecessarily for if I was absoribing less depth by relying on LLMs.
- currently a monstrosity. the ChatInterface component has gotten so big
  that Columbus wants to circumnavigate it.
- This is something that needs to be havily refactored, at the least for
  elegance and brevity if not rewrites.


---

### Commit: 7311b28
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Oct 20 01:47:20 2024 +0530

> feat: added endpoint to transcribe voice

Note:
- tried building it as a streaming response, but have not succeeded.
- part i get stuck on is handling hte file. The file chunks sliced up do
  not retail their filetype information. Trying to combine the first and
  the current chunk also doesnt do anything to preserve headers.
- for true streaming that needs to be fixed


---

### Commit: b7cd436
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sat Oct 19 17:57:34 2024 +0530

> feat: added a hook to record voice from the browser

Notes:
- using webrtc apis to record audio after taking permissions
- the way this is connected to the chatComponent is messy and not
  elegant. This needs to be refactored but works for now
- there is a record button and a play button which can only play, there
  isnt a logic to get it to stop playing yet


---

### Commit: d8d2a36
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Oct 15 13:19:57 2024 +0530

> feat: agent with internal cognition taking shape

Notes:
- generates a rating rubric
- generates a job card to fill out
- through the conversation fills both of these artefacts out
- At the end you have a filled out rating rubric for hiring manager, and
  a job card

Concerns:
- the rating rubric gets filled fully in a single go. It shoule be
  progressively filled in
- rating rubric seems to always favor high scores
- The datacard also is filled based on the info given but there are
  parts that are not filled out. How do you deal with that?
- latency is very high


---

### Commit: da79db4
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 14 20:46:59 2024 +0530

> feat: added payment session create with stripe in backend with tests



---

### Commit: a20b33e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 14 14:35:06 2024 +0530

> feat: experimental agent running

Notes:
- agent asks the hiring manager questions
- agent can also parallely generate evaluation answers
- conversational back and forth is simulated in teh simplest possible
  way
- all of the strings setting the agent up are currently handwritten
- very little programmatically happening, but still having the
  evaluation in line is interesting
- current evaluation does not take into account history


---

### Commit: fbcaf9a
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Oct 10 21:58:26 2024 +0530

> feat: terrible terrible implementation of knowledge generator

Note:
- I am lamopst embarassed to commit this. But need to capture a
  checkpoint.
- The structured response is used as a hook to start generating the
  role, team, company descriptions and more.
- But the implemetation is so hacky I want to redo everything. But i
  will do that tomorrow, for today this is an honest day's work. But
  seruiosly, burn everything and redo it. Feel free to even go back a
  commit and start from there.


---

### Commit: 276c410
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Oct 10 15:16:22 2024 +0530

> chore: reorganized code, cleaned up repeated dunctions, and added typing.



---

### Commit: 4b13963
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Oct 10 12:43:57 2024 +0530

> feat: updated hte frontend to work with types of outputs

Note:
- Modified the layout so as to accept structured outputs
- Modified the layout ttto show single view rather than side by side
- Added a simple routing key into the communication with the backend


---

### Commit: e5d08cb
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Oct 10 12:42:18 2024 +0530

> feat: added a structured output to the websocket message

Note:
- Currently only works for a single strtucttured type, InterviewConfig
- Lots of redundant code, that I will remove in the next commit if
  everything is working as expected
- restructured the code to make it more modular


---

### Commit: 8f4b8a6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Thu Oct 10 10:36:45 2024 +0530

> chore: separated intelligence into its own space, and added a router for generating by type

Note:
- Have a basic untested version of structured output generation
- to accomodate this, broke process_response to streaming and structured
  types using a case match
- Even with changes, the original parts of the code work.


---

### Commit: 9a3645e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 9 23:01:12 2024 +0530

> feat: added dark mode, and mode switcher



---

### Commit: 643504b
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 9 10:32:29 2024 +0530

> feat: added markdown support and partial syntax highlighting

Notes:
- Got the code to wrap and respect the container width
- the syntax highlighting is not colored, dont know why but it isnt the
  highest priority now, so will come back to it
- the inline and style elements in the syntaxhighlighter and
  reactmarkdown blocks are erroring, I dont know why.


---

### Commit: e2fc596
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Oct 8 22:08:17 2024 +0530

> feat: used reducer to handle state updates, works beautifully now

Notes:
- used a reducer to handle the state updates and man instantly
  everything started working
- streamign response now works great!

Good job.


---

### Commit: ee57014
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Oct 8 20:15:55 2024 +0530

> feat: streaming response with websockets working with dropped packets

Note:
- Committing this to log a working point
- The websocket works, the streaming responses work but there are
  dropped packets
- Actually there are many dropped packets, the reason being my strategy.
	- I am using a state as a waypoint for consuming chunks and
	  using that to update the message list.
	- This is failing becuase the state is updating faster than the
	  exchange can happen. Large chunks are being dropped.
- I need to update the strategy to avoid a state that updates so rapidly


---

### Commit: de947a1
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Oct 8 10:05:57 2024 +0530

> feat: implemented a simple agent with streaming responses

Note:
- Used async client with streaming response that print to stdio
- Still to connect with the frontend


---

### Commit: 8b62377
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 7 15:52:37 2024 +0530

> chore: refactored chatinterface to separate header and input area



---

### Commit: 07f928e
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 7 13:26:30 2024 +0530

> feat: frontend websocket connection working phewwww

Notes:
- websocket that can accept all kinds of inputs including string, binary
  and more is set up.
  	- heartbeat also set up
	- Reconnect also set up
- Added a Simple Chat interface to test tthe websockets because man they
  werent working
- Cleaned up useFirebaseAuth and useWebsockets to avoid logging
  anything, because that gets picked up by the server (even if it is all
  in a client component)
- Also removed unecessary calls to hooks especially if conttext is being
  used (useFirebaseAuth) to avoid multiple calls.
- Added types into typoes folder

Complaint:
- Really struggled with this, and the problem turned out to be that
  while useEffect unmounts, a disconnect was being called. The
  disconnect was indiscriminately closing the websocket even when it
  wasnt ready. Checking that it was open was all it took to fix this.
  But took me way too long.


---

### Commit: ce85115
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Mon Oct 7 13:24:04 2024 +0530

> feat: set up a simple websocket server to connect to frontend

Notes:
- Additionally organized my api endpoints into a somewhat complex
  hierarchy because claude said so. I can see some of the benefits, but
  I have a feeling i overoptimized too soon.
- added a dead simple basic agent for testing. Not using right now but
  will later.


---

### Commit: 2a2f18c
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Oct 6 18:33:16 2024 +0530

> chore: redirect user to home page after log in using nextjs router



---

### Commit: 3644e01
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Sun Oct 6 17:59:33 2024 +0530

> feat: chat interface in place



---

### Commit: 971485d
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Oct 4 21:51:59 2024 +0530

> chore: changed all form inputs to textarea



---

### Commit: 9ed91c6
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Oct 4 20:23:25 2024 +0530

> feat: added a general layout and form to create an interviewer



---

### Commit: 6cded84
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Oct 4 15:23:44 2024 +0530

> chore: added a home and a home/create page



---

### Commit: ed569ab
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Oct 4 12:37:10 2024 +0530

> chore: added a global logger for server and client components, updated logs everywehere so I can centrally manage log level



---

### Commit: e13ec18
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Fri Oct 4 11:22:47 2024 +0530

> feat: added a home route and a layout for it

Notes:
- Layouts includes header and footer
- Signout button shows up on the header
- Footer has dummy links to an About page and a Terms and conditions


---

### Commit: eb58913
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 2 17:15:40 2024 +0530

> feat: added middleware that now checks for logged in user on every route



---

### Commit: 853f1f2
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Oct 2 13:17:26 2024 +0530

> chore: added a hook for firebase auth, used that to share aut functions across all apps



---

### Commit: 5f66643
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Tue Oct 1 11:10:36 2024 +0530

> feat: Auth working

Frontend:
- basic UI, google and github signin methods working in a mix of client
  and server components is working.

Backend:
- firebase admin sdk that verifies and decodes tokens is also up and
  running and utilized by the frontend.


---

### Commit: 99e0caa
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Sep 25 19:22:59 2024 +0530

> init commit for backend



---

### Commit: bb3e8c0
**Author:** Anudeep Yegireddi <anudeep.yegireddi@gmail.com>
**Date:** Wed Sep 25 10:33:12 2024 +0530

> initial commit



---
