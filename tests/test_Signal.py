import Signal
import copy

class SignalReceiver:
    def __init__(self) -> None:
        self._emit_count = 0

    def getEmitCount(self) -> int:
        return self._emit_count

    def slot(self, *args, **kwargs):
        self._emit_count += 1


def test_signal():
    # Arrange
    test = SignalReceiver()
    signal = Signal.Signal()
    signal.connect(test.slot)

    # Act
    signal.emit()

    # Assert
    assert test.getEmitCount() == 1


def test_linkedSignal():
    # Arrange
    test = SignalReceiver()
    signal_1 = Signal.Signal()
    signal_2 = Signal.Signal()
    signal_1.connect(signal_2)
    signal_2.connect(test.slot)

    # Act
    signal_1.emit()

    assert test.getEmitCount() == 1


def test_disconnect():
    # Arrange
    test = SignalReceiver()
    signal = Signal.Signal()
    signal.connect(test.slot)
    signal.disconnect(test.slot)
    # Act
    signal.emit()

    # Assert
    assert test.getEmitCount() == 0


def test_disconnectLinkedSignal():
    # Arrange
    test = SignalReceiver()
    signal_1 = Signal.Signal()
    signal_2 = Signal.Signal()
    signal_1.connect(signal_2)
    signal_2.connect(test.slot)
    # Break the chain
    signal_1.disconnect(signal_2)

    # Act
    signal_1.emit()

    assert test.getEmitCount() == 0


def test_disconnectAll():
    test = SignalReceiver()
    signal = Signal.Signal()
    signal.connect(test.slot)

    # Act
    signal.disconnectAll()
    signal.emit()

    # Assert
    assert test.getEmitCount() == 0


def test_connectSelf():
    # Arrange
    signal = Signal.Signal()
    signal.connect(signal)
    # Act & Assert
    signal.emit()  # If they are connected, this crashes with a max recursion depth error


