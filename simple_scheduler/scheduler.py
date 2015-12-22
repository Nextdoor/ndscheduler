"""Run the scheduler process."""

from ndscheduler.server import server


if __name__ == "__main__":
    server.SchedulerServer.run()
