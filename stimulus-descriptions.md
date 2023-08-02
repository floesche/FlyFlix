# Descriptions of Stimulus

An explanation of all existing stimulus in FlyFlix.

## Vertical Bars / Panels

The vertical bar or panel stimulus is the first type of stimulus in FlyFlix. It produces a strong, reliable behavioral response from drosophila. It consists of vertical bars moving horizontally across the screen. Each bar is a portion of a cylinder that surrounds the `camera`'s (or fly's) positions. An example of vertical bar stimulus can be seen below.

![Photo of vertical bar stimulus](vertical-bars.png)

[Video of vertical bar stimulus](https://drive.google.com/file/d/1iTZ0GS-XrffRtWAVukqsXhvVacvsWQXm/view?usp=sharing)

### Vertical Bar Parameters

`trial_id`: a unique identifier for the trial, preferably an integer number
`rotate_deg_hz`: movement speed in degrees per second, positive is clockwise
`osc_freq`: frequency of oscillations - overrides `rotate_deg_hz` and makes trial oscillating trials
`osc_width`: the width of an oscillation in degrees
`openloop_duration`: duration of the open loop condition
`closedloop_duration`: duration of the closed loop condition
`gain`: multiplier for orientation change read from the FicTrac instance
`fps`: client frame rate
`pretrial_duration`: duration of the pre-trial, where the stimulus is shown but not animated. Applies to open loop and closed loop conditions.
`posttrial_duration`: duration of the post-trial.
`comment`: additional comment that can be logged with the data
`bar_deg`: size of the bar (bright) in degree
`space_deg`: size of the space (dark) in degree
`sweep`: set to true, if the open loop condition is supposed to be a single stimulus sweep
`closedloop_bar_deg`: size of the bar (bright) for the closed loop condition in degrees

### Stimulus Specific Files

`panels.js`
`spatial_temporal.py`
`sweep_condition.py`

## Starfield / Spheres

The starfield stimulus is a second type of stimulus in FlyFlix that also produces strong, reliable behavioral responses from drosophila. It is currently only found in the starfield branch. It is made up of small spheres that are positioned randomly on a spherical shell that has a center at the `camera`'s position. This ensures that all spheres are equally distant from the `camera`. An example of starfield stimulus can be seen below.

[Video of Starfield Stimulus](https://drive.google.com/file/d/1ElQgWLB_mimIhPGBbX6KtHEq_A1T_7ZF/view?usp=sharing)

### Starfield Parameters

`trial_id`: a unique identifier for the trial, preferably an integer number
`rotate_deg_hz`: movement speed in degrees per second, positive is clockwise
`osc_freq`: frequency of oscillations - overrides `rotate_deg_hz` and makes trial oscillating trials
`osc_width`: the width of an oscillation in degrees
`openloop_duration`: duration of the open loop condition
`closedloop_duration`: duration of the closed loop condition
`gain`: multiplier for orientation change read from the FicTrac instance
`fps`: client frame rate
`pretrial_duration`: duration of the pre-trial, where the stimulus is shown but not animated. Applies to open loop and closed loop conditions.
`posttrial_duration`: duration of the post-trial.
`comment`: additional comment that can be logged with the data
`sphere_count`: the number of spheres surrounding the fly's position
`sphere_radius_deg`: the radius of the spheres surrounding the fly's position in degrees
`radius_dev`: the deviation of possible radius sizes from the `sphere_radius_deg` in degrees
`shell_radius`: the distance between the fly's position and the spheres
`seed``: a seed that generates a set of random points
`starfield_closedloop`: boolean that determines if there is a closed loop condition for the trial

### Stimulus Specific Files

`spheres.js`
`starfield_spatial_temporal.py`
`sweep_condition.py`