from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.ModularVisualization import ModularServer

from CooperativeCTAgent import CooperativeCTAgent
from IntelligentCTAgent import IntelligentCTAgent
from SelfishCTAgent import SelfishCTAgent
from HumanAgent import HumanCTAgent
from CTAgents import Tile, CTAgent
from CTModel import CTModel


def draw_coloured_trails(agent):
    portrayal = {"Filled": "true", }

    if type(agent) is Tile:
        portrayal["Shape"] = "rect"
        portrayal["h"] = 1.0
        portrayal["w"] = 1.0
        portrayal["Color"] = agent.return_tile_colour()
        portrayal["Layer"] = 0
        if agent.goal:
            portrayal["text"] = "Goal"
            portrayal["text_color"] = "Black"

    elif isinstance(agent, CTAgent):
        portrayal["Shape"] = "circle"
        portrayal["r"] = 0.5
        portrayal["Color"] = "Black"
        portrayal["Layer"] = 1
        portrayal["text"] = "CT " + str(agent.unique_id)
        portrayal["text_color"] = "White"

        if isinstance(agent, SelfishCTAgent):
            portrayal["text"] = "S " + str(agent.unique_id)
        elif isinstance(agent, CooperativeCTAgent):
            portrayal["text"] = "C " + str(agent.unique_id)
        elif isinstance(agent, IntelligentCTAgent):
            portrayal["text"] = "I " + str(agent.unique_id)
        elif isinstance(agent, HumanCTAgent):
            portrayal["text"] = "H " + str(agent.unique_id)
            portrayal["Color"] = "Grey"

        if not agent.active:
            portrayal["r"] = 0.25

    return portrayal


CTChart = ChartModule([{"Label": "Success",
                        "Color": "Black"}],
                      data_collector_name='datacollector')

model_params = {
    "height": 6,
    "width": 6,
    "CTAgents": UserSettableParameter("slider", "CTAgents", 2, 0, 5, 1),
    "CooperativeCTAgents": UserSettableParameter("slider", "CooperativeCTAgents", 0, 0, 5, 1),
    "SelfishCTAgents": UserSettableParameter("slider", "SelfishCTAgents", 0, 0, 5, 1),
    "IntelligentCTAgents": UserSettableParameter("slider", "IntelligentCTAgents", 0, 0, 5, 1),
    "HumanCTAgents": UserSettableParameter("slider", "HumanCTAgents", 0, 0, 5, 1)
}

CTgrid = CanvasGrid(draw_coloured_trails, 6, 6, 500, 500)

server = ModularServer(CTModel,
                       [CTgrid, CTChart],
                       "Colored Trails Model",
                       model_params)
server.port = 8521  # The default
server.launch()
