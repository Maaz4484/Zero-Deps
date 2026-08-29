# Installation & Usage

## Requirements

- Python 3 (standard library only — no `pip install` needed)
- No external packages, frameworks, or database libraries required

## 1. Clone the repository

```bash
git clone https://github.com/Maaz4484/Zero-Deps.git
cd Zero-Deps
```

## 2. Start the server

In one terminal window:

```bash
python nodepdb/server.py
```

This starts the NoDepDB server, listening on `127.0.0.1:6380`.

## 3. Start the client

In a **second** terminal window:

```bash
python client.py
```

You should see:

```
Connected to NoDepDB
Type EXIT to quit
```

## 4. Run commands

Type commands one at a time, pressing Enter after each:

```
> SET language Python
+OK
> GET language
Python
> DELETE language
+OK
> EXIT
```

Type `EXIT` to disconnect and close the client.

## Supported Commands

| Command | Description | Example |
|---|---|---|
| `SET key value` | Stores a value under a key | `SET name Alice` |
| `GET key` | Retrieves the value for a key | `GET name` |
| `DELETE key` | Removes a key and its value | `DELETE name` |

> Additional commands (`EXISTS`, `KEYS`, `PING`, `STATS`) were part of the
> original design — confirm with the Network & Protocol Lead whether
> they are implemented in the current server before listing them as
> supported in judge-facing materials.

## Troubleshooting

- **"Connection refused" error:** Make sure `nodepdb/server.py` is running first,
  in its own terminal, before starting `client.py`.
- **Port already in use:** Another process may already be using port
  6380. Close other running instances of the server and try again.
