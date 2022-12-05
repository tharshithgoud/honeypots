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

import logging
import hpfeeds
import json

from heralding.reporting.base_logger import BaseLogger

logger = logging.getLogger(__name__)


class HpFeedsLogger(BaseLogger):

  def __init__(self, session_channel, auth_channel, host, port, ident, secret):
    super().__init__()
    self.session_channel = session_channel
    self.auth_channel = auth_channel
    self.host = host
    self.port = port
    self.ident = ident
    self.secret = secret
    self._initial_connection_happend = False
    logger.info('HpFeeds logger started.')

  def start(self):
    if not self._initial_connection_happend:
      self.hp_connection = hpfeeds.new(self.host, self.port, self.ident,
                                       self.secret, True)
      self._initial_connection_happend = True
      logger.info('HpFeeds logger connected to %s:%s.', self.host, self.port)
    # after we established that we can connect enter the subscribe and enter the polling loop
    super().start()

  def loggerStopped(self):
    self.stop()
    self.close()

  def handle_auth_log(self, data):
    if self._initial_connection_happend:
      self.hp_connection.publish(self.auth_channel, json.dumps(data).encode())

  def handle_session_log(self, data):
    if self._initial_connection_happend:
      self.hp_connection.publish(self.session_channel,
                                 json.dumps(data).encode())
