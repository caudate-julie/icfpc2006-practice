from telnet_server import Handler, proxy
import byteio

def test_proxy_smoke():
    response = proxy(b'GET / HTTP/1.1\r\nUser-Agent: test\r\n', byteio.BaseWriter())
    assert response.startswith(b'HTTP/1.1 200 OK\n'), response
    assert response.endswith(b'</html>\n'), response

