import time
from src.agents.manager_agent import create_manager_agent

def test_system():
    manager, state_manager, _ = create_manager_agent()
    
    print("\n--- Test 1: Menu Inquiry ---")
    res1 = manager.run("What burgers do you have and how much do they cost?")
    print(res1)
    
    print("\n--- Test 2: Order Creation ---")
    res2 = manager.run("I want to order 2 Burgers and a Coke. My user ID is USR-001.")
    print(res2)
    
    print("\n--- Test 3: Status Check ---")
    # Get the latest order ID from state
    orders = state_manager.get_all_orders()
    if orders:
        latest_order_id = list(orders.keys())[-1]
        res3 = manager.run(f"What is the status of order {latest_order_id}?")
        print(res3)
        
        print("\n--- Test 4: Compliance-Gated Refund (Successful Case) ---")
        # Since it's within 10 mins, it should be approved by compliance
        res4 = manager.run(f"I want a refund for order {latest_order_id} because I changed my mind. It was just placed.")
        print(res4)
    else:
        print("No orders found to test refund.")

    print("\n--- Test 5: Compliance-Gated Refund (Denial Case Simulation) ---")
    # We can't easily wait 10 mins, but we can manually set the timestamp back
    if orders:
        order_id = list(orders.keys())[0]
        state_manager.state["orders"][order_id]["timestamp"] = time.time() - 3600 # 1 hour ago
        state_manager._save_state()
        
        res5 = manager.run(f"I want a refund for order {order_id}. I placed it an hour ago.")
        print(res5)

if __name__ == "__main__":
    test_system()
