'''
Calculate confidence intervals of correlation coefficients

Parameters:
--------------------
x, y -- array_like,
        two 1-D arrays between which the correlation will be calculated
method -- string, optional, by default it is 'kendall_tau'
          which correlation measure we are going to use
          'kendall_tau': Kendall's tau-b, scipy.stats.kendalltau is used
          'spearman_rho': Spearman's rho, scipy.stats.spearmanr is used
          'pearson_r': Pearson's r, scipy.stats.pearsonr is used
          'customized': customized correlation measure, if this is used then
                        custom_corr_func must be provided
skip_ci -- bool, optional, by default it is false
           if the CI calculation will be skipped
bootstrap -- bool, optional, by default it is false
             Whether the non-parametric bootstrap approach will be used for
             CI calculation.
             If it is set to false, we rely on a normal approximation (parametric)
alpha -- float, optional, by default it is 0.05
         alpha-level, significance level, equals to 1 - confidence interval
ci -- float or None, optional, by default it is None
      confidence interval (e.g. 0.95), if it is set, then alpha will be ignored
custom_corr_func -- function, optional, by default it is None
                    customized correlation measure
bootstrap_samples -- int, optional, by default it is 5000
                     number of bootstrap samples, usually we choose a number that
                     is >= 1000
additional -- additinoal arguments that will be passed to the correlation function

Returns:
--------------------
correlation -- float,
               the correlation coefficient returned from the correlation function
correlation_lower -- float,
                     lower endpoint of the correlation (1 - alpha) CI
correlation_upper -- float,
                     upper endpoint of the correlation (1 - alpha) CI
p-value -- float,
           p-value returned from the correlation function

Examples:
--------------------
>>> a, b = list(range(2000)), list(range(200, 0, -1)) * 10
>>> corr(a, b, method='spearman_rho')
(-0.0999987624920335,
 -0.14330929583811683,
 -0.056305939127336606,
 7.446171861744971e-06)
>>> corr(a, b, method='spearman_rho', bootstrap=True)
(-0.0999987624920335,
 -0.14391512571311846,
 -0.05473641854997709,
 7.446171861744971e-06)

References:
--------------------
[1] Bonett, Douglas G., and Thomas A. Wright.
    "Sample size requirements for estimating Pearson, Kendall and Spearman correlations."
    Psychometrika 65, no. 1 (2000): 23-28.
[2] Bishara, Anthony J., and James B. Hittner.
    "Confidence intervals for correlations when data are not normal."
    Behavior research methods 49, no. 1 (2017): 294-309.
'''


try:
    import numpy as np
    from scipy.stats import kendalltau as kendall_tau_scipy
    from scipy.stats import spearmanr as spearman_rho_scipy
    from scipy.stats import pearsonr as pearson_r_scipy
    from scipy.stats import norm as norm_scipy
except ImportError:
    raise ImportError('To use this package, numpy and scipy are required')

bootstrap_samples_default = 5000
alpha_default = 0.05

corr_functions = {'kendall_tau': kendall_tau_scipy,
                  'spearman_rho': spearman_rho_scipy,
                  'pearson_r': pearson_r_scipy,
                  'customized': None}
param_corr_thres = {'kendall_tau': 0.8,
                    'spearman_rho': 0.95,
                    'pearson_r': 1.,
                    'customized': 0.}
se_numerator_func = {'kendall_tau': lambda r: .437,
                     'spearman_rho': lambda r: 1 + r ** 2 / 2.,
                     'pearson_r': lambda r: 1}
se_denominator_diff = {'kendall_tau': 4,
                       'spearman_rho': 3,
                       'pearson_r': 3}


def corr(x, y, method='kendall_tau', skip_ci=False, alpha=alpha_default, ci=None,
         bootstrap_samples=bootstrap_samples_default, bootstrap=False,
         custom_corr_func=None, **kwargs):
    if method == 'customized' and custom_corr_func is not None:
        # we could also pass a customized correlation function (e.g. kendall's tau-c)
        # in that case, we would only rely on bootstrap to calculate CI
        corr_func = custom_corr_func
    else:
        if method in corr_functions:
            corr_func = corr_functions[method]
        else:
            raise KeyError('method must be one of the following strings:'
                           + ' kendall_tau, spearman_rho, pearson_r, customized')

    corr_mean, p_value = corr_func(x, y, **kwargs)

    if skip_ci:
        return corr_mean, None, None, p_value
    if abs(corr_mean) == 1:
        return corr_mean, corr_mean, corr_mean, p_value
    if ci is not None:
        alpha = 1 - ci

    x = np.asarray(x).ravel()
    y = np.asarray(y).ravel()
    sample_size = len(x)

    if (not bootstrap) and (abs(corr_mean) < param_corr_thres[method]):
        # if the absolute value of correlation is smaller than the given threshold,
        # a transformation of the correlation approximately follows a normal distribution
        # see reference for more details

        z = np.log((1 + corr_mean) / (1 - corr_mean)) / 2  # the transformation
        # standard error of z
        se = np.sqrt(se_numerator_func[method](corr_mean)
                     / (sample_size - se_denominator_diff[method]))
        z_lower = z - norm_scipy.ppf(1 - alpha / 2.) * se
        z_upper = z + norm_scipy.ppf(1 - alpha / 2.) * se
        # inverse the transformation to obtain the upper and lower endpoints
        corr_lower = (np.exp(2 * z_lower) - 1) / (np.exp(2 * z_lower) + 1)
        corr_upper = (np.exp(2 * z_upper) - 1) / (np.exp(2 * z_upper) + 1)

    else:
        # if choose to use bootstrap or the absolute value of correlation is too large
        # we will use bootstrap (sample pairs with replacement) to calculate CI

        new_idx = np.random.choice(np.arange(sample_size), replace=True,
                                   size=(bootstrap_samples, sample_size))
        bootstrap_x, bootstrap_y = x[new_idx], y[new_idx]
        bootstrap_corrs = list([corr_func(bootstrap_x[i], bootstrap_y[i], **kwargs)[0]
                                for i in range(bootstrap_samples)])
        corr_lower = np.quantile(bootstrap_corrs, alpha / 2.)
        corr_upper = np.quantile(bootstrap_corrs, 1 - alpha / 2.)

    return corr_mean, corr_lower, corr_upper, p_value
