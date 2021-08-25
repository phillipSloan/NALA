from CTAgents import CTAgent


class CooperativeCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)

    def can_help(self, tile_wanted):
        # Agent checks if they have the tile requested
        if self.path_tiles[tile_wanted] > 0:
            return True
        else:
            return False
