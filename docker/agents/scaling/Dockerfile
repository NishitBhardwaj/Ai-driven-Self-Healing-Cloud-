# Build stage
FROM golang:1.24-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache git make

# Copy go mod files
COPY go.mod ./
COPY go.sum* ./
RUN go mod download

# Copy source code
COPY . .

# Download all dependencies (including missing ones)
RUN go mod download

# Build the application from cmd directory
WORKDIR /build/cmd/agents/scaling
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o agent .

# Runtime stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates tzdata

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/cmd/agents/scaling/agent /app/agent

# Ensure binary is executable
RUN chmod +x /app/agent

# Expose port
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the application with absolute path
ENTRYPOINT ["/app/agent"]
