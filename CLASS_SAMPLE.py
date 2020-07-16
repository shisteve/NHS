from CLASS_BABY import *

ALL_NAMES = master['Study Number (Original)'].dropna()

NAMES_COMPLETE = []
for name in ALL_NAMES:
    if "INCOM" not in name.upper():
        NAMES_COMPLETE.append(name)


def days_to_week(x):
    return x  / 7.
def weeks_to_days(x):
    return x * 7


class SAMPLE:
    '''provide the list of baby ids to be read and 
    the class will instantiate an array of baby objects.'''
    def __init__(self,list_of_names):
        self.list_of_names = list_of_names
        self.babies = []
        self.all_babies_are_good = True
        self.failed_names = []
        # create list of baby objects 
        for name in self.list_of_names:
            try:
                b_temp = baby(name)
                if b_temp.data_found:
                    self.babies.append(b_temp)
            except:
                self.all_babies_are_good=False
                self.failed_names.append(name)
        if not self.all_babies_are_good:
            print('Not able to read the following babies: ')
            print(list(self.failed_names))
            
        #average values
        self.weight_grams = []
        self.gestational_age_days = []
        self.delivery = []
        self.SpO2_med = []
        self.PR_med = []
        self.PI_med = []

        for b in self.babies:
            #print(b.baby_id)
            self.weight_grams.append(b.weight_grams)
            self.gestational_age_days.append(b.gestational_age_days)
            self.delivery.append(b.delivery)
            self.SpO2_med.append(b.measurements_SpO2_median[0])
            self.PR_med.append(b.measurements_PR_median[0])
            self.PI_med.append(b.measurements_PI_median[0])
            

        # covert in numpy array
        self.weight_grams = np.array(self.weight_grams)
        self.gestational_age_days = np.array(self.gestational_age_days)
        self.delivery = np.array(self.delivery)
        self.SpO2_med = np.array(self.SpO2_med)
        self.PR_med   = np.array(self.PR_med)
        self.PI_med   = np.array(self.PI_med)
        
        
    def select_girls(self):    
        girls = []
        for b in self.babies:
            if (b.gender).upper() == 'FEMALE':
                girls.append(b)
        return np.array(girls)
    
    def select_girls_names(self):    
        girls_names = []
        for b in self.babies:
            if (b.gender).upper() == 'FEMALE':
                girls_names.append(b.original_name)
        return np.array(girls_names)
    
    
    def select_boys(self):    
        boys = []
        for b in self.babies:
            if (b.gender).upper() == 'MALE':
                boys.append(b)
        return np.array(boys)
    
    def select_boys_names(self):    
        boys_names = []
        for b in self.babies:
            if (b.gender).upper() == 'MALE':
                boys_names.append(b.original_name)
        return np.array(boys_names)
    
    def create_subsample(self,list_of_names):
        '''Return an object of the class SAMPLE made 
        by babies whose name are in the list'''
        SUB = SAMPLE(list_of_names)
        return SUB
    
    def create_subsample_girls(self):
        '''create a new object SAMPLE for the girls'''
        list_of_girls = self.select_girls_names()
        GIRLS = SAMPLE(list_of_girls)
        return GIRLS
    
    def create_subsample_boys(self):
        '''create a new object SAMPLE for the boys'''
        list_of_boys = self.select_boys_names()
        BOYS = SAMPLE(list_of_boys)
        return BOYS
     
