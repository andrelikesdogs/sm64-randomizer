from typing import NamedTuple

class Level(NamedTuple):
  address_start: int
  address_end: int
  level_id: int
  name: str

  @property
  def address(self):
    return (self.address_start, self.address_end)

