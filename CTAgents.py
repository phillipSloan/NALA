from mesa import Agent
import pandas as pd
import random


def make_message(message_id, agent, other_agent, message_type, tile_wanted, tile_offered):
    message = {"step": [agent.model.schedule.steps],
               "message_id": [message_id],
               "read": [False],
               "message_type": [message_type],
               "debtor": [agent],
               "creditor": [other_agent],
               "antecedent": [tile_wanted],
               "consequent": [tile_offered],
               "conditional": [None],
               "detached": [None],
               "released": [None]
               }
    message = pd.DataFrame(message)
    message.set_index("message_id", inplace=True)
    return message


def make_swap(commitment_id, agent, tile):
    swap = {"step": [agent.model.schedule.steps],
            "commitment_id": [commitment_id],
            "agent": [agent],
            "tile": [tile]
            }
    swap = pd.DataFrame(swap)
    return swap


# Create a tile class - Each tile has a colour
class Tile(Agent):
    colours = list(('Red', 'Green', 'Blue', 'Yellow', 'Cyan'))

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

    def select_path(self):
        pass

    def check_for_commitments(self):
        pass

    def execute_commitments(self):
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
        self.first_move = True
        self.num_of_moves = 0
        self.pos = pos
        self.strikes = 0
        self.score = 0
        self.tiles = {'Red': 0, 'Green': 0, 'Blue': 0, 'Yellow': 0, 'Cyan': 0}
        self.path_tiles = {}
        # List of all possible paths from the agents position to the goal
        self.all_paths = []
        self.filtered_paths = []
        # Path the agent has selected to try and get too
        self.path = []
        # Tile the Agent Needs / Will Swap to get to through path
        self.tile_wanted = 'Blank'
        self.tile_offered = 'Blank'
        # Dataframe used to store the agents previous games
        self.messages = pd.DataFrame(
            columns=["step", "message_id", "read",
                     "message_type", "debtor",
                     "creditor", "antecedent", "consequent",
                     "conditional", "detached", "released"])
        self.messages.set_index("message_id", inplace=True)

        self.swaps = pd.DataFrame(
            columns=["step", "commitment_id", "agent", "tile"])

        self.populate_agent_tiles()
        x, y = self.pos
        self.find_all_paths(self.model, [], x, y)
        self.filter_paths()
        # Agent picks a path to offer on
        self.pick_path()
        self.analyse_path()

    ''' Ensures the Agent has x amount of tiles '''

    def populate_agent_tiles(self):
        colours = list(('Red', 'Green', 'Blue', 'Yellow', 'Cyan'))
        x = 0
        total = int(self.model.get_manhattan() * 0.5)
        while x < total:
            # Popping a random colour out of the colours list
            colour = random.choice(colours)
            self.tiles[colour] += 1
            x += 1

    ''' 
        Recursive DFS algorithm to find all possible paths from current
        position to the models goal position
    '''

    def find_all_paths(self, model, path, x, y):
        dx, dy = model.get_goal()
        # if we are outside of the grid, return
        if out_of_bounds(model, x, y):
            return

        #  if we are at the destination of the path, add the solution to
        #  the possible paths

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

    def pick_path(self):
        highest = -2147483648
        best_paths = []
        path_list = []
        for index, path in enumerate(self.filtered_paths):
            self.path = path
            self.analyse_path()
            length = 0
            for key, value in self.path_tiles.items():
                if value < 0:
                    length += value
            if length > highest:
                highest = length
            path_list.append((index, length))

        for path in path_list:
            if highest == path[1]:
                best_paths.append(self.filtered_paths[path[0]])

        self.path = random.choice(best_paths)
        self.analyse_path()

    def analyse_path(self):
        self.path_tiles = self.tiles.copy()
        for tile in self.path:
            _, _, colour = tile
            self.path_tiles[colour] -= 1

    def add_message_to_memory(self, message, read):
        if read:
            message['read'] = True
        self.messages = self.messages.append(message)
        message['read'] = False

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
        offers = self.messages[(self.messages['debtor'] == self) &
                               (self.messages['creditor'] == other_agent)]

        for _, offer in offers.iterrows():
            if offer['consequent'] == colour:
                return True
        return False

    def is_human(self):
        return self.human

    # Sends an offer to another agent
    def offer(self, other_agent=None):
        if other_agent is None:
            other_agent = self.model.pick_agent(self)

        if self.needs_tiles():
            self.select_tile_needed()
            if self.select_tile_offered(other_agent):
                # Record an offered commitment and send the offer to the other agent
                # offer = self.make_offer(self, other_agent)
                message = make_message(self.model.return_id(), self, other_agent, "OFFER",
                                       self.tile_wanted, self.tile_offered)
                self.add_message_to_memory(message, True)
                # Send offer message to other agent
                other_agent.send_message(message)

    def counter_offer(self, other_agent, tile_requested, tile_offered, message_id):
        # If the agents does not have the tile requested available
        if self.tiles[tile_requested] <= 0:
            return

        if self.needs_tiles():
            for new_colour, amount in self.path_tiles.items():
                if amount > 0:
                    if new_colour != tile_offered and new_colour != tile_requested:
                        # Generate Offer
                        message = make_message(message_id, other_agent, self, "COUNTER",
                                               tile_requested, new_colour)
                        self.add_message_to_memory(message, True)
                        # Send offer message to other agent
                        other_agent.send_message(message)
                        return

    def send_message(self, message):
        self.add_message_to_memory(message, False)

    def evaluate_offers(self):
        # Create a DataFrame with offers that have not yet been reviewed
        # offers = self.memory[(self.memory['evaluated'] == False)]
        offers = self.messages[(self.messages['message_type'] == 'OFFER') &
                               (self.messages['read'] == False)]
        # for each offer
        for index, offer in offers.iterrows():
            if offer['debtor'] is not self:
                debtor = offer['debtor']
                tile_wanted = offer['antecedent']
                tile_offered = offer['consequent']
                self.messages.at[index, 'read'] = True
                self.evaluate_offer(index, debtor, tile_wanted, tile_offered)
            else:
                creditor = offer['creditor']
                tile_wanted = offer['consequent']
                tile_offered = offer['antecedent']
                # Check if it aligns with the agents values
                self.messages.at[index, 'read'] = True
                self.evaluate_offer(index, creditor, tile_wanted, tile_offered)

    def evaluate_offer(self, offer_id, other_agent, tile_wanted, tile_offered):
        # Basic agent always sends an accept message back to the other agent
        message = make_message(offer_id, other_agent, self, "ACCEPT",
                               tile_wanted, tile_offered)
        self.add_message_to_memory(message, True)
        # Send offer message to other agent
        other_agent.send_message(message)

    def check_for_commitments(self):
        accept_msg = self.messages[(self.messages['message_type'] == "ACCEPT") &
                                   (self.messages['debtor'] == self) &
                                   (self.messages['read'] == False)]

        for index, commitment in accept_msg.iterrows():
            self.messages.at[index, 'read'] = True
            creditor = commitment['creditor']
            antecedent = commitment['antecedent']
            consequent = commitment['consequent']
            commitment = make_message(index, self, creditor, 'CREATE',
                                      antecedent, consequent)
            commitment['conditional'] = True
            self.add_message_to_memory(commitment, True)
            self.model.commitments_created += 1
            # Send offer message to other agent
            creditor.send_message(commitment)

    def execute_commitments(self):
        self.execute_conditionals()
        self.execute_detached()

    def execute_conditionals(self):
        # Create a list of commitments that have not yet been actioned
        commitments = self.messages[(self.messages['message_type'] == 'CREATE') &
                                    (self.messages['creditor'] == self) &
                                    (self.messages['read'] == False)]

        for index, commitment in commitments.iterrows():
            self.messages.at[index, 'read'] = True
            debtor = commitment['debtor']
            antecedent = commitment['antecedent']
            consequent = commitment['consequent']
            if self.send_tile(index, debtor, antecedent):
                commitment = make_message(index, debtor, self, 'DETACH',
                                          antecedent, consequent)
                commitment['conditional'] = True
                commitment['detached'] = True
                self.add_message_to_memory(commitment, True)
                # Send offer message to other agent
                debtor.send_message(commitment)
                self.model.detached_commitments += 1

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
            if self.send_tile(index, creditor, antecedent):
                commitment = make_message(index, self, creditor, 'RELEASE',
                                          antecedent, consequent)
                commitment['conditional'] = True
                commitment['detached'] = True
                commitment['released'] = True
                self.add_message_to_memory(commitment, True)
                # Send offer message to other agent
                creditor.send_message(commitment)
                self.model.released_commitments += 1

    def send_tile(self, commitment_id, agent_receiving, tile):
        # remove the tiles from the agent and add them to the agent receiving the tiles
        # if the agent giving tiles has enough, perform the trade.
        if self.tiles[tile] > 0:
            self.tiles[tile] -= 1
            self.path_tiles[tile] -= 1
            agent_receiving.tiles[tile] += 1
            agent_receiving.path_tiles[tile] += 1
            swap = make_swap(commitment_id, self, tile)
            agent_receiving.record_swap(swap)
            return True
        else:
            return False

    def record_swap(self, swap):
        self.swaps = self.swaps.append(swap)

    def select_path(self):
        if len(self.filtered_paths) == 1:
            self.path = random.choice(self.all_paths)
            return
        longest_paths = []
        lengths = []
        max_length = 0
        for index, path in enumerate(self.filtered_paths):
            path_length = 0
            tiles = self.tiles.copy()
            for tile in path:
                _, _, colour = tile
                path_length += 1
                tiles[colour] -= 1
                if tiles[colour] < 0:
                    path_length -= 1
                    break
            if path_length > max_length:
                max_length = path_length
            lengths.append((index, path_length))

        for length in lengths:
            if length[1] == max_length:
                longest_paths.append(self.filtered_paths[length[0]])
        self.path = random.choice(longest_paths)

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
