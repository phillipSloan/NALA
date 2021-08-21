def verbose(other_agent, tile_requested, tile_offered):
    print('You have formed a commitment with Agent ' + str(other_agent.unique_id) + 'to exchange their '
          + str(tile_requested)) + ' tile for your ' + str(tile_offered) + 'tile.'


class Commitment:
    def __init__(self, offer_id, agent_debtor, agent_creditor, tile_requested, tile_offered):
        # C(debtor, creditor, antecedent_tile , consequent_tile)
        self.id = offer_id
        agent_debtor.model.commitments_created += 1
        self.debtor = agent_debtor
        self.creditor = agent_creditor
        self.consequent_tile = tile_offered
        self.antecedent_tile = tile_requested

        self.debtor.memory.at[self.id, 'conditional'] = True
        self.creditor.memory.at[self.id, 'conditional'] = True

        if self.debtor.is_human():
            verbose(self.creditor, self.antecedent_tile, self.consequent_tile)
        if self.creditor.is_human():
            verbose(self.creditor, self.consequent_tile, self.antecedent_tile)

    # Make a function for antecedent and consequent
    def antecedent(self):
        if self.creditor.send_tile(self.debtor, self.antecedent_tile):
            self.debtor.memory.at[self.id, 'detached'] = True
            self.creditor.memory.loc[self.id, 'detached'] = True
            return True
        else:
            return False

    def consequent(self):
        if self.debtor.send_tile(self.creditor, self.consequent_tile):
            self.debtor.memory.at[self.id, 'released'] = True
            self.creditor.memory.at[self.id, 'released'] = True
            return True
        else:
            return False
