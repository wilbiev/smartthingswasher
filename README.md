# SmartThings Dryer - Steam Closet - Washer
Custom integration for SmartThings Dryers, Steam Closets and Washers

Test version based on SmartThings integration of @JoostLek

## Instructions for installation

### Remove the standard SmartThings integration

The standard integration and this test version can not be installed both in one HA instance!

### Setup custom repository in HACS

Open your Home Assistant instance and add https://github.com/wilbiev/smartthingswasher as a custom repository [Home Assistant Community Store (HACS)](https://hacs.xyz/docs/faq/custom_repositories/)  <br>
![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store](https://my.home-assistant.io/badges/hacs_repository.svg)  <br>
Download the custom repository and restart Home Assistant.

### Setup integration in Home Assistant

After installing, you can easily configure your devices using the Integrations configuration UI. Go to Settings / Devices & Services and press the Add Integration button, or click the shortcut button below (requires My Homeassistant configured).

![Add Integration to your Home Assistant instance](https://my.home-assistant.io/badges/config_flow_start.svg)  <br>
A red box is displayed in the integration while it replaces the standard integration

## Additional SmartThings dryer/washer support

### Button entities
* Cancel
* Start
* Pause / Resume
* Estimate operation time

### Binary sensor entities
* BubbleSoak support (shows if BubbleSoak is supported by selected course)
* Child lock (standard)
* Remote control (standard)

### Number entities
* Delay time

### Sensor entities
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

### Select entities
* Auto dispense detergent amount
* Auto dispense detergent density
* Auto dispense softener amount
* Auto dispense softener density
* Course (when dryer/steam closet/washer cycle not available)
* Cycle courses
* Dry level*
* Dring temperature* (dryer only)
* Drying time (dryer only)
* Rinse cyle*
* Soil level*
* Spin level*
* Water temperature*

(* select options based on selected course when remote control is on)

### Switch entities
* BubbleSoak (washer only)
* Keep fresh mode (steam closet only)
* Sanitize mode (steam closet only)
* Switch per dryer/washer course

### Current dryer/steam closet/washer course support
| Name course       | Table_00      | Table_01      | Table_02      | Table_03      |
|-------------------|---------------|---------------|---------------|---------------|
|	15m Quick Wash	| Course_66	    |	        	| Course_1E	    |		        |
|	15m Quick Wash	| Course_DC	    |	        	| Course_1E	    |		        |
|	Activewear	    |		        |	        	| Course_2F	    |		        |
|	AI Dry	        |		        |	        	|		        | Course_29 	|
|	AI Wash	        |		        |		        | Course_2B	    |	        	|
|	Air Refresh	    | Course_61	    |		        | Course_37	    |	        	|
|	Baby Care	    |		        |	        	| Course_2E	    |	        	|
|	Bedding	        | Course_D6	    |	        	| Course_24	    | Course_1B	    |
|	Cloudy Day	    |		        |	        	| Course_30	    |	        	|
|	Colours	        |		        |	            | Course_21	    |		        |
|	Cool Air	    |		        |	        	|		        | Course_24	    |
|	Cotton	        | Course_5B	    |	        	| Course_1B	    | Course_16	    |
|	Cotton	        | Course_D0	    |		        | Course_1B	    | Course_16	    |
|	Cotton Dry	    |		        |		        | Course_38	    |		        |
|	Daily Wash	    | Course_5D	    |		        | Course_34	    |		        |
|	Dark Garment	| Course_D9	    |		        |		        |		        |
|	Delicates	    | Course_D3	    |		        | Course_26	    | Course_19	    |
|	Denim	        |		        |	        	| Course_2A	    |		        |
|	Denim	        |		        |		        | Course_66	    |		        |
|	Drain/Spin	    | Course_BA	    |		        | Course_28	    |		        |
|	Drum Clean	    |		        |		        | Course_29	    |		        |
|	Drum Clean	    |		        |		        | Course_3A	    |		        |
|	Drum Clean+	    |		        |		        |		        |	        	|
|	Drying	        | Course_63	    |		        |		        |		        |
|	Eco 40-60	    |		        |		        | Course_1C	    |		        |
|	Eco Drum Clean	| Course_60	    |		        |		        |		        |
|	Eco Drum Clean	| Course_D5	    |		        |		        |		        |
|	eCotton	        | Course_D1	    |		        | Course_35	    |	        	|
|	Hygiene Care	|		        |		        |	        	|		        |
|	Hygiene Steam	|		        |		        | Course_20	    |	        	|
|	Intense Cold	|		        |		        | Course_1F	    |		        |
|	Intense Cold	|		        |		        | Course_8F	    |		        |
|	Iron Dry	    |		        |	        	|		        | Course_20	    |
|	Less Microfiber	|		        |		        | Course_96	    |		        |
|	Mixed Load	    |		        |		        |		        |	        	|
|	Outdoor	        | Course_D7	    |		        | Course_23	    | Course_1E	    |
|	Quick Dry 35m	|		        |	        	|		        | Course_23 	|
|	Rinse+Spin	    | Course_5F	    |		        | Course_27	    |		        |
|	Rinse+Spin	    | Course_D4	    |	        	| Course_27	    |	        	|
|	Self Tub Dry	|		        |		        |		        | Course_2B	    |
|	Shirts	        |	        	|		        | Course_32	    | Course_1C	    |
|	Silent Dry	    |		        |		        |		        |	        	|
|	Silent Wash	    |		        |	        	| Course_2D	    |		        |
|	Spin	        | Course_5E	    |	        	|		        |		        |
|	Super Eco Wash	| Course_DA	    |	        	|		        |		        |
|	Super Speed	    | Course_DB	    |	            | Course_1D	    |	        	|
|	Synthetics	    | Course_5C	    |		        | Course_25	    | Course_18	    |
|	Synthetics	    | Course_D2	    |		        | Course_25	    | Course_18	    |
|	Synthetics Dry	|		        |		        | Course_39	    |		        |
|	Time Dry	    |		        |		        |		        | Course_27	    |
|	Towels	        |		        |		        | Course_33	    | Course_1D	    |
|	Warm Air	    |		        |		        |		        | Course_25	    |
|	Wash+Dry	    |		        |		        | Course_36	    |		        |
|	Wool	        | Course_D8	    |		        | Course_22	    | Course_1A	    |

Please share the information when your dryer/steam closet/washer courses are not supported! 