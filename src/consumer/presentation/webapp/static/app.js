(function () {
    "use strict";

    const API_BASE = "";
    const PLAYER_ID = sessionStorage.getItem("player_id") || crypto.randomUUID();
    sessionStorage.setItem("player_id", PLAYER_ID);

    let peerConnection = null;
    let sessionRunning = false;
    let prevFrames = 0;
    let prevTime = Date.now();
    let dataChannel = null;
    let pingInterval = null;
    let smoothedLatency = 0;

    const $ = (sel) => document.querySelector(sel);
    const video = $("#video");
    const statusEl = $("#connection-status");
    const overlay = $("#video-overlay");
    const sessionState = $("#session-state");
    const playerCount = $("#player-count");

    function setStatus(text, connected) {
        statusEl.textContent = text;
        statusEl.className = "status " + (connected ? "connected" : "disconnected");
    }

    async function api(method, path, body) {
        const opts = { method, headers: { "Content-Type": "application/json" } };
        if (body) opts.body = JSON.stringify(body);
        const resp = await fetch(API_BASE + path, opts);
        return { status: resp.status, data: await resp.json() };
    }

    async function connectWebRTC() {
        setStatus("Connecting...", false);
        overlay.classList.remove("hidden");

        let iceServers = [];
        try {
            const resp = await fetch("/api/ice-servers");
            iceServers = await resp.json();
        } catch (e) {
            // fall back to empty — no TURN relay
        }

        peerConnection = new RTCPeerConnection({
            iceServers: iceServers,
            iceTransportPolicy: "relay",
        });
        window._pc = peerConnection;

        peerConnection.ontrack = (event) => {
            if (event.streams && event.streams[0]) {
                video.srcObject = event.streams[0];
            } else {
                const stream = new MediaStream([event.track]);
                video.srcObject = stream;
            }
            overlay.classList.add("hidden");
            setStatus("Connected", true);
        };

        peerConnection.onconnectionstatechange = () => {
            const state = peerConnection.connectionState;
            if (state === "failed" || state === "disconnected" || state === "closed") {
                stopPing();
                api("POST", "/api/player/disconnect", { player_id: PLAYER_ID }).catch(() => {});
                setStatus("Disconnected", false);
                overlay.classList.remove("hidden");
                peerConnection = null;
                setTimeout(connectWebRTC, 3000);
            }
        };

        const transceiver = peerConnection.addTransceiver("video", { direction: "recvonly" });

        startPing();

        const offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);

        try {
            const { data } = await api("POST", "/api/webrtc/offer", {
                sdp: peerConnection.localDescription.sdp,
                type: peerConnection.localDescription.type,
            });
            await peerConnection.setRemoteDescription(
                new RTCSessionDescription({ sdp: data.sdp, type: data.type })
            );
        } catch (err) {
            console.error("Signalling failed:", err);
            peerConnection.close();
            peerConnection = null;
            setStatus("Signalling failed", false);
            setTimeout(connectWebRTC, 5000);
        }
    }

    async function sendInput(button) {
        try {
            await api("POST", "/api/input", {
                player_id: PLAYER_ID,
                button: button,
            });
        } catch (err) {
            console.error("Input failed:", err);
        }
    }

    function setupGamepad() {
        document.querySelectorAll("[data-button]").forEach((btn) => {
            const buttonName = btn.dataset.button;

            const press = (e) => {
                e.preventDefault();
                btn.classList.add("pressed");
                sendInput(buttonName);
            };

            const release = (e) => {
                e.preventDefault();
                btn.classList.remove("pressed");
            };

            btn.addEventListener("mousedown", press);
            btn.addEventListener("mouseup", release);
            btn.addEventListener("mouseleave", release);
            btn.addEventListener("touchstart", press, { passive: false });
            btn.addEventListener("touchend", release, { passive: false });
            btn.addEventListener("touchcancel", release, { passive: false });
        });
    }

    async function updateSessionInfo() {
        try {
            const { data } = await api("GET", "/api/session");
            sessionState.textContent = data.session_state;
            const count = data.connected_players;
            playerCount.textContent = count + " players";

            const others = count > 1 ? " + " + (count - 1) + " others" : "";
            const playersEl = $("#players-display");
            if (playersEl) playersEl.textContent = "Users Connected: You" + others;

            sessionRunning = ["RUNNING", "PAUSED", "STARTING"].includes(data.session_state);
            $("#btn-start").disabled = sessionRunning;
            $("#btn-stop").disabled = !sessionRunning;
            $("#btn-pause").disabled = data.session_state !== "RUNNING";
            $("#btn-resume").classList.toggle("hidden", data.session_state !== "PAUSED");
            $("#btn-pause").classList.toggle("hidden", data.session_state === "PAUSED");
        } catch {
            sessionState.textContent = "Offline";
        }

        try {
            const { data: status } = await api("GET", "/api/status");
            const now = Date.now();
            const frameDelta = status.frames_executed - prevFrames;
            const timeDelta = (now - prevTime) / 1000;
            if (timeDelta > 0 && prevFrames > 0) {
                const fps = Math.round(frameDelta / timeDelta);
                const fpsEl = $("#fps-display");
                if (fpsEl) fpsEl.textContent = fps + " FPS";
            }
            prevFrames = status.frames_executed;
            prevTime = now;
            if (status.recent_actions && status.recent_actions.length > 0) {
                const actionsEl = $("#actions-display");
                if (actionsEl) {
                    const parts = ["Last Actions:"];
                    const reversed = [...status.recent_actions].reverse();
                    for (let i = 0; i < reversed.length; i++) {
                        const a = reversed[i];
                        parts.push(a.button + " (" + a.display_name + ")");
                    }
                    actionsEl.textContent = parts.join("\n");
                }
            }
        } catch { }
    }

    async function connectPlayer() {
        try {
            await api("POST", "/api/player/connect", {
                player_id: PLAYER_ID,
                display_name: "Player",
            });
        } catch (err) {
            console.error("Connect player failed:", err);
        }
    }

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

    function setupSessionActions() {
        $("#btn-start").addEventListener("click", async () => {
            await api("POST", "/api/session/start", {
                control_mode: "fifo",
                voting_interval: 30,
                autosave_interval: 300,
            });
            await connectPlayer();
            updateSessionInfo();
        });

        $("#btn-stop").addEventListener("click", async () => {
            await api("POST", "/api/session/stop");
            updateSessionInfo();
        });

        $("#btn-pause").addEventListener("click", async () => {
            await api("POST", "/api/session/pause");
            updateSessionInfo();
        });

        $("#btn-resume").addEventListener("click", async () => {
            await api("POST", "/api/session/resume");
            updateSessionInfo();
        });
    }

    function init() {
        setupGamepad();
        setupSessionActions();
        updateSessionInfo();
        setInterval(updateSessionInfo, 5000);
        connectWebRTC();
        connectPlayer();

        window.addEventListener("beforeunload", () => {
            navigator.sendBeacon(
                API_BASE + "/api/player/disconnect",
                JSON.stringify({ player_id: PLAYER_ID })
            );
        });
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
