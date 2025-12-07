package config

import (
	"fmt"

	"github.com/nats-io/nats.go"
	"github.com/sirupsen/logrus"
)

var globalConn *nats.Conn

// MessageBus represents a message bus connection
type MessageBus interface {
	Connect() error
	Disconnect() error
	Publish(subject string, data []byte) error
	Subscribe(subject string, handler func([]byte)) error
	IsConnected() bool
}

// NATSMessageBus implements MessageBus using NATS
type NATSMessageBus struct {
	conn   *nats.Conn
	url    string
	logger *logrus.Logger
}

// NewNATSMessageBus creates a new NATS message bus instance
func NewNATSMessageBus(url string) *NATSMessageBus {
	return &NATSMessageBus{
		url:    url,
		logger: GetLogger(),
	}
}

// Connect establishes connection to NATS server
func (mb *NATSMessageBus) Connect() error {
	conn, err := nats.Connect(mb.url, nats.Name("ai-cloud-system"))
	if err != nil {
		return fmt.Errorf("failed to connect to NATS: %w", err)
	}

	mb.conn = conn
	globalConn = conn
	mb.logger.WithField("url", mb.url).Info("Connected to NATS message bus")
	return nil
}

// Disconnect closes the NATS connection
func (mb *NATSMessageBus) Disconnect() error {
	if mb.conn != nil && mb.conn.IsConnected() {
		mb.conn.Close()
		mb.logger.Info("Disconnected from NATS message bus")
	}
	return nil
}

// Publish sends a message to a subject
func (mb *NATSMessageBus) Publish(subject string, data []byte) error {
	if !mb.IsConnected() {
		return fmt.Errorf("not connected to message bus")
	}
	return mb.conn.Publish(subject, data)
}

// Subscribe subscribes to a subject with a handler
func (mb *NATSMessageBus) Subscribe(subject string, handler func([]byte)) error {
	if !mb.IsConnected() {
		return fmt.Errorf("not connected to message bus")
	}

	_, err := mb.conn.Subscribe(subject, func(msg *nats.Msg) {
		handler(msg.Data)
	})
	return err
}

// IsConnected checks if the connection is active
func (mb *NATSMessageBus) IsConnected() bool {
	return mb.conn != nil && mb.conn.IsConnected()
}

// ConnectMessageBus connects to the message bus based on configuration
func ConnectMessageBus() (MessageBus, error) {
	cfg := GetConfig()
	
	switch cfg.MessageBusType {
	case "nats":
		bus := NewNATSMessageBus(cfg.MessageBusURL)
		if err := bus.Connect(); err != nil {
			return nil, err
		}
		return bus, nil
	default:
		return nil, fmt.Errorf("unsupported message bus type: %s", cfg.MessageBusType)
	}
}

// GetMessageBusConnection returns the global message bus connection
func GetMessageBusConnection() *nats.Conn {
	return globalConn
}

