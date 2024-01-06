from concurrent import futures
import grpc
from train_pb2 import Ticket, User
from train_pb2_grpc import TrainServiceServicer, add_TrainServiceServicer_to_server

class TrainServiceImplementation(TrainServiceServicer):
    tickets = []
    sections = {"A": [], "B": []}

    def PurchaseTicket(self, request, context):
        request.price = 20.0
        request.section = "A" if len(self.sections["A"]) <= len(self.sections["B"]) else "B"
        self.sections[request.section].append(request)
        return request

    def ShowReceipt(self, request, context):
        for ticket in self.tickets:
            if ticket.user.email == request.email:
                return ticket
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("User not found")
        return Ticket()

    def ViewUsersBySection(self, request, context):
        for ticket in self.sections.get(request, []):
            yield ticket

    def RemoveUser(self, request, context):
        for section in self.sections.values():
            for i, ticket in enumerate(section):
                if ticket.user.email == request.email:
                    del section[i]
                    return ticket
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("User not found")
        return Ticket()

    def ModifyUserSeat(self, request, context):
        current_section = None
        for section in self.sections.values():
            for i, ticket in enumerate(section):
                if ticket.user.email == request.user.email:
                    current_section = section
                    del section[i]
                    break

        if current_section:
            request.section = "A" if len(self.sections["A"]) <= len(self.sections["B"]) else "B"
            self.sections[request.section].append(request)
            return request
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("User not found")
            return Ticket()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    add_TrainServiceServicer_to_server(TrainServiceImplementation(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
