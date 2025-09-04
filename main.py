from dotenv import load_dotenv
import os

load_dotenv()

# Import document tools instead of meeting tools
from MCP.tools.document_tools import app as document_mcp_server

server = document_mcp_server


def main():
    print("Hello from poc-mcp! (This message is from your main() function).")
    print("To start the MCP server, you MUST use the command: `mcp run main:server --port 8001`.")
    print("This main() function does not start the MCP server itself.")


# This block ensures that if you run `python main.py` directly,
# your `def main()` function is called.
if __name__ == "__main__":
    main()
    