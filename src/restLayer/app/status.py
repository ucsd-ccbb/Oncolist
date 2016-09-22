import time
import math
import logging as log

class Status:
    def __init__(self, name, logger=None):
        self._time = time.time()
        self._last_period = 0
        self._period = 1
        self._name = name
        self._logger = logger if logger else log

        self._template = "{name}: {m} of {n} ({percent:0.1%}) in {elapsed} ({remaining} remaining)"

    def units(self, units):
        self._template = "{name}: {m} of {n} " + units + " ({percent:0.1%}) in {elapsed} ({remaining} remaining)"
        return self

    def template(self, template):
        self._template = template
        return self

    def period(self, period):
        self._period = period
        return self

    def n(self, n):
        self._n = n
        return self

    def fid(self, fid):
        self._fid = fid
        p = fid.tell()
        fid.seek(0, 2) # move to end
        self.n(fid.tell())
        fid.seek(p) # return to original location
        self.units('bytes')
        self._logger.debug("file is %d bytes", self._n)
        return self

    def log(self, m=None):
        dt = time.time() - self._time
        this_period = math.floor(dt / self._period)
        if this_period > self._last_period:
            self._last_period = this_period
            if m is None:
                try:
                    m = self._fid.tell()
                except AttributeError:
                    self._logger.warn("need to call status.log with a value")

            p = float(m) / float(self._n)

            msg = self._template.format(
                name=self._name,
                m=m,
                n=self._n,
                percent=p,
                elapsed=humanize(dt),
                remaining=humanize((1 - p) / p * dt) if m > 0 else "unknown"
                )

            self._logger.info(msg)
        return self

    def start(self):
        self._logger.info(("" if self._name is None else self._name + " - ") + "started")

        self._time = time.time()
        self._last_period = 0
        return self

    def stop(self):
        self._logger.info(("" if self._name is None else self._name + " - ") + "finished in %s", humanize(time.time() - self._time))
        return self


def humanize(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)

