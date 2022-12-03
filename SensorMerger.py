''' MERGES all DATA FOR ONE SENSOR from August 21 - March 31 '''
import pandas as pd
from datetime import datetime

SensorID = "7160"; # Given the sensor id to extract info for

RawDataFrame1 = pd.DataFrame(pd.read_excel("PrePre{}.xlsx".format(SensorID))); # August - Early Sep
RawDataFrame2 = pd.DataFrame(pd.read_excel("Pre{}.xlsx").format(SensorID)); # Early Sep-  Nov
RawDataFrame3 = pd.DataFrame(pd.read_excel("{}.xlsx")); # Dec - end of March


''' August '''
AirlyData1 = RawDataFrame1;

Aug = AirlyData1[['Date','pm10','pm25']].copy();

#************************************************************************ THIS SECTION NEEDS TO BE FINISHED


''' Sept - Nov '''
AirylData2 = RawDataFrame2;

SeptNov = AirlyData2[['Date','pm10','pm25']].copy();

#***********************************************************************


''' Dec - March '''
AirlyData3 = RawDataFrame3;

DecMar = AirlyData3[['Date','pm10', 'pm25']].copy();

#***********************************************************************



''' Final Exportation '''
#FinalFrame = pd.concat([Aug, SeptNov, DecMar]); # New Subframe
FinalFrame = pd.concat([SeptNov, DecMar]); # New Subframe
print(FinalFrame);

#FinalFrame.to_csv("{}.csv".format(SensorID), header = True );


