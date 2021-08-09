from mesa import Agent
from Commitment import Commitment
import pandas as pd
import random


# Create a tile class - Each tile has a colour
class Tile(Agent):
    colours = list(('Red', 'Green', 'Blue', 'Yellow'))

    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        self.colour = random.choice(self.colours)
        self.pos = pos
        self.visited = False
        self.goal = False
        self.set_goal()

    def set_goal(self):
        self.goal = False
        if self.pos == self.model.get_goal():
            self.goal = True

    def return_tile_colour(self):
        return self.colour

    ''' Randomizes tile's colour on every iteration '''

    def move(self):
        pass

    def offer(self):
        pass

    def evaluate_offers(self):
        pass


def out_of_bounds(model, x, y):
    return x < 0 or y < 0 or x >= model.grid.height or y >= model.grid.width


def longest_path_length(paths):
    maximum = 0
    for path in paths:
        if path[1] > maximum:
            maximum = path[1]
    return maximum


# filter duplicates and paths not of the right length
def filter_paths(paths):
    maximum = longest_path_length(paths)
    filtered_paths = []
    for path, length in paths:
        if length == maximum:
            if path not in filtered_paths:
                filtered_paths.append(path)
    return filtered_paths


class CTAgent(Agent):
    def __init__(self, unique_id, model, pos):
        super().__init__(unique_id, model)
        # self.pos = coords
        self.active = True
        self.human = False
        self.num_of_moves = 0
        self.pos = pos
        self.strikes = 0
        self.score = 0
        self.tiles = {'Red': 0, 'Green': 0, 'Blue': 0, 'Yellow': 0}
        self.path_tiles = {}
        # List of all possible paths from the agents position to the goal
        self.all_paths = []
        self.filtered_paths = []
        # Paths the agent is able to get too
        self.possible_paths = []
        # Paths the agent will need to negotiate to get too
        self.negotiable_paths = []
        # Path the agent has selected to try and get too
        self.path = []
        # Tile the Agent Needs / Will Swap to get to through path
        self.tile_wanted = 'Blank'
        self.tile_offered = 'Blank'
        # Dataframe used to store the agents previous games
        self.memory = pd.DataFrame(
            columns=["step", "negotiation_id", "evaluated", "creditor", "debtor",
                     "antecedent", "consequent", "conditional", "detached", "released"])
        self.memory.set_index("negotiation_id", inplace=True)

        self.populate_agent_tiles()
        x, y = self.pos
        self.find_all_paths(self.model, [], x, y)
        self.filter_paths()
        self.select_path()
        self.analyse_path()


    ''' Ensures the Agent has x amount of tiles '''

    def populate_agent_tiles(self):
        colours = list(('Red', 'Green', 'Blue', 'Yellow'))
        x = 0
        total = int(self.model.get_manhattan() * 0.7)
        while x < total:
            # Popping a random colour out of the colours list
            colour = random.choice(colours)
            self.tiles[colour] += 1
            x += 1

        self.path_tiles = self.tiles.copy()

    ''' 
        Recursive DFS algorithm to find all possible paths from current
        position to the models goal position
    '''

    def find_all_paths(self, model, path, x, y):
        dx, dy = model.get_goal()
        # if we are outside of the grid, return
        if out_of_bounds(model, x, y):
            return

        '''
         if we are at the destination of the path, add the solution to
         the possible paths
        '''

        if x == dx and y == dy:
            path.append((x, y, self.model.get_tile(x, y).colour))
            # creating a new list in memory
            solution = path.copy()
            # removing the agents starting location from the route
            solution.pop(0)
            self.all_paths.append(solution)
            path.pop()
            return

        # if that path has been visited before, return
        if self.model.get_tile(x, y).visited:
            return

        # set as visited

        path.append([x, y, self.model.get_tile(x, y).colour])
        self.model.set_tile_visited(x, y)

        if y < dy:
            self.find_all_paths(model, path, x, y + 1)
        if x < dx:
            self.find_all_paths(model, path, x + 1, y)
        if y > dy:
            self.find_all_paths(model, path, x, y - 1)
        if x > dx:
            self.find_all_paths(model, path, x - 1, y)

        # backtracking
        self.model.set_tile_visited(x, y)
        path.pop()

    def shortest_path_length(self) -> int:
        # initially set to max int value
        shortest = 2147483647
        for path in self.all_paths:
            if len(path) < shortest:
                shortest = len(path)
        return shortest

    # filter duplicates and paths not of the right length
    def filter_paths(self):
        length = self.shortest_path_length()

        for path in self.all_paths:
            if length == len(path):
                if path not in self.filtered_paths:
                    self.filtered_paths.append(path)

    def select_path(self):
        self.path = random.choice(self.filtered_paths)

    def analyse_path(self):
        for path in self.path:
            _, _, colour = path
            self.path_tiles[colour] -= 1

    def add_offer_to_memory(self, offer, evaluated):
        if evaluated:
            offer['evaluated'] = True
        self.memory = self.memory.append(offer)
        offer['evaluated'] = False

    def needs_tiles(self):
        for value in self.path_tiles.values():
            if value < 0:
                return True
        return False

    def has_next_tile(self):
        _, _, colour = self.path[self.num_of_moves]
        if self.tiles[colour] > 0:
            return True
        else:
            return False

    def select_tile_needed(self):
        if not self.has_next_tile():
            _, _, colour = self.path[self.num_of_moves]
            self.tile_wanted = colour
        else:
            for key, value in self.path_tiles.items():
                if value < 0:
                    self.tile_wanted = key

    def select_tile_offered(self, other_agent):
        for tile_colour, amount in self.path_tiles.items():
            if self.path_tiles[tile_colour] > 0:
                if not self.offered_before(other_agent, tile_colour):
                    self.tile_offered = tile_colour
                    return True
        else:
            return False

    def offered_before(self, other_agent, colour):
        if len(self.memory) == 0:
            return False
        offers = self.memory[(self.memory['creditor'] == self)
                             & (self.memory['debtor'] == other_agent)]

        for _, offer in offers.iterrows():
            if offer['consequent'] == colour:
                return True
        return False

    def is_human(self):
        return self.human

    def make_offer(self, other_agent):
        offer = {"step": [self.model.schedule.steps],
                 "negotiation_id": [self.model.return_negotiation_id()],
                 "evaluated": [False],
                 "creditor": [self],
                 "debtor": [other_agent],
                 "antecedent": [self.tile_wanted],
                 "consequent": [self.tile_offered],
                 "conditional": [False],
                 "detached": [False],
                 "released": [False]
                 }
        offer = pd.DataFrame(offer)
        offer.set_index("negotiation_id", inplace=True)
        return offer

    # Sends an offer to another agent
    def offer(self, other_agent=None):
        if other_agent is None:
            other_agent = self.model.pick_agent(self)
        if self.needs_tiles():
            self.select_tile_needed()
            if self.select_tile_offered(other_agent):
                # Record an offered commitment and send the offer to the other agent
                offer = self.make_offer(other_agent)
                self.add_offer_to_memory(offer, True)
                # Send offer message to other agent
                other_agent.send_offer(offer)

    def send_offer(self, offer):
        self.add_offer_to_memory(offer, False)

    def evaluate_offers(self):
        # Create a DataFrame with offers that have not yet been reviewed
        offers = self.memory[(self.memory['evaluated'] == False)]
        # for each offer
        for index, offer in offers.iterrows():
            creditor = offer['creditor']
            tile_requested = offer['antecedent']
            tile_offered = offer['consequent']
            self.memory.at[index, 'evaluated'] = True
            # Check if it aligns with the agents values
            self.evaluate_offer(index, creditor, tile_offered, tile_requested)

    def evaluate_offer(self, offer_id, other_agent, tile_offered, tile_requested):
        # Basic agent always creates a commitment
        commitment = Commitment(offer_id, other_agent, self, tile_requested, tile_offered)
        # if the antecedent holds
        if commitment.antecedent():
            # if the consequent holds
            if commitment.consequent():
                # we release the commitment
                self.model.released_commitments += 1

    def send_tile(self, agent_receiving, tile):
        # remove the tiles from the agent and add them to the agent receiving the tiles
        # if the agent giving tiles has enough, perform the trade.
        if self.tiles[tile] > 0:
            self.tiles[tile] -= 1
            self.path_tiles[tile] -= 1
            agent_receiving.tiles[tile] += 1
            agent_receiving.path_tiles[tile] += 1
            return True
        else:
            return False

    def move(self):
        if not self.active:
            return
        if self.strikes >= 3:
            self.active = False
        if self.pos == self.model.get_goal():
            self.active = False

        if self.active:
            x, y, colour = self.path[self.num_of_moves]
            if self.tiles[colour] > 0:
                self.strikes = 0
                self.model.grid.move_agent(self, (x, y))
                self.tiles[colour] -= 1
                self.num_of_moves += 1
            else:
                self.strikes += 1
