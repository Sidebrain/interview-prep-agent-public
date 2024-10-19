# Architecture v2

Conversational experiences

At the root are `threads`

Each thread is a purpose driven interaction.

```mermaid
---
title: Flow
---
%%{init: {"flowchart": {"htmlLabels": false}} }%%
flowchart TD
    start([start])
    intro[introduce yourself]
    t1[thread-1]
    gen[generate internal knoweledge]

    start-->intro
    intro -->t1
    subgraph loop till goal achieved
    t1-- loop -->t1
    end
    t1 -- generate internal knowledge --> gen
```

```python

class Thread(BaseModel): 
    goal = "gather minimum requirements to conduct an interview"
    ideal_state = """The interview is for the following:
        - role: Senior consultant
        - company: Bain Consulting
        - 
"""
    current_state: str

    def check_if_ideal_state_has_been_achieved():
        ...

```

Questions for hiring manager:
- designation and role
- why the requirement
- deep dive into requirement (required)
  - expereince
  - leading a team
  - junior / senior
  - roadmap for their career
- roi of the role 
- salary / budget 
- backup - if the role does not work (overhire) how we can push to a different role (get somebody with two skillsets)
- culture --> style of work 

# Sid 
Personal - attitude
technical 
scenario based questions - sales questions (appvle vs..)
senioir manager - scenario based, berhavioral 
hr - acceptance 

Insights from Masai:
- pardon please, askign the ai to repeat themselves
- clarifications on the question (can you tell me how i can share my screen)
- reference to the speaker as AI, as in "hi AI"

```mermaid
flowchart TD
    subgraph intro
        start(AI intro)
    end
    subgraph interaction loop
        ai-q(ai ask question)
        human-r(user responds)
    end
    subgraph human-input-gen
        human-proc[human response generator]
    end
    subgraph ai output gen
        ai-proc[ai response generator]
    end
    subgraph context-builder
        acc[accumulates responses]
    end
    ai-proc-->start-->acc
    ai-proc-->ai-q-->acc
    ai-q-->human-proc
    human-proc-->human-r --> acc
    


```