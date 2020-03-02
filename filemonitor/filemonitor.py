##
## Copyright 2020 mgenest
##
## Permission is hereby granted, free of charge, to any
## person obtaining a copy of this software and associated
## documentation files (the "Software"), to deal in the
## Software without restriction, including without
## limitation the rights to use, copy, modify, merge,
## publish, distribute, sublicense, and/or sell copies of
## the Software, and to permit persons to whom the Software
## is furnished to do so, subject to the following conditions:
##
## The above copyright notice and this permission notice
## shall be included in all copies or substantial portions
## of the Software.
##
## THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
## KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
## THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
## PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS
## OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR
## OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
## OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
## SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
##

import time
import os
import copy
import datetime

## call file and folder monitor ##
class FileMonitor():
    def __init__(self):
        self.__file_list = list()
        self.__folder_list = list()
        self.__monitored_file_dict = None      # will be a dict()
        self.__monitored_temp_file_dict = dict()
        self.__poll_interval = 60 * 5    #default 5 minutes
        self.__stop_flag = False
        self.__stop_date_time = None
        self.__file_function_to_call = None
        self.__a_list_of_file_func_args = None
        self.__fldr_function_to_call = None
        self.__a_list_of_fldr_func_args = None
        self.__poll_function_to_call = None
        self.__a_list_of_poll_func_args = None
        self.__msg_for_file_call_bk = list()    # info for file callback
        #self.__msg_for_fldr_call_bk = list()
        self.__msg_for_fldr_created_call_bk = list()
        self.__msg_for_fldr_removed_call_bk = list()
        self.__polling_datetime = None

    def get_poll_datetime(self):
        """getter for the last poll time

           this is meant to be used in a call back like
           the function you would pass to
           set_func_to_call_on_polling(...)
           return type: datetime.datetime
        """
        return self.__polling_datetime

    def set_func_to_call_on_polling(self, function_name, arglist):
        """set the callback function when for when a polling occurs
           ARGS: function_name --> the name of the function to call
                 arglist   --> the args to pass to the callback function
        """
        self.__poll_function_to_call = function_name
        self.__a_list_of_poll_func_args = arglist

    def __call_function_poll_mon(self):
        self.__poll_function_to_call(*self.__a_list_of_poll_func_args)


    def set_file_list(self, filelist):
        """a list of paths and files that you want to
           check for.  this will monitor to see if that
           file(s) exist.
           you can pass a callback function to
           set_func_to_call_file_mon(...) to provide feedback
           and potentially perform an action based on
           that feedback
           ARGS: filelist --> a list of 1 or more
                                  paths and files
        """
        self.__file_list = filelist

    def get_file_list(self):
        return self.__file_list

    def set_folder_list(self, folderlist):
        self.__folder_list = folderlist

    def get_folder_list(self):
        return self.__folder_list

    def get_file_call_bk_msg(self):
        return self.__msg_for_file_call_bk

    def get_folder_created_call_bk_msg(self):
        return self.__msg_for_fldr_created_call_bk

    def get_folder_removed_call_bk_msg(self):
        return self.__msg_for_fldr_removed_call_bk

    def stop_monitor(self):
        self.__stop_flag = True

    def set_stop_datetime(self, thedatetime):
        self.__stop_date_time = thedatetime

    def set_func_to_call_file_mon(self, function_name, arglist):
        self.__file_function_to_call = function_name
        self.__a_list_of_file_func_args = arglist

    def __call_function_file_mon(self):
        self.__file_function_to_call(*self.__a_list_of_file_func_args)

    def set_func_to_call_fldr_mon(self, function_name, arglist):
        self.__fldr_function_to_call = function_name
        self.__a_list_of_fldr_func_args = arglist

    def __call_function_fldr_mon(self):
        self.__fldr_function_to_call(*self.__a_list_of_fldr_func_args)

    def start_monitor(self, int_poll_interval):
        self.__poll_interval = int_poll_interval

        while not self.__stop_flag:                           # stop flag Flase
            current_datetime = datetime.datetime.now()
            self.__polling_datetime = current_datetime
            if self.__stop_date_time is not None and current_datetime >= self.__stop_date_time:
                self.__stop_flag = True
                break

            if self.__poll_function_to_call is not None:
                self.__call_function_poll_mon()

            self.__msg_for_file_call_bk.clear()   # remove old file messages
            #self.__msg_for_fldr_call_bk.clear()   # remove old folder messages
            self.__msg_for_fldr_created_call_bk.clear()   # clear temp list for next iteration
            self.__msg_for_fldr_removed_call_bk.clear()   # ditto

            ### checks on specified file lists ###
            for somefile in self.__file_list:
                # check on file existance
                if os.path.exists(somefile):
                    self.__msg_for_file_call_bk.append([somefile, os.stat(somefile).st_atime])
            if self.__file_function_to_call is not None:
                self.__call_function_file_mon()

                #check for datetime changes on existing file

            ### checks on specified folders ###
            self.__monitored_temp_file_dict.clear()   #clear dict for new data
            for somedir in self.__folder_list:
                filelist = os.listdir(somedir)
                if not somedir.endswith("\\"):
                    somedir += "\\"

                for somefile in filelist:
                    stRes = os.stat(somedir + somefile)
                    self.__monitored_temp_file_dict[somedir + somefile] = [stRes.st_atime, stRes.st_mtime]


            #1) new files
            #2) removed files
            #3) datetime changes (atime,mtime) on existing files

            ## compare folders/files ##

            if self.__monitored_file_dict is not None:
                # new file created?
                for currF in self.__monitored_temp_file_dict:
                    if currF not in self.__monitored_file_dict:
                        #print("created file: " + currF)
                        self.__msg_for_fldr_created_call_bk.append(currF)
                    ## check for time stamp changes

                # old file removed?
                for prevF in self.__monitored_file_dict:
                    if prevF not in self.__monitored_temp_file_dict:
                        #print("Removed file: " + prevF)
                        self.__msg_for_fldr_removed_call_bk.append(prevF)

                if self.__call_function_fldr_mon is not None:
                    self.__call_function_fldr_mon()
            else:
                self.__monitored_file_dict = dict() # set field to a new dictionary

            ## folder monitoring  - update and copy as needed ##

            self.__monitored_file_dict.clear()   # clear current dictionary
            self.__monitored_file_dict = copy.deepcopy(self.__monitored_temp_file_dict)

            if self.__stop_flag == False:
                time.sleep(self.__poll_interval)

                ###  probably need to and a elese and break when true stopflag
