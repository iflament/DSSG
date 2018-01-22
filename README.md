ta-Driven Planning for Sustainable Tourism in Tuscany <br> 

<p align="center">
  <img src="./florence.png"><br>
  <strong>
    <a href="" target="_blank">View Demo</a> 
  </strong>
</p>

### News & Developments

This fork is an initiative to build an application from the exploratory DSSG 2017 Florence project.  I'm currently working on an extension of the project (CityFlows: https://github.com/iflament/cityflows), which will further expand this to be city-agnostic, and support additional data sources (such as subway and bus data). 
For any questions please email me at iflament[dot]auc[at]gmail.com. 
Happy coding! Io Flament

### Description

Mass tourism, a form of tourism that involves thousands of people visiting the same area often at the same time of year, 
is on the rise. High-speed trains and low-cost airlines allow larger amounts of people to travel faster, and more frequently than ever before. Online resources, social media, and mapping applications are making it easier to choose a destination and plan an itinerary.

Tourism is of great economic benefit to communities worldwide, however many touristic destinations are insufficiently equipped to react to the increasing flux of visitors. An unprecedented number of tourists is causing concern among local, regional and national goverment agencies. Cities working with analog management of their cultural resources are often insufficently equipped to react to the effects of mass crowding, and are looking for sustainable solutions to provide the best experience for both tourists and residents.

During summer 2017, our team at Data Science for Social Good analysed the spatial and temporal patterns of tourist movements within the city of Florence (data from summer 2016), one of Europe's oldest and most beautiful historical landmarks. This attempt to quantify and describe the extent of the situation is only one of the several ongoing intiatives that local government and tourism agencies are taking to better manage the influx of thousands of visitors, improve decision-making and maintain public safety. 

Original project code and documentation: https://github.com/DSSG2017/florence

### What does this software do?

The code in this repo is designed to run spatial and temporal analyses on multiple civic data sources.

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

```
museum_name: str
longitude: float	
latitude: float
museum_id: int
short_name: str
user_id: int
entry_time: str
total_adults: int (optional field)
minors: int (optional field)

```

### Call detail Records Format

```
user_id: int
date_time: str
user_origin: str (optional field)
in_city: bool
latitude: float
longitude: float	

```

#### Visualizations

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


