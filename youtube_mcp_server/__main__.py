# 🎯 TEMPLATE INSTRUCTIONS - Update import when you rename the folder!
# When you rename "mcp_server" folder to your unique name (e.g., "weather_server"):
# Change line 2: from .server import run_server
# to use your new folder name (the relative import stays the same)
# BUT the folder itself must be renamed

import asyncio
from .server import (
    run_server,
)  # 👈 This stays the same (relative import) but folder name must change


def main() -> None:
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
