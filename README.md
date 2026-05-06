# RPC Framework - A Complete Remote Procedure Call Implementation from Scratch

A production-quality, educational RPC framework built entirely from scratch in Python using only standard library modules. No external RPC libraries (no gRPC, xmlrpc, rpyc, etc.).

## 📋 Features

- **Complete RPC Framework**: Full-stack implementation including transport, protocol, and runtime layers
- **Custom IDL**: Simple, intuitive Interface Definition Language for service contracts
- **Code Generation**: Automatic stub and skeleton generation from IDL
- **At-Least-Once Delivery**: Built-in request deduplication and retry logic
- **Type Safety**: Parameter type validation and serialization
- **Error Handling**: Structured error responses and network failure recovery
- **TCP Transport**: Efficient socket-based communication with proper message framing
- **Production Code**: Clean architecture, comprehensive error handling, logging, documentation

## 🏗️ Architecture

The framework follows a modular, layered architecture:

```
┌─────────────────────────────────────────────────────────────┐
│                      CLIENT / SERVER                         │
├─────────────────────────────────────────────────────────────┤
│  RUNTIME LAYER                                              │
│  ├─ Stub (Client): Python method proxies for remote calls   │
│  ├─ Skeleton (Server): Request dispatcher & method invoker  │
│  └─ Registry: Service implementation registry               │
├─────────────────────────────────────────────────────────────┤
│  PROTOCOL LAYER                                             │
│  ├─ Message: Request/Response definitions                   │
│  └─ Serializer: JSON marshaling/unmarshaling                │
├─────────────────────────────────────────────────────────────┤
│  TRANSPORT LAYER                                            │
│  ├─ TCP Server: Socket server with multi-threaded handling  │
│  └─ TCP Client: Socket client with retry logic              │
├─────────────────────────────────────────────────────────────┤
│  IDL LAYER                                                  │
│  ├─ Parser: IDL syntax parsing                              │
│  └─ Generator: Stub/skeleton code generation                │
├─────────────────────────────────────────────────────────────┤
│  UTILITIES                                                  │
│  ├─ Logger: Structured logging                              │
│  └─ Retry: Automatic retry with exponential backoff         │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
RPC-on-python/
├── rpc_framework/                 # Core RPC framework
│   ├── transport/
│   │   ├── tcp_server.py         # TCP server implementation
│   │   └── tcp_client.py         # TCP client implementation
│   ├── protocol/
│   │   ├── message.py            # RPC message definitions
│   │   └── serializer.py         # JSON serialization
│   ├── idl/
│   │   ├── parser.py             # IDL language parser
│   │   └── generator.py          # Code generator
│   ├── runtime/
│   │   ├── stub.py               # Client-side proxy
│   │   ├── skeleton.py           # Server-side dispatcher
│   │   └── registry.py           # Service registry
│   └── utils/
│       ├── logger.py             # Logging utilities
│       └── retry.py              # Retry mechanism
├── services/                      # Example services
│   └── calculator/
│       ├── calculator.idl         # Service interface definition
│       ├── calculator_impl.py     # Implementation
│       ├── server.py             # Server runner
│       └── client.py             # Client examples
├── demo.py                        # Full end-to-end demo
└── README.md                      # This file
```

## 🔄 How RPC Works in This Implementation

### 1. **Interface Definition (IDL)**

Services are defined using a simple IDL syntax:

```idl
service Calculator {
    int add(int a, int b)
    int subtract(int a, int b)
    int multiply(int a, int b)
    int divide(int a, int b)
    string greet(string name)
}
```

### 2. **Code Generation**

The framework generates:
- **Stub** (Client): Python classes that look like local method calls
- **Skeleton** (Server): Request dispatcher and method invoker

### 3. **Request Flow**

```
CLIENT                              SERVER
  │                                   │
  ├─ Call: stub.add(5, 3)            │
  ├─ Serialize request                │
  │   {request_id, method, params}    │
  ├─ Serialize to JSON                │
  ├─ Frame with length header         │
  ├─ Send over TCP ──────────────────>│
  │                                   ├─ Deserialize request
  │                                   ├─ Validate types
  │                                   ├─ Dispatch to method
  │                                   ├─ Execute: 5 + 3 = 8
  │                                   ├─ Serialize response
  │                                   ├─ Frame with length header
  │<──────────────── Send over TCP ───┤
  ├─ Deserialize response             │
  ├─ Parse: {request_id, result: 8}   │
  └─ Return result: 8                 │
```

### 4. **Message Format**

**Request:**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "add",
  "params": [5, 3],
  "timestamp": 1609459200.123,
  "service": "Calculator"
}
```

**Response:**
```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "result": 8,
  "error": null,
  "timestamp": 1609459200.456
}
```

### 5. **At-Least-Once Delivery**

- **Request ID**: Every request has a unique ID for correlation
- **Deduplication**: Server caches responses and detects duplicate requests
- **Automatic Retry**: Client retries with exponential backoff on failures
- **Idempotency**: Applications should design methods to be idempotent

## 🚀 Quick Start

### Prerequisites
- Python 3.7+
- Standard library only (no external dependencies!)

### 1. Start the Server

```bash
python services/calculator/server.py
```

Output:
```
============================================================
Calculator RPC Server
============================================================

[1/4] Parsing Calculator.idl...
✓ Parsed 1 service(s)

[2/4] Generating RPC code...
✓ Generated 2 file(s)

[3/4] Registering service...
✓ Service registered

[4/4] Starting TCP server...
✓ Server started on 127.0.0.1:5000

============================================================
Server is running. Press Ctrl+C to stop.
============================================================
```

### 2. Run the Client (in another terminal)

```bash
python services/calculator/client.py
```

Output:
```
============================================================
Calculator RPC Client
============================================================

Connecting to server at 127.0.0.1:5000...
✓ Connected to server

Running test cases:

✓ 5 + 3               = 8
✓ 10 - 4              = 6
✓ 6 × 7               = 42
✓ 20 ÷ 4              = 5
✓ greet("Alice")      = Hello, Alice! Welcome to the Calculator Service.
✓ 100 + 200           = 300

Testing error handling:
✓ divide(10, 0) correctly raised error: Remote error: Division by zero

✓ Connection closed

============================================================
All tests completed!
============================================================
```

### 3. Run Full Demo

```bash
python demo.py
```

This runs both server and client in separate processes with automatic cleanup.

## 💡 Creating Your Own Service

### Step 1: Define the Interface

Create `myservice/myservice.idl`:

```idl
service MyService {
    string process(string data)
    int count(int n)
}
```

### Step 2: Implement the Service

Create `myservice/myservice_impl.py`:

```python
class MyService:
    def process(self, data: str) -> str:
        return data.upper()
    
    def count(self, n: int) -> int:
        return n * 2
```

### Step 3: Create Server

Create `myservice/server.py`:

```python
from rpc_framework.idl.parser import IDLParser
from rpc_framework.transport.tcp_server import TCPServer
from rpc_framework.runtime.skeleton import RPCSkeleton
from rpc_framework.runtime.registry import ServiceRegistry
from myservice.myservice_impl import MyService

# Parse IDL and create service
parser = IDLParser()
parser.parse_file("myservice/myservice.idl")

service = MyService()
registry = ServiceRegistry()
methods = {"process": service.process, "count": service.count}
signatures = {"process": [str], "count": [int]}

registry.register_service("MyService", service, methods, signatures)
skeleton = RPCSkeleton(registry)

# Start server
server = TCPServer(port=5001)
server.start(request_handler=skeleton.dispatch_request)
```

### Step 4: Create Client

```python
from rpc_framework.transport.tcp_client import TCPClient
from rpc_framework.runtime.stub import RPCStub

client = TCPClient(port=5001)
client.connect()
stub = RPCStub(client, "MyService")

# Call remote methods
result1 = stub.invoke("process", ["hello"], str)
result2 = stub.invoke("count", [5], int)
```

## 🔍 Key Implementation Details

### Transport Layer (TCP)

- **Message Framing**: 4-byte big-endian length header + JSON payload
- **Non-blocking Accept**: Server accepts connections in background thread
- **Per-client Threading**: Each client handled in separate thread
- **Timeout**: Configurable socket timeout for reliability
- **Graceful Shutdown**: Proper resource cleanup

### Protocol Layer

- **JSON Serialization**: Human-readable, no security risks (vs pickle)
- **Type Validation**: Parameters validated against expected types
- **Type Conversion**: Automatic conversion (e.g., float to int)
- **Error Messages**: Detailed error information for debugging

### Runtime Layer

- **Dynamic Dispatch**: Registry-based method lookup
- **Stub Proxies**: Methods appear as normal Python functions
- **Skeleton Dispatcher**: Routes requests to appropriate methods
- **Type Signatures**: Optional type hints for validation

### At-Least-Once Semantics

```python
# Client automatically retries failed requests
@with_retry(strategy=RetryStrategy(max_attempts=3, initial_delay=0.1))
def send_request(self, message):
    # Exponential backoff: 0.1s, 0.2s, 0.4s, ...
    pass

# Server deduplicates duplicate requests
def dispatch_request(self, request_dict):
    if request_id in self._processed_requests:
        return self._processed_requests[request_id]  # Return cached
    # Process and cache result...
```

### Logging

The framework includes comprehensive logging at all levels:

```python
# DEBUG: Method execution, message framing
# INFO: Connection events, service registration
# ERROR: Failures, exceptions

logger = setup_logger(__name__, "DEBUG")
logger.debug(f"Executing method with params {params}")
```

## 📊 Performance Characteristics

- **Latency**: Single-digit milliseconds per RPC call (depends on network)
- **Throughput**: Scales with number of client threads/processes
- **Concurrency**: Server handles multiple simultaneous clients
- **Memory**: Minimal overhead; caches processed requests for deduplication

## ⚠️ Limitations & Future Improvements

### Current Limitations
- **No Async/Await**: Synchronous blocking calls only
- **Limited Types**: int, string, float, bool, list (no custom types/objects)
- **No Authentication**: No security/authorization
- **Single Machine**: No service discovery or load balancing
- **No Caching**: Except for deduplication

### Future Enhancements
- Async/await support with asyncio
- Custom type serialization (dataclasses, etc.)
- TLS/SSL encryption
- Service discovery and health checks
- Client-side caching with TTL
- Circuit breaker pattern
- Rate limiting and throttling
- Metrics and monitoring

## 🧪 Testing

Run individual components:

```bash
# Start server
python services/calculator/server.py

# In another terminal, run client
python services/calculator/client.py

# Or run full demo (auto-manages both)
python demo.py
```

## 📚 Learning Resources

This implementation demonstrates:

1. **Network Programming**: TCP sockets, message framing, multi-threading
2. **Distributed Systems**: RPC semantics, deduplication, retries
3. **Code Generation**: Parsing and template-based code generation
4. **Serialization**: JSON marshaling/unmarshaling with type safety
5. **Clean Architecture**: Separation of concerns, modularity
6. **Error Handling**: Graceful degradation, structured errors
7. **Logging**: Structured logging for debugging and monitoring

## 📝 Code Quality

- **Type Hints**: Full type annotations for clarity
- **Docstrings**: Comprehensive docstrings for all classes/functions
- **Error Handling**: Try-catch with meaningful error messages
- **Logging**: DEBUG/INFO/ERROR level logging throughout
- **Clean Code**: PEP 8 compliant, readable, maintainable
- **No Dependencies**: Uses only Python standard library

## 🎓 Educational Value

This project is ideal for learning:

- How RPC frameworks work internally
- Distributed systems design patterns
- Network programming with sockets
- Serialization and marshaling
- Code generation techniques
- Design patterns (Registry, Proxy, Strategy)

## 📄 License

Educational implementation - Feel free to use, modify, and learn from this code.

## 🤝 Contributing

Suggestions for improvements:
- Add async/await support
- Implement more complex types (dataclasses, nested objects)
- Add authentication/encryption
- Implement service discovery
- Add performance benchmarks
- Create more example services

---

**Built with ❤️ as an educational demonstration of RPC framework internals**