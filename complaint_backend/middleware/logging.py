import time
from django.db import connection
import logging

logger = logging.getLogger("django.db")  # Make sure Heroku logs capture this

class QueryLoggingMiddleware:
    """Logs all SQL queries and total time per request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        total_time = time.time() - start_time

        queries = connection.queries
        if queries:
            logger.info(f"==== {len(queries)} queries in {total_time:.2f}s for {request.path} ====")
            for q in queries:
                sql = q.get("sql")
                q_time = q.get("time")
                logger.info(f"[{q_time}s] {sql}")
        else:
            logger.info(f"No queries executed for {request.path} in {total_time:.2f}s")

        return response
