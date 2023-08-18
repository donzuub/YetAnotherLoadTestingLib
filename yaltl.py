import requests
import time
import threading
from datetime import datetime, timedelta
import logging


class LoadTester:
    def __init__(self, url):
        """
        Initialize the LoadTester with a target URL.

        Args:
        - url (str): The target URL to test.
        """
        self.url = url
        self.response_times = []
        self.errors = 0
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
        )

    def _request(self):
        """
        Makes a single request to the target URL and logs response time.
        Errors and non-200 status codes are logged.
        """
        start_time = time.time()
        try:
            response = requests.get(self.url)
            if response.status_code != 200:
                logging.warning(f"Received {response.status_code} status code")
                self.errors += 1
        except Exception as e:
            logging.error(f"Request failed: {e}")
            self.errors += 1
        end_time = time.time()
        self.response_times.append(end_time - start_time)

    def _analyze_results(self):
        """
        Analyze the recorded response times and errors.
        Logs the average response time and total errors encountered.
        """
        avg_time = (
            sum(self.response_times) / len(self.response_times)
            if self.response_times
            else 0
        )
        logging.info(f"Average Response Time: {avg_time:.2f} seconds")
        logging.info(f"Total Errors: {self.errors}")

    def volume_testing(self, n_requests):
        """
        Simulates a volume of requests to the target URL.

        Args:
        - n_requests (int): Number of requests to make.
        """
        for _ in range(n_requests):
            self._request()
        self._analyze_results()

    def stress_testing(self, threshold_time, step=10):
        """
        Gradually increases load on the target URL until response times exceed a threshold.

        Args:
        - threshold_time (float): Time in seconds at which to stop the test if average response time exceeds.
        - step (int): Incremental number of requests to add in each iteration.
        """
        concurrent_requests = 0
        while True:
            concurrent_requests += step
            threads = []
            for _ in range(concurrent_requests):
                t = threading.Thread(target=self._request)
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            avg_response_time = (
                sum(self.response_times[-concurrent_requests:]) / concurrent_requests
            )
            if avg_response_time > threshold_time:
                break
        self._analyze_results()

    def soak_testing(self, duration_minutes):
        """
        Continuously sends requests to the target URL for an extended period of time.

        Args:
        - duration_minutes (int): Duration in minutes for which the test will run.
        """
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        while datetime.now() < end_time:
            self._request()
        self._analyze_results()

    def spike_testing(self, spikes, delay_between_spikes=1):
        """
        Simulates sudden bursts or spikes of traffic to the target URL.

        Args:
        - spikes (int): Number of spikes.
        - delay_between_spikes (int): Delay in seconds between spikes.
        """
        for _ in range(spikes):
            threads = []
            for _ in range(100):  # Let's say 100 requests simultaneously for a spike
                t = threading.Thread(target=self._request)
                t.start()
                threads.append(t)
            for t in threads:
                t.join()
            time.sleep(delay_between_spikes)
        self._analyze_results()

    def concurrency_testing(self, n_concurrent_requests):
        """
        Simulates a defined number of concurrent requests to the target URL.

        Args:
        - n_concurrent_requests (int): Number of concurrent requests to simulate.
        """
        threads = []
        for _ in range(n_concurrent_requests):
            t = threading.Thread(target=self._request)
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
        self._analyze_results()


# Example Usage
tester = LoadTester("http://example.com")
tester.stress_testing(threshold_time=2)  # threshold_time is in seconds
