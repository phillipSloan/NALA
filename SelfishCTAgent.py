from CTAgents import CTAgent
from Commitment import Commitment


class SelfishCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)

    # Selfish agent will only accept an offer if it matches
    # what they need, rejecting everything else
    def evaluate_offer(self, offer_id, other_agent, tile_requested, tile_offered):
        # Checking to see if this trade helps the agent reach the goal
        if self.helpful_trade(tile_offered):
            commitment = Commitment(offer_id, other_agent, self, tile_requested, tile_offered)
            # if the antecedent holds
            if commitment.antecedent():
                # if the consequent holds
                if commitment.consequent():
                    # we release the commitment
                    self.model.released_commitments += 1
        else:
            self.offer(other_agent)

    def helpful_trade(self, tile_offered):
        if self.path_tiles[tile_offered] < 0:
            return True
        else:
            return False
