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

    def getPollDatetime(self):
        """getter for the last poll time
           
           this is meant to be used in a call back like
           the function you would pass to 
           setFuncToCallOnPolling(...)
           return type: datetime.datetime
        """
        return self.__polling_datetime

    def setFuncToCallOnPolling(self, aFunctionName, aListOfArgs):
        """set the callback function when for when a polling occurs
           ARGS: aFunctionName --> the name of the function to call
                 aListOfArgs   --> the args to pass to the callback function 
        """
        self.__poll_function_to_call = aFunctionName
        self.__a_list_of_poll_func_args = aListOfArgs

    def __callFunctionPollMon(self):
        self.__poll_function_to_call(*self.__a_list_of_poll_func_args)
        
    
    def setFileList(self, aListOfFiles):
        """a list of paths and files that you want to
           check for.  this will monitor to see if that
           file(s) exist.
           you can pass a callback function to 
           setFuncToCallFileMon(...) to provide feedback
           and potentially perform an action based on
           that feedback
           ARGS: aListOfFiles --> a list of 1 or more 
                                  paths and files
        """
        self.__file_list = aListOfFiles

    def getFileList(self):
        return self.__file_list

    def setFolderList(self, aListOfFolders):
        self.__folder_list = aListOfFolders

    def getFolderList(self):
        return self.__folder_list

    def getFileCallBkMsg(self):
        return self.__msg_for_file_call_bk

    def getFolderCreatedCallBkMsg(self):
        return self.__msg_for_fldr_created_call_bk

    def getFolderRemovedCallBkMsg(self):
        return self.__msg_for_fldr_removed_call_bk
    
    def stopMonitor(self):
        self.__stop_flag = True

    def setStopDateTime(self, aDateTime):
        self.__stop_date_time = aDateTime

    def setFuncToCallFileMon(self, aFunctionName, aListOfArgs):
        self.__file_function_to_call = aFunctionName
        self.__a_list_of_file_func_args = aListOfArgs

    def __callFunctionFileMon(self):
        self.__file_function_to_call(*self.__a_list_of_file_func_args)
        
    def setFuncToCallFldrMon(self, aFunctionName, aListOfArgs):
        self.__fldr_function_to_call = aFunctionName
        self.__a_list_of_fldr_func_args = aListOfArgs

    def __callFunctionFldrMon(self):
        self.__fldr_function_to_call(*self.__a_list_of_fldr_func_args)
        
    def startMonitor(self, intPollInterval):
        self.__poll_interval = intPollInterval

        while self.__stop_flag == False:
            curDtTm = datetime.datetime.now()
            self.__polling_datetime = curDtTm
            if self.__stop_date_time != None and curDtTm >= self.__stop_date_time:
                self.__stop_flag = True
                break

            if self.__poll_function_to_call != None:
                self.__callFunctionPollMon()

            self.__msg_for_file_call_bk.clear()   # remove old file messages
            #self.__msg_for_fldr_call_bk.clear()   # remove old folder messages
            self.__msg_for_fldr_created_call_bk.clear()   # clear temp list for next iteration
            self.__msg_for_fldr_removed_call_bk.clear()   # ditto

            ### checks on specified file lists ###
            for aFile in self.__file_list:
                # check on file existance
                if os.path.exists(aFile):
                    self.__msg_for_file_call_bk.append([aFile, os.stat(aFile).st_atime])
            if self.__file_function_to_call != None:
                self.__callFunctionFileMon()

                #check for datetime changes on existing file

            ### checks on specified folders ###
            self.__monitored_temp_file_dict.clear()   #clear dict for new data
            for aDir in self.__folder_list:
                aFileList = os.listdir(aDir)
                if not aDir.endswith("\\"):
                    aDir += "\\"

                for aFile in aFileList:
                    stRes = os.stat(aDir + aFile)
                    self.__monitored_temp_file_dict[aDir + aFile] = [stRes.st_atime, stRes.st_mtime]
                    

            #1) new files
            #2) removed files
            #3) datetime changes (atime,mtime) on existing files

            ## compare folders/files ##
            
            if self.__monitored_file_dict != None:
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
                        
                if self.__callFunctionFldrMon != None:
                    self.__callFunctionFldrMon()
            else:
                self.__monitored_file_dict = dict() # set field to a new dictionary

            ## folder monitoring  - update and copy as needed ##

            self.__monitored_file_dict.clear()   # clear current dictionary
            self.__monitored_file_dict = copy.deepcopy(self.__monitored_temp_file_dict)

            if self.__stop_flag == False:
                time.sleep(self.__poll_interval)

                ###  probably need to and a elese and break when true stopflag
                    
