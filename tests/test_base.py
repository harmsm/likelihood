
import pytest

import likelihood
import numpy as np

import inspect

# ---------------------------------------------------------------------------- #
# Test __init__
# ---------------------------------------------------------------------------- #

def test_init():
    """
    Test model initialization.
    """

    f = likelihood.fitters.base.Fitter()
    assert f.fit_type == ""

# ---------------------------------------------------------------------------- #
# Test setters, getters, and internal sanity checks
# ---------------------------------------------------------------------------- #

def test_model_setter_getter(binding_curve_test_data):
    """
    Test the model setter.
    """

    f = likelihood.fitters.base.Fitter()

    with pytest.raises(ValueError):
        f.model = "a"
    with pytest.raises(ValueError):
        def dummy(): pass
        f.model = dummy

    # Test passing a simple, prewrapped model (not a ModelWrapper)
    f.model = binding_curve_test_data["prewrapped_model"]
    assert f.model is not None
    assert f.model == binding_curve_test_data["prewrapped_model"]
    assert f.guesses is None
    assert f.bounds is None
    assert f.names is None

    # Test passing a ModelWrapper instance.  Should update guesses, bounds,
    # names
    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = likelihood.ModelWrapper(model_to_test_wrap)

    f = likelihood.fitters.base.Fitter()
    f.model = mw
    assert f.model == mw._mw_observable
    assert np.array_equal(f.guesses,np.array([1,20]))
    assert np.array_equal(f.bounds,np.array([[-np.inf,-np.inf],[np.inf,np.inf]]))
    assert np.array_equal(f.names,np.array(["K1","K2"]))

    # Test passing a ModelWrapper.model method. Should update guesses, bounds,
    # names
    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = likelihood.ModelWrapper(model_to_test_wrap)

    f = likelihood.fitters.base.Fitter()
    f.model = mw.model
    assert f.model == mw._mw_observable
    assert np.array_equal(f.guesses,np.array([1,20]))
    assert np.array_equal(f.bounds,np.array([[-np.inf,-np.inf],[np.inf,np.inf]]))
    assert np.array_equal(f.names,np.array(["K1","K2"]))

def test_guesses_setter_getter(binding_curve_test_data):
    """
    Test the guesses setter.
    """

    f = likelihood.fitters.base.Fitter()

    with pytest.raises(ValueError):
        f.guesses = "a"
    with pytest.raises(ValueError):
        def dummy(): pass
        f.guesses = dummy
    f.guesses = binding_curve_test_data["guesses"]
    assert f.guesses is not None
    assert np.array_equal(f.guesses,binding_curve_test_data["guesses"])

    # Test passing a ModelWrapper.model method.
    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = likelihood.ModelWrapper(model_to_test_wrap)

    f = likelihood.fitters.base.Fitter()
    f.model = mw.model
    assert f.model == mw._mw_observable
    assert np.array_equal(f.guesses,np.array([1,20]))

    f.guesses = [2,40]
    assert np.array_equal(f.guesses,np.array([2,40]))

    with pytest.raises(TypeError):
        mw.guesses = [4,80]
    mw.K1.guess = 4
    mw.K2.guess = 80

    assert np.array_equal(mw.guesses,np.array([4,80]))
    assert np.array_equal(f.guesses,np.array([4,80]))

def test_bounds_setter_getter(binding_curve_test_data):
    """
    Test the bounds setter.
    """

    f = likelihood.fitters.base.Fitter()

    with pytest.raises(ValueError):
        f.bounds = "a"
    with pytest.raises(ValueError):
        def dummy(): pass
        f.bounds = dummy

    # Base low-dimensional array
    with pytest.raises(ValueError):
        f.bounds = [0,1]

    bnds = [[-np.inf for _ in range(len(binding_curve_test_data["guesses"]))],
            [ np.inf for _ in range(len(binding_curve_test_data["guesses"]))]]
    bnds = np.array(bnds)

    f.bounds = bnds
    assert f.bounds is not None
    assert np.array_equal(f.bounds,bnds)

def test_names_setter_getter(binding_curve_test_data):
    """
    Test the names setter.
    """

    f = likelihood.fitters.base.Fitter()

    names = ["p{}".format(i)
                   for i in range(len(binding_curve_test_data["guesses"]))]
    f.names = names
    assert f.names is not None
    assert np.array_equal(f.names,names)


def test_param_mismatch_check(binding_curve_test_data):
    """
    Test the check for mismatches in the number of parameters in guesses,
    bounds, and names.
    """

    f = likelihood.fitters.base.Fitter()

    f.guesses = binding_curve_test_data["guesses"]
    with pytest.raises(ValueError):
        f.names = ["p{}".format(i)
                         for i in range(len(binding_curve_test_data["guesses"])-1)]
    f.names = ["p{}".format(i)
                     for i in range(len(binding_curve_test_data["guesses"]))]

    with pytest.raises(ValueError):
        bnds = [[-np.inf for _ in range(len(binding_curve_test_data["guesses"])-1)],
                [ np.inf for _ in range(len(binding_curve_test_data["guesses"])-1)]]
        bnds = np.array(bnds)
        f.bounds = bnds

    bnds = [[-np.inf for _ in range(len(binding_curve_test_data["guesses"]))],
            [ np.inf for _ in range(len(binding_curve_test_data["guesses"]))]]
    bnds = np.array(bnds)
    f.bounds = bnds


def test_y_obs_setter_getter(binding_curve_test_data):
    """
    Test the y_obs setter.
    """

    f = likelihood.fitters.base.Fitter()

    with pytest.raises(ValueError):
        f.y_obs = "a"
    with pytest.raises(ValueError):
        def dummy(): pass
        f.y_obs = dummy
    f.y_obs = binding_curve_test_data["df"].Y
    assert f.y_obs is not None
    assert np.array_equal(f.y_obs,binding_curve_test_data["df"].Y)

def test_y_stdev_setter_getter(binding_curve_test_data):
    """
    Test the y_stdev setter.
    """

    f = likelihood.fitters.base.Fitter()

    with pytest.raises(ValueError):
        f.y_stdev = "a"
    with pytest.raises(ValueError):
        def dummy(): pass
        f.y_stdev = dummy
    f.y_stdev = binding_curve_test_data["df"].Y_stdev
    assert f.y_stdev is not None
    assert np.array_equal(f.y_stdev,binding_curve_test_data["df"].Y_stdev)

def test_obs_mismatch_check(binding_curve_test_data):
    """
    Test the check for mismatches in the number of observations in y_obs
    and y_stdev.
    """

    f = likelihood.fitters.base.Fitter()

    f.y_obs = binding_curve_test_data["df"].Y
    with pytest.raises(ValueError):
        f.y_stdev = binding_curve_test_data["df"].Y_stdev[:-1]
    f.y_stdev = binding_curve_test_data["df"].Y_stdev

    f = likelihood.fitters.base.Fitter()

    f.y_stdev = binding_curve_test_data["df"].Y_stdev
    with pytest.raises(ValueError):
        f.y_obs = binding_curve_test_data["df"].Y[:-1]
    f.y_obs = binding_curve_test_data["df"].Y


def test_fit_completeness_sanity_checking(binding_curve_test_data):

    f = likelihood.fitters.base.Fitter()

    # This should not work because we have not specified a model, guesses,
    # or y_obs yet
    with pytest.raises(RuntimeError):
        f.fit()

    f.model = binding_curve_test_data["prewrapped_model"]

    # This should not work because we have not specified guesses or y_obs
    # yet.
    with pytest.raises(RuntimeError):
        f.fit()

    f.guesses = binding_curve_test_data["guesses"]

    # This should not work because we have not specified y_obs yet
    with pytest.raises(RuntimeError):
        f.fit()

    f.y_obs = binding_curve_test_data["df"].Y

    # Should now work because we've set everything essential (model, gueses,
    # and y_obs).  It won't do anything b/c this is the base class, but it
    # will still run.
    f.fit()


# ---------------------------------------------------------------------------- #
# Test residuals and the like
# ---------------------------------------------------------------------------- #

def test_unweighted_residuals(binding_curve_test_data):
    """
    Test unweighted residuals call against "manual" code used to generate
    test data.
    """

    f = likelihood.fitters.base.Fitter()

    input_params = binding_curve_test_data["input_params"]

    # Should fail, haven't loaded a model or y_obs yet
    with pytest.raises(RuntimeError):
        f.unweighted_residuals(input_params)

    f.model = binding_curve_test_data["prewrapped_model"]

    # Should fail, haven't loaded y_obs yet
    with pytest.raises(RuntimeError):
        f.unweighted_residuals(input_params)

    df = binding_curve_test_data["df"]
    f.y_obs = df.Y

    r = f.unweighted_residuals(input_params)

    assert np.allclose(r,df.residual)


def test_weighted_residuals(binding_curve_test_data):
    """
    Test weighted residuals call against "manual" code used to generate
    test data.
    """

    f = likelihood.fitters.base.Fitter()

    input_params = binding_curve_test_data["input_params"]

    # Should fail, haven't loaded a model, y_obs or y_stdev yet
    with pytest.raises(RuntimeError):
        f.weighted_residuals(input_params)

    f.model = binding_curve_test_data["prewrapped_model"]

    # Should fail, haven't loaded y_obs or y_stdev yet
    with pytest.raises(RuntimeError):
        f.weighted_residuals(input_params)

    df = binding_curve_test_data["df"]
    f.y_obs = df.Y

    # Should fail, haven't loaded y_stdev yet
    with pytest.raises(RuntimeError):
        f.weighted_residuals(input_params)

    f.y_stdev = df.Y_stdev
    r = f.weighted_residuals(input_params)

    assert np.allclose(r,df.weighted_residual)


def test_ln_like(binding_curve_test_data):
    """
    Test log likelihood call against "manual" code used to generate
    test data.
    """

    f = likelihood.fitters.base.Fitter()

    input_params = binding_curve_test_data["input_params"]

    # Should fail, haven't loaded a model, y_obs or y_stdev yet
    with pytest.raises(RuntimeError):
        f.ln_like(input_params)

    f.model = binding_curve_test_data["prewrapped_model"]

    # Should fail, haven't loaded y_obs or y_stdev yet
    with pytest.raises(RuntimeError):
        f.ln_like(input_params)

    df = binding_curve_test_data["df"]
    f.y_obs = df.Y

    # Should fail, haven't loaded y_stdev yet
    with pytest.raises(RuntimeError):
        f.ln_like(input_params)

    f.y_stdev = df.Y_stdev
    L = f.ln_like(input_params)

    assert np.allclose(L,binding_curve_test_data["ln_like"])

def test_num_params():

    f = likelihood.fitters.base.Fitter()
    assert f.num_params is None

    f.guesses = np.array([1,2])
    assert f.num_params == 2

    with pytest.raises(ValueError):
        f.guesses = np.array([7,8,9,10])

    f = likelihood.fitters.base.Fitter()
    f.guesses = np.array([])
    assert f.num_params == 0

def test_num_obs():

    f = likelihood.fitters.base.Fitter()
    assert f.num_obs is None

    f.y_obs = np.arange(10)
    assert f.num_obs == 10

    with pytest.raises(ValueError):
        f.y_obs = np.arange(2)

    f = likelihood.fitters.base.Fitter()
    f.y_obs = np.array([])
    assert f.num_obs == 0


def test_base_properties():

    f = likelihood.fitters.base.Fitter()

    assert f.estimate is None
    assert f.stdev is None
    assert f.ninetyfive is None
    assert f.fit_result is None
    assert f.success is None
    assert f.fit_info is None
    assert f.samples is None
    assert f.fit_to_df is None

def test_base_functions():

    f = likelihood.fitters.base.Fitter()
    assert f.corner_plot() is None
