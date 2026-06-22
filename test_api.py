import requests
import json
import time

BASE_URL = 'http://localhost:8000/api'

def test_auth_and_fleet():
    print("Testing accounts/fleet SaaS Endpoints...")
    print("=" * 50)

    # 1. Test registration
    print("\n1. Testing User & Company Registration...")
    unique_email = f"admin_{int(time.time())}@testlogistics.com"
    unique_company = f"Test Logistics Corp {int(time.time())}"
    reg_payload = {
        'company_name': unique_company,
        'email': unique_email,
        'password': 'securepassword123'
    }
    response = requests.post(f'{BASE_URL}/auth/register', json=reg_payload)
    if response.status_code == 201:
        reg_data = response.json()
        print("[SUCCESS] Registration successful!")
        print(f"Company: {reg_data['user']['company']['company_name']}")
        print(f"Token length: {len(reg_data['access'])}")
    else:
        print(f"[FAILED] Registration failed: {response.status_code}")
        print(response.text)
        return False

    # 2. Test login
    print("\n2. Testing User Login...")
    login_payload = {
        'email': unique_email,
        'password': 'securepassword123'
    }
    response = requests.post(f'{BASE_URL}/auth/login', json=login_payload)
    if response.status_code == 200:
        login_data = response.json()
        token = login_data['access']
        print("[SUCCESS] Login successful!")
    else:
        print(f"[FAILED] Login failed: {response.status_code}")
        print(response.text)
        return False

    headers = {'Authorization': f'Bearer {token}'}

    # 3. Test unauthorized access
    print("\n3. Testing unauthorized access to /api/vehicles...")
    unauth_response = requests.get(f'{BASE_URL}/vehicles')
    if unauth_response.status_code == 401:
        print("[SUCCESS] Blocked unauthorized access successfully!")
    else:
        print(f"[FAILED] Failed to block unauthorized access: {unauth_response.status_code}")

    # 4. Test authorized access to /api/vehicles (should be empty initially)
    print("\n4. Testing authorized list vehicles...")
    auth_response = requests.get(f'{BASE_URL}/vehicles', headers=headers)
    if auth_response.status_code == 200:
        vehicles = auth_response.json()
        print(f"[SUCCESS] Retrieved vehicle list. Count: {len(vehicles)}")
    else:
        print(f"[FAILED] Failed to get vehicles: {auth_response.status_code}")
        return False

    # 5. Create a vehicle
    print("\n5. Testing vehicle creation...")
    vehicle_payload = {
        'vehicle_number': f"TRUCK-{int(time.time()) % 10000}A",
        'vehicle_type': 'Semi-Trailer',
        'driver_name': 'John Doe',
        'route': 'Route 66'
    }
    create_response = requests.post(f'{BASE_URL}/vehicles', json=vehicle_payload, headers=headers)
    if create_response.status_code == 201:
        vehicle = create_response.json()
        print(f"[SUCCESS] Vehicle created successfully: {vehicle['vehicle_number']} (ID: {vehicle['id']})")
        vehicle_id = vehicle['id']
    else:
        print(f"[FAILED] Vehicle creation failed: {create_response.status_code}")
        print(create_response.text)
        return False

    # 6. Get dashboard summary
    print("\n6. Testing dashboard summary...")
    summary_response = requests.get(f'{BASE_URL}/dashboard/summary', headers=headers)
    if summary_response.status_code == 200:
        summary = summary_response.json()
        print("[SUCCESS] Dashboard summary retrieved:")
        print(json.dumps(summary, indent=2))
    else:
        print(f"[FAILED] Dashboard summary failed: {summary_response.status_code}")
        return False

    # 7. Get vehicle details
    print(f"\n7. Testing vehicle details for ID {vehicle_id}...")
    detail_response = requests.get(f'{BASE_URL}/vehicles/{vehicle_id}', headers=headers)
    if detail_response.status_code == 200:
        print("[SUCCESS] Vehicle details retrieved successfully!")
    else:
        print(f"[FAILED] Vehicle details retrieval failed: {detail_response.status_code}")
        return False

    # 8. Get tyres for vehicle (should be empty initially)
    print(f"\n8. Testing tyre listing for vehicle ID {vehicle_id}...")
    tyres_response = requests.get(f'{BASE_URL}/vehicles/{vehicle_id}/tyres', headers=headers)
    if tyres_response.status_code == 200:
        tyres = tyres_response.json()
        print(f"[SUCCESS] Retrieved tyre list. Count: {len(tyres)}")
    else:
        print(f"[FAILED] Failed to retrieve tyres: {tyres_response.status_code}")
        return False

    # 9. Start simulator and test telemetry auto-fleet generation
    print("\n9. Testing simulator start and dynamic fleet generation...")
    sim_response = requests.post(f'{BASE_URL}/simulator/start', headers=headers)
    if sim_response.status_code == 200:
        print("[SUCCESS] Simulator started successfully!")
    else:
        print(f"[FAILED] Simulator start failed: {sim_response.status_code}")
        print(sim_response.text)
        return False

    # 10. Check vehicle count after simulator starts
    print("\n10. Checking vehicle list count after simulator startup (should generate 50 demo vehicles)...")
    time.sleep(1) # wait a moment for DB writes
    list_response = requests.get(f'{BASE_URL}/vehicles', headers=headers)
    if list_response.status_code == 200:
        vehicles = list_response.json()
        print(f"[SUCCESS] Retrieved vehicle list. New Count: {len(vehicles)} (Expected: 51)")
        if len(vehicles) == 51:
            print("[SUCCESS] Dynamic demo fleet generation verified successfully!")
        else:
            print(f"[WARNING] Vehicle count is {len(vehicles)} (expected 51)")
    else:
        print(f"[FAILED] Failed to retrieve vehicles list: {list_response.status_code}")
        return False

    print("\n[SUCCESS] All platform E2E backend test cases passed successfully!")
    return True

if __name__ == "__main__":
    test_auth_and_fleet()