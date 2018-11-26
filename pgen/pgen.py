import asyncio
import numpy as np
import sys
import time
import aiohttp
from datetime import datetime

__all__ = ['PGen']


class PGen:
    def __init__(self, f_gen, seconds_per_point, max_requests_per_second, url, timeout_seconds):
        self._f_gen = f_gen
        self._seconds_per_point = seconds_per_point
        self._max_requests_per_second = max_requests_per_second
        self._url = url
        self._request_timeout = timeout_seconds

        self._session = None
        self._epoch = np.int32(0)
        self._total = 0
        self._bad = 0
        self._pending_tasks = set()
        self._start_time = None
        self._epoch_total_requests = 0
        self._epoch_next_request = 0

    def _calc_timeout(self):
        deadline = self._start_time + (self._epoch - 1) * self._seconds_per_point
        if self._epoch_total_requests:
            deadline += self._seconds_per_point / self._epoch_total_requests * self._epoch_next_request
        else:
            # if no requests to send during this epoch, skip to the next one
            deadline += self._seconds_per_point
        now = time.time()
        return deadline - now

    def _print_stat(self):
        sys.stdout.write(f'\u001b[2K\r[{datetime.now()}]epoch:{self._epoch}\t'
                         f'sent:{self._epoch_next_request}/{self._epoch_total_requests}\t'
                         f'total:{self._total}\t'
                         f'bad:{self._bad}\t'
                         f'pending:{len(self._pending_tasks)}')
        sys.stdout.flush()

    def _add_tasks(self):
        while True:
            if self._epoch_next_request == self._epoch_total_requests:
                # start a new epoch
                if self._epoch != 0:
                    sys.stdout.write('\n')
                self._epoch += 1
                self._epoch_total_requests = max(0, int(self._f_gen(self._epoch) * self._max_requests_per_second * self._seconds_per_point))
                self._epoch_next_request = 0
                self._print_stat()
                if self._epoch_total_requests == 0:
                    # if no requests to send during this epoch, sleep until the next one
                    break

            if self._calc_timeout() <= 0:
                # add a new task
                self._pending_tasks.add(self._session.get(self._url))
                self._total += 1
                self._epoch_next_request += 1
            else:
                # within deadline, don't need more tasks yet
                break

    async def _send_tasks(self, timeout):
        done_tasks, self._pending_tasks = await asyncio.wait(self._pending_tasks,
                                                             timeout=timeout,
                                                             return_when=asyncio.FIRST_COMPLETED)
        for task in done_tasks:
            try:
                status = task.result().status
                if status != 200:
                    self._bad += 1
            except aiohttp.client_exceptions.ClientError:
                self._bad += 1
            except asyncio.TimeoutError:
                self._bad += 1
        self._print_stat()

    async def run(self):
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=0),
                                         timeout=aiohttp.ClientTimeout(total=self._request_timeout)) as session:
            self._session = session
            self._start_time = time.time()
            while True:
                # add tasks
                self._add_tasks()

                # double check that the timeout > 0
                timeout = self._calc_timeout()
                if timeout > 0:
                    if self._pending_tasks:
                        # send if any
                        await self._send_tasks(timeout)
                    else:
                        # otherwise sleep
                        await asyncio.sleep(timeout)
