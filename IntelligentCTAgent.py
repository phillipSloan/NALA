from CTAgents import CTAgent
from Commitment import Commitment


def offer_success_rate(offers) -> int:
    total_offers = len(offers)
    if total_offers > 0:
        offers_accepted = offers['conditional'].sum()
        return offers_accepted / total_offers
    else:
        return total_offers


class IntelligentCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)

    def evaluate_offer(self, offer_id, other_agent, tile_requested, tile_offered):
        if self.calculate_response(other_agent):
            commitment = Commitment(offer_id, other_agent, self, tile_requested, tile_offered)
            # if the antecedent holds
            if commitment.antecedent():
                # if the consequent holds
                if commitment.consequent():
                    # we release the commitment
                    self.model.released_commitments += 1
        else:
            self.offer(other_agent)

    def calculate_response(self, other_agent):
        # Offers from the other agent to this agent
        offers_other_to_self = self.memory[(
                self.memory['creditor'] == other_agent)]

        # Offers from this agent to the other agent
        offers_self_to_other = self.memory[(
                self.memory['debtor'] == other_agent)]

        # This agents success rate at forming commitments
        self_success = offer_success_rate(offers_other_to_self)
        # Other agents success rate at forming commitments
        other_success = offer_success_rate(offers_self_to_other)

        # if this agents success rate is less than the other agents
        # return true, otherwise return false
        if self_success <= other_success:
            return True
        else:
            # if self_success is higher than other_success,
            # other_agent has accepted less than this agent
            return False
