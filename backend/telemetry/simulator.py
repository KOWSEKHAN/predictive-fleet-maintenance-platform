import time
import random
import threading
from django.utils import timezone
from fleet.models import Vehicle, Tyre
from telemetry.models import Telemetry
from predictions.models import Prediction
from accounts.models import Company, User
from predictions.ml_utils import run_prediction_for_telemetry

simulator_thread = None
simulator_running = False
lock = threading.Lock()

def generate_demo_fleet_for_company(company):
    """
    Create exactly 50 demo vehicles (with 6 tyres each) for a specific company
    if they do not already have 50+ demo vehicles.
    Uses get_or_create to be fully idempotent — safe to call multiple times.
    """
    if not company:
        return

    # Count ALL demo vehicles for this company regardless of format prefix
    demo_count = Vehicle.objects.filter(
        company=company, vehicle_number__startswith="DEMO-"
    ).count()

    if demo_count >= 50:
        print(f"Demo fleet already exists for {company.company_name} ({demo_count} vehicles). Skipping.")
        return

    needed = 50 - demo_count
    print(f"Generating {needed} demo vehicles for {company.company_name}...")

    vehicle_types = ['Semi-Trailer', 'Heavy Cargo Truck', 'Box Truck', 'Delivery Van']
    routes = [
        'Route A (Chicago - NY)',
        'Route B (LA - SF)',
        'Route C (Dallas - Houston)',
        'Route D (Miami - Atlanta)',
        'Route E (Seattle - Portland)'
    ]
    drivers = [
        'James Smith', 'John Johnson', 'Robert Williams', 'Michael Brown',
        'William Jones', 'David Miller', 'Richard Davis', 'Charles Rodriguez',
        'Joseph Wilson', 'Thomas Martinez', 'Daniel Anderson', 'Matthew Taylor'
    ]
    tyre_positions = [
        'Front Left', 'Front Right',
        'Rear Left Outer', 'Rear Left Inner',
        'Rear Right Outer', 'Rear Right Inner'
    ]

    created_count = 0
    i = 1
    while created_count < needed:
        veh_num = f"DEMO-{company.id}-{1000 + i}"
        i += 1
        # Skip if this vehicle number already exists for any company
        vehicle, created = Vehicle.objects.get_or_create(
            vehicle_number=veh_num,
            defaults={
                'company': company,
                'vehicle_type': random.choice(vehicle_types),
                'driver_name': random.choice(drivers),
                'route': random.choice(routes),
                'status': 'Healthy'
            }
        )
        if created:
            for pos in tyre_positions:
                Tyre.objects.create(
                    vehicle=vehicle,
                    tyre_position=pos,
                    installation_date=timezone.now().date()
                )
            created_count += 1

    print(f"Demo fleet generation complete for {company.company_name} ({demo_count + created_count} total demo vehicles).")


def run_simulator_loop(interval=5):
    """
    Periodically creates telemetry and prediction logs.
    IMPORTANT: Does NOT auto-generate demo fleets. Fleet generation is
    handled exclusively by StartSimulatorView per authenticated company.
    The loop only processes vehicles for companies that have explicitly
    started the simulator (i.e., companies that own demo vehicles).
    """
    global simulator_running
    print(f"Simulator thread started with interval of {interval} seconds.")

    while True:
        with lock:
            if not simulator_running:
                break

        try:
            # Only simulate vehicles belonging to companies that have demo fleets.
            # This preserves strict multi-tenant isolation.
            vehicles = list(
                Vehicle.objects.filter(vehicle_number__startswith="DEMO-")
                | Vehicle.objects.exclude(vehicle_number__startswith="DEMO-")
            )
            for vehicle in vehicles:
                tyres = vehicle.tyres.all()
                tyre_conditions = []

                for tyre in tyres:
                    psi = round(random.uniform(70, 110), 1)
                    depth = round(random.uniform(1.0, 10.0), 1)
                    temp = round(random.uniform(20.0, 60.0), 1)

                    telemetry = Telemetry.objects.create(
                        vehicle=vehicle,
                        tyre=tyre,
                        psi=psi,
                        depth=depth,
                        temperature=temp
                    )

                    run_prediction_for_telemetry(telemetry)

                    latest_pred = Prediction.objects.filter(tyre=tyre).latest('created_at')
                    tyre_conditions.append(latest_pred.condition)

                # Update vehicle status based on worst tyre condition
                if "Bad" in tyre_conditions:
                    vehicle.status = "Critical"
                elif "Average" in tyre_conditions:
                    vehicle.status = "Warning"
                else:
                    vehicle.status = "Healthy"
                vehicle.save()

        except Exception as e:
            print(f"Error in simulator loop execution: {e}")

        time.sleep(interval)

    print("Simulator thread exiting.")


def start_background_simulator(interval=5):
    """Spawns simulator loop as a daemon thread (idempotent — safe to call multiple times)."""
    global simulator_thread, simulator_running
    with lock:
        if simulator_running:
            print("Simulator is already running.")
            return False
        simulator_running = True

    simulator_thread = threading.Thread(target=run_simulator_loop, args=(interval,), daemon=True)
    simulator_thread.start()
    return True


def stop_background_simulator():
    """Stops background simulator loop."""
    global simulator_running
    with lock:
        if not simulator_running:
            return False
        simulator_running = False
    return True
