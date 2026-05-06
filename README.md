# Bring your HA SmartThings integration to the next level!

This custom integration provides some amazing features for Dishwashers, Dryers, Ovens, Steam Closets and Washers

Custom version based on SmartThings integration of @JoostLek

## Instructions for installation

### Remove the standard SmartThings integration

The standard integration and this custom version can not be installed both in one HA instance!

### Setup custom repository in HACS

Open your Home Assistant instance and add https://github.com/wilbiev/smartthingswasher as a custom repository [Home Assistant Community Store (HACS)](https://hacs.xyz/docs/faq/custom_repositories/) <br>
![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store](https://my.home-assistant.io/badges/hacs_repository.svg) <br>
Download the custom repository and restart Home Assistant.

### Setup integration in Home Assistant

After installing, you can easily configure your devices using the Integrations configuration UI. Go to Settings / Devices & Services and press the Add Integration button, or click the shortcut button below (requires My Homeassistant configured).

![Add Integration to your Home Assistant instance](https://my.home-assistant.io/badges/config_flow_start.svg) <br>
A red box is displayed in the integration while it replaces the standard integration

## SmartThings dishwasher support

### Button entities

- Cancel
- Start
- Pause / Resume
- Start later

### Binary sensor entities (are hidden by default and can be enabled)

- Add Rinse support (shows if Add Rinse is supported by selected course)
- Dry Plus support (shows if Dry Plus is supported by selected course)
- Heated Dry support (shows if Heated Dry is supported by selected course)
- High Temp Wash support (shows if High Temp Wash is supported by selected course)
- Hot Air Dry support (shows if Hot Air Dry is supported by selected course)
- Multi Tab support (shows if Multi Tab is supported by selected course)
- Rinse Plus support (shows if Rinse Plus is supported by selected course)
- Sanitizing Wash support (shows if Sanitizing Wash is supported by selected course)
- Speed Booster support (shows if Speed Booster is supported by selected course)
- Steam Soak support (shows if Steam Soak is supported by selected course)
- Storm Wash support (shows if Storm Wash is supported by selected course)
- Child lock (standard)
- Remote control (standard)

### Number entities

- Delay start time

### Sensor entities

- Completion time (standard)
- Energy/Power consumption (standard)
- Job state (standard)
- Operating state
- Operation time
- Progress
- Remaining time
- Time left to start
- Water consumption

### Select entities

- Operating state (hidden by default)
- Selected Zone\* (if supported by dishwasher)
- Washing course
- Zone Booster\* (if supported by dishwasher)

(\* select options based on selected course when remote control is on)

### Switch entities

- Add Rinse support (if supported by dishwasher)
- Dry Plus support (if supported by dishwasher)
- Heated Dry support (if supported by dishwasher)
- High Temp Wash support (if supported by dishwasher)
- Hot Air Dry (if supported by dishwasher)
- Multi Tab (if supported by dishwasher)
- Rinse Plus (if supported by dishwasher)
- Sanitizing Wash (if supported by dishwasher)
- Speed Booster (if supported by dishwasher)
- Steam Soak (if supported by dishwasher)
- Storm Wash (if supported by dishwasher)
- Switch per dishwasher course

### Current dishwasher course support

| Name course | Name course   | Name course   |
| ----------- | ------------- | ------------- |
| AI Wash     | Eco 08        | Plastics      |
| Auto        | Eco 10        | Pots and Pans |
| Baby Bottle | Express       | Pre Blast     |
| Babycare    | Express 0C    | Pre Wash      |
| Chef        | Extra Silence | Quick         |
| Cold Rinse  | Glasses       | Quick 14      |
| Daily       | Heavy         | Rinse Dry     |
| Daily 09    | Intensive     | Rinse Only    |
| Delicate    | Machine Care  | Self Clean    |
| Drinkware   | Night         | Self Sanitize |
| Dry Only    | Night Silence | Steam Soak    |
| Eco         | Normal        | Upper Express |

Please share the information when your dishwasher courses are not supported!

## SmartThings dryer/steam closet/washer support

### Button entities

- Cancel
- Start
- Pause / Resume
- Estimate operation time

### Binary sensor entities

- Bubble Soak support (shows if Bubble Soak is supported by selected course)
- Child lock (standard)
- Remote control (standard)

### Number entities

- Delay time

### Sensor entities

- Completion time (standard)
- Energy (standard)
- Job state (standard)
- Machine state (standard)
- Operation time
- Operation state
- Progress
- Remaining detergent
- Remaining softener
- Remaining time
- Water consumption

### Select entities

- Auto dispense detergent amount (washer only)
- Auto dispense detergent density (washer only)
- Auto dispense softener amount (washer only)
- Auto dispense softener density (washer only)
- Course (when dryer/steam closet/washer cycle not available)
- Cycle courses
- Dry level\*
- Dring temperature\* (dryer only)
- Drying time (dryer only)
- Rinse cycle\*
- Soil level\*
- Spin level\*
- Water temperature\*

(\* select options based on selected course when remote control is on)

### Switch entities

- BubbleSoak (washer only)
- Keep fresh mode (steam closet only)
- Sanitize mode (steam closet only)
- Switch per dryer/washer course

### Current dryer/steam closet/washer course support

| Name course     | Table_00  | Table_01 | Table_02  | Table_03  |
| --------------- | --------- | -------- | --------- | --------- |
| 15m Quick Wash  | Course_66 |          | Course_1E |           |
| 15m Quick Wash  | Course_DC |          | Course_1E |           |
| Activewear      |           |          | Course_2F |           |
| AI Dry          |           |          |           | Course_29 |
| AI Wash         |           |          | Course_2B |           |
| Air Refresh     | Course_61 |          | Course_37 |           |
| Baby Care       |           |          | Course_2E |           |
| Bedding         | Course_D6 |          | Course_24 | Course_1B |
| Cloudy Day      |           |          | Course_30 |           |
| Colours         |           |          | Course_21 |           |
| Cool Air        |           |          |           | Course_24 |
| Cotton          | Course_5B |          | Course_1B | Course_16 |
| Cotton          | Course_D0 |          | Course_1B | Course_16 |
| Cotton Dry      |           |          | Course_38 |           |
| Daily Wash      | Course_5D |          | Course_34 |           |
| Dark Garment    | Course_D9 |          |           |           |
| Delicates       | Course_D3 |          | Course_26 | Course_19 |
| Denim           |           |          | Course_2A |           |
| Denim           |           |          | Course_66 |           |
| Drain/Spin      | Course_BA |          | Course_28 |           |
| Drum Clean      |           |          | Course_29 |           |
| Drum Clean      |           |          | Course_3A |           |
| Drum Clean+     |           |          |           |           |
| Drying          | Course_63 |          |           |           |
| Eco 40-60       |           |          | Course_1C |           |
| Eco Drum Clean  | Course_60 |          |           |           |
| Eco Drum Clean  | Course_D5 |          |           |           |
| eCotton         | Course_D1 |          | Course_35 |           |
| Hygiene Care    |           |          |           |           |
| Hygiene Steam   |           |          | Course_20 |           |
| Intense Cold    |           |          | Course_1F |           |
| Intense Cold    |           |          | Course_8F |           |
| Iron Dry        |           |          |           | Course_20 |
| Less Microfiber |           |          | Course_96 |           |
| Mixed Load      |           |          |           |           |
| Outdoor         | Course_D7 |          | Course_23 | Course_1E |
| Quick Dry 35m   |           |          |           | Course_23 |
| Rinse+Spin      | Course_5F |          | Course_27 |           |
| Rinse+Spin      | Course_D4 |          | Course_27 |           |
| Self Tub Dry    |           |          |           | Course_2B |
| Shirts          |           |          | Course_32 | Course_1C |
| Silent Dry      |           |          |           |           |
| Silent Wash     |           |          | Course_2D |           |
| Spin            | Course_5E |          |           |           |
| Super Eco Wash  | Course_DA |          |           |           |
| Super Speed     | Course_DB |          | Course_1D |           |
| Synthetics      | Course_5C |          | Course_25 | Course_18 |
| Synthetics      | Course_D2 |          | Course_25 | Course_18 |
| Synthetics Dry  |           |          | Course_39 |           |
| Time Dry        |           |          |           | Course_27 |
| Towels          |           |          | Course_33 | Course_1D |
| Warm Air        |           |          |           | Course_25 |
| Wash+Dry        |           |          | Course_36 |           |
| Wool            | Course_D8 |          | Course_22 | Course_1A |

Please share the information when your dryer/steam closet/washer courses are not supported!

## SmartThings oven support

### Button entities

- Pause
- Start\*
- Stop
- Time sync

(\* Can only be used when supported by selected mode)

### Binary sensor entities (are hidden by default and can be enabled)

- Dual mode

### Number entities

- Temperature\*
- Operation time\*

(\* Minimum, maximum and step values based on selected mode)

### Sensor entities

- Completion time (additional sensor for Dual mode)
- Energy/Power consumption (standard)
- Job state (additional sensor for Dual mode)
- Operating state (additional sensor for Dual mode)
- Operation time (additional sensor for Dual mode)
- Progress (additional sensor for Dual mode)
- Setpoint (additional sensor for Dual mode)

### Select entities

- Oven mode Single (Dual mode: Single/Upper\*)
- Oven mode Lower (only Dual mode)

(\* Modes depend on status Dual mode binary_sensor, conditional card can be used in dashboard to switch between Single and Dual mode)

### Current oven mode support

| Name mode                 | Name mode                        | Name mode                      |
| ------------------------- | -------------------------------- | ------------------------------ |
| AI defrost                | Four part pure convection single | Roast                          |
| AI reheat                 | Frozen food                      | Roasting                       |
| AI sousvide               | Frozen mode                      | Seafood                        |
| Air fry                   | Green clean                      | Self clean                     |
| Air fryer                 | Green clean real                 | Sensor self diagnosis          |
| Air fry max               | Grill                            | Slim fry middle                |
| Air sousvide              | Grill convection                 | Slim fry strong                |
| Autocook                  | Guided cook                      | Slim middle                    |
| Autocook custom           | Homecare wizard v2               | Slim strong                    |
| Bake                      | Healthycook 1                    | Slow cook                      |
| Bottom                    | Healthycook 2                    | Slow cook beef                 |
| Bottom convection         | Healthycook 3                    | Slow cook poultry              |
| Bottom heat               | Healthycook 4                    | Slow cook stew                 |
| Bottom heat + convection  | Healthycook 5                    | Small grill                    |
| Bottom heat + eConvection | Healthycook 6                    | Spare rib                      |
| Bread proof               | Heating                          | Speed bake                     |
| Broil                     | Hot blast                        | Speed broil                    |
| Broil combi               | Intensive cook                   | Speed brown                    |
| Broil convection          | Internal clean                   | Speed conv sear                |
| Broil S                   | Keep warm                        | Speed convection               |
| Brownie                   | Large grill                      | Speed grill                    |
| Catalytic clean           | Memory cook                      | Speed power convection         |
| Chef bake                 | Microwave                        | Speed roast                    |
| Chef broil                | Microwave convection             | Steam assist                   |
| Chef proof                | Microwave fan grill              | Steam autocook                 |
| Clean air pyro            | Microwave grill                  | Steam bake                     |
| Convection                | Microwave hot blast              | Steam bottom convection        |
| Convection bake           | Microwave roast                  | Steam bottom heat + convection |
| Convection broil          | Microwave + grill                | Steam bread proof              |
| Convection combi          | Microwave + convection           | Steam clean                    |
| Convection roast          | Microwave + hot blast            | Steam clean real               |
| Convection sear           | Microwave + hot blast 2          | Steam convection               |
| Convection vegetable      | Moist steam                      | Steam cook                     |
| Conventional              | Multi grill                      | Steam proof                    |
| Cookie                    | Multi level cook                 | Steam reheat                   |
| Defrost                   | Natural steam                    | Steam roast                    |
| DefrostA                  | No operation                     | Steam top convection           |
| Defrosting                | Others                           | Stone mode                     |
| Dehydrate                 | Pizza                            | Strong steam                   |
| Deodorization             | Pizza cook                       | Three part pure convection     |
| Descale                   | Pizza naan                       | Toast bagle                    |
| Drain                     | Plate warm                       | Toast croissant                |
| Drying                    | Power bake                       | Toast sliced bread             |
| Easycook1                 | Power convection                 | Top convection                 |
| Easycook2                 | Power convection combi           | Top heat plus eConvection      |
| Easycook3                 | Preheat                          | Turkey                         |
| Eco convection            | Pro convection                   | Vapor bottom heat + convection |
| Eco grill                 | Pro roasting                     | Vapor cleaning                 |
| Fan conventional          | Proof                            | Vapor convection               |
| Fan grill                 | Prove dough                      | Vapor grill                    |
| Favorite cook             | Pure convection                  | Vapor MWO                      |
| Favorite recipes          | Pure convection sear             | Vapor top heat + convection    |
| Fermentation              | Pure steam                       | Warm hold                      |
| Fine steam                | Pyro free                        | Warming                        |
| Four part pure convection | Rinse                            |                                |

Please share the information when your oven modes are not supported!
