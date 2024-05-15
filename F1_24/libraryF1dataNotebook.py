# Author: Franccy del Piero Sambrano Ganoza
from urllib.request import urlopen
import json
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns

"""
Function: obtain_information
Description: This function it is used to obtain the information about the different OpenF1 API that the user wants to consult.
Parameters:
    key_info: API method to consult
    session_key:Session to consult.
    driver_number:Number of the driver.
    year:Year of the event
    country_acronym:Country code of the session.
"""
def obtain_information(key_info,session_key=None,driver_number=None,year=None,country_acronym=None):
    url = 'https://api.openf1.org/v1/'
    if key_info != 'sessions':
        url+=str(key_info)+'?'
        url+='session_key='+str(session_key)
        if key_info== 'car_data':
            url+= '&driver_number='+str(driver_number) 
    else:
        url+=str(key_info)+'?'
        url+='year='+str(year)+'&country_code='+str(country_acronym)
    response = urlopen(url)  
    data = json.loads(response.read().decode('utf-8'))
    return pd.DataFrame(data)

"""
Function: stint_configuration
Description: The function is used to create a dataset that contains the information about the stints and drivers divided per lap.
Parameters:
    drivers: Dataset that contains all the information related to drivers
    stintInformation: Dataset that contains the information related with the stints.
"""
def stint_configuration(drivers,stintInformation):
    stintsDataFrame = pd.DataFrame()
    for index,row in stintInformation.iterrows():
        number_driver = row.driver_number
        acronym_driver = drivers.query('driver_number == @number_driver').name_acronym.to_string(index=False)
        full_name = drivers.query('driver_number == @number_driver').full_name.to_string(index=False)
        team_name = drivers.query('driver_number == @number_driver').team_name.to_string(index=False)
        if row.lap_start != row.lap_end:
            contador = row.lap_start
            while contador <=row.lap_end :
                new_row = {'driver_number':row.driver_number,'compound':row.compound,'lap_number':contador,'name_acronym':acronym_driver,'full_name':full_name,'team_name':team_name}
                stintsDataFrame = pd.concat([stintsDataFrame, pd.DataFrame([new_row])], ignore_index=True)
                contador+=1
        else:
        
            new_row = {'driver_number':row.driver_number,'compound':row.compound,'lap_number':row.lap_start,'name_acronym':acronym_driver,'full_name':full_name,'team_name':team_name}
            stintsDataFrame =pd.concat([stintsDataFrame, pd.DataFrame([new_row])], ignore_index=True)
    return stintsDataFrame


"""
Function: define_colour
Description: Define the colour of the compound
Parameter:
compound: Compound to consult
"""
def define_colour(compound):
    if compound == "SOFT":
        colour = "red"
    elif compound == "MEDIUM":
        colour = "yellow"
    elif compound == "HARD":
        colour = "grey"
    elif compound == "INTERMEDIATE":
        colour = "green"
    else:
        colour = "blue"
    return colour

    """
    Function:show_plot
    Description: This function shows the plot of the laptimes with the compound used.
    Parameters:
    arrayDataframes: Dataset that contains all the information related with the stints and drivers.
    colour: Colour of the compound(defined by define_colour)
    """
def show_plot(arrayDataframes,colour):
    figure, axis = plt.subplots(len(arrayDataframes),figsize=(15,85))
    i=0
    for arr in arrayDataframes:
        arr.reset_index(drop=True, inplace=True)
        axis[(i)].plot( arr.lap_duration,marker ="o",color=colour,label = str(arr.full_name[0]) )
        axis[i].set_xlabel("Lap time")
        axis[i].set_ylabel("Lap Time Seconds")
        axis[i].legend()
        i = i+1
    """
    Function: obtain_data_tyres
    Description: Obtain the information of the tyres
    Parameters:
    dataset: Dataset to consult
    compound:Compound to consult
    duration: Maximum duration to consult those laptimes below this threshold.
    """
def obtain_data_tyres(dataset,compound,duration):
    setTyres = dataset.query('compound == @compound and lap_duration < '+str(duration))
    drivers_number = []
    set_dict = {}
    for index,row in setTyres.iterrows():
        if row.driver_number not in drivers_number:
            set_dict[row.driver_number] = []
            drivers_number.append(row.driver_number)

        set_dict[row.driver_number].append(row)

    arrayDataframes = []
    for valor in set_dict.values():
        arrayDataframes.append(pd.DataFrame(valor))
    colour = define_colour(compound)
    show_plot(arrayDataframes,colour)

# Source: https://www.geeksforgeeks.org/how-to-annotate-bars-in-barplot-with-matplotlib-in-python/
    """
    Function: obtainchart
    Description: Function to obtain the chart with annotations (only available for horizontal charts)
    Parameters:
    xvariable: Maximum X value
    yvariable: Maximum Y value
    dataset: Dataset to consult
    """
def obtainchart(xvariable,yvariable,dataset):
    plt.figure(figsize=(12, 9))
    plots = sns.barplot(x=xvariable, y=yvariable, data=dataset,color='red')
    for bar in plots.patches:
        plots.annotate(format(bar.get_height(), '.3f'), 
                       (bar.get_x() + bar.get_width() / 2, 
                        bar.get_height()), ha='center', va='center',
                       size=8, xytext=(0, 7),
                       textcoords='offset points')
    plt.show()

    """
    Function: obtain_fastest_lap
    Description: Function used to obtain the information about the fastest lap per driver
    Parameters:
        driver: Driver to consult
        dataset: Dataset to consult 
    """
def obtain_fastest_lap(driver,dataset,newdataset):
    fastest_lap = dataset.query("driver_number == @driver").lap_duration.min()
    team_name = dataset.query("driver_number == @driver").head(1).team_name.to_string(index=False)
    #team_colour = dataset.query("driver_number == @driver").head(1).team_colour.to_string(index=False)
    name_acronym = dataset.query('driver_number == @driver').head(1).name_acronym.to_string(index=False)
    new_row = {'driver_number':driver,'fastest_lap':fastest_lap,'name_acronym': name_acronym, 'team_name':team_name}
    newdataset =pd.concat([newdataset, pd.DataFrame([new_row])], ignore_index=True)
    return newdataset

    """
    Function: obtain_deltas
    Description: Function used to obtain the deltas of the fastest lap of each driver
    Parameters:
        dataset: Dataset with the fastest laps
    """
def obtain_deltas(dataset):
    array = []
    fastest_lap = dataset.fastest_lap.min()
    for row in dataset.iterrows():
        lap = row[1][1]
        delta = lap-fastest_lap
        array.append(delta)
    return array
    """
    Function: getinfolonglaps
    Description: Fucntion used to obtain the information related to longlaps with the relevant information
    Parameters:
    dataset: Dataset with the information
    driver_number: Driver whose long laps will be consulted
    team: Team of the driver
    lap_duration_min: Low threshold considered to obtain the longlaps
    lap_duration_max: High threshold considered to obtain the longlaps
    """
def getinfolonglaps(dataset,driver_number,team,lap_duration_min=90,lap_duration_max=95):
    dataset = dataset.query("is_pit_out_lap == False and driver_number == @driver_number and team_name == @team and lap_duration < @lap_duration_max and lap_duration > @lap_duration_min ")
    return dataset[['full_name','compound','date_start','lap_number','duration_sector_1','duration_sector_2','duration_sector_3','lap_duration']]
    """
    Function: obtain_difference_regard_reference
    Description: Function used to obtain the difference with the driver at risk
    Parameters:
    row: row to consult
    reference: driver at risk
    """
def obtain_difference_regard_reference(row,reference,newdataset):
    difference_sector_1 = row.duration_sector_1 - reference.duration_sector_1.iloc[0]
    difference_sector_2 = row.duration_sector_2 - reference.duration_sector_2.iloc[0]
    difference_sector_3 = row.duration_sector_3 - reference.duration_sector_3.iloc[0]
    lap_duration = row.lap_duration - reference.lap_duration.iloc[0]
    new_row = {'driver_number':row.driver_number,'lap_duration':lap_duration,'difference_sector_1':difference_sector_1 ,'difference_sector_2':difference_sector_2,'difference_sector_3':difference_sector_3,'name_acronym':row.name_acronym   }
    
    newdataset =pd.concat([newdataset, pd.DataFrame([new_row])], ignore_index=True)
    return newdataset


    """
    Function: obtainInfoAboutQualySession
    Description: Function done to obtain more information about the qualyfing session
    Parameters:
    dataset: Dataset to consult
    date: date to consult
    
    """
# 
def obtainInfoAboutQualySession(dataset,date):
    sessiondataset =dataset.query(date).sort_values(by='lap_duration')
    isFastestLap = []
    for index,row in sessiondataset.iterrows():
        driver = row.driver_number
        fastest_lap = sessiondataset.query("driver_number == @driver").lap_duration.min()
        if row.lap_duration == fastest_lap:
            isFastestLap.append(True)
        else:
            isFastestLap.append(False)
    sessiondataset['isFastestLap'] = isFastestLap
    return sessiondataset


def obtain_information_qualy(driver,dataset,newdataset):
    fastest_lap = dataset.query("driver_number == @driver").lap_duration.min()
    fastest_lap_absolute = dataset.lap_duration.min()
    delta = fastest_lap - fastest_lap_absolute
    st_speed = dataset.query("driver_number == @driver").st_speed.min()
    i1_speed = dataset.query("driver_number == @driver").i1_speed.min()
    i2_speed = dataset.query("driver_number == @driver").i2_speed.min()
    new_row = {'driver_number':driver,'fastest_lap':fastest_lap,'delta': delta,'st_speed':st_speed,'i1_speed':i1_speed,'i2_speed':i2_speed}
    newdataset =pd.concat([newdataset, pd.DataFrame([new_row])], ignore_index=True)
    return newdataset

if __name__ == "__main__":
    print("ok")
   #print(obtain_information('sessions',year=2024,country_acronym='CHN'))
   #print(obtain_information('car_data',session_key=9663,driver_number=11))
   #print(obtain_information('drivers',session_key=9963))
   