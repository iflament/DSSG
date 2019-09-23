## Data-Driven Planning for Sustainable Tourism - A Data Science for Social Good Project<br> 

<p align="center">
  <img src="./florence.png"><br>
  <strong>
  </strong>
</p>

This project was conducted as part of Data Science for Social Good (DSSG) Europe 2017 fellowship, further details of the twelve week summer fellowship can be found here: https://dssg.uchicago.edu/europe/

DSSG Fellows: Io Flament, Momim Malik, Cristina Lozano
Technical Mentor: Qiwei Han
Project Manager: Laura Szczuczak

Project website with interactive visualizations: http://dssg-eu.org/florence

### Description

Mass tourism, a form of tourism that involves thousands of people visiting the same area often at the same time of year, 
is on the rise. High-speed trains and low-cost airlines allow larger amounts of people to travel faster, and more frequently than ever before. Online resources, social media, and mapping applications are making it easier to choose a destination and plan an itinerary.

Tourism is an economic asset to communities worldwide. However, many touristic destinations are insufficiently equipped to properly respond to the increasing flux of visitors. The unprecedented number of tourists is causing concern among local, regional and national goverment agencies. Cities working with analog management of their cultural resources are searching for sustainable solutions that will benefit both tourists and residents alike.

During summer 2017, our team at Data Science for Social Good analysed the spatial and temporal patterns of tourist movements within the city of Florence (data from summer 2016), one of Europe's oldest and most beautiful historical landmarks. This attempt to quantify and describe the extent of the situation is only one of the several ongoing intiatives that local government and tourism agencies are taking to better manage the influx of thousands of visitors, improve decision-making and maintain public safety.  

The code in this repo was developed to run the spatial and temporal analyses of the project, and generate informative dynamic visualizations, on multiple civic data sources. Research questions included: What locations are the most crowded, at specific: hours of the day / days of the week / dates over the summer? Where do people transition to and from?

#### Anonymized call detail records (Telecom) EDA analyses: http://dssg-eu.org/florence/cdr_index.html
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


