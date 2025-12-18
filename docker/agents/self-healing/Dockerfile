# Build stage
FROM golang:1.22-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache git make

# Copy go mod files
COPY go.mod ./
COPY go.sum* ./

# Copy source code first to ensure go.mod can resolve all imports
COPY . .

# Ensure all dependencies are downloaded and go.sum is updated
RUN go mod tidy && go mod download

# Build the application from cmd directory
WORKDIR /build/cmd/agents/self-healing
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o agent .

# Runtime stage
FROM alpine:3.19

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/cmd/agents/self-healing/agent /app/agent

# Copy configuration files
COPY --from=builder /build/agents/self-healing/config.json /app/config.json

# Ensure binary is executable
RUN chmod +x /app/agent

# Expose port
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the application with absolute path
ENTRYPOINT ["/app/agent"]
