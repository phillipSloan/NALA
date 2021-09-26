from CTModel import *
import random
import pandas as pd

commitments_satisfied = 0
conditional_commitments = 0
commitments_detached = 0

model = CTModel(4, 4, CooperativeCTAgents=1, CTAgents=1)
x = 100
for i in range(x):
    model.run_model()
    commitments_satisfied += model.released_commitments
    commitments_detached += model.detached_commitments
    conditional_commitments += model.commitments_created
    model.reset_model()
agent_list = model.create_agent_list()

overall = 0
for agent in agent_list:
    print(str(agent) + ' id = ' + str(agent.unique_id) + ' score is ' + str(agent.score))
    print(str(agent) + ' id = ' + str(agent.unique_id) + ' won ' + str(agent.games_won) + ' games')
    print(str(agent) + ' id = ' + str(agent.unique_id) + ' reached the goal  ' + str(agent.reached_goal) + ' times')
    print()
    overall += agent.score

print('overall = ' + str(overall))

agent = random.choice(agent_list)
file_name = str(agent) + '.csv'
agent.messages.to_csv('/Users/phillip/Documents/thesis/' + file_name)
df = agent.messages

conditionals = df[(df['message_type'] == 'ACCEPT')]
print('Number of Reciprocal Commitments created in this game was ' + str(conditionals['reciprocal'].sum()))
# detached = df[(df['message_type'] == 'DETACH')]
# print('Number of Detached Commitments created in this game was ' + str(detached['detached'].sum()))
satisfied = df[(df['message_type'] == "SATISFIED")]
print('Number of Satisfied Commitments for this game was ' + str(satisfied['satisfied'].sum()))

# scores = pd.DataFrame.from_dict(model.agent_scores)
# scores.to_csv('/Users/phillip/Documents/thesis/scores.csv')
