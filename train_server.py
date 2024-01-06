package main

import (
	"context"
	"fmt"
	"io"
	"log"
	"net"

	"google.golang.org/grpc"
	"google.golang.org/protobuf/types/known/emptypb"
)

type trainServer struct {
	tickets  []*Ticket
	sections map[string][]*Ticket
}

func (s *trainServer) PurchaseTicket(ctx context.Context, request *Ticket) (*Ticket, error) {
	request.Price = 20.0
	request.Section = "A"
	if len(s.tickets)%2 == 1 {
		request.Section = "B"
	}
	s.tickets = append(s.tickets, request)
	s.sections[request.Section] = append(s.sections[request.Section], request)
	return request, nil
}

func (s *trainServer) ShowReceipt(ctx context.Context, user *User) (*Ticket, error) {
	for _, ticket := range s.tickets {
		if ticket.User.Email == user.Email {
			return ticket, nil
		}
	}
	return nil, fmt.Errorf("User not found")
}

func (s *trainServer) ViewUsersBySection(section *string, stream TrainService_ViewUsersBySectionServer) error {
	for _, ticket := range s.sections[*section] {
		if err := stream.Send(ticket); err != nil {
			return err
		}
	}
	return nil
}

func (s *trainServer) RemoveUser(ctx context.Context, user *User) (*Ticket, error) {
	for i, ticket := range s.tickets {
		if ticket.User.Email == user.Email {
			removedTicket := ticket
			s.tickets = append(s.tickets[:i], s.tickets[i+1:]...)
			delete(s.sections, ticket.Section)
			return removedTicket, nil
		}
	}
	return nil, fmt.Errorf("User not found")
}

func (s *trainServer) ModifyUserSeat(ctx context.Context, request *Ticket) (*Ticket, error) {
	removedTicket, err := s.RemoveUser(ctx, request.User)
	if err != nil {
		return nil, err
	}
	return s.PurchaseTicket(ctx, request)
}

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("Failed to listen: %v", err)
	}

	server := grpc.NewServer()
	trainService := &trainServer{sections: make(map[string][]*Ticket)}
	RegisterTrainServiceServer(server, trainService)

	log.Println("Server started at :50051")
	if err := server.Serve(lis); err != nil {
		log.Fatalf("Failed to serve: %v", err)
	}
}
