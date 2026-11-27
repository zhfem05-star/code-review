    def get_backoff_time(self) -> float:
        """Formula for computing the current backoff

        :rtype: float
        """
        # We want to consider only the last consecutive errors sequence (Ignore redirects).
        consecutive_errors_len = len(
            list(
                takewhile(lambda x: x.redirect_location is None, reversed(self.history))
            )
        )
        if consecutive_errors_len <= 1:
            return 0

        backoff_value = self.backoff_factor * (2 ** (consecutive_errors_len - 1))
        if self.backoff_jitter != 0.0:
            backoff_value += random.random() * self.backoff_jitter
        return float(max(0, min(self.backoff_max, backoff_value)))

    # ... parse_retry_after / get_retry_after 생략 ...

    def sleep_for_retry(self, response: BaseHTTPResponse) -> bool:
        retry_after = self.get_retry_after(response)
        if retry_after:
            time.sleep(retry_after)
            return True

        return False

    def _sleep_backoff(self) -> None:
        backoff = self.get_backoff_time()
        if backoff <= 0:
            return
        time.sleep(backoff)

    def sleep(self, response: BaseHTTPResponse | None = None) -> None:
        """Sleep between retry attempts.

        This method will respect a server's ``Retry-After`` response header
        and sleep the duration of the time requested. If that is not present, it
        will use an exponential backoff. By default, the backoff factor is 0 and
        this method will return immediately.
        """

        if self.respect_retry_after_header and response:
            slept = self.sleep_for_retry(response)
            if slept:
                return

        self._sleep_backoff()

    def _is_connection_error(self, err: Exception) -> bool:
        """Errors when we're fairly sure that the server did not receive the
        request, so it should be safe to retry.
        """
        if isinstance(err, ProxyError):
            err = err.original_error
        return isinstance(err, ConnectTimeoutError)

    def _is_read_error(self, err: Exception) -> bool:
        """Errors that occur after the request has been started, so we should
        assume that the server began processing it.
        """
        return isinstance(err, (ReadTimeoutError, ProtocolError))
