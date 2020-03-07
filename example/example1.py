import filemonitor.filemonitor
import datetime


################## Callback for polling info #######################
def poll_check(msg):
    """
    set up as a function to call back
    args 
       msg --> str that will be part of the dispay 
               during each poll
    """
    print(msg + str(datetime.datetime.now()))

############### Callback to monitor folders #######################
def action_on_file_changes(a_filemonitor):
    newfiles = a_filemonitor.get_folder_created_call_bk_msg()
    remfiles = a_filemonitor.get_folder_removed_call_bk_msg()
    
    if len(newfiles) > 0:
        print("Folder Monitoring - new files: " + str(newfiles))
    if len(remfiles) > 0:
        print("Folder Monitoring - removed files" + str(remfiles))


###                                    ####
#  set up a instance of the file monitor  #
###                                    ####
fm = filemonitor.filemonitor.FileMonitor()



###                                    ####
#  set up call back for to display info   #
#  each poll                              #
###                                    ####
fm.set_func_to_call_on_polling(poll_check,["example1 polling: "])

fm.set_func_to_call_fldr_mon(action_on_file_changes, [fm])

###                                    ####
#  set up a folder to monitor for file    #
#  changes                                #
###                                    ####
fm.set_folder_list(["./example/a_watched_folder/"])

###                                    ####
#   start monitor with poll interval      #
#   in seconds                            #
###                                    ####
fm.start_monitor(3)

