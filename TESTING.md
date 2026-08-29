# Testing Instructions

## Manual Testing (do this before submission)

Run through this checklist on a **freshly cloned copy** of the repo —
not your existing working folder, which may have leftover state.

### 1. Server starts correctly
```bash
python server.py
```
- [ ] Server starts without errors
- [ ] Prints a message confirming it's listening (e.g. on port 6380)

### 2. Client connects
```bash
python client.py
```
- [ ] Prints "Connected to NoDepDB"
- [ ] Prompts for input with `>`

### 3. Core commands work
- [ ] `SET key value` returns success (e.g. `+OK`)
- [ ] `GET key` returns the value just set
- [ ] `GET` on a key that was never set returns a "not found" style response
- [ ] `DELETE key` removes the key
- [ ] `GET` on a deleted key confirms it's gone

### 4. Invalid input handling
- [ ] Typing an unknown command doesn't crash the server or client
- [ ] Empty input (just pressing Enter) doesn't crash anything
- [ ] `EXIT` disconnects cleanly, no error printed

### 5. Multiple clients (if server supports concurrency)
- [ ] Open two separate terminals, run `client.py` in each
- [ ] Both can `SET`/`GET` independently without interfering with each other

### 6. Persistence (only if storage engine/WAL is merged into `main`)
- [ ] `SET` a key
- [ ] Stop the server (Ctrl+C)
- [ ] Restart the server
- [ ] `GET` the same key — confirm the value is still there

> If the storage engine PR is not yet merged into `main`, skip this
> section and note it as a known limitation in the README instead of
> claiming persistence works.

## Automated Tests (if present)

If the team has written `unittest`-based tests, run them with:

```bash
python -m unittest discover
```

- [ ] All tests pass with no failures or errors
- [ ] If any test file exists but isn't run, note it here and confirm
      with the author whether it's expected to pass

## Fresh-Clone Test (do this last, right before submitting)

- [ ] `git clone` the repo into a brand-new empty folder
- [ ] Follow only the steps in `INSTALLATION.md` — no manual fixes
- [ ] Confirm it runs end-to-end exactly as documented
