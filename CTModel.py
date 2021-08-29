import random

from mesa import Model
from mesa.datacollection import DataCollector
from CTtime import CTSchedule
from mesa.space import MultiGrid
from CTAgents import CTAgent, Tile
from CooperativeCTAgent import CooperativeCTAgent
from SelfishCTAgent import SelfishCTAgent
from IntelligentCTAgent import IntelligentCTAgent
from CompetitiveCTAgent import CompetitiveCTAgent
from HumanAgent import HumanCTAgent


def success_negotiations(model):
    return model.released_commitments


class CTModel(Model):
    def __init__(
            self,
            height=4,
            width=4,
            CTAgents=0,
            CooperativeCTAgents=0,
            SelfishCTAgents=0,
            IntelligentCTAgents=0,
            CompetitiveCTAgents=0,
            HumanCTAgents=0
    ):
        super().__init__()
        self.height = height
        self.width = width
        self.grid = MultiGrid(width, height, False)
        self.schedule = CTSchedule(self, ["offer", "evaluate_offers",
                                          "execute_conditionals", "execute_detached"],
                                   ["move"])
        self._goal = (self.random.randrange(
            self.grid.height), self.random.randrange(self.grid.width))
        self.CTAgents = CTAgents
        self.CooperativeCTAgents = CooperativeCTAgents
        self.SelfishCTAgents = SelfishCTAgents
        self.IntelligentCTAgents = IntelligentCTAgents
        self.CompetitiveCTAgents = CompetitiveCTAgents
        self.HumanCTAgents = HumanCTAgents

        self.add_tiles()
        self.add_agents()
        self.released_commitments = 0
        self.detached_commitments = 0
        self.commitments_created = 0
        self.game_number = 1
        self.agents_negotiating = True
        self.agents_select_path = True

        self._id = 0

        self.datacollector = DataCollector(
            model_reporters={"Success": success_negotiations},
        )

    def return_id(self) -> int:
        self._id += 1
        return self._id - 1

    def get_goal(self):
        return self._goal

    def get_manhattan(self) -> int:
        return (self.height - 1) + (self.width - 1)

    # Provides a set of coordinates for an agent to be placed into the model.
    # Avoids placing the agent on the same coordinates as the models goal.
    def return_coords(self):
        xy = (self.random.randrange(self.grid.height), self.random.randrange(self.grid.width))
        while xy == self._goal:
            xy = (self.random.randrange(self.grid.height), self.random.randrange(self.grid.width))
        return xy

    def add_tiles(self):
        # Add Tiles to the Model
        for x in range(self.grid.height):
            for y in range(self.grid.width):
                tile = Tile(self.next_id(), self, (x, y))
                self.grid.place_agent(tile, (x, y))
                self.schedule.add(tile)

    def run_model(self) -> None:
        while self.running:
            self.step()

    def reset_model(self) -> None:
        self.running = True
        self.agents_negotiating = True
        self.agents_select_path = True
        self.released_commitments = 0
        self.detached_commitments = 0
        self.commitments_created = 0
        self._goal = (self.random.randrange(self.grid.height), self.random.randrange(self.grid.width))
        self.move_agents()
        self.schedule.steps = 0
        self.game_number += 1

    def move_agents(self):
        # Reset agents on the grid
        agent_list = self.create_agent_list()
        for agent in agent_list:
            coords = self.return_coords()
            self.grid.move_agent(agent, coords)
            agent.reinitialize_agent(coords)

    def add_agents(self):
        # Place agents onto the model
        for i in range(self.CTAgents):
            coords = self.return_coords()
            agent = CTAgent(self.next_id(), self, coords)
            self.schedule.add(agent)
            self.grid.place_agent(agent, coords)

        for i in range(self.CooperativeCTAgents):
            coords = self.return_coords()
            agent = CooperativeCTAgent(self.next_id(), self, coords)
            self.schedule.add(agent)
            self.grid.place_agent(agent, coords)

        for i in range(self.SelfishCTAgents):
            coords = self.return_coords()
            agent = SelfishCTAgent(self.next_id(), self, coords)
            self.schedule.add(agent)
            self.grid.place_agent(agent, coords)

        for i in range(self.IntelligentCTAgents):
            coords = self.return_coords()
            agent = IntelligentCTAgent(self.next_id(), self, coords)
            self.schedule.add(agent)
            self.grid.place_agent(agent, coords)

        for i in range(self.CompetitiveCTAgents):
            coords = self.return_coords()
            agent = CompetitiveCTAgent(self.next_id(), self, coords)
            self.schedule.add(agent)
            self.grid.place_agent(agent, coords)

        for i in range(self.HumanCTAgents):
            coords = self.return_coords()
            agent = HumanCTAgent(self.next_id(), self, coords)
            self.schedule.add(agent)
            self.grid.place_agent(agent, coords)

    ''' Returns the tile agent, from an x,y grid coordinate '''

    def get_tile(self, x, y) -> Tile:
        for tile in self.grid[x][y]:
            if isinstance(tile, Tile):
                return tile

    ''' Sets Tiles from True -> False and False -> True '''

    def set_tile_visited(self, x, y):
        for tile in self.grid[x][y]:
            if isinstance(tile, Tile):
                if tile.visited:
                    tile.visited = False
                else:
                    tile.visited = True

    # Returns a list of only CTAgents
    def create_agent_list(self):
        all_agents = self.schedule.agents.copy()
        agent_list = []
        for agent in all_agents:
            if isinstance(agent, CTAgent):
                agent_list.append(agent)
        return agent_list

    def pick_agent(self, agent):
        all_agents = self.create_agent_list()
        all_agents.remove(agent)
        return random.choice(all_agents)

    def still_running(self):
        all_agents = self.create_agent_list()
        for agent in all_agents:
            if agent.active:
                return True
        return False

    def score_agents(self):
        all_agents = self.create_agent_list()
        for agent in all_agents:
            score = 0
            tiles_remaining = sum(agent.tiles.values())
            if agent.pos == self.get_goal():
                score = agent.num_of_moves * 3 + tiles_remaining
            else:
                score = agent.num_of_moves * 1.5 + tiles_remaining

            agent.score += score

    def get_scores(self):
        return self.agent_scores

    def step(self):
        if self.schedule.steps == 15:
            self.agents_negotiating = False

        if self.agents_negotiating:
            self.schedule.step()
            self.datacollector.collect(self)
        else:

            if self.agents_select_path:
                agents = self.create_agent_list()
                for agent in agents:
                    agent.select_path()
                self.agents_select_path = False

            self.schedule.move_agents()
            if not self.still_running():
                self.running = False

                self.score_agents()


        ''' What is a successful negotiation
         is it when tiles are traded?
         or is it when a commitment is made?
         
         look in literature to check which is successful
         
         what is the ratio of commitments to released commitments?
         
         '''
