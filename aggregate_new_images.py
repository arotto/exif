from pandas import DataFrame, read_pickle, read_csv, read_excel
from pandas import concat
from random import shuffle
from copy import copy
from numpy import *
import os

#use this if you're starting your database from scratch...
#df = DataFrame() 

df = read_pickle('gps_res_all.dat')

for new_res_file in os.listdir('output'):
    new_df = read_csv('output/'+new_res_file, header=None, 
                      names=['index','desc', 'img_url', 'lat', 'lon', 'url'] )
    new_df['index'] = range(len(df), len(df) +len(new_df))
    df = concat([df, new_df])

    print new_res_file, len(new_df)    

    os.system('rm output/'+new_res_file)

df['index'] = range(df.shape[0])
df.to_pickle('gps_res_all.dat')


