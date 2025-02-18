from langchain_core.tools import tool
from typing import List, Dict
from vector_store import FlowerShopVectorStore
import json

vector_store = FlowerShopVectorStore()

customers_database = [
    {
        "name": "Claudio Pacini",
        "dob": "1996-04-16",
        "customer_id": "CUST001",
        "phone_number": "3272809656",
    },
]

orders_database = []

with open("inventory.json", "r") as f:
    inventory_database = json.load(f)

data_protection_checks = []


@tool
def data_protection_check(name: str) -> Dict:
    """
    Perform a data protection check against a customer to retrieve customer details.

    Args:
        name (str): Customer first and last name

    Returns:
        Dict: Customer details
    """
    data_protection_checks.append(
        {
            "name": name,
        }
    )
    for customer in customers_database:
        if customer["name"].lower() == name.lower():
            return f"DPA check passed - Retrieved customer details:\n{customer}"

    return "DPA check failed, no customer with these details found"


@tool
def create_new_customer(
    first_name: str,
    surname: str,
    year_of_birth: int,
    month_of_birth: int,
    day_of_birth: int,
    phone_number: str,
) -> str:
    """
    Creates a customer profile, so that they can place orders.

    Args:
        first_name (str): Customers first name
        surname (str): Customers surname
        year_of_birth (int): Year customer was born
        month_of_birth (int): Month customer was born
        day_of_birth (int): Day customer was born
        phone_number (str): Customer's phone number

    Returns:
        str: Confirmation that the profile has been created or any issues with the inputs
    """
    customer_id = len(customers_database) + 1
    customers_database.append(
        {
            "name": first_name + " " + surname,
            "dob": f"{year_of_birth}-{month_of_birth:02}-{day_of_birth:02}",
            "phone_number": phone_number,
            "customer_id": f"CUST{customer_id}",
        }
    )
    return f"Customer registered, with customer_id {f'CUST{customer_id}'}"


@tool
def query_knowledge_base(query: str) -> List[Dict[str, str]]:
    """
    Looks up information in a knowledge base to help with answering customer questions and getting information on business processes.

    Args:
        query (str): Question to ask the knowledge base

    Return:
        List[Dict[str, str]]: Potentially relevant question and answer pairs from the knowledge base
    """
    return vector_store.query_faqs(query=query)


@tool
def retrieve_existing_customer_orders(customer_id: str) -> List[Dict]:
    """
    Retrieves the orders associated with the customer, including their status, items and ids

    Args:
        customer_id (str): Customer unique id associated with the order

    Returns:
        List[Dict]: All the orders associated with the customer_id passed in
    """
    customer_orders = [
        order for order in orders_database if order["customer_id"] == customer_id
    ]
    if not customer_orders:
        return f"No orders associated with this customer id: {customer_id}"
    return customer_orders


@tool
def place_appointment(service: str, customer_id: str, appointment_day: str, appointment_month: str, appointment_hour: str) -> str:
    """
    Book an appointment for the requested services.

    Args:
        service (str): The service ID to book
        customer_id (str): The customer ID to place the order for
        appointment_day (str): The day of the appointment
        appointment_month (str): The month of the appointment
        appointment_hour (str): The hour of the appointment

    Returns:
        str: Message indicating that the appointment has been booked, or, it hasnt been booked due to an issue
    """
    # Place the order (in pretend database)
    order_id = len(orders_database) + 1
    orders_database.append(
        {
            "order_id": order_id,
            "customer_id": customer_id,
            "status": "Waiting for appointment",
            "date": f"{appointment_day} on {appointment_month} at {appointment_hour}",
            "service": service,
        }
    )
    # Update the inventory
    return f"Order with id {order_id} has been placed successfully"
