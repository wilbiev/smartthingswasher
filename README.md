# SmartThings Washer - Dryer
Custom integration for SmartThings Washers and Dryers

Based on SmartThings integration of @JoostLek

### Button entity support:
* Cancel
* Start
* Pause / Resume
* Estimate operation time

### Binary sensor entity support:
* BubbleSoak support (shows if BubbleSoak is supported by selected program)
* Child lock (standard)
* Remote control (standard)
* 

### Number entity support:
* Washer delay time

### Sensor entity support:
* Completion time (standard)
* Energy (standard) 
* Job state (standard)
* Machine state (standard)
* Operation time
* Operation state
* Progress
* Remaining detergent
* Remaining softener
* Remaining time
* Water consumption

### Select entity support:
* Auto dispense detergent
* Auto dispense softener
* Dry level
* Rinse cyle
* Soil level
* Spin level
* Water temperature
(select options based on selected program when remote control is on)

### Switch entity support
* BubbleSoak
* Switch per program

## Instructions for installation:

### Remove the standard SmartThings integration

### Setup custom repository in HACS

Open your Home Assistant instance and add a custom repository [Home Assistant Community Store (HACS)](https://hacs.xyz/docs/faq/custom_repositories/)
![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store](https://my.home-assistant.io/badges/hacs_repository.svg)

### Setup integration in Home Assistant

After installing, you can easily configure your devices using the Integrations configuration UI. Go to Settings / Devices & Services and press the Add Integration button, or click the shortcut button below (requires My Homeassistant configured).

![Add Integration to your Home Assistant instance](https://my.home-assistant.io/badges/config_flow_start.svg)
A red box is displayed in the integration while it replaces the standard integration

