# NoDepDB

**NoDepDB** is a zero-dependency key-value database built for the **Unstop Zero Dependency Hackathon**. It demonstrates how a functional client-server database system can be built using only a programming language's standard library—without external packages, frameworks, or database libraries.

## Introduction

Modern applications often rely on many external dependencies for networking, storage, serialization, testing, and command-line interfaces. While useful, these dependencies can add installation complexity, compatibility issues, security concerns, and maintenance overhead.

NoDepDB takes a different approach: it provides a lightweight database experience using only built-in language capabilities. The project includes a TCP server, storage engine, network protocol, and a CLI client.

## Problem Statement

Build a functional database system without using any third-party packages.

The system must support client-server communication, persistent or in-memory data storage, command parsing, error handling, and a usable command-line interface while maintaining strict standard-library-only compliance.

## Why Zero Dependency?

A zero-dependency project is easier to understand, run, audit, and distribute.

Benefits include:

- No package installation or dependency conflicts
- Smaller deployment footprint
- Reduced supply-chain risk
- Easier portability across environments
- Better understanding of core networking and storage concepts
- Faster onboarding for contributors and hackathon evaluators

NoDepDB intentionally focuses on fundamentals: sockets, files, parsing, command execution, and data structures.

## Project Goals

- Build a functional TCP-based key-value database.
- Use only standard library modules.
- Provide a simple text-based request/response protocol.
- Support a command-line client.
- Keep the architecture simple, modular, and beginner-friendly.

## System Architecture

```
             Client
                |
                | TCP Socket Connection (127.0.0.1:6380)
                | Text-Based Protocol
                v
        +----------------+
        |  NoDepDB Server|
        |----------------|
        | Network Layer  |
        | Protocol Parser|
        | Command Handler|
        +----------------+
                |
                v
        +----------------+
        | Storage Engine |
        |----------------|
        | In-Memory Store|
        | WAL / Recovery |
        +----------------+
```

## Components Overview

### Storage Engine

Owned by the Storage Engine Lead. Manages database records and implements core key-value operations: storing, retrieving, and deleting keys, and persisting data via a write-ahead log (WAL) with crash recovery on restart.

**Status:** Implemented on a separate branch/pull request. Confirm merge status into `main` before relying on persistence in a live demo.

### Network Layer

Owned by the Network & Protocol Lead. Enables communication between clients and the NoDepDB server through TCP sockets — binding to a host/port, accepting connections, reading requests, and sending responses.

### Protocol Layer

NoDepDB uses a simple text-based command format:

```
COMMAND argument1 argument2
```

Example:

```
SET username alice
```

Responses are also text-based, e.g. `OK` or the requested value. This keeps the protocol easy to inspect, test, and extend.

### CLI Client

Owned by the Client / DX Lead. Connects to a NoDepDB server and sends commands typed by the user, one at a time, until `EXIT` is typed.

## Standard Library Compliance

NoDepDB is built with **only standard library modules**. See [STDLIB.md](./STDLIB.md) for the full breakdown of what third-party package each standard-library module replaces (e.g. `socket` instead of `requests`/`aiohttp`, `argparse` instead of `click`/`typer`, `unittest` instead of `pytest`).

No external package manager, framework, ORM, networking library, or database library is required.

## Running the Project

Start the server (from the project root):

```bash
python server.py
```

Start the client in a separate terminal:

```bash
python client.py
```

The client connects to `127.0.0.1:6380`.

Example session:

```
Connected to NoDepDB
Type EXIT to quit
> SET name Lalit
+OK
> GET name
Lalit
> EXIT
```

## Team Roles

| Role | Responsibilities |
|---|---|
| Storage Engine Lead | In-memory key-value store, WAL, crash recovery |
| Network & Protocol Lead (Team Lead) | TCP server, protocol design, concurrency, integration |
| Client / DX Lead | CLI client for connecting and running commands |
| Docs, Build & Submission Lead | README, STDLIB.md, build verification, submission |

## Status at Submission Time

This project was built under a 72-hour hackathon deadline. In the interest of accuracy for judges, here is the honest state of things at submission:

- **Storage engine (WAL + crash recovery):** implemented by the Storage Engine Lead. Confirm with the team whether it has been merged into `main` at the time of review.
- **CLI:** currently supports typing one command at a time and reading the response, until `EXIT`. Interactive REPL polish, a batch/scripted mode, and `argparse`-based flags (`--host`, `--port`) were part of the original design goals but are not confirmed present in the current client as of this writing.
- **Server / protocol implementation:** owned by the Network & Protocol Lead; refer to their branch for the latest state.

We chose to document the project honestly rather than overstate features that may still have been in progress at submission time.

## Known Limitations

1. Confirm current merge status of the storage engine into `main` before a live demo.
2. CLI may not yet include REPL mode, batch mode, or `argparse`-based flags — verify against the latest client code.
3. Concurrent-client behavior and error handling should be spot-checked before demo.

## Future Improvements

- Interactive REPL and batch command execution for the CLI
- Connection retry logic
- `PING` / `STATS` commands
- TTL / key expiration
- Additional test coverage for concurrent clients
- Namespaces, authentication, and other stretch features

## Conclusion

NoDepDB demonstrates that a practical client-server database — networking, protocol design, storage management, and command-line tooling — can be built from first principles using only the standard library, for the Unstop Zero Dependency Hackathon.
