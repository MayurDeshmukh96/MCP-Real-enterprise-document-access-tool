from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

async def main():
    client = MultiServerMCPClient(
        {
            'secure-enterprise-mcp':{
                'command':r'D:\Mayur\Learning\MCP\.venv\Scripts\python.exe',
                'args' : ['-m','app.main'],
                'transport' : 'stdio'
            }
        }
    )

    tools = await client.get_tools()

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature = 0)
    
    agent = create_agent(llm,tools)
    # print('Available MCP Tools')

    response = await agent.ainvoke(
        {
            'messages':[
                (
                    'user',
                    "Read the file 'policies.txt' using the read_file tool. Use path='company_docs/policies.txt' and Use API key: 48v114OPkpsyIOt0ST00XKZt-nzm9HpZ8zF_J-NeR_s  Summarize the main DATA PRIVACY & SECURITY POLICY." 
                )
            ]
        }
    )

    print(response)

if __name__ == "__main__":
    asyncio.run(main())