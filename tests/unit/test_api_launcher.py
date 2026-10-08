import errno
import socket
import unittest
from unittest.mock import AsyncMock, patch
import uvicorn
from troubleshoot.api.__main__ import BrowserServer, reserve_listener

class ListenerTests(unittest.TestCase):
    def test_occupied_port_uses_a_distinct_reserved_listener(self):
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 0))
            port = occupied.getsockname()[1]
            with reserve_listener(port, fallback=True) as listener:
                self.assertGreater(listener.getsockname()[1], port)
                self.assertLessEqual(listener.getsockname()[1], min(port+20, 65535))
                with socket.socket() as other:
                    with self.assertRaises(OSError):
                        other.bind(listener.getsockname())

    def test_explicit_port_failure_does_not_attach_to_existing_server(self):
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 0))
            with self.assertRaises(OSError) as caught:
                reserve_listener(occupied.getsockname()[1])
            self.assertEqual(caught.exception.errno, errno.EADDRINUSE)

class BrowserStartupTests(unittest.IsolatedAsyncioTestCase):
    async def test_browser_opens_only_after_successful_startup(self):
        server = BrowserServer(uvicorn.Config(lambda: None))
        server.launch_url = "http://127.0.0.1:12345/#session=synthetic"
        with patch.object(uvicorn.Server, "startup", new=AsyncMock()), patch("troubleshoot.api.__main__.threading.Thread") as thread:
            server.started = False
            await server.startup()
            thread.assert_not_called()
            server.started = True
            await server.startup()
            thread.return_value.start.assert_called_once()
