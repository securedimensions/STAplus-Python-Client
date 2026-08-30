# Copyright (C) 2026 Secure Dimensions GmbH, Munich, Germany.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from typing import Any


class CellAttribute:
    """
    Optional Cell navigation for type checkers and for sta_dggs_client.compose().

    Cell JSON round-trip is provided by STA-DGGS when the clients are composed.
    The value is typically a sta_dggs_client.model.cell.Cell instance.
    """

    @property
    def cell(self) -> Any:
        return getattr(self, '_cell', None)

    @cell.setter
    def cell(self, value: Any) -> None:
        self._cell = value
