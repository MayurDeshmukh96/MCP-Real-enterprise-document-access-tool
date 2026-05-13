from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, Resource, Prompt, TextContent, GetPromptResult, PromptMessage
from app.db.postgres import engine
from sqlalchemy import text
from dotenv import load_dotenv
from pathlib import Path
import asyncio
import os

# Load .env using absolute path (works regardless of working directory)
load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / '.env')

server = Server("secure-enterprise-mcp")

MCP_API_KEY = os.getenv('MCP_API_KEY')




# ********************************** Tools ***************************************


@server.list_tools()
async def list_tools():
    return [
        # 1) ----------------------------------query_database-----------------------------------
        Tool(
            name='query_database',
            description = 'Run safe SELECT queries on POstgreSQL',
            inputSchema={
                'type':'object',
                'properties':{
                    'sql':{
                        'type':'string',
                        'description':'SQL SELECT query'
                    },
                    'api_key':{
                        'type':'string',
                        'description': 'Authentication API key'
                    }
                },
                'required':['sql','api_key']
            }
        ),

        # 2) ----------------------------------read_file-----------------------------------

        Tool(
            name='read_file',
            description='Read approved internal files',
            inputSchema={
                'type':'object',
                'properties':{
                    'path':{
                        'type':'string',
                        'description':'Path to approved file'
                    },
                    'api_key':{
                        'type':'string',
                        'description': 'Authentication API key'
                    }
                },
                'required':['path','api_key']
            }
        )
    ]


# ********************************** Resources ***************************************

# 1) ----------------------------------list_resources-----------------------------------

# When AI asks for available resources, run this function (Show my document library.)
@server.list_resources()   
async def list_resources():

    resources = []  # Take empty list for resources
    
    # Defines safe document folder. Look inside company_docs.
    base_dir = os.path.abspath("company_docs")

    # Loop through all files. Check every document.
    for filename in os.listdir(base_dir):
        file_path = os.path.join(base_dir,filename)

        # Only include real files,not folders.Ignore subfolders
        if os.path.isfile(file_path):
            resources.append(

                # Define one MCP resource.
                Resource(
                    # Unique identifier. Ex - file://policies.txt
                    uri=f'file://{filename}',

                    # Visible file name. Ex- policies.txt
                    name = filename,

                    # Explains file purpose.
                    description=f'Internal company document:{filename}',

                    # File type, Text document
                    mimeType='text/plain'
                )
            )

    # Send full resource list to AI.
    return resources


# ********************************** Prompts ***************************************

@server.list_prompts() # When AI asks for available prompts, run this function.
async def list_prompts(): # Function that returns prompt list.
    return[

        # Define one MCP prompt. Create one reusable workflow.
        Prompt(

            # Official prompt name, AI references this prompt later.
            name='sql_assistant', 

            # Explains prompt purpose.AI uses descriptions to decide: “Should I use this prompt?”
            description='Analyze SQL query results and explain then clearly.'
        )
    ]


# ********************************** Get Prompts ***************************************

@server.get_prompt()  # When AI wants prompt instructions, use this function.
async def get_prompt(name:str):  # AI sends prompt name.

    if name == 'sql_assistant':
        return GetPromptResult(
            description='Enterprise SQL analyst prompt',
            messages=[
                PromptMessage(
                    role='user',
                    content=TextContent(
                        type='text',
                        text=(
                            "You are an enterprise SQL analyst.\n\n"
                            "Your responsibilities:\n"
                            "- Explain SQL query results clearly\n"
                            "- Summarize important patterns\n"
                            "- Identify anomalies\n"
                            "- Recommend business actions\n"
                            "- Present findings in simple business language\n"
                            "- Highlight security or compliance concerns when relevant"
                        )
                    )
                )
            ]
        )
    
    else:
        raise ValueError("Prompt not found")



# -----------------------------------read_resource-------------------------------


# This tells MCP: “When AI wants to open a resource, use this function.”
@server.read_resource()
async def read_resource(uri:str): # AI sends resource identifier. Ex - file://policies.txt
    
    base_dir = os.path.abspath('company_docs')

    # Extract actual file name.
    filename = uri.replace("file://","") # Here Remove file:// label and I get Ex - policies.txt

    # Build full secure path.
    requested_path = os.path.abspath(os.path.join(base_dir,filename))
    # NOTE: do NOT print() here - stdout is the MCP transport channel

    # Security check - Prevent unauthorized access.
    # Path traversal prevention
    if not requested_path.startswith(base_dir):
        raise ValueError("Unauthorized Resource Access")
    
    # Ensure file exists.
    if not os.path.exists(requested_path):
        raise FileNotFoundError("Resource not found")
    
    # Open file safely and Read document content
    with open(requested_path,'r',encoding='utf-8') as file:
        file_content = file.read()
    
    # MCP requires a list of TextContent objects, not a raw string
    return [TextContent(type='text', text=file_content)]


# ********************************** Call Tool ***************************************


@server.call_tool()
async def call_tool(name:str, arguments:dict):



    api_key = arguments.get('api_key')    # Read API key from incoming request.
    if api_key != MCP_API_KEY:      # Compare provided key with server key.
        raise ValueError("Unauthorized: Invalid API key")




    if name == 'query_database':
        sql = arguments['sql']

        # Basic safety check
        # forbidden = ['DELETE','DROP','UPDATE','INSERT','ALTER']
        # if any(word in sql.upper() for word in forbidden):
        #     raise ValueError('Unsafe query detected')




        # Only allow SELECT commands.
        allowed_prefix = 'SELECT'

        # Check query start.
        if not sql.strip().upper().startswith(allowed_prefix):
            raise ValueError("Only SELECT queries are allowed.")



        ALLOWED_TABLES = ["users"] # “Only specific tables are allowed.”
        # If SELECT * FROM salaries; (Blocked)

        # Check if query contains approved table names.
        if not any(table in sql.lower() for table in ALLOWED_TABLES):
            raise ValueError("Unauthorized table access")

        with engine.connect() as connection:
            result = connection.execute(text(sql))
            rows = [dict(row._mapping) for row in result]

        import json
        return [TextContent(type='text', text=json.dumps(rows, default=str, indent=2))]

    
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

        return [TextContent(type='text', text=content)]

    else :
        raise ValueError("Unknown tool")


if __name__ == "__main__":
    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )

    asyncio.run(main())
    # --- old tests (uncomment to re-run) ---

    # async def test():
    #     print("=== TEST 1: Valid Database Query ===")
    #     result = await call_tool(
    #         "query_database",
    #         {
    #             "sql": "SELECT * FROM users;",
    #             "api_key": "48v114OPkpsyIOt0ST00XKZt-nzm9HpZ8zF_J-NeR_s"
    #         }
    #     )
    #     print(result)

    #     print("\n=== TEST 2: Valid File Read ===")
    #     result = await call_tool(
    #         "read_file",
    #         {
    #             "path": "policies.txt",
    #             "api_key": "48v114OPkpsyIOt0ST00XKZt-nzm9HpZ8zF_J-NeR_s"
    #         }
    #     )
    #     print(result)

    #     print("\n=== TEST 3: Invalid API Key ===")
    #     try:
    #         result = await call_tool(
    #             "query_database",
    #             {
    #                 "sql": "SELECT * FROM users;",
    #                 "api_key": "wrong_key"
    #             }
    #         )
    #         print(result)
    #     except Exception as e:
    #         print("Blocked:", e)

    #     print("\n=== TEST 4: Unauthorized Table ===")
    #     try:
    #         result = await call_tool(
    #             "query_database",
    #             {
    #                 "sql": "SELECT * FROM salaries;",
    #                 "api_key": "48v114OPkpsyIOt0ST00XKZt-nzm9HpZ8zF_J-NeR_s"
    #             }
    #         )
    #         print(result)
    #     except Exception as e:
    #         print("Blocked:", e)

    #     print("\n=== TEST 5: Dangerous Query ===")
    #     try:
    #         result = await call_tool(
    #             "query_database",
    #             {
    #                 "sql": "DROP TABLE users;",
    #                 "api_key": "48v114OPkpsyIOt0ST00XKZt-nzm9HpZ8zF_J-NeR_s"
    #             }
    #         )
    #         print(result)
    #     except Exception as e:
    #         print("Blocked:", e)

    #     print("\n=== TEST 6: Path Traversal Attack ===")
    #     try:
    #         result = await call_tool(
    #             "read_file",
    #             {
    #                 "path": "../.env",
    #                 "api_key": "48v114OPkpsyIOt0ST00XKZt-nzm9HpZ8zF_J-NeR_s"
    #             }
    #         )
    #         print(result)
    #     except Exception as e:
    #         print("Blocked:", e)

    #     print("\n=== TEST 7: List Resources ===")
    #     resources = await list_resources()
    #     print(resources)

    #     print("\n=== TEST 8: Read Resource ===")
    #     content = await read_resource("file://policies.txt")
    #     print(content)

    #     print("\n=== TEST 9: List Prompts ===")
    #     prompts = await list_prompts()
    #     print(prompts)

    #     print("\n=== TEST 10: Get Prompt ===")
    #     prompt = await get_prompt("sql_assistant")
    #     print(prompt)

    # asyncio.run(test())