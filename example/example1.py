import filemonitor.filemonitor
import datetime


################################################
def poll_check(msg):
    """
    set up as a function to call back
    args 
       msg --> str that will be part of the dispay 
               during each poll
    """
    print(msg + str(datetime.datetime.now()))

###                                    ####
#  set up a instance of the file monitor  #
###                                    ####
fm = filemonitor.filemonitor.FileMonitor()

###                                    ####
#  set up call back for to display info   #
#  each poll                              #
###                                    ####
fm.set_func_to_call_on_polling(poll_check,["example1 polling: "])


###                                    ####
#   start monitor with poll interval      #
#   in seconds                            #
###                                    ####
fm.start_monitor(3)

print("complete")