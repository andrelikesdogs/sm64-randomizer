import numpy as np
import RandomModules.Levels as LevelRandomizer
from Entities.LevelGeometry import LevelGeometry
from Parsers.Level import Level

mock_level = Level(0, 1e10, 0x0, "Testing Mock Level")
mock_geometry = LevelGeometry(mock_level)
mock_geometry.add_area(0, [
  # center triangle
  [-1.0, -1.0, 0.0],
  [1.0, -1.0, 0.0],
  [0.0, 1.0, 0.0],

  [-1.0, -1.0, 10.0],
  [1.0, -1.0, 10.0],
  [0.0, 1.0, 10.0],

  [9.0, 9.0, 0.0],
  [11.0, 9.0, 0.0],
  [9.0, 11.0, 0.0],
], [
  [0, 1, 2],
  [3, 4, 5],
  [6, 7, 8]
], 0x0)

class TestGeometry(object):
  def test_trace_hit(self):
    # straight down through one
    (count, intersections) = LevelRandomizer.trace_geometry_intersections(mock_geometry, (np.array([0.0, 0.0, 1.0]), np.array([0.0, 0.0, -1000000])))
    assert count == 1

    (count, intersections) = LevelRandomizer.trace_geometry_intersections(mock_geometry, (np.array([0.0, 0.0, 1000000.0]), np.array([0.0, 0.0, -1000000])))
    assert count == 2

    (count, intersections) = LevelRandomizer.trace_geometry_intersections(mock_geometry, (np.array([10.0, 10.0, 100.0]), np.array([10.0, 10.0, -100.0])))
    assert count == 1