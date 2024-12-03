1. Slow-to-Start: As in the BJH rule, if v = 0 and d > 1 then with probability
1 − pslow the car accelerates normally (this step is ignored), and with probability pslow the car stays at velocity 0 on this time step (does not move)
and accelerates to v = 1 on the next time step.
2. Deceleration (when the next car is near): if d <= v and either v < vnext
or v <= 2, then the next car is either very close or going at a faster speed,
and we prevent a collision by setting v ← d − 1, but do not slow down more
than is necessary. Otherwise, if d <= v, v >= vnext , and v > 2 we set
v ← min(d − 1, v − 2) in order to possibly decelerate slightly more, since the
car ahead is slower or the same speed and the velocity of the current car is
substantial.
3. Deceleration (when the next car is farther): if v < d <= 2v, then if v >=
vnext +4, decelerate by 2 (v ← v−2). Otherwise, if vnext +2 <= v <= vnext +3
then decelerate by 1 (v ← v − 1).
4. Acceleration: if the speed has not been modiﬁed yet by one of rules 1-3 and
v < vmax and d > v + 1, then v ← v + 1.
5. Randomization: if v > 0, with probability pf ault , velocity decreases by one
(v ← v − 1).
6. Motion: the car advances v cells.

Slow-to-Start
1. When a car is completely stopped and there's enough space ahead, it doesn't always start moving right away. 
Instead, there's a chance it decides to wait for one more moment before it begins to move.

2. Deceleration (When the Next Car Is Near)
If the car in front is very close or moving slower, the following car will slow down to avoid a crash. Specifically:

If the distance to the next car is less than or equal to the current car's speed, and either:
* The next car is going faster, or
* The current speed is low (2 or below),
then the following car reduces its speed just enough to stay safe.

3. Deceleration (When the Next Car Is Farther)
Even if the next car isn't immediately close, if it's somewhat far but within twice your speed, 
you might still need to slow down, especially if:

You're going much faster than the car ahead (by 4 or more),

Then: Slow down by 2 units of speed.

Or if you're going a bit faster than the car ahead (by 2 or 3),

Then: Slow down by 1 unit of speed.

4. 