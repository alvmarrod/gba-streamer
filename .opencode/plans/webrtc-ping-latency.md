# Plan: Add Ping/Latency Measurement via WebRTC Data Channel

## Goal
Display per-user RTT (round-trip time) next to FPS in the webapp info block, measured via WebRTC data channel on the same ICE connection as the video stream.

## Approach
- Client creates a `DataChannel("ping")` on the same `RTCPeerConnection`
- Client sends `Date.now()` every 2s
- Server echoes the message back
- Client computes `RTT = Date.now() - sent_timestamp`
- Display smoothed (EMA) value as a green badge next to FPS

## Changes (3 files)

### 1. `src/consumer/presentation/api/signalling.py` — Server echo handler
Add a `datachannel` event handler on the `RTCPeerConnection` that echoes back any received message.

**After** the `@pc.on("icegatheringstatechange")` block (line 49-50) and **before** `publisher.add_peer(pc)` (line 52), insert:

```python
    @pc.on("datachannel")
    def _on_datachannel(channel: object) -> None:  # type: ignore[no-untyped-def]
        _log.info("datachannel_created label=%s", channel.label)  # type: ignore[union-attr]

        @channel.on("message")  # type: ignore[union-attr]
        def _on_message(message: str) -> None:
            channel.send(message)  # type: ignore[union-attr]
```

### 2. `src/consumer/presentation/webapp/index.html` — Latency badge div
In `#info-block`, **after** the FPS badge (`<div id="fps-display" class="info-badge">-- FPS</div>` on line 41), insert:

```html
                        <div id="latency-display" class="info-badge">-- ms</div>
```

### 3. `src/consumer/presentation/webapp/static/app.js` — Client-side ping logic

**A.** Add new state variables after line 11 (`const actionHistory = [];`):

```js
    let dataChannel = null;
    let pingInterval = null;
    let smoothedLatency = 0;
```

**B.** Add `startPing()` and `stopPing()` functions — insert after the `connectPlayer()` function definition (line 183, before `setupSessionActions`):

```js
    function startPing() {
        dataChannel = peerConnection.createDataChannel("ping");

        dataChannel.onopen = () => {
            pingInterval = setInterval(() => {
                if (dataChannel && dataChannel.readyState === "open") {
                    dataChannel.send(String(Date.now()));
                }
            }, 2000);
        };

        dataChannel.onmessage = (event) => {
            const sent = parseInt(event.data, 10);
            if (isNaN(sent)) return;
            const rtt = Date.now() - sent;
            smoothedLatency = smoothedLatency
                ? Math.round(0.8 * smoothedLatency + 0.2 * rtt)
                : rtt;
            const el = $("#latency-display");
            if (el) el.textContent = smoothedLatency + " ms";
        };
    }

    function stopPing() {
        if (pingInterval) {
            clearInterval(pingInterval);
            pingInterval = null;
        }
        dataChannel = null;
    }
```

**C.** Call `startPing()` in `connectWebRTC()` — insert after `peerConnection.addTransceiver(...)` (line 71) and before `const offer = await peerConnection.createOffer()` (line 73):

```js
        startPing();
```

**D.** Clean up ping on disconnect — in the `onconnectionstatechange` handler (line 61), add cleanup before `setStatus("Disconnected", false)`:

```js
        peerConnection.onconnectionstatechange = () => {
            const state = peerConnection.connectionState;
            if (state === "failed" || state === "disconnected" || state === "closed") {
                stopPing();
                setStatus("Disconnected", false);
```

### No CSS changes needed
`.info-badge` already provides the green badge style used for FPS.

## Verification
- Run existing tests: `uv run pytest tests/ -q` — no regressions expected (only JS/HTML changed)
- mypy: `uv run mypy src/ tests/` — type ignores on aiortc types should satisfy
- Manual test: connect to webapp, verify `-- ms` updates to a latency value after WebRTC connects
