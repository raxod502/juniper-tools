def bisect(test_fn, starting_value=1, starting_velocity=1.5, accuracy=0.95):
    """
    Perform an interactive binary search, like git-blame. It is
    assumed that `test_fn` takes one positive numeric argument and
    returns a boolean. The function should be approximately monotonic
    and increasing, so that it should approximately return false below
    a particular cutoff argument and return true above that cutoff.
    The bisection algorithm attempts to approximate this cutoff point.

    It operates by initializing the function's argument as per
    `starting_value`, and then adjusting it by multiplying or dividing
    repeatedly by `starting_velocity` to move closer to the cutoff.
    Once the cutoff point is passed, the multiplication factor is cut
    in half (sort of; actually, 1.5 goes to 1.25 goes to 1.125 and so
    on) and the algorithm proceeds. Once the cutoff point has been
    passed enough times and the velocity is small enough to achieve
    the desired `accuracy`, the algorithm terminates and returns the
    current function argument. The promise is that if `accuracy` is
    (for example) 0.95, then the returned value will be within 5% of
    the actual cutoff point.

    As a hack to support our Clinic project specifically, the last
    evaluation of the function is guaranteed to return true.
    """
    if starting_value <= 0:
        raise ValueError("starting_value must be positive")
    if starting_velocity <= 1:
        raise ValueError("starting_velocity must be greater than 1")
    if not (0 < accuracy < 1):
        raise ValueError("accuracy must be between 0 and 1")
    arg = starting_value
    velocity = starting_velocity
    last_side = None
    while velocity >= 1 / accuracy or last_side != True:
        cur_side = test_fn(arg)
        if cur_side != last_side:
            if last_side is not None:
                velocity = 1 + (velocity - 1) / 2
            last_side = cur_side
        if cur_side:
            new_arg = arg / velocity
        else:
            new_arg = arg * velocity
        # If too many iterations are provided, we may no longer be
        # able to adjust arg due to floating-point precision limits.
        if new_arg == arg:
            break
        arg = new_arg
    return arg
