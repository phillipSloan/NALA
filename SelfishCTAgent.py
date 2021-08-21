from CTAgents import CTAgent, make_message
from Commitment import Commitment


class SelfishCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)

    # Selfish agent will only accept an offer if it matches
    # what they need, rejecting everything else
    def evaluate_offer(self, offer_id, other_agent, tile_wanted, tile_offered):
        # Checking to see if this trade helps the agent reach the goal
        if self.helpful_trade(tile_offered):
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

    def helpful_trade(self, tile_offered):
        if self.path_tiles[tile_offered] < 0:
            return True
        else:
            return False



