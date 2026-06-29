# Design Patterns

## Creational Patterns
**Factory Method** — defines an interface for creating objects but lets subclasses decide which class to instantiate. Useful when the exact type isn't known at compile time.

**Singleton** — ensures a class has only one instance. Use sparingly; makes testing harder and introduces hidden global state.

**Builder** — separates the construction of a complex object from its representation. Good when an object has many optional parameters.

## Structural Patterns
**Adapter** — wraps an incompatible interface so it matches what a client expects. Common when integrating third-party libraries.

**Decorator** — attaches additional behaviour to an object at runtime by wrapping it. Preferred over subclassing when behaviour needs to be composed flexibly.

**Facade** — provides a simplified interface to a complex subsystem. Reduces the surface area a client needs to understand.

## Behavioural Patterns
**Strategy** — defines a family of algorithms, encapsulates each one, and makes them interchangeable. Replaces conditionals with polymorphism.

**Observer** — lets objects subscribe to events from another object. The subject notifies all observers when its state changes. Foundation of event-driven UIs and pub/sub systems.

**Command** — encapsulates a request as an object. Enables undo/redo, queueing, and logging of operations.

**Repository** — abstracts the data layer behind a collection-like interface. The domain layer talks to repositories, not databases directly.

## When to Apply Patterns
Patterns solve recurring problems — apply them when you recognise the problem, not to show pattern knowledge. Premature pattern use adds complexity without benefit.
