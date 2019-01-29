from telnet_server import Handler, proxy
import byteio

# (printf 'GET / HTTP/1.1\n\n' | nc 127.0.0.1 5017) &(printf 'GET / HTTP/1.1\n\n' | nc 127.0.0.1 5017)

def test_proxy_smoke():
    response = proxy(b'GET / HTTP/1.1\r\nUser-Agent: test\r\n', byteio.BaseWriter())
    assert response.startswith(b'HTTP/1.1 200 OK\n'), response
    assert response.endswith(b'</html>\n'), response

