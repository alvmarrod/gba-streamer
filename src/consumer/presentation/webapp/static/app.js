(function () {
    "use strict";

    const API_BASE = "";
    const PLAYER_ID = crypto.randomUUID();

    let peerConnection = null;
    let sessionRunning = false;

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
                setStatus("Disconnected", false);
                overlay.classList.remove("hidden");
                peerConnection = null;
                setTimeout(connectWebRTC, 3000);
            }
        };

        const transceiver = peerConnection.addTransceiver("video", { direction: "recvonly" });

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
            playerCount.textContent = data.connected_players + " players";

            sessionRunning = ["RUNNING", "PAUSED", "STARTING"].includes(data.session_state);
            $("#btn-start").disabled = sessionRunning;
            $("#btn-stop").disabled = !sessionRunning;
            $("#btn-pause").disabled = data.session_state !== "RUNNING";
            $("#btn-resume").classList.toggle("hidden", data.session_state !== "PAUSED");
            $("#btn-pause").classList.toggle("hidden", data.session_state === "PAUSED");
        } catch {
            sessionState.textContent = "Offline";
        }
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
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", init);
    } else {
        init();
    }
})();
