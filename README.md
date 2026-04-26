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

| Name course   |
| ------------- |
| AI Wash       |
| Auto          |
| Baby Bottle   |
| Babycare      |
| Chef          |
| Cold Rinse    |
| Daily         |
| Daily 09      |
| Delicate      |
| Drinkware     |
| Dry Only      |
| Eco           |
| Eco 08        |
| Eco 10        |
| Express       |
| Express 0C    |
| Extra Silence |
| Glasses       |
| Heavy         |
| Intensive     |
| Machine Care  |
| Night         |
| Night Silence |
| Normal        |
| Plastics      |
| Pots and Pans |
| Pre Blast     |
| Pre Wash      |
| Quick         |
| Quick 14      |
| Rinse Dry     |
| Rinse Only    |
| Self Clean    |
| Self Sanitize |
| Steam Soak    |
| Upper Express |

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

| Name mode                        | Name mode                      |
| -------------------------------- | ------------------------------ |
| AI defrost                       | Microwave roast                |
| AI reheat                        | Moist steam                    |
| AI sousvide                      | Multi grill                    |
| Air fry                          | Multi level cook               |
| Air fryer                        | Microwave + grill              |
| Air fry max                      | Microwave + convection         |
| Air sousvide                     | Microwave + hot blast          |
| Autocook                         | Microwave + hot blast 2        |
| Autocook custom                  | Natural steam                  |
| Bake                             | No operation                   |
| Bottom                           | Others                         |
| Bottom convection                | Pizza                          |
| Bottom heat                      | Pizza cook                     |
| Bottom heat + convection         | Pizza naan                     |
| Bottom heat + eConvection        | Plate warm                     |
| Bread proof                      | Power bake                     |
| Broil                            | Power convection               |
| Broil combi                      | Power convection combi         |
| Broil convection                 | Preheat                        |
| Broil S                          | Pro convection                 |
| Brownie                          | Pro roasting                   |
| Catalytic clean                  | Proof                          |
| Chef bake                        | Prove dough                    |
| Chef broil                       | Pure convection                |
| Chef proof                       | Pure convection sear           |
| Clean air pyro                   | Pure steam                     |
| Convection                       | Pyro free                      |
| Convection bake                  | Rinse                          |
| Convection broil                 | Roast                          |
| Convection combi                 | Roasting                       |
| Convection roast                 | Seafood                        |
| Convection sear                  | Self clean                     |
| Convection vegetable             | Sensor self diagnosis          |
| Conventional                     | Slim fry middle                |
| Cookie                           | Slim fry strong                |
| Defrost                          | Slim middle                    |
| DefrostA                         | Slim strong                    |
| Defrosting                       | Slow cook                      |
| Dehydrate                        | Slow cook beef                 |
| Deodorization                    | Slow cook poultry              |
| Descale                          | Slow cook stew                 |
| Drain                            | Small grill                    |
| Drying                           | Spare rib                      |
| Easycook1                        | Speed bake                     |
| Easycook2                        | Speed broil                    |
| Easycook3                        | Speed brown                    |
| Eco convection                   | Speed conv sear                |
| Eco grill                        | Speed convection               |
| Fan conventional                 | Speed grill                    |
| Fan grill                        | Speed power convection         |
| Favorite cook                    | Speed roast                    |
| Favorite recipes                 | Steam assist                   |
| Fermentation                     | Steam autocook                 |
| Fine steam                       | Steam bake                     |
| Four part pure convection        | Steam bottom convection        |
| Four part pure convection single | Steam bottom heat + convection |
| Frozen food                      | Steam bread proof              |
| Frozen mode                      | Steam clean                    |
| Green clean                      | Steam clean real               |
| Green clean real                 | Steam convection               |
| Grill                            | Steam cook                     |
| Grill convection                 | Steam proof                    |
| Guided cook                      | Steam reheat                   |
| Homecare wizard v2               | Steam roast                    |
| Healthycook1                     | Steam top convection           |
| Healthycook2                     | Stone mode                     |
| Healthycook3                     | Strong steam                   |
| Healthycook4                     | Three part pure convection     |
| Healthycook5                     | Toast bagle                    |
| Healthycook6                     | Toast croissant                |
| Heating                          | Toast sliced bread             |
| Hot blast                        | Top convection                 |
| Intensive cook                   | Top heat plus eConvection      |
| Internal clean                   | Turkey                         |
| Keep warm                        | Vapor bottom heat + convection |
| Large grill                      | Vapor cleaning                 |
| Memory cook                      | Vapor convection               |
| Microwave                        | Vapor grill                    |
| Microwave convection             | Vapor MWO                      |
| Microwave fan grill              | Vapor top heat + convection    |
| Microwave grill                  | Warm hold                      |
| Microwave hot blast              | Warming                        |

Please share the information when your oven modes are not supported!
