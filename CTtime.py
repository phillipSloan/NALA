from mesa.time import StagedActivation
from collections import OrderedDict
from typing import Dict, Iterator, List, Optional, Union
from mesa.agent import Agent
from mesa.model import Model

TimeT = Union[float, int]


class CTSchedule(StagedActivation):
    """A scheduler which allows agent activation to be divided into several
        stages instead of a single `step` method. All agents execute one stage
        before moving on to the next.

        Agents must have all the stage methods implemented. Stage methods take a
        model object as their only argument.

        This schedule tracks steps and time separately. Time advances in fractional
        increments of 1 / (# of stages), meaning that 1 step = 1 unit of time.
        """

    def __init__(
            self,
            model: Model,
            stage_list: Optional[List[str]] = None,
            move_list: Optional[List[str]] = None,
            shuffle: bool = False,
            shuffle_between_stages: bool = False,
    ) -> None:
        """Create an empty Staged Activation schedule.

        Args:
            model: Model object associated with the schedule.
            stage_list: List of strings of names of stages to run, in the
                         order to run them in.
            shuffle: If True, shuffle the order of agents each step.
            shuffle_between_stages: If True, shuffle the agents after each
                                    stage; otherwise, only shuffle at the start
                                    of each step.

        """
        super().__init__(model, stage_list)
        self.move_list = ["move"] if not move_list else move_list
        self.shuffle = shuffle
        self.shuffle_between_stages = shuffle_between_stages
        self.stage_time = 1 / len(self.stage_list)

    def move_agents(self) -> None:
        agent_keys = list(self._agents.keys())
        if self.shuffle:
            self.model.random.shuffle(agent_keys)
        for stage in self.move_list:
            for agent_key in agent_keys:
                getattr(self._agents[agent_key], stage)()  # Run stage
            if self.shuffle_between_stages:
                self.model.random.shuffle(agent_keys)
            self.time += self.stage_time
