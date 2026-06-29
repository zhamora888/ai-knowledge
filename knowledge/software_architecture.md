# Software Architecture

## Layered Architecture
Organises code into horizontal layers: Presentation, Application, Domain, Infrastructure. Each layer only depends on the one below it. Simple to reason about; can become rigid as systems grow.

## Hexagonal Architecture (Ports and Adapters)
The domain sits at the centre. External systems (databases, APIs, UIs) connect through ports (interfaces) and adapters (implementations). Makes the core logic independent of infrastructure — easy to test and swap adapters without touching business logic.

## Microservices
Breaks a system into small, independently deployable services, each owning its own data. Enables scaling and deployment flexibility. Adds operational complexity: network calls, distributed tracing, eventual consistency.

## Event-Driven Architecture
Services communicate by publishing and consuming events rather than calling each other directly. Decouples producers from consumers. Useful for workflows that span multiple services. Harder to trace and debug than direct calls.

## CQRS (Command Query Responsibility Segregation)
Separates write operations (commands) from read operations (queries) using different models for each. Allows optimising reads and writes independently. Often paired with Event Sourcing.

## Key Tradeoffs
- Simplicity vs. flexibility: more layers and abstractions = more moving parts
- Coupling vs. cohesion: low coupling between modules, high cohesion within them
- Consistency vs. availability: distributed systems often must choose (CAP theorem)
