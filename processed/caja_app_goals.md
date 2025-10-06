# Caja App – Goals and Requirements (Processed from Transcript)

## High-Level Goals

- **Live Event Engagement:**  
  Create a platform to boost audience engagement at events (town halls, tech talks, training sessions).

- **Extensible Foundation:**  
  Allow engineering leaders and contributors to easily add new games or interaction types to the platform.

- **Real-Time, Device-Friendly Interaction:**  
  Enable participation via personal devices (QR codes, live polls, voting, drawing, etc.), supporting both shared and individual displays.

---

## Functional Requirements

1. **Room and Session Management**
   - Users join rooms/sessions via simple code (no login/account needed).
   - Admin can create/manage rooms and start events/games.
   - Each session is tied to a specific activity type.

2. **Device Integration**
   - Large/shared display projection, plus support for mobile device views.
   - QR codes for quick join and device access.

3. **Game/Engagement Types**
   - Support multiple interaction modes:
     - Pointing poker (storypoint voting)
     - Live polls/quizzes
     - Drawing games
     - Trivia games
   - Not restricted to a single use case.

4. **Real-Time Sync and Feedback**
   - Live updates on both large display and personal devices.
   - Show individual and aggregated results (e.g., tallies, scores).

5. **Extensibility**
   - Modular design for easy addition of new games/types.
   - Abstractions for activities: questions, answers, voting, results.

6. **Content Versioning**
   - Ability to version game/trivia/training content (e.g., regional variants).

7. **Low Barrier to Entry**
   - Fast, frictionless joining (room code, QR scan, no login).

8. **Admin Controls**
   - Admin can launch/manage games and control result display.
   - Game flow management.

---

## Non-Functional Requirements

- **Scalability:**  
  Must support large numbers of users (e.g., for company-wide events).

- **Extensibility/Modularity:**  
  Platform must be easily extendable by contributors.

- **Accessibility:**  
  Works on mobile and desktop, easy to join/participate.

- **Reliability:**  
  Stable, real-time sync (webhooks, pub/sub, etc).

- **Documentation & Onboarding:**  
  Built-in resources for contributors to understand and extend the repo.

---

## Tech Stack Preferences

- **Frontend:** React (default/common, but flexible)
- **Backend:** Python (preferred for backend)
- **Real-Time:** Dynamic frontend
- **Integration:** Slack integration considered
- **Microservices:** Option to split into microservices for each game/type

---

## Name/Branding

- **Caja:** Spanish for "box"—distinct from "Jackbox," meant to evoke extensibility and modularity.

---

## Related Documentation

- **[Detailed Features Specification](./caja_app_features.md)** - Comprehensive breakdown of all platform features with user story foundations

## Summary

Caja is a modular, extensible platform for live event engagement, supporting real-time polling, trivia, voting, and other interactive activities. It emphasizes ease-of-use, rapid participation, and provides a base for engineering leaders to add new engagement mechanisms. The goal is to raise engagement in work/training events, with flexibility for future expansion.
