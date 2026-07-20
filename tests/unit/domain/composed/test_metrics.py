from consumer.domain.composed.metrics import Metrics


class TestMetrics:
    def test_initial_state(self) -> None:
        m = Metrics()
        assert m.total_commands == 0
        assert m.connected_players == 0
        assert m.votes_processed == 0
        assert m.frames_executed == 0

    def test_increment_commands(self) -> None:
        m = Metrics()
        m.increment_commands()
        m.increment_commands()
        assert m.total_commands == 2

    def test_increment_connected_players(self) -> None:
        m = Metrics()
        m.increment_connected_players()
        m.increment_connected_players()
        assert m.connected_players == 2

    def test_decrement_connected_players(self) -> None:
        m = Metrics()
        m.increment_connected_players()
        m.increment_connected_players()
        m.decrement_connected_players()
        assert m.connected_players == 1

    def test_increment_votes_processed(self) -> None:
        m = Metrics()
        m.increment_votes_processed()
        assert m.votes_processed == 1

    def test_increment_frames_executed(self) -> None:
        m = Metrics()
        m.increment_frames_executed()
        m.increment_frames_executed()
        m.increment_frames_executed()
        assert m.frames_executed == 3
