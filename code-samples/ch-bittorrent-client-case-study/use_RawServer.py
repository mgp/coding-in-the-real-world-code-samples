# To connect, run: nc localhost 8080

from threading import Event
from RawServer import RawServer

done_flag = Event()
class Handler:
  def external_connection_made(self, connection):
    connection.write("hello there stranger!\n")
  def connection_flushed(self, connection):
    # Wrote string, so close all connections and quit.
    done_flag.set()

timeout_check_interval = 60 * 60
timeout = timeout_check_interval
server = RawServer(done_flag, timeout_check_interval, timeout)
server.bind(8080)
server.listen_forever(Handler())

