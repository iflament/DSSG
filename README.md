## Data-Driven Planning for Sustainable Tourism in Tuscany <br> 

<p align="center">
  <img src="./florence.png"><br>
  <strong>
  </strong>
</p>

### News & Developments

This fork is an initiative to build an application from the exploratory DSSG 2017 Florence project.  I'm currently working on an extension of the project (CityFlows: https://github.com/iflament/cityflows), which will further expand this to be city-agnostic, and support additional data sources (such as subway and bus data). 
For any questions please email me at iflament[dot]auc[at]gmail.com. 
Happy coding! Io Flament

### Description

Mass tourism, a form of tourism that involves thousands of people visiting the same area often at the same time of year, 
is on the rise. High-speed trains and low-cost airlines allow larger amounts of people to travel faster, and more frequently than ever before. Online resources, social media, and mapping applications are making it easier to choose a destination and plan an itinerary.

Tourism is an economic asset to communities worldwide. However, many touristic destinations are insufficiently equipped to properly respond to the increasing flux of visitors. The unprecedented number of tourists is causing concern among local, regional and national goverment agencies. Cities working with analog management of their cultural resources are searching for sustainable solutions that will benefit both tourists and residents alike.

During summer 2017, our team at Data Science for Social Good analysed the spatial and temporal patterns of tourist movements within the city of Florence (data from summer 2016), one of Europe's oldest and most beautiful historical landmarks. This attempt to quantify and describe the extent of the situation is only one of the several ongoing intiatives that local government and tourism agencies are taking to better manage the influx of thousands of visitors, improve decision-making and maintain public safety. 

Original project code and documentation: https://github.com/DSSG2017/florence

### What does this software do?

The code in this repo is designed to run spatial and temporal analyses, and generate informative dynamic visualizations, on multiple civic data sources. 

Types of analyses supported in this version:
- Call detail records
- Site data (user entries at  specific locations). Can be applicable to museums or others attractions.

The all analyses modules are called from the main Pipeline.py module, which can be run as follows:
``` $ python3 Pipeline.py ```

### Getting Started

> **Note:** If you don't want to re-build the project, you may just clone this branch directly  ```https://github.com/iflament/florence```

### 1. [Download ZIP](https://github.com/iflament/florence/archive/iflament.zip) or Git Clone

```
$ git clone https://github.com/iflament/florence.git
$ cd florence
$ pip3 install -r requirements.txt
```

### Folder Structure

```  
├── viz/                # visualizations
├── src/                # source files
    ├── sql_templates/      # sql files
    └── data                # data files
```

<br>

### Input Data File Structure

Data can be input either as files (currently supporting only csv files) or directly connecting to a database containing tables with the raw data. 

Types of data supported in this version:
- Call detail records
- Tourist attraction visit data (user entries in time). Can be applicable to museums or other types of attractions that have user entry information.

### Museum data Format

Example:
WIP

```
museum_name: (str) name of the tourist attraction being visited
longitude: (float) longitude of tourist attraction being visited
latitude: (float) latitude of tourist attraction being visited
user_id: (int) user identification number or hash id (anonymized) 
entry_time: (str) time of entry at the tourist attraction
total_adults: (int) number of adults in the given entry (optional field)
minors: (int) number of minors in the given entry (optional field)

```

### Call detail Records Format

Example:
WIP

```
user_id:  (int) user identification number or hash id (anonymized) 
date_time: (str) date or time of call event
user_origin: (str) origin country or region of user (optional field)
latitude: (float) latitude of cell tower handling the call (call, sms, or other call event)
longitude: (float) longitude of cell tower handling the call (call, sms, or other call event)

```

#### Visualizations

WIP

The cloned/downloaded repository doesn't contain prebuilt version of the project and you need to build it. You need to have [NodeJs](https://nodejs.org/en/) with npm. 


Install npm dependencies 
```
npm install
```

Build the project and start local web server
```
npm start
```

Open the project [http://localhost:4000](http://localhost:4000).



