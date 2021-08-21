from CTAgents import CTAgent, make_message
from Commitment import Commitment


class CooperativeCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)

    def evaluate_offer(self, offer_id, other_agent, tile_wanted, tile_offered):
        if self.can_help(tile_wanted):
            # Trade is possible - agree to make a commitment
            message = make_message(offer_id, other_agent, self, "ACCEPT",
                                   tile_wanted, tile_offered)
            self.add_message_to_memory(message, True)
            # Send offer message to other agent
            other_agent.send_message(message)
        else:
            # If Agent does not have these tile to give reject that offer
            message = make_message(offer_id, other_agent, self, "REJECT",
                                   tile_wanted, tile_offered)
            self.add_message_to_memory(message, True)
            # Send offer message to other agent
            other_agent.send_message(message)
            # Sends a counter offer back if possible
            self.counter_offer(other_agent, tile_wanted, tile_offered, offer_id)

    def can_help(self, tile_wanted):
        # Agent checks if they have the tile requested
        if self.path_tiles[tile_wanted] > 0:
            # if self.tiles[tile_wanted] > 0:
            return True
        else:
            return False
