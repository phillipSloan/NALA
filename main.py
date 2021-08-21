from CTModel import *

commitments_satisfied = 0
conditional_commitments = 0

for i in range(1):
    model = CTModel(8, 8, CooperativeCTAgents=2)
    model.run_model()
    commitments_satisfied += model.released_commitments
    conditional_commitments += model.commitments_created

print('Number of Satisfied Commitments for this game was ' + str(commitments_satisfied))
print('Number of Conditional Commitments created in this game was ' + str(conditional_commitments))


