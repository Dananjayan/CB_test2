package main

import (
	"context"
	"fmt"
	"log"

	"google.golang.org/grpc"
)

func main() {
	conn, err := grpc.Dial("localhost:50051", grpc.WithInsecure())
	if err != nil {
		log.Fatalf("Failed to connect: %v", err)
	}
	defer conn.Close()

	client := NewTrainServiceClient(conn)

	user := &User{FirstName: "John", LastName: "Doe", Email: "john.doe@example.com"}
	purchasedTicket, err := client.PurchaseTicket(context.Background(), &Ticket{From: "London", To: "France", User: user})
	if err != nil {
		log.Fatalf("Error purchasing ticket: %v", err)
	}
	fmt.Println("Ticket purchased:", purchasedTicket)

	receipt, err := client.ShowReceipt(context.Background(), user)
	if err != nil {
		log.Fatalf("Error showing receipt: %v", err)
	}
	fmt.Println("Receipt:", receipt)

	section := "A"
	usersBySection, err := client.ViewUsersBySection(context.Background(), &section)
	if err != nil {
		log.Fatalf("Error viewing users by section: %v", err)
	}
	fmt.Printf("Users in Section %s:\n", section)
	for {
		ticket, err := usersBySection.Recv()
		if err == io.EOF {
			break
		}
		if err != nil {
			log.Fatalf("Error receiving user: %v", err)
		}
		fmt.Println(ticket)
	}

	removedTicket, err := client.RemoveUser(context.Background(), user)
	if err != nil {
		log.Fatalf("Error removing user: %v", err)
	}
	fmt.Println("Removed User's Ticket:", removedTicket)

	modifiedTicket, err := client.ModifyUserSeat(context.Background(), purchasedTicket)
	if err != nil {
		log.Fatalf("Error modifying user's seat: %v", err)
	}
	fmt.Println("Modified User's Seat:", modifiedTicket)
}
