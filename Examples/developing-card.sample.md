---
type: incubator/idea
stage: developing
created: '2026-10-05'
updated: '2026-10-21'
output-format: null
domain: platform
themes:
  - feedback
  - learning-continuity
customer-sentiment: medium
user-experience: high
revenue-potential: low
industry-disruption: medium
strategic-alignment: high
related-ideas:
  - comment-bank-for-teachers
initiative: null
source: conversation
output-file: null
research:
  - Research/feedback-carried-forward/synthesis-handoff.md
  - Research/feedback-carried-forward/development-research.md
research-ids: []
blocked_by: null
jira-key: null
jira-pushed-at: null
jira-sidecar-url: null
---
## Feedback That Carries Forward

**Core insight:** A teacher's comment on a piece of work is the most specific thing Coursebook knows about a student, and it is shown once, beside the grade, and never again.
**Problem it addresses:** A student starts the next essay without the advice written on the last one, and the teacher ends up writing the same comment twice.
**Who cares:** Students who are told the same thing every term, teachers who write a comment on each of thirty scripts, and heads of department who are asked whether feedback changes anything.
**Strategic connection:** Extends Entered Once to the comments teachers write, so that a comment is written one time and shown wherever the next piece of work begins.

### Opportunity Assessment

| Dimension | Rating | Rationale |
| ----------- | -------- | ----------- |
| Customer sentiment | Medium | Teachers describe repeating themselves, and none has asked for an old comment to reappear. |
| User experience | High | A student opens a new task and the last advice on that skill is already beside it. |
| Revenue potential | Low | It ships inside Coursebook and gives no district a new line to buy. |
| Industry disruption | Medium | Competitors help a teacher reuse a comment, and none shows a student the comments already received. |
| Strategic alignment | High | A comment that stays with the learner is Entered Once applied to the record teachers write most often. |

### Research Summary

- Students acted on a written comment in 3 of 10 cases when it appeared only beside the grade, and in 6 of 10 when it was shown again as the next task opened. ([Fernhollow Institute, Written Feedback Study 2026](https://example.com/fernhollow-written-feedback-2026))
- Corvid Classroom's comment bank lets a teacher reuse a saved comment; neither it nor Pennywhistle Assess shows a student a comment from an earlier task. ([Kestrel Ridge Research, Classroom Platform Scan, March 2026](https://example.com/kestrel-ridge-classroom-platform-scan-2026))
- 14 of 20 teachers interviewed had written the same comment to the same student in consecutive terms. ([Larkmoor teacher interviews, September 2026](https://example.com/larkmoor-teacher-interviews-2026-09))
- Coursebook stores every comment against a submission and tags every task with a skill, so an old comment can be matched to a new task from data already held. ([Coursebook data model notes, 2026](https://example.com/coursebook-data-model-notes))

### Thought Outline

The move is to show a comment again at the moment it can be used. Coursebook already keeps every comment and already knows which skill each task practises, so when a student opens a new task the last advice on that skill sits beside the brief, and the teacher marking it sees what was said before. That gets students opening Coursebook's feedback every time they start a task while taking a repeated comment off the teachers whose goodwill decides a renewal while giving a district the evidence of feedback use it now asks vendors to show — one move serving adoption, retention, and positioning together. Nothing new is asked of the teacher. The open decision is how much history to show: the last comment, or the pattern across a year.

### Open Questions

- Does a student read a comment shown before a task, or scroll past it as they do the grade?
- Will teachers write differently once they know a comment will be seen again?
- Are tasks tagged with skills consistently enough to match an old comment to a new task?
- Does a comment written in one teacher's class make sense when a different teacher sets the next task?
