import grpc
from train_pb2 import Ticket, User
from train_pb2_grpc import TrainServiceStub

def main():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = TrainServiceStub(channel)

        # Purchase Ticket
        user = User(first_name="John", last_name="Doe", email="danajaya@gmail.com")
        ticket_request = Ticket(from="London", to="France", user=user)
        purchased_ticket = stub.PurchaseTicket(ticket_request)
        print("Ticket purchased:", purchased_ticket)

        # Show Receipt
        receipt_request = User(email="danajaya@gmail.com")
        receipt = stub.ShowReceipt(receipt_request)
        print("Receipt:", receipt)

        # View Users By Section
        section_request = "A"
        users_by_section = stub.ViewUsersBySection(section_request)
        print(f"Users in Section {section_request}:")
        for user_ticket in users_by_section:
            print(user_ticket)

        # Remove User
        remove_user_request = User(email="danajaya@gmail.com")
        removed_ticket = stub.RemoveUser(remove_user_request)
        print("Removed User's Ticket:", removed_ticket)

        # Modify User's Seat
        modify_seat_request = Ticket(from="London", to="France", user=user)
        modified_ticket = stub.ModifyUserSeat(modify_seat_request)
        print("Modified User's Seat:", modified_ticket)

if __name__ == '__main__':
    main()
