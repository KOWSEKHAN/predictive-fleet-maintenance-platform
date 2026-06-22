from django.core.management.base import BaseCommand
from telemetry.simulator import run_simulator_loop

class Command(BaseCommand):
    help = 'Continuously generate telemetry and prediction records for the demo fleet'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS("Starting fleet telemetry simulator... (Press Ctrl+C to exit)"))
        try:
            run_simulator_loop(interval=5)
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS("Simulator successfully terminated."))
