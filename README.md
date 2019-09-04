## Data-Driven Planning for Sustainable Tourism<br> 

<p align="center">
  <img src="./florence.png"><br>
  <strong>
  </strong>
</p>

### News & Developments

This fork is an extension of the exploratory DSSG 2017 Florence project: 
For any questions please email me at iflament[dot]auc[at]gmail.com.  Io Flament

### Description

Mass tourism, a form of tourism that involves thousands of people visiting the same area often at the same time of year, 
is on the rise. High-speed trains and low-cost airlines allow larger amounts of people to travel faster, and more frequently than ever before. Online resources, social media, and mapping applications are making it easier to choose a destination and plan an itinerary.

Tourism is an economic asset to communities worldwide. However, many touristic destinations are insufficiently equipped to properly respond to the increasing flux of visitors. The unprecedented number of tourists is causing concern among local, regional and national goverment agencies. Cities working with analog management of their cultural resources are searching for sustainable solutions that will benefit both tourists and residents alike.

During summer 2017, our team at Data Science for Social Good analysed the spatial and temporal patterns of tourist movements within the city of Florence (data from summer 2016), one of Europe's oldest and most beautiful historical landmarks. This attempt to quantify and describe the extent of the situation is only one of the several ongoing intiatives that local government and tourism agencies are taking to better manage the influx of thousands of visitors, improve decision-making and maintain public safety. 

The code in this repo was designed to run the spatial and temporal analyses for the project, and generate informative dynamic visualizations, on multiple civic data sources. Original project code and documentation: https://github.com/DSSG2017/florence

#### Questions addressed:
- What locations are the most crowded, at specific: hours of the day / days of the week / dates over the summer ?
- Where do people transition to and from?

Types of data supported in this version:
- Call detail records
- Site data (user entries at  specific locations). Can be applicable to museums or others attractions.

#### Telecom EDA analyses: http://dssg-eu.org/florence/cdr_index.html
#### Museum card EDA analyses: http://dssg-eu.org/florence/firenze_index.html

<p align="left">
  <img src="./museums.gif" width="50%" height="50%"><br>
  <strong>
  </strong>
</p>

#### Interactive visualization of network of tourists mouvements throughout Florence

Additionally to informative data summaries and timeseries plots, the software also generates interactive visualizations using  Uber's DECK-GL library. These visualizations aggregate the movements of users from the different data sources, in time and space, and create 3 dimensional representations of crowding in the city.

Full page here: http://dssg-eu.org/florence/fountain.html

<p align="center">
  <img src="./transitions.gif"><br>
  <strong>
  </strong>
</p>


