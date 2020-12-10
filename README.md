# NHS
Prakash project

001 First simple plots to have a taste of the data.

002 developing of the class baby that I have then moved into CLASS_BABY.py

003 fixing some babies properties and create the class SAMPLE. I use this class in 006 to create the txt table, however I haven't used it a lot. There are probably smarter ways to create a class for the entire sample. As the class baby, I have moved this class into a python file (CLASS_SAMPLE.py). This notebook also includes some plots fpr the entire sample.

004 implementation of the Student T-test manually 

005 example of graphical interface to read and plotting some baby's properties just inputting the name (baby_id).

006 Notebook to create a txt file that includes all of the average properties of the babies to make the analysis easy and fast without passing through the class baby (which is slow when analysing the entire sample of babies).

007 is the file that use the txt file created by 006 and do all the games with avarage properties of babies. It doesn't go through the class baby but just use the average properties saved in the txt file.

009 Counting object easily from the txt table with the average properties. Very useful to fill table 2 and 3 of Prakash's final analysis. And the last table on perfusion index as well. In this notebook I also create my definition of median and percentile.

011 Plot for the final analysis Prakash's document. I first analyse the difference between mean and median. I double check the 11 babies with mean minus median greater then 10 (more on this in notebook 013) and I finally do some final plots for the paper. Including box plots. It includes some plots of wrist versus foot for single babies.

015 Analysis on bradycardia. Counting of episodes and computing duration of those. It includes some plots using different thresholds to define bradycardia. And some MannWhitney tests for finding statistical difference. It also include the plot for the paper of median PR vs time colouring points outside 100 < PR < 160.

016 First attempt of Neural Network using average properties to predict the bradycardia. It comes from a copy of the NN that I used to predict the redshift in the small galform lightcone from the magnitudes.
 
016a same NN as 016 but I have removed all the unnneccessary things so that is easy to use and intuitive.

016b NN that instead of using only the median of the PR and of the other properties, it uses all the available datapoints recorded every 2 seconds so that we have a sample of about one million datapoints.

017 Example of time series analysis on completely different data (sales of furniture).

018 Counts the number of all the 2-seconds datapoints from all of the babies and looks for relations between the different vital signs.
