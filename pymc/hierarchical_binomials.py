#!/usr/bin/env python
import sys
import numpy as np
from pymc import Uniform, Beta, Binomial, MCMC
from matplotlib import pyplot as plt
import scipy.stats as stats

n = np.array([20,20,20,20,20,20,20,19,19,19,19,18,18,17,20,20,20,20,19,19,18,18,
              25,24,23,20,20,20,20,20,20,10,49,19,46,27,17,49,47,20,20,13,48,50,
              20,20,20,20,20,20,20,48,19,19,19,22,46,49,20,20,23,19,22,20,20,20,
              52,47,46,24])
tumors = np.array([0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,2,2,2,2,2,2,2,2,
                   2,1,5,2,5,3,2,7,7,3,3,2,9,10,4,4,4,4,4,4,4,10,4,4,4,5,11,12,
                   5,5,6,5,6,6,6,6,16,15,15,9])
print "++++++++++ The tumor data ++++++++++"
print "n.size:", n.size, "tumors.size:", tumors.size
print "ratio of means:", tumors.mean() / n.mean()
thetas_freq = 1.0 * tumors/n
print "mean of ratios:", thetas_freq.mean()
print "frequentist thetas:\n", thetas_freq

# Build the model. We're modelling the tumor rate in each group as a draw from a
# Beta distribution shared across all the groups. The number of tumors in a
# group is then sampled as a Binomial(n, rate)
a = Uniform('a', lower=1, upper=15)
b = Uniform('b', lower=1, upper=15)
thetas = Beta('thetas', alpha=a, beta=b, size=n.size)
y = Binomial('y', n=n, p=thetas, value=tumors, observed=True)

# sample from the model
M = MCMC({'y':y, 'thetas': thetas, 'a':a, 'b':b})
M.sample(iter=30000, burn=10000, thin=10)

# compute posterior estimates
thetas_bayes = M.trace('thetas')[:].mean(axis=0)
a_post = M.trace('a')[:].mean()
b_post = M.trace('b')[:].mean()

print "++++++++++ Mixing spot checks ++++++++++"
print "a.trace:", M.trace('a')[:]
print "theta[4].trace:", M.trace('thetas')[:,4]

print "++++++++++ Posteriors ++++++++++"
print "a posterior:", a_post
print "b posterior:", b_post
print "thetas posterior:\n", thetas_bayes

# plot the quality of the fit to empirical distribution of thetas
plt.title('Theta goodness of fit')
plt.ylabel('density')
plt.xlabel('theta')
plt.hist(thetas_freq, normed=True)
x = np.linspace(0,1)
plt.plot(x, stats.beta.pdf(x, a_post, b_post))
plt.show()

# plot the resulting smoothed thetas
x = np.arange(n.size)
plt.subplot(211)
plt.title('Smoothing tumor rates in similar groups via a Bayesian prior')
plt.ylabel('estimated tumor rate')
plt.plot(x, thetas_freq, 'ko', label='sample mean')
plt.plot(x, thetas_bayes, 'ro', label='posterior mean')
plt.vlines(x, thetas_freq, thetas_bayes)
plt.legend(loc='best')
plt.subplot(212)
plt.ylabel('group size')
plt.xlabel('group')
plt.bar(x, n)
plt.show()
