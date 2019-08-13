from configuration import Signal

configuration = {
"Sine1":Signal(
    range_x=[-1.0, 1.0],
    color='white',
    holdup=False,
    precision=('h', 7, 8)
    ),
"Sine2":Signal(
    range_x=[-1.0, 1.0],
    color='blue',
    holdup=False,
    precision=('b', 3, 4)
    ),
"sine3":Signal(
    range_x=[-1.0, 1.0],
    color='red',
    holdup=False,
    precision=('h', 15, 0)
    ),
"square":Signal(
    range_x=[-1.0, 1.0],
    color='green',
    holdup=False,
    precision=('h', 4, 13)
    ),
"time_scale":0.05,
}