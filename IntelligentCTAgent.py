from CTAgents import CTAgent, make_message


def success_rate(denominator, numerator):
    denom = len(denominator)
    numer = len(numerator)
    if denom > 0:
        return numer / denom
    else:
        return denom


class IntelligentCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)

    def evaluate_offer(self, offer_id, other_agent, tile_wanted, tile_offered):
        if self.calculate_response(other_agent) and self.can_help(tile_wanted):
            # Trade is possible - agree to make a commitment
            message = make_message(offer_id, self, self, other_agent, "ACCEPT",
                                   tile_offered, tile_wanted)
            message['reciprocal'] = True
            self.add_message_to_memory(message, True)
            # Send offer message to other agent
            other_agent.send_message(message)
        else:
            message = make_message(offer_id, self, other_agent, self, "REJECT",
                                   tile_wanted, tile_offered)
            self.add_message_to_memory(message, True)
            # Send offer message to other agent
            other_agent.send_message(message)
            # Sends a counter offer back if possible
            self.counter_offer(other_agent, tile_wanted, tile_offered, offer_id)

    def can_help(self, tile_wanted):
        # Agent checks if they have the tile requested
        if self.tiles[tile_wanted] > 0:
            return True
        else:
            return False

    def calculate_response(self, other_agent):
        # All offers from the other agent to this agent
        self_offers = self.messages[(self.messages['message_type'] == 'OFFER') &
                                    (self.messages['debtor'] == other_agent)]

        # Offers from this agent accepted from other agent
        self_accepted = self.messages[(self.messages['message_type'] == 'ACCEPT') &
                                      (self.messages['debtor'] == self)]

        # Offers from this agent that other agent accepted
        other_accepted = self.messages[(self.messages['message_type'] == 'ACCEPT') &
                                       (self.messages['debtor'] == other_agent)]

        # All offers from this agent to the other agent
        other_offers = self.messages[(self.messages['message_type'] == 'OFFER') &
                                     (self.messages['debtor'] == self)]

        # This agents success rate at forming commitments
        self_success = success_rate(other_offers, self_accepted)
        # Other agents success rate at forming commitments
        other_success = success_rate(self_offers, other_accepted)

        # if this agents success rate is less than the other agents
        # return true, otherwise return false
        if self_success <= other_success:
            return True
        else:
            # if self_success is higher than other_success,
            # other_agent has accepted less than this agent
            return False

    def execute_conditionals(self):
        # Create a list of commitments that have not yet been actioned
        commitments = self.messages[(self.messages['message_type'] == 'ACCEPT') &
                                    (self.messages['creditor'] == self) &
                                    (self.messages['read'] == False)]

        for index, commitment in commitments.iterrows():
            self.messages.at[index, 'read'] = True
            debtor = commitment['debtor']
            msg_id = commitment['message_id']
            antecedent = commitment['antecedent']
            consequent = commitment['consequent']
            if self.calculate_swap(debtor) and self.send_tile(index, debtor, antecedent):
                message = make_message(msg_id, self, debtor, self, 'DETACHED',
                                       antecedent, consequent)
                # self.satisfy_commitment(commitment)
                message['reciprocal'] = True
                message['detached'] = True
                self.add_message_to_memory(message, True)
                # Send offer message to other agent
                debtor.send_message(message)
                self.model.detached_commitments += 1
            else:
                message = make_message(msg_id, self, debtor, self, 'RELEASE',
                                       antecedent, consequent)
                message['reciprocal'] = True
                message['detached'] = False
                self.add_message_to_memory(message, True)
                # Send offer message to other agent
                debtor.send_message(message)

    def execute_detached(self):
        self.execute_released()
        # Create a list of detached commitments
        commitments = self.messages[(self.messages['message_type'] == 'DETACHED') &
                                    (self.messages['debtor'] == self) &
                                    (self.messages['read'] == False)]

        for index, commitment in commitments.iterrows():
            self.messages.at[index, 'read'] = True
            msg_id = commitment['message_id']
            creditor = commitment['creditor']
            antecedent = commitment['antecedent']
            consequent = commitment['consequent']

            if self.calculate_swap(creditor) and self.send_tile(index, creditor, consequent):
                message = make_message(msg_id, self, self, creditor, 'SATISFIED',
                                       antecedent, consequent)
                message['reciprocal'] = True
                message['detached'] = True
                message['satisfied'] = True
                self.add_message_to_memory(message, True)
                # Send offer message to other agent
                creditor.send_message(message)
                self.model.released_commitments += 1
            else:
                message = make_message(msg_id, self, self, creditor, 'CANCEL',
                                       antecedent, consequent)
                message['reciprocal'] = True
                message['detached'] = True
                message['satisfied'] = False
                self.add_message_to_memory(message, True)
                # Send offer message to other agent
                creditor.send_message(message)

    def calculate_swap(self, other_agent):
        # All reciprocal commitments agreed by the this agent
        self_accepted_commitments = self.messages[(self.messages['message_type'] == 'ACCEPT') &
                                                  (self.messages['debtor'] == self)]

        # All reciprocal commitments cancelled by this agent
        self_cancelled_commitments = self.messages[(self.messages['message_type'] == 'CANCEL') &
                                                   (self.messages['debtor'] == self)]

        # All reciprocal commitments agreed by other agent
        other_accepted_commitments = self.messages[(self.messages['message_type'] == 'ACCEPT') &
                                                   (self.messages['debtor'] == other_agent)]

        # All reciprocal commitments cancelled by other agent
        other_cancelled_commitments = self.messages[(self.messages['message_type'] == 'CANCEL') &
                                                    (self.messages['debtor'] == other_agent)]

        self_cancel = success_rate(self_accepted_commitments, self_cancelled_commitments)
        other_cancel = success_rate(other_accepted_commitments, other_cancelled_commitments)

        if self_cancel >= other_cancel:
            return True
        else:
            return False
