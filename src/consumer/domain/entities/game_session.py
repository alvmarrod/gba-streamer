from __future__ import annotations

import asyncio
from datetime import datetime

from consumer.domain.composed.input_history import InputHistory
from consumer.domain.composed.input_queue import InputQueue
from consumer.domain.composed.metrics import Metrics
from consumer.domain.composed.save_manager import SaveManager
from consumer.domain.composed.session_state_machine import SessionStateMachine
from consumer.domain.composed.vote_round import VoteRound
from consumer.domain.entities.player import Player
from consumer.domain.composed.player_manager import PlayerManager
from consumer.domain.enums import ControlMode, SessionState
from consumer.domain.exceptions import (
    PlayerNotConnectedException,
    SessionNotRunningException,
)
from consumer.domain.services.session_validator import SessionValidator
from consumer.domain.value_objects import (
    GameInput,
    PlayerId,
    SaveMetadata,
    SessionConfiguration,
    SessionId,
)


class GameSession:
    def __init__(
        self,
        session_id: SessionId,
        configuration: SessionConfiguration,
    ) -> None:
        self._session_id = session_id
        self._configuration = configuration
        self._players = PlayerManager()
        self._input_queue = InputQueue()
        self._input_history = InputHistory()
        self._metrics = Metrics()
        self._save_manager = SaveManager()
        self._state_machine = SessionStateMachine()
        self._current_vote: VoteRound | None = None
        self._lock = asyncio.Lock()

    @property
    def session_id(self) -> SessionId:
        return self._session_id

    def _validate(self) -> None:
        SessionValidator.validate(self)

    @property
    def configuration(self) -> SessionConfiguration:
        return self._configuration

    @property
    def current_state(self) -> SessionState:
        return self._state_machine.current_state

    @property
    def metrics(self) -> Metrics:
        return self._metrics

    @property
    def input_queue(self) -> InputQueue:
        return self._input_queue

    @property
    def input_history(self) -> InputHistory:
        return self._input_history

    @property
    def save_manager(self) -> SaveManager:
        return self._save_manager

    @property
    def current_vote(self) -> VoteRound | None:
        return self._current_vote

    @property
    def players(self) -> PlayerManager:
        return self._players

    async def start(self) -> None:
        async with self._lock:
            self._state_machine.transition_to(SessionState.RUNNING)
            self._validate()

    async def stop(self) -> None:
        async with self._lock:
            self._state_machine.transition_to(SessionState.STOPPED)
            self._validate()

    async def pause(self) -> None:
        async with self._lock:
            self._state_machine.transition_to(SessionState.PAUSED)
            self._validate()

    async def resume(self) -> None:
        async with self._lock:
            self._state_machine.transition_to(SessionState.RUNNING)
            self._validate()

    async def connect_player(self, player: Player) -> None:
        async with self._lock:
            is_new = self._players.get(player.player_id) is None
            self._players.connect(player)
            if is_new:
                self._metrics.increment_connected_players()
            self._validate()

    async def disconnect_player(self, player_id: PlayerId) -> None:
        async with self._lock:
            player = self._players.get(player_id)
            if player is None:
                raise PlayerNotConnectedException(
                    f"Player {player_id.value} not connected"
                )
            self._players.disconnect(player_id)
            self._metrics.decrement_connected_players()
            self._validate()

    async def configure(self, configuration: SessionConfiguration) -> None:
        async with self._lock:
            self._configuration = configuration
            if configuration.control_mode == ControlMode.FIFO:
                self._current_vote = None

    async def change_control_mode(self, new_mode: ControlMode) -> None:
        async with self._lock:
            if new_mode == self._configuration.control_mode:
                return
            self._configuration = SessionConfiguration(
                control_mode=new_mode,
                voting_interval=self._configuration.voting_interval,
                autosave_interval=self._configuration.autosave_interval,
            )
            if new_mode == ControlMode.FIFO:
                self._current_vote = None
            self._validate()

    async def submit_input(self, game_input: GameInput) -> None:
        async with self._lock:
            if self._state_machine.current_state != SessionState.RUNNING:
                raise SessionNotRunningException(
                    f"Cannot submit input in state {self._state_machine.current_state.value}"
                )
            self._metrics.increment_commands()
            self._input_history.record(game_input)
            if self._configuration.control_mode == ControlMode.FIFO:
                self._input_queue.enqueue(game_input)
            else:
                if self._current_vote is None:
                    self._current_vote = VoteRound()
                self._current_vote.collect_vote(game_input.player_id, game_input)

    async def create_snapshot(self) -> None:
        async with self._lock:
            self._save_manager.create_snapshot()

    async def restore_snapshot(self) -> None:
        async with self._lock:
            self._save_manager.restore_snapshot()

    def take_vote_round(self) -> VoteRound | None:
        vote = self._current_vote
        self._current_vote = None
        return vote

    async def resolve_vote(self) -> None:
        async with self._lock:
            self._metrics.increment_votes_processed()

    async def record_tick(self) -> None:
        async with self._lock:
            self._metrics.increment_frames_executed()

    async def record_save(self, timestamp: datetime) -> SaveMetadata:
        async with self._lock:
            self._save_manager.update_metadata(timestamp)
            assert self._save_manager.metadata is not None
            return self._save_manager.metadata

    async def restore_metadata(self, last_save_at: datetime, save_count: int) -> None:
        async with self._lock:
            self._save_manager.restore_metadata(last_save_at, save_count)
