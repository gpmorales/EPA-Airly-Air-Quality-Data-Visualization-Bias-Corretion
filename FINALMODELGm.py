# Author : George Morales @ Emory University
# Import Necessary Libraries 
import warnings
import pytz
import numpy as np
import pandas as pd
from datetime import datetime
from matplotlib import pyplot as plt, dates
from matplotlib import style
from statistics import mean
from sklearn import linear_model

warnings.filterwarnings("ignore"); # Ignores insignificant warning

''' PREPARING DATA FROM EXCEL/CSV '''
''' Create DataFrame containing Airly raw data '''
fileName = "Pre7284.xlsx";
RawDataFrame = pd.DataFrame(pd.read_excel(fileName)); # *************************************

''' Create DataFrame containing EPA data '''
RegulatedDataFrame = pd.DataFrame(pd.read_excel("EPA_regulatory_continuous.xlsx"));


''' SELECT TIME PERIOD for Model + Daily/Hourly Averages + Sensor Type '''
StartTime = "2021-09-06 06:00:00"; # **** SELECT Start Period ****
EndTime = "2021-11-08 00:00:00"; # **** SELECT End Period **** 11-08 00:00:00
sensor = 'pm25'; # **** SELECT Sensor/Temp/Quantity ****
SensId = fileName[3:7]; #DO NOT MODIFY THIS FOR DEMO! 
TimeUnits = 60; #DO NOT MODIFY THIS LINE !

Daily = False; # IF true, Daily Averages will be used for model, otherwise Hourly averages will be utilized
FileName = "Airly_Dec.xlsx";


''' Format and prepare Raw Airly Data '''
RawDataFrame.Date = pd.to_datetime(RawDataFrame.Date);
AirlyTime = RawDataFrame['Date']; # DateTime for AIRLY Data

AirlyTime = AirlyTime[AirlyTime >= StartTime];
AirlyTime = AirlyTime[AirlyTime <= EndTime];

AirlyData = RawDataFrame[RawDataFrame.Date >= StartTime];
AirlyData = AirlyData[AirlyData.Date <= EndTime];
TempAirly = AirlyData[sensor]; # Temp Variable
 # Prepares EPA data for linear regression modeling

if( Daily ):
    AirlyData = AirlyData[RawDataFrame.Date.dt.hour%24 == 0];
    AirlyData = AirlyData[RawDataFrame.Date.dt.minute == 0];
    AirlyTime = AirlyTime[RawDataFrame.Date.dt.hour%24 == 0];
    AirlyTime = AirlyTime[RawDataFrame.Date.dt.minute == 0];

else:
    AirlyData = AirlyData[RawDataFrame.Date.dt.minute%TimeUnits == 0];
    AirlyTime = AirlyTime[RawDataFrame.Date.dt.minute%TimeUnits == 0];

AirlyTime = AirlyTime.apply(lambda x : str(x)); # Convert datetime obj to Str for timezone conversion
AirlyData = AirlyData[sensor]; # PM25 Airly Data particular matter, id7604


''' Computing Average for Given Time Periods '''
def GroupifyData(NewData, TempData, bool):
    if( Daily ):
        j = 1;
        if( bool == False ): j = 5; # If its NOT regulatory
        i = 0;
        Lo = 0;
        Hi = int(1440/j);
        for item in NewData:
            ind = NewData.index[i]
            Val = TempData.iloc[Lo:Hi].mean(axis=0, skipna = True)
            NewData[ind] = Val;
            Lo = Lo + int(1440/j);
            Hi = Hi + int(1440/j);
            i = i + 1;

    else: # If HOURLY
        j = 1;
        if( bool == False ): j = 5;
        i = 0;
        Lo = 0;
        Hi = int(TimeUnits/j);
        for item in NewData:
            ind = NewData.index[i]
            Val = TempData.iloc[Lo:Hi].mean(axis=0, skipna = True)
            NewData[ind] = Val;
            Lo = Lo + int(TimeUnits/j);
            Hi = Hi + int(TimeUnits/j);
            i = i + 1;


GroupifyData(AirlyData, TempAirly, False); # Group data into average for Different periods (daily or hourly)

''' Time Conversion Function '''
def convTz(dt, tzOld, tzNew):
    tzOld = pytz.timezone(tzOld);
    tzNew = pytz.timezone(tzNew);

    dt = datetime.strptime(dt,"%Y-%m-%d %H:%M:%S")
    dt = tzOld.localize(dt);
    dt = dt.astimezone(tzNew);
    dt = dt.strftime("%Y-%m-%d %H:%M:%S")
    return dt;

AirlyTime = AirlyTime.apply(lambda x : convTz(x, "Europe/Dublin","America/Cancun")); # APPLY Time conversion to all Airly Data
AirlyTime = pd.to_datetime(AirlyTime); # convert to Datetime obj



''' Create and format EPA sensor Data '''
RegulatedDataFrame['Date-Time'] = pd.to_datetime(RegulatedDataFrame['Date-Time']);

''' Selects TIME FRAME for comparisons from EPA since its Data Per Minute '''
RegulTime = RegulatedDataFrame['Date-Time'];
RegulTime = RegulTime[RegulTime >= StartTime];
RegulTime = RegulTime[RegulTime <= EndTime];

EpaSens = "";
if( sensor == 'pm25'): EpaSens = "PM2.5";
else: EpaSens = "PM10";

RegulData = RegulatedDataFrame[EpaSens]; # Prepares EPA data for linear regression modeling
RegulData = RegulData[RegulatedDataFrame['Date-Time'] >= StartTime];
RegulData = RegulData[RegulatedDataFrame['Date-Time'] <= EndTime];
TempRegul = RegulData;
TempRegul = TempRegul.astype(float);

if( Daily ):
    RegulData = RegulData[RegulatedDataFrame['Date-Time'].dt.hour%24 == 0];
    RegulData = RegulData[RegulatedDataFrame['Date-Time'].dt.minute == 0];
    RegulTime = RegulTime[RegulTime.dt.hour%24 == 0];
    RegulTime = RegulTime[RegulTime.dt.minute == 0];

else:
    RegulData = RegulData[RegulatedDataFrame['Date-Time'].dt.minute%TimeUnits == 0];
    RegulTime = RegulTime[RegulTime.dt.minute%TimeUnits == 0];


GroupifyData(RegulData, TempRegul, True); # Group data into Daily averages OR Hourly averages

RegulData = RegulData.dropna();
RegulTime = RegulTime.dropna();


''' Visualization BEFORE Correction '''
def Visualize(AirlyTime, RegulTime):
    plt.plot(RegulTime,RegulData, color = 'green');
    plt.plot(AirlyTime,AirlyData, color = 'red'); #Individual trends over time for both Air and EPA
    plt.ylabel("Reading");
    plt.legend(["EPA","Airly"]);
    plt.title("Raw PM25 Readings Early September");
    plt.show();

#Visualize(AirlyTime,RegulTime); ***


''' Prepare Airly Data for Linear Regression '''
RegulData = RegulData.dropna();
AirlyData = AirlyData.dropna();

EPAlist = RegulData.tolist();
AirlyList = AirlyData.tolist();

for item in range(len(EPAlist) - len(AirlyList)):
    EPAlist.pop();

''' Convert our dataframes into Numpy Arrays '''
Xs = np.array( AirlyList, dtype = np.float64);
Ys = np.array( EPAlist, dtype = np.float64);


''' *************** Creating the Model **************** '''
''' METHOD takes in two lists and calculates line of best fit for all data '''
def SkLearnModel(): # Sci-Kit least Sqaures modeling and prediction tool 
    Epa_Airly = linear_model.LinearRegression(); ''' Create Linear Regression Object '''
    Epa_Airly.fit(Xs.reshape(-1,1),Ys); '''train the model'''
    regression_line = Epa_Airly.predict(Xs.reshape(-1,1));
    #plt.plot(Xs,regression_line);
    return Epa_Airly.coef_, Epa_Airly.intercept_;
    #Return our OUR SLOPE Coefficient and Y-Intercept Coefficient ********

''' Extraction of Coefficients for Bias Correction Modeling '''
CoefA,CoefB = SkLearnModel(); # We will use these values later !!!!
print(CoefA, CoefB);
CoefA = float(CoefA); # Quick data type conversion

''' Linear Regression Visualization '''
def LinearRegress():
    style.use('seaborn');
    plt.scatter(Xs,Ys, label = 'Data Points', alpha = 0.6, color = 'green', s = 75);# ******** Quick Data Scattering Visual ********
    plt.show();

#LinearRegress(); ***

''' After Regression is Applied '''
def FinalPlot():
    AirlyData = AirlyData.apply(lambda x : CoefA*x + CoefB); # USing lamdba function on DataFrame for Airly PM25
    plt.plot(RegulTime, RegulData, color = 'green');
    plt.plot(AirlyTime, AirlyData, color = 'red');
    plt.ylabel("Reading");
    plt.legend(["EPA","Airly"]);
    plt.title("Corrected PM25 Readings Early September");
    plt.show();

#FinalPlot(); ***



''' ***************** USING THE MODEL ***************** '''
''' Make new data frame for time period Dec -> March -> and apply linear regression model to raw Airly Data'''

#fileName = ********************************************************
#FileName = "Airly_Jan.xlsx";
RawAirly = pd.DataFrame(pd.read_excel(FileName)); # Create Dataframe from Excel file

intSensID = int(SensId); # 
RawAirlyData = RawAirly[RawAirly.id == intSensID];
RawAirlyData['Date'] = pd.to_datetime(RawAirlyData['Date']);
RawAirlyTime = RawAirlyData['Date'];

Temp = RawAirlyData[sensor]; # sensor is predefined - just the readings for that sensor for all times

if( Daily ):
    RawAirlyData = RawAirlyData[RawAirlyData['Date'].dt.hour%24 == 0];
    RawAirlyData = RawAirlyData[RawAirlyData['Date'].dt.minute == 0];
    RawAirlyTime = RawAirlyTime[RawAirlyTime.dt.hour%24 == 0];
    RawAirlyTime = RawAirlyTime[RawAirlyTime.dt.minute == 0];

else:
    RawAirlyData = RawAirlyData[RawAirlyData['Date'].dt.minute%TimeUnits== 0];
    RawAirlyTime = RawAirlyTime[RawAirlyTime.dt.minute%TimeUnits == 0];

RawAirlyData = RawAirlyData[sensor];

GroupifyData(RawAirlyData, Temp, False); # Group data into averages periods
style.use('seaborn');

''' FINAL visualization of Bias Correction on Data for Spring Period '''
plt.plot(RawAirlyTime, RawAirlyData, color = 'red'); #Individual trends over time for both Air and EPA

Time = "";
if( Daily ): Time = "Daily";
else: Time = "Hourly";

# Y-Axis labeling
if( sensor == 'pm25' ):
    plt.ylabel("$PM_{2.5}$ [μg/m^3]");
else:
    plt.ylabel("$PM_{10}$ [μg/m^3]");

plt.title("Sensor {} - South Paulding County High School".format(SensId));

CorrectedAirlyData = RawAirlyData.apply(lambda x : CoefA*x + CoefB); # ******** USE COEFFICIENTS FOR BIAS CORRECTION
plt.plot(RawAirlyTime, CorrectedAirlyData, color = 'green'); #Individual trends over time for both Air and EPA


if( Daily ):
    plt.xlabel("Date[daily]");
else:
    plt.xlabel("Date[hourly]");

if( Daily and sensor == 'pm25' ):
    plt.axhline(y = 35, color = "black", linestyle = '--');
    plt.legend(["Raw","Bias-Corrected","EPA Daily Average Standard"]);

elif( not Daily or sensor != 'pm25'):
    plt.legend(["Raw","Bias-Corrected"]);


plt.axhline(y = 45, color = "white", linewidth = 0); # MANUALLY EDIT ****************************************************

print(CorrectedAirlyData.max(skipna = True));
print(CorrectedAirlyData.min(skipna = True));
print(CorrectedAirlyData.mean(skipna = True));

plt.show();
#ALL CODE WRITTEN BY GEORGE MORALES
