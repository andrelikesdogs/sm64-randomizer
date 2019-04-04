from typing import NamedTuple

class Level(NamedTuple):
  address_start: int # start of level command area on ROM
  address_end: int # end of level command area on ROM
  level_id: int # not course-id
  name: str # human readable name
  level_area: int = 0 # area this levels painting is in

  @property
  def address(self):
    return (self.address_start, self.address_end)

