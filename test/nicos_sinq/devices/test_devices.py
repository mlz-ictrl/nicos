import time

import pytest

from nicos.core import status

session_setup = 'sinq_devices'


class TestReadableToChannel:

    @pytest.fixture(autouse=True)
    def initialize_devices(self, session):
        self.session = session
        self.dev_preset = session.getDevice('dev_preset')
        self.device = session.getDevice('dev')
        yield 'resource'
        self.dev_preset._preselection_reached = True
        self.dev_preset._history = []
        self.dev_preset.window = 5

    def test_status_done_if_reads_same_as_preselection(self):
        preset = 10
        self.dev_preset.preselection = preset
        self.dev_preset._preselection_reached = False
        for _ in range(10):
            self.dev_preset._history.append((0, preset))
        assert self.dev_preset.doStatus() == (status.OK, 'Done')

    def test_status_done_if_reads_are_within_precision(self):
        preset = 10
        self.dev_preset.preselection = preset
        self.dev_preset._preselection_reached = False
        eps = self.dev_preset.precision / 10
        for n in range(-10, 10):
            self.dev_preset._history.append((0, preset + n * eps))
        assert self.dev_preset.doStatus() == (status.OK, 'Done')

    def test_status_busy_if_reads_are_outside_precision(self):
        preset = 10
        self.dev_preset.preselection = preset
        self.dev_preset._preselection_reached = False
        eps = self.dev_preset.precision
        for n in range(-10, 10):
            self.dev_preset._history.append((0, preset + n * eps))
        assert self.dev_preset.doStatus() == (
        status.BUSY, 'target not reached')

    def test_all_cache_entries_in_window_are_kept_in_history(self):
        now = time.time()
        howmany_reads = 100

        self.dev_preset.window = 100
        for t in range(-howmany_reads, 0):
            self.dev_preset._cacheCB('', 10, now + .1 * t)

        assert len(
            [now - t for t, v in self.dev_preset._history]) == howmany_reads

    def test_smaller_time_window_reduces_entries(self):
        now = time.time()
        howmany_reads = 100

        self.dev_preset.window = 5
        for t in range(-howmany_reads, 0):
            self.dev_preset._cacheCB('', 10, now + t)

        len_5 = len([now - t for t, v in self.dev_preset._history])
        self.dev_preset._history = []

        self.dev_preset.window = 10
        for t in range(-howmany_reads, 0):
            self.dev_preset._cacheCB('', 10, now + t)

        len_10 = len([now - t for t, v in self.dev_preset._history])

        assert len_5 < howmany_reads
        assert len_10 < howmany_reads
        assert len_5 < len_10

    def test_set_preset_sets_preselection_reached_to_false(self):
        preset = 5
        self.dev_preset.setChannelPreset('dev_preset', preset)
        assert self.dev_preset.preselection == preset
        assert not self.dev_preset._preselection_reached
