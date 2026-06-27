# Vanguard Telematics: UC Berkeley AI Hackathon

### 1st place prize QNX track + honorable mentions @ Fetch AI

*They protect us. Who protects them? This is more than a hackathon idea... Vanguard Telematics is our effort to ensure that those who run toward danger are never left behind in the data silence.*

## Quick Links
- **ASI:One Shared Chat Links:** 
  - [Link 1](https://asi1.ai/invite?channelInviteKey=EUZbyUu8nbYVK2xhekQN3EtGY60i_5mh0dGM9UuKV7I)
  - [Link 2](https://asi1.ai/invite?channelInviteKey=5Mb2Ov6_U4rAzxkd5rPNcIdd2zxD5tkx_E99IssFui4)
- **Agentverse Profiles:** 
  - [Agent 1](https://agentverse.ai/agents/details/agent1q05xhz7crc75lwt84v0u78mt2lswwr2a7n0wntp0zpuyedum80m3qwm4rnu/profile)
  - [Agent 2](https://agentverse.ai/agents/details/agent1qgsr563q7gy2y97s4wp8rp3hjw3979xhcdjpnzu3f2vmf4c8pda0jkgsdsv/profile)
  - [Agent 3](https://agentverse.ai/agents/details/agent1q0sfkv77ye39d8ctsj6rxgzapmulas4lx0ygd8ek2lxuw2ks3p3659kj04g/profile)

## The Blind Spot in Disaster Response (Inspiration)

82% of U.S. fire departments are all- or mostly-volunteer, protecting roughly 100 million people concentrated exactly in the rural, lower-density areas where cell and radio coverage is weakest. Federal studies have found that communications outages hit within the first 24 hours in more than half of recent major U.S. wildfires.

Current solutions fall short:
- **Infrastructure Dependencies:** FirstNet is the dominant public-safety connectivity platform and invests in deployable cell sites—but those are requested ground assets, not native gear riding on every truck by default.
- **Blind Communications Pipes:** Mesh tech like goTenna Pro/Pro X is real, proven off-grid tech used by humanitarian responders. However, it relays messages perfectly but acts solely as a pipe. It doesn't sense or diagnose anomalies on its own.
- **The Operator Dependency:** If an incident occurs and the operator is incapacitated, the best radio network in the world cannot transmit a cry for help.

We kept circling back to the same question: *what happens in the minutes after an incident, before anyone has even picked up a radio?* A vehicle that can sense and describe what just happened to it—without needing a human to triage it first—is a massive, underserved need.

## What It Does: Live 3D Telemetry & Edge Sensing

Our project watches a vehicle's vitals in real time—accelerometer, vibration, temperature, and pressure from an industrial sensor rig, plus a proximity sensor and a camera that feeds live video the moment something gets too close. 

All of it streams into a live dashboard with a 3D model (we used a Cybertruck) that visually reacts to the incoming data. A human supervisor can see exactly what the truck is "feeling" at any exact millisecond, without relying on verbal reports.

Underneath that, a custom Fetch.ai multi-agent system watches the same streams and decides, on its own, when something anomalous has actually happened. It then generates a free-text, situation-specific description of the event instead of picking from a small, hardcoded list of crash types. The pipeline generalizes across first-responder vehicle types, accounting for the very different normal operating signatures of an ambulance versus a fire engine.

## Deterministic Edge Architecture: How We Built It

### Hardware & Real-Time Foundation
- **Raspberry Pi 5 + QNX:** The rig runs under QNX—a real-time OS providing the strict reliability first responders need. Event detection stays low-latency and deterministic instead of fighting a general-purpose scheduler.
- **Industrial Nucleo Rig:** Feeds raw accelerometer, vibration, temperature, and pressure data seamlessly. It processes vehicular physics directly, remaining completely agnostic to specific vehicle CAN buses.
- **Redis Telemetry Store:** Redis sits behind everything as the live, ultra-low latency telemetry store. Both the dashboard visualizer and the downstream agent pipeline read directly from this high-speed memory layer.

### The Crash-Detection Brain
Built as a layered Fetch.ai (uAgents) pipeline. Because we didn't have a pre-built "sentry" crash-detection signal to lean on, the trigger agent had to derive one itself. It maintains a rolling, per-vehicle baseline (mean and standard deviation) for each sensor feature and computes a z-score. It flags an event only when multiple sensors cross the threshold together for several consecutive samples. This filters out single-sensor noise (like a pothole or a slammed door) while catching real multi-sensor anomalies. 

That trigger hands a buffered pre/post-event window to downstream agents, which extract physics features, pull context for the specific vehicle, and feed an LLM-grounded synthesis step that writes an open-ended incident description rather than forcing the event into a few fixed categories.

## Challenges & Technical Realities

- **The Radio Reality:** We originally wanted true off-grid relay—in the spirit of what goTenna does for mesh comms—so the system could report out even with no cell or Wi-Fi coverage. We tried wiring a radio link to the Pi 5 and hit a wall: strict FCC regulatory limits on unlicensed RF and massive practical RF interference made it unreliable to get clean text through to and from the board. We made the call to descope it for the weekend and treat it as a natural next step.
- **Generalized Detection:** Without an existing crash-detection signal to wrap, we had to build trigger logic from raw sensor physics. We wanted to avoid arbitrary thresholds and generalizing events across vehicles. Getting a rolling baseline that adapts per vehicle—separating real multi-sensor signals from noise without missing genuine events—took immense iterations.

## Accomplishments We're Proud Of

- Building a dashboard visualizer that showed our data was realistic and reliable enough to generate meaningful analytics from.
- Getting real sensor hardware talking to a real-time OS on actual embedded hardware, end-to-end, in a single weekend.
- Building an anomaly detector from first principles (rolling baselines and multi-sensor z-scores) instead of a hardcoded if/else crash classifier.
- Pairing deterministic signal processing with a reasoning layer that produces open-ended, vehicle-specific incident descriptions instead of forcing every event into canned labels.
- Doing the homework before writing code: we went in with real numbers on who this actually affects and a clear-eyed view of the gap we were actually trying to close.

## What We Learned

Radio is a much harder problem than "just send a signal"—between licensing and interference, it's a real compliance and RF-engineering problem, not a wiring exercise you can finish in a weekend. We also learned that you can't shortcut crash detection with a single magic threshold number if you actually care about it generalizing across vehicles. You have to understand what a real anomaly looks like across multiple sensors at once, which pushed us toward a statistically grounded approach instead of guessed constants. And splitting the pipeline into agents—deterministic, testable signal processing in one layer, open-ended LLM reasoning in another—made the whole system much easier to debug than one big classifier would have been.

## The Road Ahead

- **Certified Mesh Integration:** Solving off-grid relay properly by pairing our data pipeline with certified mesh hardware like goTenna Pro, rather than fighting licensing constraints and raw RF interference ourselves.
- **Real-World Drop Testing:** Executing physical impact testing across more vehicle types (ambulance, fire engine) to calibrate the rolling baselines per vehicle class instead of relying purely on bench simulation.
- **Analytics Loop:** Closing the loop with the multi-agent system to gain more meaningful macro-analytics to aid second responders, helping inform authorities of shifting disaster zones.

---

## Technical Details

### DataLogFusion Clone
Repurposed from https://www.st.com/en/embedded-software/x-cube-mems1.html. Modified clone of the DataLogFusion firmware from STMicroElectronics:  `\x-cube-mems1\Projects\NUCLEO-F401RE\Applications\IKS5A1\DataLogFusion`

Logs to Serial port - 115200 8N1

The sampling frequency of the measurements is 100 Hz (a sampling period of 10 ms).

```c
# app_mems.c

#define ALGO_FREQ  100U /* Algorithm frequency 100Hz */
#define ALGO_PERIOD  (1000U / ALGO_FREQ) /* Algorithm period [ms] = 10ms */
```

### Output format

```bash
timestamp,acc_x_mg,acc_y_mg,acc_z_mg,gyr_x_mdps,gyr_y_mdps,gyr_z_mdps,mag_x_mgauss,mag_y_mgauss,mag_z_mgauss,press_hpa,roll_deg,pitch_deg,yaw_deg
00:02:54.60,-50,-21,996,0,210,-210,526,-162,-345,1005.83,17.68,2.88,1.12
00:02:54.61,-51,-22,997,-210,70,-210,531,-165,-345,1005.83,17.68,2.88,1.12
```

### CSV Header Summary

| Column Name | Data Type | Units | Description |
| :--- | :--- | :--- | :--- |
| **`timestamp`** | String | `HH:MM:SS.hh` | Real-Time Clock (RTC) timestamp (Hours:Minutes:Seconds.hundredths) |
| **`acc_x_mg`** / **`y`** / **`z`** | Integer | $mg$ (milli-g) | Accelerometer axes value ($1000\text{ mg} \approx 9.81\text{ m/s}^2$) |
| **`gyr_x_mdps`** / **`y`** / **`z`** | Integer | $mdps$ | Gyroscope axes angular rate value (milli-degrees per second) |
| **`mag_x_mgauss`** / **`y`** / **`z`**| Integer | $mgauss$ | Magnetometer axes magnetic field intensity value (milli-gauss) |
| **`press_hpa`** | Float | $hPa$ | Ambient atmospheric pressure (hectopascals) |
| **`roll_deg`** | Float | Degrees | Estimated device **Roll** angle from MotionFX Sensor Fusion |
| **`pitch_deg`** | Float | Degrees | Estimated device **Pitch** angle from MotionFX Sensor Fusion |
| **`yaw_deg`** | Float | Degrees | Estimated device **Yaw** (heading) angle from MotionFX Sensor Fusion |

---

### QNX configuration

Plug in the kit.

```bash
[qnxuser@qnxpi18 ~]$ usb -v
USB 0 (XHCI) v10.00, v1.01 DDK, v2.00 HCD, DLL: Active
    Control, Interrupt, Bulk(SG), Isoch(Stream), High Speed, Super Speed, DMA:32-bit

Device Address             : 1
Upstream Host Controller   : 0
Upstream Device Address    : 0
Upstream Port              : 1
Upstream Port Speed        : Full
Vendor                     : 0x0483 (STMicroelectronics)
Product                    : 0x374b (STM32 STLink)
Device Release             : r1.00
Class                      : 0xef (Miscellaneous)
Subclass                   : 0x02
Protocol                   : 0x01
Max PacketSize0            : 64
Configurations             : 1
  Configuration            : 1
    Attributes             : 0x80 (Bus-powered)
    Max Power              : 300 mA

USB 1 (XHCI) v10.00, v1.01 DDK, v2.00 HCD, DLL: Active
    Control, Interrupt, Bulk(SG), Isoch(Stream), High Speed, Super Speed, DMA:32-bit
```

You must configure the the driver tool to help the pi/qnx to understand the USB 

https://devblog.qnx.com/get-gps-data-on-qnx-with-a-usb-gps/

```bash
# you can request the binary from john in the discord
# or it is in the tools somewhere :D
scp devc-serusb qnxuser@172.20.10.7:/tmp/

# give permissions to the binary and configure anything active
chmod +x /tmp/devc-serusb
sudo /tmp/devc-serusb

# check what serial line the USB device is using
ls -l /dev/ser*

# ex gives me /dev/serusb1

# set the correct baud rate to that line
stty baud=115200 < /dev/serusb1

# verify 
stty < /dev/serusb1
```

### Raspberry Pi Hardware Sensor Code

We have cloned QNX's example repository for sensors: 

https://github.com/qnx/Raspberry-Pi-Hardware-Component-Samples
(pi sensor sample code)

https://gitlab.com/qnx/projects/camera-projects/applications/camera-dump-frame-no-screen
(camera sample code)

And modified for "poor mans sentry mode", where we use an infrared sensor to start a camera only when infrared activity is detected

#### Wiring IR Obstacle Sensor 

Wiring: Connected VCC to 3.3V to protect the Pi's GPIO pins, GND to ground, and SIG (Signal / OUT) to GPIO 21.

```bash
# ssh helper shortcut 
ssh qnxuser@172.20.10.7
```
