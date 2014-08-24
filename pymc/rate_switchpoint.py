#!/usr/bin/env python
# from http://pymc-devs.github.io/pymc/tutorial.html

import numpy as np
import matplotlib.pyplot as plt
from pymc import DiscreteUniform, Exponential, deterministic, Poisson, Uniform
from pymc import MCMC
from pymc.Matplot import plot

disasters_array =   \
        np.array([ 4, 5, 4, 0, 1, 4, 3, 4, 0, 6, 3, 3, 4, 0, 2, 6,
                  3, 3, 5, 4, 5, 3, 1, 4, 4, 1, 5, 5, 3, 4, 2, 5,
                  2, 2, 3, 4, 2, 1, 3, 2, 2, 1, 1, 1, 1, 3, 0, 0,
                  1, 0, 1, 1, 0, 0, 3, 1, 0, 3, 2, 2, 0, 1, 1, 1,
                  0, 1, 0, 1, 0, 0, 0, 2, 1, 0, 0, 0, 1, 1, 0, 2,
                  3, 3, 1, 1, 2, 1, 1, 1, 1, 2, 4, 2, 0, 0, 1, 4,
                  0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 1])

# We're modelling the number of disasters as a poisson with a step function
# rate. The rate is larger in the first part of the data, and smaller in the
# second part. Our goal is to find the most likely value for the switchpoint.

# uninformative prior for the switchpoint
switchpoint = DiscreteUniform('switchpoint', lower=0, upper=110,
                              doc='Switchpoint[year]')

# our prior for the means has an expected value of 1, with smaller means being
# more likely than larger means. I think this is just a way of providing a
# relatively uninformative prior that has finite mean and variance without
# explictly ruling any values out. If the values in the disasters_array above
# were much larger, for example, this would be a poor choice of prior as it would
# nudge the rates to be much lower than the data seems to indicate.
early_mean = Exponential('early_mean', beta=1.)
late_mean = Exponential('late_mean', beta=1.)

# Given switchpoint, early_mean, and late_mean, the rate parameter is
# deterministic
@deterministic(plot=False)
def rate(s=switchpoint, e=early_mean, l=late_mean):
    ''' Concatenate Poisson means '''
    out = np.empty(len(disasters_array))
    out[:s] = e
    out[s:] = l
    return out

# our observed data
disasters = Poisson('disasters', mu=rate, value=disasters_array, observed=True)

###############################################################################

# inspect the model
print 'switchpoint.parents:', switchpoint.parents
print 'switchpoint.children:', switchpoint.children
print 'rate.parents:', rate.parents
print 'rate.children:', rate.children
print ''

# initial sampled values for parameters
print 'switchpoint.value:', switchpoint.value
print 'rate.value:', rate.value
print ''


###############################################################################

model = {
    'switchpoint': switchpoint,
    'early_mean': early_mean,
    'late_mean': late_mean,
    'rate': rate,
    'disasters': disasters
}

# fit the model
M = MCMC(model)
print 'M.switchpoint:', M.switchpoint
print ''
M.sample(iter=10000, burn=1000, thin=10)

###############################################################################

switchpoint_mean = M.trace('switchpoint')[:].mean()

# inspect the results
print 'switchpoint trace:', M.trace('switchpoint')[:10], '...'
print 'switchpoint mean:', switchpoint_mean

print M.stats()
plot(M)
plt.show()

###############################################################################

# Plot the mean a posteriori estimate of the switchpoint on the original data
plt.plot(disasters_array)
plt.vlines(switchpoint_mean, 0, disasters_array.max(), linewidth=3.0)
plt.title('Disasters per year and the estimated switchpoint')
plt.xlabel('year')
plt.ylabel('number of disasters')
plt.show()
