from CTAgents import CTAgent
from Commitment import Commitment


def get_choice(choices):
    user_input = ""
    count = 0
    while user_input not in choices:
        if count > 0:
            print('Select one of the following: ' + str(choices))
        user_input = input()
        count += 1
    return user_input


class HumanCTAgent(CTAgent):
    def __init__(self, unique_id, model, coords):
        super().__init__(unique_id, model, coords)
        self.human = False

    def is_human(self):
        return self.human

    def offer(self, other_agent=None):
        offer = ["Y", "Yes", "No", "N"]
        colours = ['Red', 'Blue', 'Yellow', 'Green']
        choice = ""

        if other_agent is None:
            other_agent = self.model.pick_agent(self)
        print('----------------------------------------------')
        print('These are your current tiles: ' + str(self.tiles))
        print('Do you want to offer a tile?')
        result = get_choice(offer)
        if result == 'Y' or result == 'Yes':
            print('What tile do you need?')
            result = get_choice(colours)
            self.tile_wanted = result
            print('What tile do you want to offer for trade?')
            result = get_choice(colours)
            self.tile_offered = result
            offer = self.make_offer(other_agent)
            self.add_offer_to_memory(offer, True)
            # Send offer message to other agent
            other_agent.send_offer(offer)
            print('Offer Sent!')

    def evaluate_offers(self):
        print('----------------------------------------------')
        # Create a DataFrame with offers that have not yet been reviewed
        offers = self.memory[(self.memory['evaluated'] == False)]
        # for each offer
        if len(offers) == 0:
            print('No Offers to Review')
            return

        for index, offer in offers.iterrows():
            creditor = offer['creditor']
            tile_requested = offer['antecedent']
            tile_offered = offer['consequent']
            self.memory.at[index, 'evaluated'] = True
            # Check if it aligns with the agents values
            self.evaluate_offer(index, creditor, tile_offered, tile_requested)

    def evaluate_offer(self, offer_id, other_agent, tile_offered, tile_requested):
        offer = ["Y", "Yes", "No", "N"]

        print('You have received an offer for trade from agent ' + str(other_agent.unique_id))
        print('The agent is asking for a ' + str(tile_requested) + " tile .")
        print('The agent is offering a ' + str(tile_offered) + " tile in return.")
        print('These are your current tiles: ' + str(self.tiles))
        print('Do you accept the trade?')
        result = get_choice(offer)
        if result == 'Y' or result == 'Yes':
            commitment = Commitment(offer_id, other_agent, self, tile_requested, tile_offered)
            # if the antecedent holds
            if commitment.antecedent():
                # if the consequent holds
                if commitment.consequent():
                    # we release the commitment
                    self.model.released_commitments += 1
        else:
            print('Do you want to send a counter offer?')
            result = get_choice(offer)
            if result == 'Y' or result == 'Yes':
                self.offer(other_agent)

    def move(self):
        if not self.active:
            return
        print('----------------------------------------------')
        if self.strikes >= 3:
            print('You have reached three strikes, you are out!')
            self.active = False
            return
        if self.pos == self.model.get_goal():
            print('Congratulations, you reached the goal!')
            self.active = False
            return

        move = self.check_movement()
        print('Which way do you want to move?')
        print('These are your current tiles: ' + str(self.tiles))
        print('You can move in these directions: ' + str(move))
        result = get_choice(move)
        x, y = self.move_agent(result)
        # find the colour of the tile we are moving too
        colour = self.model.get_tile(x, y).colour
        if self.tiles[colour] > 0:
            self.strikes = 0
            self.model.grid.move_agent(self, (x, y))
            self.tiles[colour] -= 1
            self.num_of_moves += 1
        else:
            print('You did not have the tiles to move that way')
            self.strikes += 1
            print('Strike ' + str(self.strikes) + "!")

    def move_agent(self, direction):
        x, y = self.pos
        if direction == "Up":
            y += 1
        elif direction == "Down":
            y -= 1
        elif direction == "Left":
            x -= 1
        elif direction == "Right":
            x += 1
        return x, y

    def check_movement(self) -> list:
        move = ["Up", "Down", "Left", "Right"]
        x, y = self.pos
        if x - 1 < 0:
            move.remove("Left")
        if x + 1 >= self.model.grid.width:
            move.remove("Right")
        if y - 1 < 0:
            move.remove("Down")
        if y + 1 >= self.model.grid.height:
            move.remove("Up")
        return move

    # Overriding these methods as a human agent doesn't need pathfinding
    def find_all_paths(self, model, path, x, y):
        pass

    def filter_paths(self):
        pass

    def select_path(self):
        pass

    def analyse_path(self):
        pass
