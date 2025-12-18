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
WORKDIR /build/cmd/agents/optimization
RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o agent .

# Runtime stage
FROM alpine:3.19

RUN apk --no-cache add ca-certificates tzdata

# Create non-root user for security (UID 1000 to match Kubernetes securityContext)
RUN addgroup -g 1000 appgroup && adduser -u 1000 -G appgroup -s /bin/sh -D appuser

WORKDIR /app

# Copy binary from builder
COPY --from=builder /build/cmd/agents/optimization/agent /app/agent

# Ensure binary is executable and owned by appuser
RUN chmod +x /app/agent && chown appuser:appgroup /app/agent

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8080 8081

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --no-verbose --tries=1 --spider http://localhost:8080/health || exit 1

# Run the application with absolute path
ENTRYPOINT ["/app/agent"]
