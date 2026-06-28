from langgraph.types import Interrupt

def get_interrupt_decisions(interrupt: Interrupt) -> list[dict]:
    full_res = []
    for request in interrupt.value["action_requests"]:
        print(request["description"])

        response = ""
        while response != "y" and response != "n":
            print("Confirm ? [y/n]")
            response = input().strip().lower()
        
        if response == "y":
            full_res.append({"type": "approve"})
        else:
           full_res.append({"type": "reject", "message": "User rejected the action."})
    return full_res
