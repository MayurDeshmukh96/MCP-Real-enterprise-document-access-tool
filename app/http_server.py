from fastapi import FastAPI
from mcp.server.sse import SseServerTransport
from starlette.routing import Mount,Route
from starlette.requests import Request

from app.main import server

# Creates official MCP SSE transport.This manages remote communication.
# This is official SDK transport,not manual protocol handling.
sse = SseServerTransport('/messages/')


# Handles incoming remote MCP clients.Accept AI client connection.
async def handle_sse(request : Request):
    # Start live conversation channel. Open secure streaming communication session.
    async with sse.connect_sse( 
        request.scope,
        request.receive,
        request._send
    )as streams:
        # Run official MCP server over SSE streams.
        await server.run(
            streams[0],
            streams[1],
            server.create_initialization_options()
    )


app = FastAPI(title="Secure Enterprise MCP")

@app.get('/')
async def root():
    return{
        "message":"Secure Enterprise MCP HTTP Server Running"
    }

@app.get('/health')
async def health():
    return{
        'status':'healthy'
    }

# Connection endpoint, Start MCP session here.
app.router.routes.append(
    Route('/sse',endpoint=handle_sse,methods=['GET'])
)

# Receives MCP client messages, Send protocol requests here.
app.router.routes.append(
    Mount('/messages/',app=sse.handle_post_message)
)