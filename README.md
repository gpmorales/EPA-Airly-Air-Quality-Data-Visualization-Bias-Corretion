# EPA-Airly-Air-Quality-Data-Visualization-Bias-Corretion
Desgined Air-quality measuring that performs within 95% of the standard EPA federal monitors at 1/500th of the price. Pandas and SciKit-Learn were used to process preliminary data collected from our fleet of Airly® sensors as well as data from the EPA federal monitors. Using linear regression and the EPA data as the variable for correction, this code produces coefficents for a bias correction model that is applied to the raw Airly readings and is then graphed + presented to our buisness partners. 

Incorporates Machine-Learning through SciKit’s linear regression toolkit to bias-correct the raw Airly® sensor data and code creates easy-to-read graphics for the refined Airly® sensor readings using Python’s Matplotlib & Seaborn libraries. The SensorMerger File was used to manipulate several large excel sheets which contained the data.

