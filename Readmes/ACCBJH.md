



## ACC Rules for BJH 

1. **Emergency Deceleration**:  
   If the distance to the next car is less than 2 cells, set `v ← max(d - 1, 0)` to prevent a collision.

2. **Maintaining Safe Distance**:  
   - Calculate desired gap: `desired_gap = base_gap + time_headway × v`  
   - If `d < desired_gap`:  
     - If `v > vnext`, set `v ← max(vnext, v - 1)`  
     - Else, set `v ← max(v - 1, 0)`  
   - If `d > desired_gap + 1` and `v < vmax`, set `v ← v + 1`

3. **Cruise Speed Adjustment**:  
   If the car is below cruise speed and the gap is sufficient, increment speed: `v ← v + 1` until `v = vmax`.

4. **Randomization (Fault Simulation)**:  
   If `v > 0`, with probability `pfault`, set `v ← v - 1` to simulate unexpected slowdowns.

5. **Motion**:  
   Advance the car by `v` cells: `position ← (position + v) % road_length`.

---

### Explanation:

1. **Emergency Deceleration**  
   - In situations where the car is critically close to the vehicle ahead, it reduces speed drastically to prevent collisions.

2. **Maintaining Safe Distance**  
   - ACC ensures that the car keeps a safe and dynamic gap from the vehicle in front, adapting based on speed and the traffic situation.  
   - If the gap is too small, it slows down. If there's enough room, it speeds up.

3. **Cruise Speed Behavior**  
   - When no immediate adjustments are needed, the car aims to reach and maintain a steady cruising speed.

4. **Randomization**  
   - This adds realism by introducing occasional unexpected slowdowns, mimicking real-world variability in driver behavior or road conditions.

5. **Motion**  
   - The car's position is updated after all speed calculations, reflecting its movement on the road.  





