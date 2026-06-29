# SOLID Principles

Five principles for writing maintainable object-oriented code.

## S — Single Responsibility Principle
A class should have one reason to change. If a class handles both business logic and database access, changing the database forces changes to business logic. Split them.

## O — Open/Closed Principle
Software entities should be open for extension but closed for modification. Add new behaviour by adding new code (e.g. a new subclass or strategy), not by editing existing code.

## L — Liskov Substitution Principle
Subtypes must be substitutable for their base types without altering program correctness. If a function works with a `Shape`, it must work with any `Shape` subclass without special-casing.

## I — Interface Segregation Principle
Clients should not be forced to depend on interfaces they do not use. Prefer several small, focused interfaces over one large general-purpose interface.

## D — Dependency Inversion Principle
High-level modules should not depend on low-level modules — both should depend on abstractions. The `OrderService` should depend on a `PaymentGateway` interface, not on `StripePaymentGateway` directly. This makes swapping implementations easy and keeps the domain clean.

## Practical Notes
- SOLID is a guide, not a checklist. Applying all five to every class produces over-engineered code.
- Start simple. Introduce a principle when you feel the pain it solves.
- SRP and DIP are the most impactful in everyday work.
