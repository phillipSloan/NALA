def offered_before(self, other_agent, colour):
    offers = self.messages[(self.messages['debtor'] == self) &
                           (self.messages['creditor'] == other_agent)]

    for _, offer in offers.iterrows():
        if offer['consequent'] == colour:
            return True
    return False


def currently_offered(self, other_agent, colour):
    offers = self.messages[(self.messages['game_number'] == self.model.game_number) &
                           (self.messages['debtor'] == other_agent) &
                           (self.messages['creditor'] == self) &
                           (self.messages['message_type'] == "ACCEPT") &
                           (self.messages['consequent'] == colour)]

    for index, offer in offers.iterrows():
        messages = self.messages[(self.messages['message_id'] == index)]

        if (messages['message_type'] == 'SATISFIED').any():
            return True
        if (messages['message_type'] == 'CANCEL').any():
            return True
        if (messages['message_type'] == 'DETACH').any():
            return False
        if (messages['message_type'] == 'RELEASE').any():
            return False
    return False