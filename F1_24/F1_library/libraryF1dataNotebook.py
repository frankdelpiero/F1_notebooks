# Author: Franccy del Piero Sambrano Ganoza
from urllib.request import urlopen
import json
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from statistics import mode

# Fast F1 libraries
import fastf1 as ff1
from fastf1 import utils

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
    Function: getinfolongruns
    Description: Fucntion used to obtain the information related to longlaps with the relevant information
    Parameters:
    dataset: Dataset with the information
    driver_number: Driver whose long laps will be consulted
    team: Team of the driver
    lap_duration_min: Low threshold considered to obtain the longlaps
    lap_duration_max: High threshold considered to obtain the longlaps
    """
def getinfolongruns(dataset,driver_number,team,lap_duration_min=90,lap_duration_max=95):
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

    """
    Function: obtain_information_qualy
    Description: Function to obtain information about each driver with a comparaison versus the poleman
    driver: Driver to consult
    newdataset = Dataset to save the data.
    """
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

    """
    Function: obtainLongRunData
    Description: Function that obtain all the related data with the long runs within the ranges obtained by parameters.
    drivers: drivers to consult
    dataset: dataset to consult
    min_range: minimum range
    max_range: maximum range 
    """
def obtainLongRunData(drivers,dataset,min_range,max_range):
    lap_duration_per_driver = []
    for index,driver in drivers.iterrows():
        longrun_data = getinfolongruns(dataset,driver.driver_number,driver.team_name,min_range,max_range)
        if len(longrun_data) > 0:
            longrun_name=mode(longrun_data.full_name)
            longrun_compound=mode(longrun_data.compound)
            lap_duration_per_driver.append([longrun_name,longrun_compound,longrun_data.lap_duration.mean(),longrun_data.duration_sector_1.mean(),longrun_data.duration_sector_2.mean(),longrun_data.duration_sector_3.mean()])
    return lap_duration_per_driver


    """
    Function: obtainMeanLongRuns
    Description: Function that obtain the data neccesary related to the summary of the long runs. It must be in the notebook because
    different combination can be consulted. For example, the driver who has the fastest sector 1 in long runs,etc
    drivers: Drivers dataset
    dataset:Dataset to consult
    minimum_threshold: Minimum threshold of the laps
    maximum_threshold: Maximum threshold of the laps
    """
def obtainMeanLongRuns(drivers,dataset,minimum_threshold,maximum_threshold):
    long_runs_summary = pd.DataFrame()
    for index,driver in drivers.iterrows():
        driver_data = getinfolongruns(dataset,driver.driver_number,driver.team_name,minimum_threshold,maximum_threshold)
        if len(driver_data) != 0:
            compound_data = driver_data.compound.mode()[0]
            mean = driver_data.query("compound == @compound_data").lap_duration.mean()
            sector1_mean = driver_data.query("compound == @compound_data").duration_sector_1.mean()
            sector2_mean = driver_data.query("compound == @compound_data").duration_sector_2.mean()
            sector3_mean = driver_data.query("compound == @compound_data").duration_sector_3.mean()
            new_row = {'driver':driver.broadcast_name,'compound':compound_data,'team_name':driver.team_name,'sector1':sector1_mean,'sector2':sector2_mean,'sector3':sector3_mean,'mean_lap_time':round(mean,3)}
            long_runs_summary = pd.concat([long_runs_summary,pd.DataFrame([new_row])],ignore_index=True)
    return long_runs_summary

    """
    Function: showDataLongRuns
    dataset:Dataset to consult
    compound: Compound to consull
    column_to_sort= Column chosen to sort the consult
    columns_to_show = Columns to show in the consult
    """
def showDataLongRuns(dataset,compound,column_to_sort,columns_to_show):
    return dataset.query("compound == @compound").sort_values(column_to_sort)[columns_to_show]


    """
    Function:qualyfing_prediction
    Description: With the datasets given, a qualyfing prediction will be obtained.
    datasets: Datasets to check
    drivers: Driver dataset associated to the sesssion
    quantile_sector_1 = Threshold sector 1
    quantile_sector_2 = Threshold sector 2
    quantile_sector_3 = Threshold sector 3
    """
def qualyfing_prediction(datasets,drivers,quantile_sector_1=0.1,quantile_sector_2=0.12,quantile_sector_3=0.1):
    teams_dict = {}
    #datasets = [jointablesfreepractice1,jointablesfreepractice2]
    # For each dataset of each session   
    for dataset in datasets:
        for team in pd.unique(drivers.team_name):
            if team not in teams_dict:
                teams_dict[team]  = []
            threshold_sector1 = dataset.query("team_name == @team").duration_sector_1.quantile(quantile_sector_1)
            threshold_sector2 = dataset.query("team_name == @team").duration_sector_2.quantile(0.12)
            threshold_sector3 = dataset.query("team_name == @team").duration_sector_3.quantile(0.1)
    
            sector1= dataset.query("team_name == @team and duration_sector_1 <=  @threshold_sector1").duration_sector_1.values.mean()
            sector2 = dataset.query("team_name == @team and duration_sector_2 <=  @threshold_sector2").duration_sector_2.values.mean()
            sector3 = dataset.query("team_name == @team and duration_sector_3 <=  @threshold_sector3").duration_sector_3.values.mean()

            teams_dict[team].append(sector1)
            teams_dict[team].append(sector2)
            teams_dict[team].append(sector3)

    qualy_simulation = pd.DataFrame()
    for team in teams_dict:
        new_row = {'team':team,'qualy_lap_time':sum(teams_dict[team])/2,
                'mean_sector_1':(teams_dict[team][0]+ teams_dict[team][3])/2,
                'mean_sector_2':(teams_dict[team][1]+ teams_dict[team][4])/2,
                'mean_sector_3':(teams_dict[team][2]+ teams_dict[team][5])/2,
                }
        qualy_simulation =pd.concat([qualy_simulation, pd.DataFrame([new_row])], ignore_index=True)
    return qualy_simulation
    """
    Function_ race_prediction
    Description: According to the free practice dataset and the threshold given, the race pace will be obtained
    free_practice : Free Practice to check
    drivers: Driver dataset
    minimum_threshold = Minimum threshold
    maximum_threshold = Maximum threshold
    """
def race_prediction(free_practice,drivers,minimum_threshold,maximum_threshold):
    race_simulation = pd.DataFrame()
    for index,data in drivers.iterrows():
        datalongrun = getinfolongruns(free_practice,data.driver_number,data.team_name,minimum_threshold,maximum_threshold) 
        mean_sector_1 = datalongrun.duration_sector_1.mean()
        mean_sector_2 = datalongrun.duration_sector_2.mean()
        mean_sector_3 = datalongrun.duration_sector_3.mean()
        mean_lap_duration = datalongrun.lap_duration.mean()
        new_row = {'team':data.team_name,
        'mean_lap_duration':mean_lap_duration,
        'mean_sector_1':mean_sector_1,
        'mean_sector_2':mean_sector_2,
        'mean_sector_3':mean_sector_3,
        }
        race_simulation =pd.concat([race_simulation, pd.DataFrame([new_row])], ignore_index=True)

    return race_simulation.sort_values(by='mean_lap_duration')

    """
    Function_ draw_gap
    Description: In this function I will obtain the gap in order to watch a comparaison among the driver at risk
    with the drivers that were eliminated in this session(Q1,Q2)
    To Q3, poleman will be the reference with the rest of drivers.
    Also, this function can be used to compare two or more drivers. To do this, it is neccesary to put the driver that you want
    to compare in driver position at risk alongside his position in position min.
    driver_at_risk: Diriver to compare
    drivers: Driver dataset
    position_min: Minimim position to compare
   position_max: Maximim position to compare
   dataset: Dataset that contains information about the laps of the session
   session: Fast F1 session
    """
def draw_gap(driver_at_risk,position_min,position_max,dataset,drivers,session):
    fastest_lap_session_qualyfing = []
    name_acronym_reference = []
    # It is necesary to take the reference of the driver that finished P10 in this session.
    driver_risk = session.laps.pick_driver(driver_at_risk.name_acronym.to_string(index=False)).query("LapTimeSeconds=="+driver_at_risk.lap_duration.to_string(index=False))
 

    #Take the reference of the eliminated drivers.
    for index,row in dataset[position_min:position_max].iterrows():
        bestlap_qualyfing_driver = session.laps.pick_driver(row.name_acronym).pick_fastest()
        name_acronym_reference.append(bestlap_qualyfing_driver.Driver)
        delta_time, ref_tel, compare_tel = utils.delta_time(driver_risk,bestlap_qualyfing_driver)
        fastest_lap_session_qualyfing.append(delta_time)
    fastest_lap_session_qualyfing.append(np.zeros(len(delta_time)))
    name_acronym_reference.append(driver_risk.Driver.to_string(index=False))
    fig, ax = plt.subplots()
    count = 0
    for row in (name_acronym_reference):
        ax.plot(ref_tel['Distance'], fastest_lap_session_qualyfing[count], '--',label=row,color = "#"+drivers.query("name_acronym=='"+row+"'").team_colour.to_string(index=False) )
        ax.legend(loc=0)
        count+=1
    plt.show()


if __name__ == "__main__":
    print("ok")
   #print(obtain_information('sessions',year=2024,country_acronym='CHN'))
   #print(obtain_information('car_data',session_key=9663,driver_number=11))
   #print(obtain_information('drivers',session_key=9963))
   
