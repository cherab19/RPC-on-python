#!/bin/bash
# RPC Framework - Feature-based Git Commits Script
# This script commits the RPC framework by features with clear commit messages

set -e

echo "🚀 Starting RPC Framework commit workflow..."
echo ""

cd /workspaces/RPC-on-python

# Check if git is configured
if ! git config user.email &> /dev/null; then
    echo "⚠️  Git is not configured. Configuring now..."
    git config user.email "rpc-framework@example.com"
    git config user.name "RPC Framework Developer"
fi

# Feature 1: Project Structure & Gitignore
echo "📦 Commit 1: Project structure and configuration..."
git add .gitignore rpc_framework/__init__.py services/__init__.py services/calculator/__init__.py
git commit -m "feat: initialize project structure with RPC framework package layout

- Create modular package structure for rpc_framework
- Organize into transport, protocol, idl, runtime, and utils layers
- Add gitignore for Python artifacts and dependencies
- Initialize services package for example implementations"

# Feature 2: Transport Layer
echo "📦 Commit 2: Transport layer (TCP server and client)..."
git add rpc_framework/transport/
git commit -m "feat: implement TCP transport layer with socket communication

- Implement TCPServer: multi-threaded socket server with connection handling
- Implement TCPClient: client with automatic retry logic
- Add message framing protocol: 4-byte length header + JSON payload
- Support concurrent client connections with per-client threading
- Implement graceful shutdown and error handling"

# Feature 3: Protocol Layer
echo "📦 Commit 3: Protocol layer (messages and serialization)..."
git add rpc_framework/protocol/
git commit -m "feat: implement RPC protocol with messages and serialization

- Define RPCRequest: method calls with unique ID tracking
- Define RPCResponse: success/error response handling
- Implement Serializer: type-safe JSON marshaling/unmarshaling
- Support primitive types: int, string, float, bool, list
- Add parameter type validation and conversion"

# Feature 4: Utilities
echo "📦 Commit 4: Utility functions (logging and retry)..."
git add rpc_framework/utils/
git commit -m "feat: implement utilities for logging and resilience

- Implement setup_logger: structured logging with consistent formatting
- Implement RetryStrategy: configurable retry with exponential backoff
- Add with_retry decorator: transparent retry mechanism for methods
- Support configurable max attempts, delays, and backoff factors"

# Feature 5: IDL System
echo "📦 Commit 5: IDL parser and code generator..."
git add rpc_framework/idl/
git commit -m "feat: implement IDL parser and automatic code generation

- Implement IDLParser: parse simple IDL interface definitions
- Support service definitions with methods and type annotations
- Implement CodeGenerator: auto-generate stub and skeleton code
- Generate type-safe client proxies and server dispatchers
- Support method signatures for type validation"

# Feature 6: Runtime Layer
echo "📦 Commit 6: Runtime layer (stub, skeleton, registry)..."
git add rpc_framework/runtime/
git commit -m "feat: implement runtime with stub, skeleton, and registry

- Implement RPCStub: client-side method proxies for remote calls
- Implement RPCSkeleton: server-side request dispatcher
- Implement ServiceRegistry: dynamic service and method registration
- Support at-least-once delivery with request deduplication
- Handle method dispatch with type validation and error handling"

# Feature 7: Calculator Service
echo "📦 Commit 7: Calculator service example implementation..."
git add services/calculator/
git commit -m "feat: implement calculator service example

- Create calculator.idl: IDL definition with 5 methods
- Implement Calculator class: add, subtract, multiply, divide, greet
- Create server.py: service registration and server startup
- Create client.py: client with comprehensive test cases
- Demonstrate error handling (division by zero) and request-response flow"

# Feature 8: Documentation and Demo
echo "📦 Commit 8: Documentation and integration demo..."
git add README.md demo.py
git commit -m "feat: add comprehensive documentation and demo script

- Add detailed README.md explaining architecture and usage
- Include quick start guide and example usage patterns
- Add architecture diagrams and feature overview
- Implement demo.py: full integration test with server and client
- Document how to create custom RPC services"

echo ""
echo "✅ All commits completed successfully!"
echo ""
echo "📋 Commits created:"
git log --oneline -8 | head -8
echo ""
echo "🚀 Ready to push to GitHub!"
echo ""
echo "To push to GitHub, run:"
echo "  git push origin main"
echo ""
