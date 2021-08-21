from CTAgents import CTAgent, make_message


def offer_success_rate(offers, commitments) -> int:
    total_offers = len(offers)
    total_commitments = len(commitments)
    if total_offers > 0:
        return total_commitments / total_offers
    else:
        return total_offers


class IntelligentCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)

    def evaluate_offer(self, offer_id, other_agent, tile_wanted, tile_offered):
        if self.calculate_response(other_agent):
            # Trade is possible - agree to make a commitment
            message = make_message(offer_id, other_agent, self, "ACCEPT",
                                   tile_wanted, tile_offered)
            self.add_message_to_memory(message, True)
            # Send offer message to other agent
            other_agent.send_message(message)
        else:
            message = make_message(offer_id, other_agent, self, "REJECT",
                                   tile_wanted, tile_offered)
            self.add_message_to_memory(message, True)
            # Send offer message to other agent
            other_agent.send_message(message)
            # Sends a counter offer back if possible
            self.counter_offer(other_agent, tile_wanted, tile_offered, offer_id)

    def calculate_response(self, other_agent):
        # All offers from the other agent to this agent
        self_offers = self.messages[(self.messages['message_type'] == 'OFFER') &
                                    (self.messages['debtor'] == other_agent)]

        # Offers from this agent accepted from other agent
        self_accepted_commitments = self.messages[(self.messages['message_type'] == 'ACCEPT') &
                                                  (self.messages['debtor'] == other_agent)]

        # Offers from this agent that other agent accepted
        other_accepted_commitments = self.messages[(self.messages['message_type'] == 'ACCEPT') &
                                                   (self.messages['creditor'] == other_agent)]

        # All offers from this agent to the other agent
        other_offers = self.messages[(self.messages['message_type'] == 'OFFER') &
                                     (self.messages['creditor'] == other_agent)]

        # This agents success rate at forming commitments
        self_success = offer_success_rate(self_offers, self_accepted_commitments)
        # Other agents success rate at forming commitments
        other_success = offer_success_rate(other_offers, other_accepted_commitments)

        # if this agents success rate is less than the other agents
        # return true, otherwise return false
        if self_success <= other_success:
            return True
        else:
            # if self_success is higher than other_success,
            # other_agent has accepted less than this agent
            return False

    # def send_tile(self, commitment_id, agent_receiving, tile):
    #     pass