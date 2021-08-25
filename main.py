from CTModel import *

commitments_satisfied = 0
conditional_commitments = 0
commitments_detached = 0

for i in range(1):
    model = CTModel(8, 8, CTAgents=1, CompetitiveCTAgents=1)
    model.run_model()
    commitments_satisfied += model.released_commitments
    commitments_detached += model.detached_commitments
    conditional_commitments += model.commitments_created

print('Number of Conditional Commitments created in this game was ' + str(conditional_commitments))
print('Number of Detached Commitments created in this game was ' + str(commitments_detached))
print('Number of Satisfied Commitments for this game was ' + str(commitments_satisfied))



