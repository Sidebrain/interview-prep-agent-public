All notable changes to this project will be documented in this file.

## [0.2.0] - 2024-11-08

### Added
- Suggested Message Button functionality
- Individual artifact segregation with titles
- Timestamps for all content chunks
- Artifact regeneration capability
- Artifact download functionality
- Artifact sharing feature

### Changed
- Updated UI: thoughts and artifacts window now hidden by default
  - Windows only appear when artifacts are generated
- Improved thoughts section positioning
  - Now anchored below and scrolls with generated data

### Fixed
- Voice-to-text transcription accuracy
- Empty input submission prevention
- Thoughts section scrolling behavior

---

## [0.1.0-alpha] - 2024-11-1

### Added
- Interviewer mode core functionality:
  - Conversational LLM experience
  - Speech-to-text capabilities
  - Artifact generation for:
    - Job Descriptions
    - Rating Rubrics
    - Interview Questions
- Authentication system implementation

### Known Issues
- Voice-to-text inconsistently captures complete audio
- Empty inputs being registered causing question skips
- Thoughts section positioning causes unnecessary scrolling
- Artifacts consolidated in single markdown file instead of being segregated