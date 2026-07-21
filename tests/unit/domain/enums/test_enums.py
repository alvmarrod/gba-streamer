from consumer.domain.enums import Button, ControlMode, PlayerState, SessionState


class TestButton:
    def test_member_count(self) -> None:
        assert len(Button) == 8

    def test_all_members(self) -> None:
        expected = {"UP", "DOWN", "LEFT", "RIGHT", "A", "B", "START", "SELECT"}
        assert {m.name for m in Button} == expected

    def test_members_are_unique(self) -> None:
        values = [b.value for b in Button]
        assert len(values) == len(set(values))


class TestControlMode:
    def test_member_count(self) -> None:
        assert len(ControlMode) == 2

    def test_all_members(self) -> None:
        expected = {"FIFO", "VOTING"}
        assert {m.name for m in ControlMode} == expected

    def test_members_are_unique(self) -> None:
        values = [c.value for c in ControlMode]
        assert len(values) == len(set(values))


class TestSessionState:
    def test_member_count(self) -> None:
        assert len(SessionState) == 4

    def test_all_members(self) -> None:
        expected = {"STARTING", "RUNNING", "PAUSED", "STOPPED"}
        assert {m.name for m in SessionState} == expected

    def test_members_are_unique(self) -> None:
        values = [s.value for s in SessionState]
        assert len(values) == len(set(values))


class TestPlayerState:
    def test_member_count(self) -> None:
        assert len(PlayerState) == 2

    def test_all_members(self) -> None:
        expected = {"CONNECTED", "DISCONNECTED"}
        assert {m.name for m in PlayerState} == expected

    def test_members_are_unique(self) -> None:
        values = [p.value for p in PlayerState]
        assert len(values) == len(set(values))
