from CTAgents import CTAgent, make_message


class CompetitiveCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)

    # A competitive agent will always accept offers
    # So it can then take a tile from the other agent
    def evaluate_offer(self, offer_id, other_agent, tile_wanted, tile_offered):
        message = make_message(offer_id, self, other_agent, "ACCEPT",
                               tile_offered, tile_wanted)
        message['conditional'] = True
        self.add_message_to_memory(message, True)
        # Send offer message to other agent
        other_agent.send_message(message)

    def execute_detached(self):
        # Create a list of detached commitments
        commitments = self.messages[(self.messages['message_type'] == 'DETACH') &
                                    (self.messages['debtor'] == self) &
                                    (self.messages['read'] == False)]

        for index, commitment in commitments.iterrows():
            self.messages.at[index, 'read'] = True
            creditor = commitment['creditor']
            antecedent = commitment['antecedent']
            consequent = commitment['consequent']

            message = make_message(index, self, creditor, 'CANCEL',
                                   antecedent, consequent)
            message['conditional'] = True
            message['detached'] = True
            message['satisfied'] = False
            self.add_message_to_memory(message, True)
            # Send offer message to other agent
            creditor.send_message(message)