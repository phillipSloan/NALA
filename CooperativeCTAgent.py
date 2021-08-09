from CTAgents import CTAgent
from Commitment import Commitment


class CooperativeCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)

    def evaluate_offer(self, offer_id, other_agent, tile_requested, tile_offered):
        if self.can_help(tile_requested):
            # Trade is possible - agree to make a commitment
            # Add to dataframe here - commitment made with this offer
            commitment = Commitment(offer_id, other_agent, self, tile_requested, tile_offered)
            # if the antecedent holds
            if commitment.antecedent():
                # if the consequent holds
                if commitment.consequent():
                    # we release the commitment
                    self.model.released_commitments += 1
        else:
            # If Agent does not have these tile to give
            # Sends a counter offer back
            self.offer(other_agent)

    def can_help(self, tile_wanted):
        # Agent checks if they have the tile requested
        if self.tiles[tile_wanted] > 0:
            return True
        else:
            return False
