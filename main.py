from CTModel import *

model = CTModel(4, 4, CooperativeCTAgents=1, SelfishCTAgents=1, IntelligentCTAgents=0)

model.run_model()

print('Number of Released Commitments for this game was ' + str(model.released_commitments))


