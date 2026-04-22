# Feature: Modular Monolith and Event-Driven Chat Flow

This plan evolves the Telegram AI chatbot into a modular monolith with clear users, chat/AI, and history boundaries, then introduces an in-memory event bus so modules communicate through public contracts instead of reaching into each other's internals.

The design follows the current Python service-oriented structure in `src/`, keeps dependencies explicit through runtime wiring, and avoids external infrastructure such as Kafka or RabbitMQ.

## Phase 1: Modular Monolith Foundation (MM-01 to MM-04)

Split the current chat flow into focused feature modules with explicit public interfaces. This phase introduces user identification, chat/AI response generation, and history management as separate package boundaries while keeping behavior compatible with the existing Telegram bot.

## Phase 2: Event Bus and Integration (EB-01 to EB-03)

Add a lightweight in-memory event system and wire module interactions through events where direct cross-module calls are not required. This phase establishes event contracts for `UserCreated`, `MessageReceived`, and `ResponseGenerated`.

## Phase 3: Validation and Documentation (VD-01 to VD-02)

Prove the architecture with focused tests and update documentation so the event-driven modular monolith is understandable, runnable, and ready for future persistence or external messaging.
