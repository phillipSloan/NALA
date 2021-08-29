from CTModel import *

commitments_satisfied = 0
conditional_commitments = 0
commitments_detached = 0

model = CTModel(4, 4, CTAgents=2)
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
    overall += agent.score
    file_name = str(agent) + '.csv'
    agent.messages.to_csv('/Users/phillip/Documents/thesis/' + file_name)

print('overall = ' + str(overall))


# print('Number of Conditional Commitments created in this game was ' + str(conditional_commitments))
# print('Number of Detached Commitments created in this game was ' + str(commitments_detached))
# print('Number of Satisfied Commitments for this game was ' + str(commitments_satisfied))



