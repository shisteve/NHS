import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as d

from datetime import date,datetime, timedelta

######################################################
### READING MASTER FILE WITH ALL BABIES ##############
######################################################
master_filename = "../TOST_data/TOST_State_Durham.xlsx"
master = pd.read_excel(master_filename,skip_blank_lines=True)

master_complementary_filename = "../TOST_data/TOST_Master_calgary.xlsx"
master_complementary = pd.read_excel(master_complementary_filename,skip_blank_lines=True)

######################################################
##### USEFUL FUNCTIONS FOR THE CLASS BABY ############
######################################################

def format_date(DATE='03-03-14', fmt='american'):
    # !!! American format
    if fmt == 'american':
        month = int(DATE[0:2])
        day = int(DATE[3:5])
    else:
        day = int(DATE[0:2])
        month = int(DATE[3:5])

    year = int('20' + DATE[6:8])
    return year, month, day


def format_time(TIME='14:55:57'):
    hours = int(TIME[0:2])
    minutes = int(TIME[3:5])
    seconds = int(TIME[6:8])
    return hours, minutes, seconds


def DELTA_TIMES_SEC(DATE1, TIME1, DATE2, TIME2, verbose=False, fmt='american'):
    '''compute time intervals for a pair of date and time'''
    year_1, month_1, day_1 = format_date(DATE1, fmt=fmt)
    hour_1, minutes_1, seconds_1 = format_time(TIME1)

    year_2, month_2, day_2 = format_date(DATE2, fmt=fmt)
    hour_2, minutes_2, seconds_2 = format_time(TIME2)

    # compute day difference
    from datetime import date
    start = date(year_1, month_1, day_1)
    end = date(year_2, month_2, day_2)
    delta_days = (end - start).days
    if verbose:
        print('delta_days = ', delta_days)

    time_1_sec = hour_1 * 60 * 60 + minutes_1 * 60 + seconds_1
    time_2_sec = hour_2 * 60 * 60 + minutes_2 * 60 + seconds_2
    delta_time_sec = (time_2_sec - time_1_sec)
    if verbose:
        print('delta_sec = ', delta_time_sec)

    delta_tot_sec = delta_days * 24 * 60 * 60 + (time_2_sec - time_1_sec)
    return delta_tot_sec


def convert_dates_times_into_deltasec(dates, times, fmt='american'):
    '''convert an array of dates and an array of times
    into an array of interval times in seconds'''
    delta_sec = np.zeros(len(dates))
    for i in range(0, len(times)):
        delta_sec[i] = DELTA_TIMES_SEC(dates[0], times[0], dates[i], times[i], fmt=fmt)
        # print(delta_sec)
    return delta_sec


# Function to search for a key in the name of the files in a folder
def find_files_in_folder(key, folder='/home/giorgio/Desktop/NHS/TOST_data/', verbose=False):
    '''give the key you want to find in file names contained in folder.
    If you want to list all the files set key="*"  '''
    import subprocess
    ls = subprocess.Popen(['ls', '', folder],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT)
    ls_out, ls_err = ls.communicate()
    ls_out = str(ls_out)
    ls_out = ls_out.split('\\n')
    found = False
    key_lines = []
    if key == '*':
        if ':' in ls_out[1]:
            key_lines = ls_out[2:-1]  # neglect parent folder
        else:
            key_lines = ls_out[1:-1]  # neglect the first apostrophy

    else:
        for line in ls_out:
            if key in line and ':' not in line:  # the ':' appears in the parent folder
                key_lines.append(line)
                found = True
        if (found and verbose):
            for kl in key_lines:
                print(kl)
        elif verbose:
            print('No file names with the key: ', key)
    return key_lines


# Find baby folder
def get_folder_for_baby(baby_id, verbose=False, whole_path=True):
    '''returns the path of the folder where the data of baby_id are stored'''
    baby_id = baby_id.upper()
    home_NHS = '/home/giorgio/Desktop/NHS/TOST_data/'
    if 'FMC' in baby_id:
        folder = home_NHS + 'TOST FMC Data Groomed/'
    elif 'PLC' in baby_id:
        folder = home_NHS + 'TOST PLC Data Groomed/'
    elif 'RGH' in baby_id:
        folder = home_NHS + 'TOST RGH Data Groomed/'
    # sometimes the id is e.g. RGH033 and sometimes RGH33
    try:
        _ = int(baby_id[-3:])
        # don't do str(int()) otherwise you lose the zeros
        keyword = str(baby_id[-3:])
    except:
        # This should handle when you give the id forgetting the initial zero
        if str(baby_id[-3]) not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            keyword = '0' + str(baby_id[-2:])
    keyword = str(keyword)
    if verbose:
        print('keyword = ', keyword)

    # even if verbose is true you don't want to print the last folder or the files here
    ls = find_files_in_folder(key=keyword, folder=folder, verbose=False)

    if verbose:
        if len(ls) > 1:
            print('WARNING: there are more occurrence for that baby id')
            print(ls)
            print('the first occurrence will be used: ', ls[0])
        elif len(ls) == 0:
            print('It seems there are no data for ', baby_id)

    if len(ls) == 0:
        ls = None

    if whole_path and ls != None:
        # print('folder= ',folder)
        # print('len(ls)= ',len(ls))
        # print('ls=',ls)
        folder = folder + ls[0] + '/'
    elif ls != None:
        folder = ls[0]

    if ls == None:
        return None
    else:
        return folder


def list_files_for_baby(baby_id, whole_path=True, verbose=False):
    '''Returns the name of the files with baby_id datas'''
    f = get_folder_for_baby(baby_id, verbose=verbose)
    ls = find_files_in_folder(key='*', folder=f)
    if whole_path:
        for i in range(len(ls)):
            ls[i] = f + ls[i]
    return ls


def interpret_date(date_measure, birth, verbose=False, warning=True):
    '''Give the date of the measurement in whatever format
    and comparing it with the date of birth (also given as input object datetime.date), this function
    will return the date in the right format, as an
    object datetime.date (no time information)'''

    # this is not to consider the information on the time
    # so that different days are counted just by the date
    birth = datetime(year=birth.year, month=birth.month, day=birth.day)
    # if I use date instead of datetime, I can't compute deltatime.timedelta()

    sp_dash = str(date_measure).split('-')
    sp_slash = str(date_measure).split('/')

    if verbose:
        print('############################################################')
        print('date birth:       ', birth.date(), ' (yyyy-mm-dd)')
        print('------------------------------------------------------------')

        print('type      :       ', type(birth.date()))
        print('date measurement: ', date_measure)
        print('numbers of info (year-month-day): ', len(sp_dash))
        print('numbers of info (year/month/day): ', len(sp_slash))

    if len(sp_dash) == 3:
        # interpret "-" as a delimiter
        sp = sp_dash
    elif len(sp_slash) == 3:
        # interpret "/" as a delimiter
        sp = sp_slash
    elif len(sp_dash)!=3 and len(sp_slash)!=3:
        if verbose:
            print('Warning, delimiter for date is not dash or slash. Likely the date is just an empty field.')
        return None
    else:
        # I am not able to split the string in 3 values
        raise ValueError('I am not able to recognise the date format.')

    if verbose:
        print("splitted string: ", sp[0], sp[1], sp[2])
        print("length of splitted units: ", len(sp[0]), len(sp[1]), len(sp[2]))
        print("fixed if necessary", sp[0][0:2], sp[1][0:2], sp[2])

    if len(sp[0]) == 6:
        if verbose:
            print('Fixed ', sp[0], ' in -->', sp[0][0:2])
        sp[0] = sp[0][0:2]
    if len(sp[1]) == 6:
        if verbose:
            print('Fixed ', sp[1], ' in -->', sp[1][0:2])
        sp[1] = sp[1][0:2]

    # try different format
    try:
        # mm dd yy
        MD1 = datetime(year=2000 + int(sp[2]), month=int(sp[0]), day=int(sp[1]))
    except:
        MD1 = -99
    try:
        # dd mm yy
        MD2 = datetime(year=2000 + int(sp[2]), month=int(sp[1]), day=int(sp[0]))
    except:
        MD2 = -99
    try:
        # yy dd mm
        MD3 = datetime(year=2000 + int(sp[0]), month=int(sp[2]), day=int(sp[1]))
    except:
        MD3 = -99

    try:
        # yy dd mm
        MD4 = datetime(year=2000 + int(sp[0]), month=int(sp[1]), day=int(sp[2]))
    except:
        MD4 = -99

    MD1_flag = False
    MD2_flag = False
    MD3_flag = False
    MD4_flag = False

    if (MD1 != -99) and ((MD1 - birth).days >= 0) and ((MD1 - birth).days <= 8):
        MD1_flag = True
        MD = MD1

    if (MD2 != -99) and ((MD2 - birth).days >= 0) and ((MD2 - birth).days <= 8):
        MD2_flag = True
        MD = MD2

    if (MD3 != -99) and ((MD3 - birth).days >= 0) and ((MD3 - birth).days <= 8):
        MD3_flag = True
        MD = MD3

    if (MD4 != -99) and ((MD4 - birth).days >= 0) and ((MD4 - birth).days <= 8):
        MD4_flag = True
        MD = MD4

    if verbose:
        print('mm dd yy: ', MD1_flag)
        print('dd mm yy: ', MD2_flag)
        print('yy dd mm: ', MD3_flag)
        print('yy mm dd: ', MD4_flag)

    only_one = False
    if (MD1_flag and not MD2_flag and not MD3_flag and not MD4_flag) or \
            (not MD1_flag and MD2_flag and not MD3_flag and not MD4_flag) or \
            (not MD1_flag and not MD2_flag and MD3_flag and not MD4_flag) or \
            (not MD1_flag and not MD2_flag and not MD3_flag and MD4_flag):
        only_one = True

    if not MD1_flag and not MD2_flag and not MD3_flag and not MD4_flag:
        # You want to print this also if you do not verbose

        if warning:
            print('#####')
            print(date_measure, ' is not within 8 days from the birth ', birth.date(), ' (whichever format you use)')
            print('Or the measurement date is before the birth.')
            print('#####')

        return None

    if verbose:
        print('ONLY ONE format is correct?', only_one)
        print('Days after the birth: ', (MD - birth).days)
        print('------------------------------------------------------------')
        print(MD.date(), ' (yyyy-mm-dd) is the right date of the measurement')
        print('############################################################')

    if not only_one:
        if MD1_flag and MD2_flag:
            if (MD1.month == birth.month and MD2.month != birth.month):
                MD = MD1
            elif (MD1.month != birth.month and MD2.month == birth.month):
                MD = MD2
            elif MD1 == MD2:
                MD = MD1
            else:
                print('The format is either mm-dd-yy or dd-mm-yy but I am not able to guess the right one')
        elif MD3_flag and MD4_flag:
            if (MD3.month == birth.month and MD4.month != birth.month):
                MD = MD3
            elif (MD3.month != birth.month and MD4.month == birth.month):
                MD = MD4
            elif MD3 == MD4:
                MD = MD3
            else:
                print('The format is either yy-mm-dd or yy-dd-mm but I am not able to guess the right one')
        else:
            raise ValueError('There are more than one format of the date that are acceptable')

    # transform in object date as I don't want time information

    MD = date(year=MD.year, month=MD.month, day=MD.day)

    return MD


def is_SameBaby(name1='FMC001', name2='FMC101', verbose=False):
    '''check if the two id for the baby are equivalent
    even if they are in different formats,
    e.g. with initial zero or lower/upper characters.'''

    hospital = bool(str(name1[0:3]).lower() in str(name2)) or (str(name1[0:3]).upper() in str(name2))
    last_three = bool(str(name1)[-3:] == str(name2)[-3:])
    last_two = bool(str(name1)[-2:] == str(name2)[-2:])
    third_last_is_zero_in_name2 = bool(str(name2)[-3] == '0')
    third_last_is_zero_in_name1 = bool(str(name1)[-3] == '0')
    third_last_is_character_in_name1 = bool(str(name1)[-3] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])
    third_last_is_character_in_name2 = bool(str(name2)[-3] not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'])

    numbers_right = bool(last_three or \
                         ((last_two and third_last_is_zero_in_name2 and third_last_is_character_in_name1) or \
                          (last_two and third_last_is_character_in_name2 and third_last_is_zero_in_name1)))

    total = bool(hospital and numbers_right)

    if verbose:
        print('#################################################################')
        print("Is the name of the hospital found in the original name? ", hospital)
        print("Are the last three character the same? \t\t\t", last_three)
        print("Are the last two character the same? \t\t\t", last_two)
        print("Are the id numbers equivalent? \t\t\t\t", numbers_right)
        print('---------------------------------------------------------------')
        print("Are the file names ", name1, ' and ', name2, " equivalent? \t", total)
        print('#################################################################')

    return total

def find_baby_name_and_index_in_master(baby_id,master=master):
    '''it scans all of the name of the babies in the master file and return the correct name and its index'''
    baby_names = np.array(master['Study Number (Original)'])
    found=False
    for i in range(len(baby_names)):
        if is_SameBaby(baby_id,baby_names[i]):
            name_original = baby_names[i]
            index_original = i
            if found: #(already)
                print('WARNING: more than one baby for the same id!!!')
                print('baby_id = ',baby_id, 'with original name = ',baby_names[i],' at index = ',i)
            else:
                found=True
    return name_original, index_original



def get_brady_episodes_durations(t, PR, threshold=100., duration_minimum=15., time_step=2.):
    '''Output: Return a list containing the duration of the episodes of bradycardia.
    The length of the list is the number of episodes.
    Input: time (t) and pulse rates measurements (PR).
    The algorithm can be used in thhe same way for SpO2.
    Parameters: duration_minimum = minimum amount of time in seconds where
    PR below the threshold are considered as an episode of bradycardia.
    If set to 0, it consider episodes of any duration.
    time_step = difference in seconds between contiguous elements of the vector time (t).'''

    episode_durations = []
    contiguous_time_bin = True
    counter_sec = 0

    for i in range(1, len(t)):
        # if in the current and the previous time bin, PR were below threshold
        if PR[i] < threshold and PR[i - 1] < threshold and contiguous_time_bin:
            counter_sec = counter_sec + time_step  # sec
            # if I am at the end I need to check the counter
            # in order not to miss any last episode.
            if i == len(t) - 1 and counter_sec > duration_minimum:
                episode_durations.append(counter_sec)
        else:
            # transition from below to above threshold
            if counter_sec > duration_minimum:
                # save the episode
                episode_durations.append(counter_sec)
            # reset the counter for new episode
            counter_sec = 0

        # check that time bins are continuous
        # without any gap in time
        if t[i - 1] == t[i] - time_step:
            contiguous_time_bin = True
        else:
            contiguous_time_bin = False
    return np.array(episode_durations)

#########################################################
### CLASS BABY ##########################################
#########################################################
class baby:
    def __init__(self, baby_id, babies=master, additional_info=master_complementary, verbose=False, warning=True):
        '''Input the study number to initialise a baby, e.g. baby_id="FMC003" '''
        self.verbose = verbose
        self.warning = warning
        self.baby_id = baby_id.upper()
        self.data_found = True
        try:
            # if the name inputted even if complicated, is found in the master file
            # than just take that baby
            index = list(babies['Study Number (Original)']).index(baby_id)
            original_name = baby_id
        except:
            # if not automatically found in the master file, let's use my more
            # complecated function to understand which baby you are looking for
            original_name, index = find_baby_name_and_index_in_master(baby_id.upper())
        if self.verbose:
            print('#####################################################')
            print('The original name of the baby case is: ', original_name)
        self.original_name = original_name
        self.incomplete = False
        if "INCOM" in self.original_name.upper():
            self.incomplete = True
        self.gender = babies['Gender'][index]
        self.weight_grams = babies['Birth Weight in Grams'][index]
        self.gestational_age_days = babies['Gestational Age in weeks'][index] * 7 + babies['Gestational Age (additional days)'][index]
        self.delivery = babies['Type of delivery'][index]
        self.date_time = str(babies['Date & Time of Birth'][index]).split()

        self.date_birth = str(babies['Date & Time of Birth'][index]).split(' ')[0]
        self.time_birth = str(babies['Date & Time of Birth'][index]).split(' ')[1]
        self.year_birth = int(self.date_birth.split('-')[0])
        self.month_birth = int(self.date_birth.split('-')[1])
        self.day_birth = int(self.date_birth.split('-')[2])
        self.hours_birth = int(str(self.time_birth).split(':')[0])
        self.minutes_birth = int(str(self.time_birth).split(':')[1])
        self.seconds_birth = int(str(self.time_birth).split(':')[2])

        self.birth = datetime(year=self.year_birth,
                              month=self.month_birth,
                              day=self.day_birth,
                              hour=self.hours_birth,
                              minute=self.minutes_birth,
                              second=self.seconds_birth)

        self.ethnicity = babies['Ethinicity'][index]
        self.age_mum = additional_info['Maternal Age in Years'][index]
        self.gestational_diabetes = additional_info['Gesataional Diabetes'][index]
        self.smoking = additional_info['Smoking'][index]
        self.meconium = babies['Meconium Stained Liqor'][index]
        self.apgar5 = babies['Total Apgar score @ 5min'][index]
        
        self.preeclampsia = additional_info['Pregnancy induced Hypertension'][index]

        
        self.pr_threshold = 120.
        self.spo2_threshold = 98.

        try:
            self.files = list_files_for_baby(self.baby_id, verbose=verbose)
            if verbose:
                print('I am loading the files for baby = ', self.baby_id)
        except:
            print('NO MEASUREMENTS FOR BABY', self.baby_id)
            self.data_found = False
            # raise ValueError('FILE NOT FOUND FOR BABY: ',self.baby_id)

        # array of tables with the measurements in different day or modality (wrist/foot)
        self.measurements = []

        if self.data_found:
            for i in range(len(self.files)):
                if self.verbose:
                    print('Loading file: ', self.files[i])

                data = pd.read_csv(self.files[i])
                # if you use the following you need to be sure that you have (all of those column name)
                # and sometimes there is no PI so it's not ideal
                # data = pd.read_csv(self.files[i],skipinitialspace=True,usecols=['Date','Time','SpO2','PR','PI'])

                self.measurements.append(data)

                # if self.verbose:
                #    print(pd.read_csv(self.files[i]))

            if self.verbose:
                print('--------------------')
            self.measurements_date = []
            self.measurements_time = []
            self.measurements_datetime = []
            self.measurements_delta_sec_since_birth = []
            self.measurements_delta_sec_since_birth_list = []

            self.measurements_SpO2_median = []
            self.measurements_PR_median = []
            self.measurements_PI_median = []

            self.measurements_SpO2_mean = []
            self.measurements_PR_mean = []
            self.measurements_SpO2_std = []
            self.measurements_PR_std = []
            self.measurements_PI_mean = []
            self.measurements_PI_std = []

            
            
            self.measurements_bradycardia_sec_pr = []
            self.measurements_bradycardia_ratio_pr = []

            self.measurements_bradycardia_sec_spo2 = []
            self.measurements_bradycardia_ratio_spo2 = []

            self.measurements_bradycardia_sec_pr_dynamic = []
            self.measurements_bradycardia_ratio_pr_dynamic = []

            self.measurements_bradycardia_episodes_durations = []
            self.measurements_bradycardia_episodes_number = []
            self.measurements_bradycardia_episodes_number_per_sec = []

            self.measurements_bradycardia_spo2_episodes_durations = []
            self.measurements_bradycardia_spo2_episodes_number = []
            self.measurements_bradycardia_spo2_episodes_number_per_sec = []

            self.good_datetime = []

            self.measurements_wrist = np.full(len(self.files),False)
            self.measurements_foot = np.full(len(self.files),False)
            self.measurements_PHN = np.full(len(self.files),False)

            for i in range(len(self.files)):

                if self.verbose:
                    print('Reading from file: ', self.files[i])
                    # print(self.measurements[i].columns.values)

                self.measurements_date.append(self.measurements[i]['Date'][0])
                self.measurements_time.append(self.measurements[i]['Time'][0])

                # add temporary PR and SpO2 without bad values
                spo2 = np.array(self.measurements[i]['SpO2'].dropna())
                pr   = np.array(self.measurements[i]['PR'].dropna())
                
                spo2_clean = np.array(spo2[np.where(spo2>10.)])
                pr_clean = np.array(pr[np.where(pr>10.)])

                self.measurements_delta_sec_since_birth_list.append(self.convert_delta_sec(i))

                dt = np.array(self.measurements_delta_sec_since_birth_list[i])

                #print(self.files[i])
                #print('len(dt) before =',len(dt))

                # equivalent of the pandas .dropna()
                dt = dt[~np.isnan(dt)]

                #print('len(dt) after =',len(dt))

                #print('len(pr) = ',len(pr))
                #print('len(spo2) = ',len(spo2))


                dt_clean_for_pr = dt[np.where(pr>10.)]
                dt_clean_for_spo2 = dt[np.where(spo2>10.)]


                self.measurements_SpO2_median.append(np.median(spo2_clean))
                self.measurements_PR_median.append(np.median(pr_clean))
                self.measurements_SpO2_mean.append(spo2_clean.mean())
                self.measurements_PR_mean.append(pr_clean.mean())
                self.measurements_SpO2_std.append(spo2_clean.std())
                self.measurements_PR_std.append(pr_clean.std())

                #dynamic_threshold_pr = (9./10.)*pr.median()
                #dynamic_threshold_pr = (2./3.)*pr.median()
                dynamic_threshold_pr = (2./3.)* np.median(pr)


                brady_sec_pr_dyn = 2. * len(np.where( pr_clean < dynamic_threshold_pr )[0])
                
                brady_sec_pr = 2. * len(np.where( pr_clean < self.pr_threshold )[0])
                brady_sec_pr_m10 = 2. * len(np.where( pr_clean < (self.pr_threshold-10) )[0])
                brady_sec_pr_m20 = 2. * len(np.where( pr_clean < (self.pr_threshold-20) )[0])
                brady_sec_pr_m30 = 2. * len(np.where( pr_clean < (self.pr_threshold-30) )[0])
                brady_sec_pr_m40 = 2. * len(np.where( pr_clean < (self.pr_threshold-40) )[0])


                
                brady_sec_spo2 = 2. * len(np.where(spo2_clean < self.spo2_threshold)[0])
                brady_sec_spo2_m1 = 2. * len(np.where(spo2_clean < self.spo2_threshold-1)[0])
                brady_sec_spo2_m2 = 2. * len(np.where(spo2_clean < self.spo2_threshold-2)[0])
                brady_sec_spo2_m3 = 2. * len(np.where(spo2_clean < self.spo2_threshold-3)[0])
                brady_sec_spo2_m4 = 2. * len(np.where(spo2_clean < self.spo2_threshold-4)[0])

                
                
                
                # Data points are recorded every 2 seconds
                tot_sec_recording_pr = 2. * len(pr_clean)
                tot_sec_recording_spo2 = 2. * len(spo2_clean)

                self.measurements_bradycardia_sec_pr.append([brady_sec_pr,
                                                             brady_sec_pr_m10,
                                                             brady_sec_pr_m20,
                                                             brady_sec_pr_m30,
                                                             brady_sec_pr_m40 ])
                self.measurements_bradycardia_ratio_pr.append([brady_sec_pr/tot_sec_recording_pr,
                                                               brady_sec_pr_m10/tot_sec_recording_pr,
                                                               brady_sec_pr_m20/tot_sec_recording_pr,
                                                               brady_sec_pr_m30/tot_sec_recording_pr,
                                                               brady_sec_pr_m40/tot_sec_recording_pr])

                
                
                self.measurements_bradycardia_sec_pr_dynamic.append(brady_sec_pr_dyn)
                self.measurements_bradycardia_ratio_pr_dynamic.append(brady_sec_pr_dyn/tot_sec_recording_pr)

                

                self.measurements_bradycardia_sec_spo2.append([brady_sec_spo2,
                                                               brady_sec_spo2_m1,
                                                               brady_sec_spo2_m2,
                                                               brady_sec_spo2_m3,
                                                               brady_sec_spo2_m4])
                self.measurements_bradycardia_ratio_spo2.append([brady_sec_spo2/tot_sec_recording_spo2,
                                                                 brady_sec_spo2_m1/tot_sec_recording_spo2,
                                                                 brady_sec_spo2_m2/tot_sec_recording_spo2,
                                                                 brady_sec_spo2_m3/tot_sec_recording_spo2,
                                                                 brady_sec_spo2_m4/tot_sec_recording_spo2])

                brady_episodes = get_brady_episodes_durations(t=dt_clean_for_pr, PR=pr_clean, threshold=self.pr_threshold, duration_minimum=15)
                self.measurements_bradycardia_episodes_durations.append(brady_episodes)
                self.measurements_bradycardia_episodes_number.append(len(brady_episodes))
                self.measurements_bradycardia_episodes_number_per_sec.append(len(brady_episodes)/tot_sec_recording_pr)

                brady_spo2_episodes = get_brady_episodes_durations(t=dt_clean_for_spo2, PR=spo2_clean, threshold=self.spo2_threshold, duration_minimum=15)
                self.measurements_bradycardia_spo2_episodes_durations.append(brady_spo2_episodes)
                self.measurements_bradycardia_spo2_episodes_number.append(len(brady_spo2_episodes))
                self.measurements_bradycardia_spo2_episodes_number_per_sec.append(len(brady_spo2_episodes)/tot_sec_recording_spo2)



                temp_date = interpret_date(date_measure=self.measurements[i]['Date'][3], birth=self.birth,
                                           warning=self.warning)
                temp_time = self.measurements[i]['Time'][0]

                if "WRIST" in self.files[i].upper():
                    self.measurements_wrist[i] = True
                    self.measurements_foot[i] = False
                elif "FOOT" in self.files[i].upper():
                    self.measurements_wrist[i] = False
                    self.measurements_foot[i] = True

                if "PHN" in self.files[i].split('/')[-1].upper():
                    self.measurements_PHN[i] = True

                self.has_been_PHN = False
                if True in self.measurements_PHN:
                    self.has_been_PHN = True

                if temp_date != None and str(temp_time) != 'nan':
                    self.good_datetime.append(True)
                    temp_datetime = datetime(year=temp_date.year,
                                             month=temp_date.month,
                                             day=temp_date.day,
                                             hour=int(str(temp_time).split(':')[0]),
                                             minute=int(str(temp_time).split(':')[1]),
                                             second=int(str(temp_time).split(':')[2]))
                    self.measurements_datetime.append(temp_datetime)
                    duration_sec = (temp_datetime - self.birth).seconds + (
                        (temp_datetime - self.birth).days) * 24 * 60 * 60
                    self.measurements_delta_sec_since_birth.append(duration_sec)
                    if verbose:
                        print('Birth: ', self.birth, " measurement: ", temp_datetime)
                        print('Interval time [sec]: ', duration_sec)
                else:
                    if verbose:
                        print('#####')
                        print('No time measurement or no correct date format')
                        print('#####')
                    self.measurements_datetime.append(None)
                    self.measurements_delta_sec_since_birth.append(None)
                    self.good_datetime.append(False)
                

                
                try:
                    pi = self.measurements[i]['PI'].dropna()
                    pi_clean = pi[pi>0.000001]
                    if len(pi_clean)>0.:    
                        PI_median = np.median(pi_clean)
                    else:
                        PI_median = np.median(np.nan)
                    if PI_median != 8000:
                        self.measurements_PI_median.append(PI_median)
                except:
                    self.measurements_PI_median.append(np.nan)
                    
                try:
                    pi = self.measurements[i]['PI'].dropna()
                    pi_clean = pi[pi>0.000001]
                    if len(pi_clean)>0:
                        PI_mean = pi_clean.mean()
                        PI_std = pi_clean.std()
                    else:
                        PI_mean = np.nan
                        PI_std = np.nan
                    
                    

                    if (PI_mean != 8000) and (PI_std != 8000):
                        self.measurements_PI_mean.append(PI_mean)
                        self.measurements_PI_std.append(PI_std)
                except:
                    self.measurements_PI_mean.append(np.nan)
                    self.measurements_PI_std.append(np.nan)

        if verbose:
            print('########################################################')

    def convert_delta_sec(self,num_file):
        date_dirty = self.measurements[num_file]['Date'].dropna()
        time = self.measurements[num_file]['Time'].dropna()

        date_clean = []
        date_time = []
        delta_sec = []

        for n in range(len(date_dirty)):
            dc = interpret_date(date_dirty[n], birth=self.birth, verbose=self.verbose)

            if dc != None:
                date_clean.append(dc)

                dc_object = datetime(year=dc.year,
                                      month=dc.month,
                                      day=dc.day,
                                      hour=int(str(time[n]).split(':')[0]),
                                      minute=int(str(time[n]).split(':')[1]),
                                      second=int(str(time[n]).split(':')[2]))

                date_time.append(dc_object)

                delta_sec.append((dc_object - self.birth).seconds + ((dc_object - self.birth).days) * 24 * 60 * 60)
            #else:
            #    date_clean.append(-99)
            #    date_time.append(-99)
            #    delta_sec.append(-99)

        delta_sec = np.array(delta_sec)

        return delta_sec

    def plot_baby_measurements(self, filenumber=0, with_bad_values=False,only_PR=False):

        #b = baby(name)

        print(self.files[filenumber].split('/')[-1])

        pr = self.measurements[filenumber]['PR'].dropna()
        spo2 = self.measurements[filenumber]['SpO2'].dropna()
        time = self.measurements[filenumber]['Time'].dropna()
        date_dirty = self.measurements[filenumber]['Date'].dropna()

        try:
            pi = self.measurements[filenumber]['PI'].dropna()
        except:
            pass

        #date_clean = []  # np.zeros(len(date_dirty))
        #date_time = []  # np.zeros(len(date_dirty))
        #delta_sec = []  # np.zeros(len(date_dirty))
        # correct date in the right format
        #for i in range(len(date_dirty)):
        #    dc = interpret_date(date_dirty[i], birth=self.birth,verbose=False)
        #    if dc != None:
        #        date_clean.append(dc)

        #        date_time.append(datetime(year=date_clean[i].year,
        #                              month=date_clean[i].month,
        #                              day=date_clean[i].day,
        #                              hour=int(str(time[i]).split(':')[0]),
        #                              minute=int(str(time[i]).split(':')[1]),
        #                              second=int(str(time[i]).split(':')[2])))#
        #
        #        delta_sec.append((date_time[i] - self.birth).seconds + ((date_time[i] - self.birth).days) * 24 * 60 * 60)
            #else:
            #    date_clean.append(-99)
            #    date_time.append(-99)
            #    delta_sec.append(-99)

        # date = np.array(date)
        # date_time = np.array(date_time)

        #delta_sec = np.array(delta_sec)
        delta_sec = self.convert_delta_sec(num_file=filenumber)
        delta_hour = np.array(delta_sec / 60. / 60.)

        plt.figure(figsize=(7, 5))
        if with_bad_values:
            plt.plot(delta_hour, pr, ".r")
        plt.title(self.original_name)
        plt.xlabel('hours since birth')
        plt.ylabel('mean PR')
        plt.plot(delta_hour[pr > 10.], pr[pr > 10.], ".b")
        plt.axhline(self.measurements_PR_mean[filenumber], color='k',
                    label='mean %.2f' % self.measurements_PR_mean[filenumber])
        plt.axhline(self.measurements_PR_median[filenumber], color='k', ls='dashed',
                    label='median %.2f' % self.measurements_PR_median[filenumber])
        plt.legend(fontsize='small')
        # plt.xlim(19.9,20.05)
        plt.show()
        if not only_PR:
            plt.figure(figsize=(7, 5))
            if with_bad_values:
                plt.plot(delta_hour, spo2, ".r")
            plt.title(self.original_name)
            plt.xlabel('hours since birth')
            plt.ylabel('mean SpO2')
            plt.plot(delta_hour[spo2 > 10.], spo2[spo2 > 10.], ".b")
            plt.axhline(self.measurements_SpO2_mean[filenumber], color="k",
                        label='mean %.2f' % self.measurements_SpO2_mean[filenumber])
            plt.axhline(self.measurements_SpO2_median[filenumber], color="k", ls='dashed',
                        label='median %.2f' % self.measurements_SpO2_median[filenumber])
            plt.legend(fontsize='small')
            plt.show()

            try:
                plt.figure(figsize=(7, 5))
                if with_bad_values:
                    plt.plot(delta_hour, pi, ".r")
                plt.title(self.original_name)
                plt.xlabel('hours since birth')
                plt.ylabel('mean pi')
                plt.plot(delta_hour[pi > 0.000001], pi[pi > 0.000001], ".b")
                plt.axhline(self.measurements_PI_mean[filenumber], color="k",
                            label='mean %.2f' % self.measurements_PI_mean[filenumber])
                plt.axhline(self.measurements_PI_median[filenumber], color="k", ls='dashed',
                            label='median %.2f' % self.measurements_PI_median[filenumber])
                plt.legend(fontsize='small')
                plt.show()
            except:
                pass


