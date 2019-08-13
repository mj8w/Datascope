from configuration import Signal

configuration = {
"comm_port":"COM1",
"Sine1":Signal(
    range_x=[-1.0, 1.0],
    color='white',
    holdup=False,
    precision=('h', 7, 8),
    _id=0
    ),
"Sine2":Signal(
    range_x=[-1.0, 1.0],
    color='blue',
    holdup=False,
    precision=('b', 3, 4),
    _id=1
    ),
"sine3":Signal(
    range_x=[-1.0, 1.0],
    color='red',
    holdup=False,
    precision=('h', 15, 0),
    _id=2
    ),
"square":Signal(
    range_x=[-1.0, 1.0],
    color='green',
    holdup=False,
    precision=('h', 4, 13),
    _id=3
    ),
"time_scale":0.05,
"pkg_delimiter":0xD5,
"MAX_SIGNAL":16,
}