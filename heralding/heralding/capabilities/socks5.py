# Copyright (C) 2018 Roman Samoilenko <ttahabatt@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from heralding.capabilities.handlerbase import HandlerBase

# Socks constants
SOCKS_VERSION = b'\x05'
AUTH_METHOD = b'\x02'  # username/password authentication. RFC 1929
SOCKS_FAIL = b'\xFF'

logger = logging.getLogger(__name__)


class Socks5(HandlerBase):

  async def execute_capability(self, reader, writer, session):
    await self._handle_session(reader, writer, session)

  async def _handle_session(self, reader, writer, session):
    # 257 - max bytes number for greeting according to RFC 1928
    greeting = await reader.read(257)
    if len(greeting) > 2:
      await self.try_authenticate(reader, writer, session, greeting)
    else:
      logger.debug("Incorrect client greeting string: %r" % greeting)
    session.end_session()

  async def try_authenticate(self, reader, writer, session, greeting):
    version, authmethods = self.unpack_msg(greeting)
    if version == SOCKS_VERSION:
      if AUTH_METHOD in authmethods:
        await self.do_authenticate(reader, writer, session)
      else:
        writer.write(SOCKS_VERSION + SOCKS_FAIL)
        await writer.drain()
      session.set_auxiliary_data(self.get_auxiliary_data(authmethods))
    else:
      logger.debug("Wrong socks version: %r" % version)

  async def do_authenticate(self, reader, writer, session):
    writer.write(SOCKS_VERSION + AUTH_METHOD)
    await writer.drain()
    # 513 - max bytes number for username/password auth according to RFC 1929
    auth_data = await reader.read(513)
    if len(auth_data) > 2:
      username, password = self.unpack_auth(auth_data)
      session.add_auth_attempt(
          'plaintext', username=username.decode(), password=password.decode())
      writer.write(AUTH_METHOD + SOCKS_FAIL)
      await writer.drain()
    else:
      logger.debug("Wrong authentication data: %r" % auth_data)

  def get_auxiliary_data(self, authmethods):
    _methods = []
    for m in authmethods:
      if m == 2:
        _methods.append("USERNAME/PASSWORD")
      elif m == 0:
        _methods.append("NO AUTHENTICATION REQUIRED")
      elif m == 1:
        _methods.append("GSSAPI")
      elif 3 <= m <= 127:
        _methods.append("IANA ASSIGNED(%s)" % hex(m))
      elif 128 <= m <= 254:
        _methods.append("PRIVATE METHOD(%s)" % hex(m))
      elif m == 255:
        _methods.append("NO ACCEPTABLE METHODS")

    data = {"client_auth_methods": _methods}
    return data

  @staticmethod
  def unpack_msg(data):
    socks_version = data[:1]  # we need byte representation
    authmethods_n = data[1]
    authmethods = data[2:2 + authmethods_n]
    return socks_version, authmethods

  @staticmethod
  def unpack_auth(auth_data):
    ulen = auth_data[1]
    username = auth_data[2:2 + ulen]
    password_part = auth_data[2 + ulen:]
    if password_part:
      plen = password_part[0]
      password = auth_data[-plen:]
    else:
      password = b""
    return username, password
