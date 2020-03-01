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
        self.__fileList                = list()
        self.__folderList              = list()
        self.__monitoredFileDict       = None      # will be a dict()
        self.__monitoredTempFileDict   = dict()
        self.__pollInterval            = 60 * 5    #default 5 minutes
        self.__stopFlag                = False
        self.__stopDateTime            = None
        self.__fileFunctionToCall      = None
        self.__aListOfFileFuncArgs     = None
        self.__fldrFunctionToCall      = None
        self.__aListOfFldrFuncArgs     = None
        self.__pollFunctionToCall      = None
        self.__aListOfPollFuncArgs     = None
        self.__msgForFileCallBk        = list()    # info for file callback
        #self.__msgForFldrCallBk        = list()
        self.__msgForFldrCreatedCallBk = list()
        self.__msgForFldrRemovedCallBk = list()
        self.__pollingDateTime         = None

    def getPollDatetime(self):
        """getter for the last poll time
           
           this is meant to be used in a call back like
           the function you would pass to 
           setFuncToCallOnPolling(...)
           return type: datetime.datetime
        """
        return self.__pollingDateTime

    def setFuncToCallOnPolling(self, aFunctionName, aListOfArgs):
        """set the callback function when for when a polling occurs
           ARGS: aFunctionName --> the name of the function to call
                 aListOfArgs   --> the args to pass to the callback function 
        """
        self.__pollFunctionToCall = aFunctionName
        self.__aListOfPollFuncArgs = aListOfArgs

    def __callFunctionPollMon(self):
        self.__pollFunctionToCall(*self.__aListOfPollFuncArgs)
        
    
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
        self.__fileList = aListOfFiles

    def getFileList(self):
        return self.__fileList

    def setFolderList(self, aListOfFolders):
        self.__folderList = aListOfFolders

    def getFolderList(self):
        return self.__folderList

    def getFileCallBkMsg(self):
        return self.__msgForFileCallBk

    def getFolderCreatedCallBkMsg(self):
        return self.__msgForFldrCreatedCallBk

    def getFolderRemovedCallBkMsg(self):
        return self.__msgForFldrRemovedCallBk
    
    def stopMonitor(self):
        self.__stopFlag = True

    def setStopDateTime(self, aDateTime):
        self.__stopDateTime = aDateTime

    def setFuncToCallFileMon(self, aFunctionName, aListOfArgs):
        self.__fileFunctionToCall = aFunctionName
        self.__aListOfFileFuncArgs = aListOfArgs

    def __callFunctionFileMon(self):
        self.__fileFunctionToCall(*self.__aListOfFileFuncArgs)
        
    def setFuncToCallFldrMon(self, aFunctionName, aListOfArgs):
        self.__fldrFunctionToCall = aFunctionName
        self.__aListOfFldrFuncArgs = aListOfArgs

    def __callFunctionFldrMon(self):
        self.__fldrFunctionToCall(*self.__aListOfFldrFuncArgs)
        
    def startMonitor(self, intPollInterval):
        self.__pollInterval = intPollInterval

        while self.__stopFlag == False:
            curDtTm = datetime.datetime.now()
            self.__pollingDateTime = curDtTm
            if self.__stopDateTime != None and curDtTm >= self.__stopDateTime:
                self.__stopFlag = True
                break

            if self.__pollFunctionToCall != None:
                self.__callFunctionPollMon()

            self.__msgForFileCallBk.clear()   # remove old file messages
            #self.__msgForFldrCallBk.clear()   # remove old folder messages
            self.__msgForFldrCreatedCallBk.clear()   # clear temp list for next iteration
            self.__msgForFldrRemovedCallBk.clear()   # ditto

            ### checks on specified file lists ###
            for aFile in self.__fileList:
                # check on file existance
                if os.path.exists(aFile):
                    self.__msgForFileCallBk.append([aFile, os.stat(aFile).st_atime])
            if self.__fileFunctionToCall != None:
                self.__callFunctionFileMon()

                #check for datetime changes on existing file

            ### checks on specified folders ###
            self.__monitoredTempFileDict.clear()   #clear dict for new data
            for aDir in self.__folderList:
                aFileList = os.listdir(aDir)
                if not aDir.endswith("\\"):
                    aDir += "\\"

                for aFile in aFileList:
                    stRes = os.stat(aDir + aFile)
                    self.__monitoredTempFileDict[aDir + aFile] = [stRes.st_atime, stRes.st_mtime]
                    

            #1) new files
            #2) removed files
            #3) datetime changes (atime,mtime) on existing files

            ## compare folders/files ##
            
            if self.__monitoredFileDict != None:
                # new file created?
                for currF in self.__monitoredTempFileDict:
                    if currF not in self.__monitoredFileDict:
                        #print("created file: " + currF)
                        self.__msgForFldrCreatedCallBk.append(currF)
                    ## check for time stamp changes

                # old file removed?
                for prevF in self.__monitoredFileDict:
                    if prevF not in self.__monitoredTempFileDict:
                        #print("Removed file: " + prevF)
                        self.__msgForFldrRemovedCallBk.append(prevF)
                        
                if self.__callFunctionFldrMon != None:
                    self.__callFunctionFldrMon()
            else:
                self.__monitoredFileDict = dict() # set field to a new dictionary

            ## folder monitoring  - update and copy as needed ##

            self.__monitoredFileDict.clear()   # clear current dictionary
            self.__monitoredFileDict = copy.deepcopy(self.__monitoredTempFileDict)

            if self.__stopFlag == False:
                time.sleep(self.__pollInterval)

                ###  probably need to and a elese and break when true stopflag
                    
