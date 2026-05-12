from mcp.server import Server
from mcp.types import Tool
from app.db.postgres import engine
from sqlalchemy import text
import os

server = Server("secure-enterprise-mcp")

@server.list_tools()
async def list_tools():
    return [
        Tool(
            name='query_database',
            description = 'Run safe SELECT queries on POstgreSQL',
            inputSchema={
                'type':'object',
                'properties':{
                    'sql':{
                        'type':'string',
                        'description':'SQL SELECT query'
                    }
                },
                'required':['sql']
            }
        ),

        Tool(
            name='read_file',
            description='Read approved internal files',
            inputSchema={
                'type':'object',
                'properties':{
                    'path':{
                        'type':'string',
                        'description':'Path to approved file'
                    }
                },
                'required':['path']
            }
        )
    ]

@server.call_tool()
async def call_tool(name:str, arguments:dict):
    if name == 'query_database':
        sql = arguments['sql']

        # Basic safety check
        forbidden = ['DELETE','DROP','UPDATE','INSERT','ALTER']

        if any(word in sql.upper() for word in forbidden):
            raise ValueError('Unsafe query detected')
        
        with engine.connect() as connection:
            result = connection.execute(text(sql))

            rows = [dict(row._mapping) for row in result]

        return {
            'status':'success',
            'data':rows
        }

    
    elif name == 'read_file':

        path = arguments['path']

        BASE_DIR = os.path.abspath("company_docs")
        requested_path = os.path.abspath(os.path.join(BASE_DIR,path))

        # Prevent Path traversal
        if not requested_path.startswith(BASE_DIR):
            raise ValueError("Unauthorized file access")
        
        if not os.path.exists(requested_path):
            raise FileNotFoundError('File not found')
        
        with open(requested_path, "r", encoding="utf-8") as file:
            content = file.read()

        return {
            'status':'success',
            'content': content
        }


    




    else :
        raise ValueError("Unknown tool")




if __name__ == "__main__":
    import asyncio

    async def test():
        result = await call_tool(
            "query_database",
            {"sql": "SELECT * FROM users;"}
        )
        print(result)

    asyncio.run(test())