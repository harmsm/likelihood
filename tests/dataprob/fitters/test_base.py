
import pytest

from dataprob.fitters.base import Fitter
from dataprob.model_wrapper import ModelWrapper

import numpy as np

import os
import pickle
import copy

# ---------------------------------------------------------------------------- #
# Test __init__ 
# ---------------------------------------------------------------------------- #

def test_Fitter__init__():
    """
    Test model initialization.
    """

    f = Fitter()
    
    assert f._num_obs is None
    assert f._num_params is None
    assert f._model_is_model_wrapper is False
    assert f._fit_has_been_run is False
    assert f._fit_type == ""

# ---------------------------------------------------------------------------- #
# Test a few utility functions
# ---------------------------------------------------------------------------- #

def test_Fitter__sanity_check():
    
    f = Fitter()
    f._sanity_check("some error",["fit_type"])
    with pytest.raises(RuntimeError):
        f._sanity_check("some error",["not_an_attribute"])

def test__fit():
    f = Fitter()
    with pytest.raises(NotImplementedError):
        f._fit()

def test__update_estimates():
    f = Fitter()
    with pytest.raises(NotImplementedError):
        f._fit()

# ---------------------------------------------------------------------------- #
# Test residuals and the like
# ---------------------------------------------------------------------------- #

def test_unweighted_residuals(binding_curve_test_data):
    """
    Test unweighted residuals call against "manual" code used to generate
    test data.
    """

    f = Fitter()

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

    f = Fitter()

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

    f = Fitter()

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

# ---------------------------------------------------------------------------- #
# Test setters, getters, and internal sanity checks
# ---------------------------------------------------------------------------- #

def test_model_setter_getter(binding_curve_test_data):
    """
    Test the model setter.
    """

    f = Fitter()
    
    # Not a function
    with pytest.raises(ValueError):
        f.model = "a"

    # Function with no arguments
    def dummy(): pass
    with pytest.raises(ValueError):
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
    mw = ModelWrapper(model_to_test_wrap)

    f = Fitter()
    f.model = mw
    assert f.model == mw._mw_observable
    assert np.array_equal(f.guesses,np.array([0,20]))
    assert np.array_equal(f.bounds,np.array([[-np.inf,-np.inf],[np.inf,np.inf]]))
    assert np.array_equal(f.names,np.array(["K1","K2"]))

    # Test passing a ModelWrapper.model method. Should update guesses, bounds,
    # names
    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = ModelWrapper(model_to_test_wrap)

    f = Fitter()
    f.model = mw.model
    assert f.model == mw._mw_observable
    assert np.array_equal(f.guesses,np.array([0,20]))
    assert np.array_equal(f.bounds,np.array([[-np.inf,-np.inf],[np.inf,np.inf]]))
    assert np.array_equal(f.names,np.array(["K1","K2"]))

   # Test passing a ModelWrapper.model method. Should update guesses, bounds,
    # names
    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = ModelWrapper(model_to_test_wrap)

    # Make sure that number of parameters validation works
    f = Fitter()
    f._num_params = 10 
    with pytest.raises(ValueError):
        f.model = mw.model


def test_guesses_setter_getter(binding_curve_test_data):
    """
    Test the guesses setter.
    """

    f = Fitter()
    assert f.guesses is None
    assert f.num_params is None
    f.guesses = np.ones(3)
    assert np.array_equal(f.guesses,[1,1,1])
    assert f._fit_has_been_run is False
    assert f.num_params == 3

    f = Fitter()
    with pytest.raises(ValueError):
        f.guesses = "a"
    with pytest.raises(ValueError):
        f.guesses = ["a",1.5]

    f = Fitter()
    assert f.guesses is None
    f.guesses = np.ones(3)
    with pytest.raises(ValueError):
        f.guesses = np.ones(2)
    
    f = Fitter()
    assert f.guesses is None
    assert f.names is None
    f.names = ["a","b"]
    with pytest.raises(ValueError):
        f.guesses = np.ones(3)
    f.guesses = [1,2]
    assert np.array_equal(f.guesses,[1,2]) 

    # Test passing a ModelWrapper.model method.
    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = ModelWrapper(model_to_test_wrap)

    f = Fitter()
    f.model = mw.model
    assert f.model == mw._mw_observable
    assert np.array_equal(f.guesses,np.array([0,20]))

    f.guesses = [2,40]
    assert np.array_equal(f.guesses,np.array([2,40]))
    assert mw.K1.guess == 2
    assert mw.K2.guess == 40

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

    f = Fitter()

    with pytest.raises(ValueError):
        f.bounds = "a"
    with pytest.raises(ValueError):
        def dummy(): pass
        f.bounds = dummy

    # Base low-dimensional array
    with pytest.raises(ValueError):
        f.bounds = [0,1]

    bnds = np.ones((2,len(binding_curve_test_data["guesses"])),dtype=float)
    bnds[0,:] *= -np.inf
    bnds[1,:] *= np.inf

    f.bounds = bnds
    assert f.bounds is not None
    assert np.array_equal(f.bounds,bnds)

    # Test setting bounds with a model wrapper
    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = ModelWrapper(model_to_test_wrap)

    f = Fitter()
    f.model = mw.model
    assert f.model == mw._mw_observable
    
    assert np.isinf(mw.fit_parameters[mw.names[0]].bounds[0])

    num_param = len(mw.fit_parameters)
    bnds = np.ones((2,num_param),dtype=float)
    bnds[0,:] *= -np.inf
    bnds[1,:] *= np.inf
    bnds[0,0] = 0

    f.bounds = bnds
    assert mw.fit_parameters[mw.names[0]].bounds[0] == 0

def test_priors_setter_getter(binding_curve_test_data):
    """
    Test the priors setter.
    """

    # Good pass of priors
    f = Fitter()
    f.priors is None
    priors = np.ones((2,len(binding_curve_test_data["guesses"])),dtype=float)
    f.priors = priors
    assert f.priors is not None
    assert np.array_equal(f.priors,priors)

    # bad value
    f = Fitter()
    with pytest.raises(ValueError):
        f.priors = "a"

    # bad value
    f = Fitter()
    with pytest.raises(ValueError):
        def dummy(): pass
        f.priors = dummy

    # single dimensional array
    f = Fitter()
    with pytest.raises(ValueError):
        f.priors = [0,1]

    # has an infinity
    f = Fitter()
    priors = np.ones((2,len(binding_curve_test_data["guesses"])),dtype=float)
    priors[0,0] = np.inf
    with pytest.raises(ValueError):
        f.priors = priors

    # Test match with the number of parameters
    f = Fitter()
    f.names = ["A","B"]
    assert f.num_params == 2
    with pytest.raises(ValueError):
        f.priors = [[1],[1]]
    with pytest.raises(ValueError):
        f.priors = [[1,2,3],[1,2,3]]
    f.priors = [[1,2],[1,2]]
    assert np.array_equal(f.priors,np.array([[1,2],[1,2]]))


    # Test setting bounds with a model wrapper
    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = ModelWrapper(model_to_test_wrap)

    f = Fitter()
    f.model = mw.model
    assert f.model == mw._mw_observable
    assert np.isinf(mw.fit_parameters[mw.names[0]].bounds[0])

    num_param = len(mw.fit_parameters)
    bnds = np.ones((2,num_param),dtype=float)
    bnds[0,:] *= -np.inf
    bnds[1,:] *= np.inf
    bnds[0,0] = 0

    f.bounds = bnds
    assert mw.fit_parameters[mw.names[0]].bounds[0] == 0

def test_names_setter_getter(binding_curve_test_data):
    """
    Test the names setter.
    """

    f = Fitter()
    assert f.names is None

    names = ["p{}".format(i)
                   for i in range(len(binding_curve_test_data["guesses"]))]
    f.names = names
    assert f.names is not None
    assert np.array_equal(f.names,names)
    assert f.num_params == len(names)

    f = Fitter()
    assert f.names is None
    f.names = ["yo"]
    assert np.array_equal(f.names,["yo"])
    assert f.num_params == 1

    f = Fitter()
    assert f.names is None
    f.names = "yo"
    assert np.array_equal(f.names,["yo"])
    assert f.num_params == 1

    f = Fitter()
    assert f.names is None
    with pytest.raises(ValueError):
        f.names = ["a","a"]

    # mismatch in number of parameters and number of parameter names
    f = Fitter()
    assert f.names is None
    assert f._num_params is None
    f._num_params = 10
    assert f.num_params == 10
    with pytest.raises(ValueError):
        f.names = ["a","b"]

    # Test setting names with a model wrapper
    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = ModelWrapper(model_to_test_wrap)

    f = Fitter()
    f.model = mw.model
    assert f.model == mw._mw_observable
    assert np.array_equal(f.names,["K1","K2"])
    assert mw.fit_parameters["K1"].name == "K1"
    assert mw.fit_parameters["K2"].name == "K2"
    
    f.names = ["A","B"]
    assert np.array_equal(f.names,["A","B"])
    assert mw.fit_parameters["K1"].name == "A"
    assert mw.fit_parameters["K2"].name == "B"

def test_y_obs_setter_getter(binding_curve_test_data):
    """
    Test the y_obs setter.
    """

    f = Fitter()
 
    f.y_obs = binding_curve_test_data["df"].Y
    assert f.y_obs is not None
    assert np.array_equal(f.y_obs,binding_curve_test_data["df"].Y)
    assert f._fit_has_been_run is False

    f = Fitter()
    with pytest.raises(ValueError):
        f.y_obs = "a"
    with pytest.raises(ValueError):
        f.y_obs = ["a","b"]

    f = Fitter()
    input_data = np.array(binding_curve_test_data["df"].Y)
    f.y_obs = input_data
    assert np.array_equal(f.y_obs,input_data)
    assert f.num_obs == input_data.shape[0]

    # Send in data with incorrect number of observations
    with pytest.raises(ValueError):
        f.y_obs = input_data[:-1]    
  
def test_y_stdev_setter_getter(binding_curve_test_data):
    """
    Test the y_stdev setter.
    """

    y_obs_input = np.array(binding_curve_test_data["df"].Y)
    y_stdev_input = np.array(binding_curve_test_data["df"].Y_stdev)

    f = Fitter()
    assert f.y_stdev is None
    assert f.num_obs is None
    f.y_stdev = y_stdev_input
    assert np.array_equal(y_stdev_input,f.y_stdev)
    assert f.num_obs == len(y_stdev_input)
    assert f._fit_has_been_run is False
    
    f = Fitter()
    assert f.y_stdev is None
    with pytest.raises(ValueError):
        f.y_stdev = "a"
    with pytest.raises(ValueError):
        f.y_stdev = ["a","b"]
    
    # Obs and stdev
    f = Fitter()
    assert f.y_obs is None
    assert f.y_stdev is None
    f.y_obs = y_obs_input
    f.y_stdev = y_stdev_input
    assert np.array_equal(y_obs_input,f.y_obs)
    assert np.array_equal(y_stdev_input,f.y_stdev)
    
    # Obs and stdev, reverse order of adding
    f = Fitter()
    assert f.y_obs is None
    assert f.y_stdev is None
    f.y_stdev = y_stdev_input
    f.y_obs = y_obs_input
    assert np.array_equal(y_obs_input,f.y_obs)
    assert np.array_equal(y_stdev_input,f.y_stdev)
    
    # Length checks
    f = Fitter()
    assert f.y_stdev is None
    assert f.num_obs is None
    f.y_stdev = y_stdev_input
    with pytest.raises(ValueError):
        f.y_stdev = y_stdev_input[:-1]

    f = Fitter()
    assert f.y_stdev is None
    assert f.num_obs is None
    f.y_obs = y_obs_input
    with pytest.raises(ValueError):
        f.y_stdev = y_stdev_input[:-1]

def test_num_params(binding_curve_test_data):

    f = Fitter()
    assert f.num_params is None

    f.guesses = np.array([1,2])
    assert f.num_params == 2

    with pytest.raises(ValueError):
        f.guesses = np.array([7,8,9,10])

    f = Fitter()
    f.guesses = np.array([])
    assert f.num_params == 0

    model_to_test_wrap = binding_curve_test_data["model_to_test_wrap"]
    mw = ModelWrapper(model_to_test_wrap)
    
    f = Fitter()
    assert f.num_params is None
    f.model = mw.model
    assert f.num_params == len(mw.fit_parameters)


def test_num_obs():

    f = Fitter()
    assert f.num_obs is None

    f.y_obs = np.arange(10)
    assert f.num_obs == 10

    with pytest.raises(ValueError):
        f.y_obs = np.arange(2)

    f = Fitter()
    f.y_obs = np.array([])
    assert f.num_obs == 0

def test_base_properties():
    """
    Test properties that can only be None in the base class.
    """

    f = Fitter()

    assert f.estimate is None
    assert f.stdev is None
    assert f.ninetyfive is None
    assert f.fit_result is None
    assert f.success is None
    assert f.fit_info is None
    assert f.samples is None
    assert f.fit_to_df is None

def test_base_functions():
    """
    Test functions that can only be None in the base class.
    """

    f = Fitter()
    assert f.corner_plot() is None

def test_write_samples(tmpdir):
    
    cwd = os.getcwd()
    os.chdir(tmpdir)

    test_file = "test-out.pickle"

    # Should not write out because samples do not exist yet
    f = Fitter()
    assert f.samples is None
    assert not os.path.exists(test_file)
    f.write_samples(test_file)
    assert not os.path.exists(test_file)

    # create fake samples and write out
    f._samples = np.ones((100,5),dtype=float)
    assert not f.samples is None
    assert not os.path.exists(test_file)
    f.write_samples(test_file)
    assert os.path.exists(test_file)

    # read samples back in to make sure they wrote as a pickle
    with open(test_file,"rb") as handle:
        read_back = pickle.load(handle)
    assert np.array_equal(read_back,f._samples)

    # Try and fail to write samples to an existing pickle files
    with open("existing-file.pickle","w") as g:
        g.write("yo")
    
    with pytest.raises(FileExistsError):
        f.write_samples("existing-file.pickle")

    os.chdir(cwd)

def test_append_samples(tmpdir):

    cwd = os.getcwd()
    os.chdir(tmpdir)

    # make some files and arrays for testing
    sample_array = np.ones((100,3),dtype=float)
    with open("test.pickle","wb") as p:
        pickle.dump(sample_array,p)
    with open("bad_file.txt","w") as g:
        g.write("yo")

    # Build a hacked Fitter object that has existing samples, three params, 
    # and an overwritten _update_estimates call that does nothing.
    base_f = Fitter()
    base_f._samples = sample_array.copy()
    base_f._num_params = 3
    assert np.array_equal(base_f.samples.shape,(100,3))
    def dummy(*args,**kwargs): pass
    base_f._update_estimates = dummy

    f = Fitter()

    # Nothing happens
    f.append_samples(sample_file=None,
                     sample_array=None)
    
    # Check for existing samples (should fail without samples)
    f = Fitter()
    assert f.samples is None
    with pytest.raises(ValueError):
        f.append_samples(sample_array=sample_array)
    f = copy.deepcopy(base_f)
    f.append_samples(sample_array=sample_array)

    # Too many inputs
    with pytest.raises(ValueError):
        f.append_samples(sample_file="test.pickle",
                         sample_array=sample_array)

    f = copy.deepcopy(base_f)
    assert np.array_equal(f.samples.shape,(100,3))
    
    f.append_samples(sample_file="test.pickle")
    assert np.array_equal(f.samples.shape,(200,3))

    f.append_samples(sample_file="test.pickle")
    assert np.array_equal(f.samples.shape,(300,3))

    f.append_samples(sample_array=sample_array)
    assert np.array_equal(f.samples.shape,(400,3))

    # Bad files
    f = copy.deepcopy(base_f)
    with pytest.raises(FileNotFoundError):
        f.append_samples(sample_file="not_real_file")
    with pytest.raises(pickle.UnpicklingError):
        f.append_samples(sample_file="bad_file.txt")

    # not coercable to floats
    f = copy.deepcopy(base_f)
    not_coercable_to_float = [["a","b","c"],
                              ["a","b","c"],
                              ["a","b","c"]]
    with pytest.raises(ValueError):
        f.append_samples(sample_array=not_coercable_to_float)

    # vector with wrong number of dimensions
    f = copy.deepcopy(base_f)
    with pytest.raises(ValueError):
        f.append_samples(sample_array=np.ones(3,dtype=float))
    
    # array with wrong number of parameter dimensions
    f = copy.deepcopy(base_f)
    with pytest.raises(ValueError):
        f.append_samples(sample_array=np.ones((100,2),dtype=float))

    # Make sure update estimates is running by hacking f._update_estimates to
    # throw an exception
    f = copy.deepcopy(base_f)
    assert np.array_equal(f.samples.shape,(100,3))
    f.append_samples(sample_array=sample_array)
    assert np.array_equal(f.samples.shape,(200,3))
    
    def dummy(*args,**kwargs):
        raise RuntimeError
    f._update_estimates = dummy
    
    with pytest.raises(RuntimeError):
        f.append_samples(sample_array=sample_array)

    os.chdir(cwd)

def xtest_fit_completeness_sanity_checking(binding_curve_test_data):

    f = Fitter()

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
    # and y_obs).  But it will throw NotImplementedError because it's the base 
    # class.
    with pytest.raises(NotImplementedError):
        f.fit()

def xtest_param_mismatch_check(binding_curve_test_data):
    """
    Test the check for mismatches in the number of parameters in guesses,
    bounds, and names.
    """

    # XXXX PRIORS???

    f = Fitter()

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
