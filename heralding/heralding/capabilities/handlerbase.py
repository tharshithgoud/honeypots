# Copyright (C) 2017 Johnny Vestergaard <jkv@unixcluster.dk>
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

import asyncio
import logging

from heralding.misc.session import Session

logger = logging.getLogger(__name__)


class HandlerBase:
  MAX_GLOBAL_SESSIONS = 800
  global_sessions = 0

  def __init__(self, options, loop):
    """
        Base class that all capabilities must inherit from.

        :param options: a dictionary of configuration options.

        """
    self.loop = loop
    self.options = options
    self.sessions = {}
    self.users = {}

    self.port = int(options['port'])
    if 'timeout' in options:
      self.timeout = options['timeout']
    else:
      self.timeout = 30

  def create_session(self, address, dest_address):
    protocol = self.__class__.__name__.lower()
    session = Session(address[0], address[1], protocol, self.users,
                      dest_address[1], dest_address[0])
    self.sessions[session.id] = session
    HandlerBase.global_sessions += 1
    logger.debug('Accepted %s session on %s:%s from %s:%s. (%s)', protocol,
                 dest_address[0], dest_address[1], address[0], address[1],
                 str(session.id))
    logger.debug('Size of session list for %s: %s', protocol,
                 len(self.sessions))
    return session

  def close_session(self, session):
    logger.debug('Closing session. (%s)', str(session.id))
    session.end_session()
    if session.id in self.sessions:
      del self.sessions[session.id]
    else:
      assert False
    HandlerBase.global_sessions -= 1

  async def execute_capability(self, reader, writer, session):
    reader = None  # NOQA
    writer = None  # NOQA
    session = None  # NOQA
    raise Exception("Must be implemented by child")

  async def handle_session(self, reader, writer):
    address = writer.get_extra_info('peername')
    dest_address = writer.get_extra_info('sockname')

    if HandlerBase.global_sessions > HandlerBase.MAX_GLOBAL_SESSIONS:
      protocol = self.__class__.__name__.lower()
      logger.warning(
          'Got %s session on port %s from %s:%s, but not handling it because the global session limit has '
          'been reached', protocol, self.port, *address)
    else:
      session = self.create_session(address, dest_address)
      try:
        await asyncio.wait_for(
            self.execute_capability(reader, writer, session),
            timeout=self.timeout,
            loop=self.loop)
      except asyncio.TimeoutError:
        logger.debug('Session timed out. (%s)', session.id)
      except (BrokenPipeError, ConnectionError) as err:
        logger.debug('Unexpected end of session: %s, errno: %s. (%s)', err,
                     err.errno, session.id)
      except (UnicodeDecodeError, KeyboardInterrupt):
        pass
      finally:
        self.close_session(session)
        if not self.loop.is_closed():
          writer.close()
